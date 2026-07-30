from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    backblaze_key_id: str = ""
    backblaze_application_key: str = ""
    backblaze_bucket: str = ""
    backblaze_endpoint: str = ""

    app_name: str = "Headcanon"
    app_version: str = "0.1.0"
    debug: bool = False


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
