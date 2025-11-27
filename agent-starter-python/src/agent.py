import logging
import os
import json
import time
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        # Minimal instructions - let tools handle the specifics
        super().__init__(
            instructions="""You are a helpful healthcare provider search assistant. 
            Use query_providers to search for providers. Use get_provider_details for specific provider information.
            When presenting search results, prioritize mentioning providers who are currently accepting new patients first.
            If no providers are accepting new patients, mention that the available providers are not currently accepting new patients.
            When no results are found, suggest trying a nearby state instead of narrowing by city.""",
        )
        self._agent_room: Optional[rtc.Room] = None
        self._available_specialties = None
        self._available_languages = None
        self._available_insurance = None

    def _log_tool_call(self, tool_name: str, params: Dict[str, Any], duration_ms: float, success: bool, result_summary: Optional[str] = None) -> None:
        """Log tool call with timing and parameters."""
        log_data = {
            "event": "tool_call",
            "tool": tool_name,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "params": {k: v for k, v in params.items() if v is not None},
        }
        if result_summary:
            log_data["result_summary"] = result_summary
        
        logger.info(f"🔧 TOOL CALL: {tool_name} | Duration: {duration_ms:.2f}ms | Success: {success} | Params: {log_data['params']}")
        if result_summary:
            logger.info(f"   Result: {result_summary}")


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
        specialty: Optional[str] = None,
        language: Optional[str] = None,
        insurance: Optional[str] = None,
        provider_name: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        """Search for healthcare providers matching the given criteria.
        
        Extract and map search criteria from the user's natural language query:
        - Map medical conditions to specialties: "heart problems" → "Cardiology", "kidney issues" → "Nephrology", "radiologist" → "Radiology"
        - Map state names to 2-letter codes: "Texas" → "TX", "California" → "CA"
        - Use exact matches for specialty, language, and insurance from available database values
        
        Parameters:
        - state: 2-letter state code (e.g., "TX", "CA")
        - city: City name
        - specialty: Medical specialty (must match database exactly)
        - language: Language name (must match database exactly)
        - insurance: Insurance name (must match database exactly)
        - provider_name: Full or partial provider name
        - limit: Maximum number of results (default: 5)
        
        Returns JSON with providers array and count.
        """
        start_time = time.time()
        params = {
            "state": state,
            "city": city,
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
                result_summary=f"Found {len(results)} providers"
            )
            
            return result_json
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log_tool_call(
                "query_providers",
                params,
                duration_ms,
                success=False,
                result_summary=f"Error: {str(e)}"
            )
            logger.error(f"Error querying providers: {e}")
            return json.dumps({"providers": [], "count": 0, "error": str(e)})

    @function_tool
    async def get_provider_details(
        self,
        context: RunContext,
        provider_id: int,
    ) -> str:
        """Get complete details for a specific provider by their ID.
        
        Use this when the user asks about a specific provider that was previously returned in search results.
        
        Parameters:
        - provider_id: The numeric ID of the provider
        
        Returns JSON with full provider information including name, specialty, location, contact info, etc.
        """
        start_time = time.time()
        params = {"provider_id": provider_id}
        
        try:
            provider = db_service.get_provider_by_id(provider_id)
            
            if not provider:
                duration_ms = (time.time() - start_time) * 1000
                self._log_tool_call(
                    "get_provider_details",
                    params,
                    duration_ms,
                    success=True,
                    result_summary="Provider not found"
                )
                return json.dumps({"provider": None, "found": False})
            
            # Send to frontend if room is available
            if self._agent_room and provider:
                provider_data = {
                    "type": "provider_data",
                    "data": {
                        "provider": provider,
                        "found": True
                    },
                    "timestamp": int(time.time() * 1000)
                }
                await self._agent_room.local_participant.send_text(
                    json.dumps(provider_data, default=str),
                    topic="lk.provider_data"
                )
            
            result_json = json.dumps({"provider": provider, "found": True}, default=str)
            
            duration_ms = (time.time() - start_time) * 1000
            self._log_tool_call(
                "get_provider_details",
                params,
                duration_ms,
                success=True,
                result_summary=f"Found provider: {provider.get('full_name', 'Unknown') if provider else 'None'}"
            )
            
            return result_json
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log_tool_call(
                "get_provider_details",
                params,
                duration_ms,
                success=False,
                result_summary=f"Error: {str(e)}"
            )
            logger.error(f"Error getting provider details: {e}")
            return json.dumps({"provider": None, "found": False, "error": str(e)})


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
