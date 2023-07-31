from typing import Optional, Any, Dict, List
from enum import Enum
from pydantic import BaseSettings, PostgresDsn, validator

class DevPhase(str, Enum):
    DEV = "dev"
    PROD = "prod"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DEV_PHASE: DevPhase = DevPhase.PROD

    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        print("values")
        print(values)
        if isinstance(v, str): return v
        return PostgresDsn.build(
            scheme="postgresql",
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path="/" + values.get("POSTGRES_DB"),
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD")
        )

    class Config:
        case_sensitive = True


settings = Settings()
