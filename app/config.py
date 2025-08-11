
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Mocking flags
    KAMRUL_USE_MOCK: bool = True
    KAMRUL_MOCK_DIR: str = "./data/mocks"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_ID: str='gen-lang-client-0475373186'
    VERTEX_LOCATION: str = "us-central1"
    VERTEX_MODEL_ID: str = "gemini-2.5-pro"

    GOOGLE_MAPS_API_KEY: str

    KAMRUL_API_BASE: str = "https://api.kamrul.example.com"
    KAMRUL_API_KEY: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    APP_ENV: str = "prod"
    LOG_LEVEL: str = "INFO"
    REQUEST_TIMEOUT_S: float = 25.0
    GRAPH_MAX_RESULTS: int = 7
    GRAPH_MAX_RADIUS_M: int = 10000

    API_KEY_AUTH_ENABLED: bool = False
    API_KEY_HEADER_NAME: str = "x-api-key"
    API_KEY_VALUE: Optional[str] = None
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI:bool

settings = Settings()
