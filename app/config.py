from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    db_name: str = "enddocument.db"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    @property
    def async_db_url(self) -> str:
        """Construct the asynchronous database URL."""
        return f"sqlite+aiosqlite:///{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
