from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kids Pokédex"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Fallback to SQLite for immediate local testing without Postgres
        return "sqlite:///./kids_pokedex.db"

    # Auth
    SECRET_KEY: str = "DEVELOPMENT_MODE_SUPER_SECRET_KEY_CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    # ADK / Gemini
    GOOGLE_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = ""

    SARVAM_API_KEY: str = ""
    SARVAM_CHAT_MODEL: str = "sarvam-30b"
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_STT_MODE: str = "transcribe"
    SARVAM_STT_LANGUAGE: str = "unknown"
    SARVAM_TTS_MODEL: str = "bulbul:v3"
    SARVAM_TTS_LANGUAGE: str = "mr-IN"
    SARVAM_TTS_SPEAKER: str = "shruti"
    SARVAM_TTS_PACE: float = 0.75
    SARVAM_TTS_CODEC: str = "mp3"
    SARVAM_LLM_TEMPERATURE: float = 0.2
    SARVAM_LLM_MAX_TOKENS: int = 180
    SARVAM_LLM_REASONING_EFFORT: str = ""
    RUNTIME_TRACE_JSONL: str = "runtime_logs/voice_turns.jsonl"

    model_config = {
        "extra": "ignore",
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
