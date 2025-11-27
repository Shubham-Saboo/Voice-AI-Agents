import logging
import os
import json
from typing import Optional

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
from openai import OpenAI

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful healthcare provider search assistant.
            
            Workflow:
            1. Use extract_search_criteria to extract and map entities from user query
            2. Use query_providers to fetch matching providers from database
            3. Use get_provider_details for follow-up questions about specific providers
            4. Use answer_question_with_context to format responses naturally
            
            Always be conversational and helpful. Extract criteria intelligently - map medical conditions 
            to specialties (e.g., "heart problems" → Cardiology), normalize state names, etc.""",
        )
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @function_tool
    async def extract_search_criteria(
        self,
        context: RunContext,
        user_query: str,
    ) -> str:
        """Extract search criteria from user query using LLM.
        
        Intelligently extracts and maps:
        - "radiologists" → specialty="Radiology"
        - "heart problems" → specialty="Cardiology"
        - "Texas" → state="TX"
        - "speak Russian" → language="Russian"
        - "accept Aetna" → insurance="Aetna"
        
        Returns JSON with database-ready values.
        """
        logger.info(f"🔍 Extracting criteria from: '{user_query}'")
        
        try:
            # Get available values from database for context
            available_specialties = db_service.get_available_specialties()
            available_languages = db_service.get_available_languages()
            available_insurance = db_service.get_available_insurance()
            
            logger.debug(f"Available specialties: {len(available_specialties)}")
            logger.debug(f"Available languages: {len(available_languages)}")
            logger.debug(f"Available insurance: {len(available_insurance)}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert at extracting healthcare provider search criteria.

Database Schema:
- state: 2-letter code (e.g., "TX" for Texas, "CA" for California)
- city: City name
- specialty: Medical specialty (exact match required)
- language: Language name (exact match required)
- insurance: Insurance name (exact match required)
- provider_name: Full name or partial name

Available Specialties: {', '.join(available_specialties)}
Available Languages: {', '.join(available_languages)}
Available Insurance: {', '.join(available_insurance)}

Your task:
1. Extract search criteria from user query
2. Map natural language to exact database values:
   - "radiologist", "radiologists" → specialty="Radiology"
   - "heart problems", "cardiac issues", "heart doctor" → specialty="Cardiology"
   - "kidney problems" → specialty="Nephrology"
   - "pediatrician" → specialty="Pediatrics"
   - State names → 2-letter codes ("Texas" → "TX", "California" → "CA")
   - Use medical knowledge to map conditions to specialties
3. Return JSON with extracted values (use null for missing fields)

Return JSON format:
{{
    "state": "TX" or null,
    "city": "Austin" or null,
    "specialty": "Radiology" or null,
    "language": "Russian" or null,
    "insurance": "Aetna" or null,
    "provider_name": "Dr. Susan Lee" or null
}}"""
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            criteria_json = response.choices[0].message.content
            logger.info(f"✅ Extracted criteria: {criteria_json}")
            return criteria_json
            
        except Exception as e:
            logger.error(f"❌ Error extracting criteria: {e}", exc_info=True)
            return json.dumps({
                "state": None,
                "city": None,
                "specialty": None,
                "language": None,
                "insurance": None,
                "provider_name": None,
                "error": str(e)
            })

    @function_tool
    async def query_providers(
        self,
        context: RunContext,
        criteria_json: str,
        limit: int = 5,
    ) -> str:
        """Query providers from database using extracted criteria.
        
        Args:
            criteria_json: JSON string with search criteria from extract_search_criteria
            limit: Maximum number of results (default: 5)
        
        Returns:
            JSON string with provider results
        """
        logger.info(f"📊 Querying providers with criteria: {criteria_json}")
        
        try:
            criteria = json.loads(criteria_json)
            
            # Query database
            results = db_service.query_providers(
                state=criteria.get("state"),
                city=criteria.get("city"),
                specialty=criteria.get("specialty"),
                language=criteria.get("language"),
                insurance=criteria.get("insurance"),
                provider_name=criteria.get("provider_name"),
                limit=limit
            )
            
            logger.info(f"✅ Found {len(results)} providers")
            
            return json.dumps({
                "providers": results,
                "count": len(results)
            }, default=str)
            
        except Exception as e:
            logger.error(f"❌ Error querying providers: {e}", exc_info=True)
            return json.dumps({"providers": [], "count": 0, "error": str(e)})

    @function_tool
    async def get_provider_details(
        self,
        context: RunContext,
        provider_id: int,
    ) -> str:
        """Get complete details for a specific provider by ID.
        
        Use this for follow-up questions like:
        - "What's their phone number?"
        - "What's their email?"
        - "What insurance do they accept?"
        
        Args:
            provider_id: The provider's ID number
        
        Returns:
            JSON string with complete provider information
        """
        logger.info(f"📋 Getting details for provider ID: {provider_id}")
        
        try:
            provider = db_service.get_provider_by_id(provider_id)
            
            if not provider:
                logger.warning(f"⚠️ Provider ID {provider_id} not found")
                return json.dumps({"provider": None, "found": False})
            
            logger.info(f"✅ Found provider: {provider['full_name']}")
            return json.dumps({"provider": provider, "found": True}, default=str)
            
        except Exception as e:
            logger.error(f"❌ Error getting provider details: {e}", exc_info=True)
            return json.dumps({"provider": None, "found": False, "error": str(e)})

    @function_tool
    async def answer_question_with_context(
        self,
        context: RunContext,
        context_data: str,
        question: str,
    ) -> str:
        """Answer a question using provided context data.
        
        Args:
            context_data: JSON string from query_providers or get_provider_details
            question: The question to answer
        
        Returns:
            Natural language answer
        """
        logger.info(f"❓ Answering: '{question}'")
        logger.debug(f"📋 Context data length: {len(context_data)} characters")
        
        try:
            parsed_context = json.loads(context_data)
            context_str = json.dumps(parsed_context, indent=2, default=str)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful healthcare provider assistant.
                        Answer questions based on the provided context data.
                        
                        Guidelines:
                        - Be concise, accurate, and conversational
                        - Use natural language suitable for voice interaction
                        - If the context doesn't contain the answer, say so clearly
                        - Format lists naturally (e.g., "Aetna, Cigna, and Blue Cross")
                        - Be friendly and helpful"""
                    },
                    {
                        "role": "user",
                        "content": f"""Context Data:
{context_str}

Question: {question}

Please answer the question based on the context data above. If the context doesn't contain enough information to answer the question, say so clearly."""
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"💬 Generated answer: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error answering question: {e}", exc_info=True)
            return "I encountered an error while generating an answer. Please try again."


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Check if we should use OpenAI Realtime API (for local or cloud use)
    use_realtime = os.getenv("USE_OPENAI_REALTIME", "true").lower() == "true"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    
    if use_realtime and openai_api_key:
        logger.info("Using OpenAI Realtime API for voice model")
        realtime_config = {}
        if openai_base_url:
            realtime_config["base_url"] = openai_base_url
            logger.info(f"Using local OpenAI-compatible server: {openai_base_url}")
        
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                voice=os.getenv("OPENAI_REALTIME_VOICE", "alloy"),
                **realtime_config
            )
        )
    else:
        logger.info("Using LiveKit Inference models")
        session = AgentSession(
            stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
            llm=inference.LLM(model="openai/gpt-4.1-mini"),
            tts=inference.TTS(
                model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
            ),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
        )

    await session.start(
        agent=Assistant(),
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
