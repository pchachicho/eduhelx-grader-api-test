from typing import Optional, Any, Dict, List
from enum import Enum
from pydantic import BaseSettings, PostgresDsn, validator

class DevPhase(str, Enum):
    DEV = "dev"
    PROD = "prod"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DEV_PHASE: DevPhase = DevPhase.PROD

    PGHOST: str
    PGPORT: str = "5432"
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str): return v
        return PostgresDsn.build(
            scheme="postgresql",
            host=values.get("PGHOST"),
            port=values.get("PGPORT"),
            path="/" + values.get("PGDATABASE"),
            user=values.get("PGUSER"),
            password=values.get("PGPASSWORD")
        )

    class Config:
        case_sensitive = True


settings = Settings()