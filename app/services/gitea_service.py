from typing import List
from app.core.config import settings
import httpx

class GiteaService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=f"{ self.api_url }",
            headers={
                "User-Agent": f"eduhelx_grader_api"
            }
        )

    @property
    def api_url(self) -> str:
        return settings.GITEA_ASSIST_API_URL
    
    async def _make_request(self, method: str, endpoint: str, headers={}, **kwargs):
        res = await self.client.request(
            method,
            endpoint,
            headers={
                **headers
            },
            **kwargs
        )
        return await self._handle_response(res)

    async def _get(self, endpoint: str, **kwargs):
        return await self._make_request("GET", endpoint, **kwargs)

    async def _post(self, endpoint: str, **kwargs):
        return await self._make_request("POST", endpoint, **kwargs)
    
    async def create_organization(organization_name: str):
        ...
    
    async def add_user_to_organization(organization_name: str, onyen: str):
        ...
    
    async def create_repository(
        self,
        name: str,
        description: str,
        owner: str,
        private: bool=False
    ) -> str:
        remote_url = await self._post("/repos", json={
            "name": name,
            "description": description,
            "owner": owner,
            "private": private
        })
        return remote_url
    
    async def fork_repository(
        self,
        name: str,
        owner: str,
        new_owner: str
    ):
        await self._post("/forks", json={
            "name": name,
            "owner": owner,
            "newOwner": new_owner
        })