from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Green Li-ion Recycling ERP"
    debug: bool = False
    database_url: str = "postgresql://erp:erp@localhost:5432/battery_erp"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_prefix": "ERP_"}


settings = Settings()
