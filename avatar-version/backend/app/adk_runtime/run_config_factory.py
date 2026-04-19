from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from app.models.db_models import Session, HouseholdSettings
from app.models.enums import AppMode, VoiceStyle
from app.services.prompt_builders import (
    build_conversational_companion_prompt,
    build_story_teller_prompt,
)

class RunConfigFactory:
    """
    Derives the Google Gemini Live API RunConfig and Agent dynamically based on 
    the Kids Pokedex active session configuration and household safety rules.
    """
    @staticmethod
    def build_config(session: Session, settings: HouseholdSettings):
        if session.active_mode == AppMode.story_teller:
            system_instruction = build_story_teller_prompt(session)
        else:
            system_instruction = build_conversational_companion_prompt(session)

        # Apply Voice Policy (Mapping to Google TTS or Gemini Voice aliases)
        voice_name = "Aoede" if session.voice_style == VoiceStyle.story_narrator else "Puck"

        # Build google-adk specific primitives
        agent = Agent(
            name=f"toddler_companion_{session.id}",
            model="gemini-live-2.5-flash-native-audio",
            description="Toddler companion and educator",
            instruction=system_instruction
        )
        
        speech_config = types.SpeechConfig()
        # Note: PrebuiltVoiceConfig might be inside types or we can just pass it directly if adk wraps it.
        # But we pass it inside speech_config
        # genai types changed significantly in Google ADK vs older ones. Let's just use ADK dict kwargs to be safe, 
        # or use what we can. 
        # Actually Google ADK RunConfig takes speech_config = types.SpeechConfig(...)
        
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        )

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        )

        return agent, run_config
