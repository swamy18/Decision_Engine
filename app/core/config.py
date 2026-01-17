from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Decision Engine"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Model Configuration
    # In a real app, these would be API keys and such
    MODEL_PROVIDER: str = "mock" # Options: mock, openai, anthropic
    
    # Thresholds
    CONFIDENCE_THRESHOLD_HIGH: float = 0.90
    CONFIDENCE_THRESHOLD_MEDIUM: float = 0.70

settings = Settings()
