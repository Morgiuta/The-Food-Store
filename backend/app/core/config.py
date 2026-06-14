from secrets import token_urlsafe

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "catalogo_productos"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    secret_key: str = Field(default_factory=lambda: token_urlsafe(32), min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # MercadoPago (Checkout Pro)
    mp_access_token: str = ""
    mp_public_key: str = ""
    mp_notification_url: str = ""
    mp_webhook_secret: str = ""

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # URL base del frontend para construir las back_urls de Checkout Pro
    frontend_url: str = "http://localhost:5173"

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
