from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    @property
    def async_db_url(self) -> str:
        """Construct the asynchronous database URL."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()