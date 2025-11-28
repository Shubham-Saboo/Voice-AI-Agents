import logging
import os
import json
import time
import uuid
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
    function_tool,
    RunContext,
)
from livekit.plugins import noise_cancellation, silero, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from db_service import db_service

# Configure logging only once (prevent duplicate handlers)
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=False  # Don't override existing configuration
    )
logger = logging.getLogger("agent")
# Prevent propagation to root logger to avoid LiveKit's duplicate logging
logger.propagate = False
# Add our own handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        # Minimal instructions - let tools handle the specifics
        super().__init__(
            instructions="""You are a helpful healthcare provider search assistant. 
            Use query_providers to search for providers whenever the user asks about finding doctors, providers, or healthcare professionals. 
            The query_providers tool returns complete provider information including all details (name, specialty, location, contact info, insurance, languages, etc.).
            If the user asks about a specific provider by name, use query_providers with the provider_name parameter.
            If the user query is very broad, ask clarifying questions regarding zip code, city, or state and their insurance provider.
            When presenting search results, prioritize mentioning providers who are currently accepting new patients first.
            If no providers are accepting new patients, mention that the available providers are not currently accepting new patients.
            When a state-level search returns zero results, NEVER suggest narrowing by city. Instead, suggest trying a nearby state or searching nationwide.
            Don't ask clarifying questions if you have enough information to perform a search - just call the tool and present results.""",
        )
        self._agent_room: Optional[rtc.Room] = None
        self._available_specialties = None
        self._available_languages = None
        self._available_insurance = None

    def _log_tool_call(self, tool_name: str, params: Dict[str, Any], duration_ms: float, success: bool, result_summary: Optional[str] = None, call_id: Optional[str] = None) -> None:
        """Log tool call with timing and parameters."""
        call_id_str = f"[{call_id}] " if call_id else ""
        params_str = {k: v for k, v in params.items() if v is not None}
        
        # Single log line to prevent duplicates
        logger.info(
            f"🔧 TOOL CALL: {call_id_str}{tool_name} | Duration: {duration_ms:.2f}ms | Success: {success} | "
            f"Params: {params_str}" + (f" | Result: {result_summary}" if result_summary else "")
        )


    def _get_available_values(self):
        """Cache available values to avoid repeated DB calls."""
        if self._available_specialties is None:
            self._available_specialties = db_service.get_available_specialties()
            self._available_languages = db_service.get_available_languages()
            self._available_insurance = db_service.get_available_insurance()
        return (
            self._available_specialties,
            self._available_languages,
            self._available_insurance,
        )

    @function_tool
    async def query_providers(
        self,
        context: RunContext,
        state: Optional[str] = None,
        city: Optional[str] = None,
        zipcode: Optional[str] = None,
        specialty: Optional[str] = None,
        language: Optional[str] = None,
        insurance: Optional[str] = None,
        provider_name: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        """Search for healthcare providers matching the given criteria.
        
        This tool returns COMPLETE provider information including all details: name, specialty, location, 
        contact info (phone, email), address, insurance accepted, languages spoken, rating, years of experience, 
        license number, board certification status, and whether accepting new patients.
        
        Extract and map search criteria from the user's natural language query:
        - Map medical conditions to specialties: "heart problems" → "Cardiology", "kidney issues" → "Nephrology", "radiologist" → "Radiology"
        - Map state names to 2-letter codes: "Texas" → "TX", "California" → "CA"
        - Use exact matches for specialty, language, and insurance from available database values
        - If user asks about a specific provider by name, use provider_name parameter
        
        Parameters:
        - state: 2-letter state code (e.g., "TX", "CA")
        - city: City name
        - zipcode: ZIP code
        - specialty: Medical specialty (must match database exactly)
        - language: Language name (must match database exactly)
        - insurance: Insurance name (must match database exactly)
        - provider_name: Full or partial provider name (use this when user asks about a specific doctor/provider)
        - limit: Maximum number of results (default: 5)
        
        Returns JSON with providers array (containing full details) and count.
        """
        # Unique call ID to track if function is called multiple times
        call_id = str(uuid.uuid4())[:8]
        logger.debug(f"[{call_id}] query_providers called")
        
        start_time = time.time()
        params = {
            "state": state,
            "city": city,
            "zipcode": zipcode,
            "specialty": specialty,
            "language": language,
            "insurance": insurance,
            "provider_name": provider_name,
            "limit": limit,
        }
        
        try:
            # Get available values for validation hints
            specialties, languages, insurances = self._get_available_values()
            
            # Validate and suggest corrections if needed
            if specialty and specialty not in specialties:
                # Find closest match
                specialty_lower = specialty.lower()
                matches = [s for s in specialties if specialty_lower in s.lower() or s.lower() in specialty_lower]
                if matches:
                    specialty = matches[0]
                    logger.info(f"Matched specialty '{specialty}' from user input")
            
            results = db_service.query_providers(
                state=state,
                city=city,
                zipcode=zipcode,
                specialty=specialty,
                language=language,
                insurance=insurance,
                provider_name=provider_name,
                limit=limit
            )
            
            # Send to frontend if room is available
            if self._agent_room and results:
                provider_data = {
                    "type": "provider_data",
                    "data": {
                        "providers": results,
                        "count": len(results)
                    },
                    "timestamp": int(time.time() * 1000)
                }
                try:
                    json_payload = json.dumps(provider_data, default=str)
                    logger.info(f"Sending provider data to frontend: {len(results)} providers")
                    await self._agent_room.local_participant.send_text(
                        json_payload,
                        topic="lk.provider_data"
                    )
                except Exception as e:
                    logger.error(f"Failed to send provider data: {e}", exc_info=True)
            
            result_json = json.dumps({
                "providers": results,
                "count": len(results)
            }, default=str)
            
            duration_ms = (time.time() - start_time) * 1000
            self._log_tool_call(
                "query_providers",
                params,
                duration_ms,
                success=True,
                result_summary=f"Found {len(results)} providers",
                call_id=call_id
            )
            
            logger.debug(f"[{call_id}] query_providers completed in {duration_ms:.2f}ms")
            return result_json
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log_tool_call(
                "query_providers",
                params,
                duration_ms,
                success=False,
                result_summary=f"Error: {str(e)}",
                call_id=call_id
            )
            logger.error(f"[{call_id}] Error querying providers: {e}", exc_info=True)
            return json.dumps({"providers": [], "count": 0, "error": str(e)})

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    use_realtime = os.getenv("USE_OPENAI_REALTIME", "true").lower() == "true"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    
    if use_realtime and openai_api_key:
        realtime_config = {}
        if openai_base_url:
            realtime_config["base_url"] = openai_base_url
        
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                voice=os.getenv("OPENAI_REALTIME_VOICE", "alloy"),
                **realtime_config
            )
        )
    else:
        # Use gpt-5-nano for extraction (cheapest OpenAI model for entity extraction)
        # Use gpt-5-mini for general LLM tasks (better performance, still affordable)
        # Available OpenAI models: openai/gpt-5-nano, openai/gpt-5-mini, openai/gpt-3.5-turbo, openai/gpt-4.1-mini
        llm_model = os.getenv("LLM_MODEL", "openai/gpt-5-nano")
        
        session = AgentSession(
            stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
            llm=inference.LLM(model=llm_model),
            tts=inference.TTS(
                model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
            ),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
        )

    assistant = Assistant()
    assistant._agent_room = ctx.room
    
    await session.start(
        agent=assistant,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
