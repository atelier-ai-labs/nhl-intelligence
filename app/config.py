from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    dashboard_api_url: str
    openai_api_key: str | None
    openai_model: str
    allowed_origins: list[str]


def get_settings() -> Settings:
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    return Settings(
        dashboard_api_url=os.getenv(
            "NHL_DASHBOARD_API_URL",
            "https://nhl-dashboard-api.bravecoast-a5240643.westus2.azurecontainerapps.io",
        ).rstrip("/"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
        allowed_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
    )
