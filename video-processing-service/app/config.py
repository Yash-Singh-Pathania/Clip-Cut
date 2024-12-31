from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_channel: str = "video_channel"
    quality: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
