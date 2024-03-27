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
        res.raise_for_status()
        return res

    async def _get(self, endpoint: str, **kwargs):
        return await self._make_request("GET", endpoint, **kwargs)

    async def _post(self, endpoint: str, **kwargs):
        return await self._make_request("POST", endpoint, **kwargs)
    
    async def create_organization(self, organization_name: str):
        await self._post("/orgs", json={
            "org_name": organization_name
        })
    
    async def add_user_to_organization(self, organization_name: str, onyen: str):
        await self._post(f"/orgs/{organization_name}/members/{onyen}")

    async def create_user(
        self,
        username: str,
        email: str,
        password: str
    ):
        await self._post("/users", json={
            "username": username,
            "email": email,
            "password": password
        })
    
    async def create_repository(
        self,
        name: str,
        description: str,
        owner: str,
        private: bool=False
    ) -> str:
        res = await self._post("/repos", json={
            "name": name,
            "description": description,
            "owner": owner,
            "private": private
        })
        remote_url = await res.text()
        return remote_url
    
    async def fork_repository(
        self,
        name: str,
        owner: str,
        new_owner: str
    ):
        res = await self._post("/forks", json={
            "name": name,
            "owner": owner,
            "newOwner": new_owner
        })
        remote_url = await res.text()
        return remote_url