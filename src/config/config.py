from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # DB connection
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    # Payment provider
    PAYMENT_WEBHOOK_SECRET: str
    DEFAULT_MAX_AGE_SECONDS: int = 60 * 15
    # JWT settings
    JWT_SECRET_KEY: str
    PASS_ALGORITHMS: str = "bcrypt"
    TOKEN_ALGORITHM: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
