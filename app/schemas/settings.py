from pydantic import BaseModel

class SettingsSchema(BaseModel):
    gitea_ssh_url: str