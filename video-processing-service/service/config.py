from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "redis-service"
    redis_port: int = 6379
    redis_channel: str = "video_uploads"
    quality: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
