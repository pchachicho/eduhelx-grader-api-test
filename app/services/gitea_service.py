from typing import List, Optional
from enum import Enum
from app.core.config import settings
import httpx
import base64
from pydantic import BaseModel

class FileOperationType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class FileOperation(BaseModel):
    content: str
    path: str
    from_path: Optional[str] = None
    operation: FileOperationType

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

    async def modify_repository_files(
        self,
        name: str,
        owner: str,
        branch_name: str,
        commit_message: str,
        files: List[FileOperation]
    ):
        files = [f.dict() for f in files]
        for file in files:
            if file["operation"] == FileOperationType.UPDATE or file["operation"] == FileOperationType.DELETE:
                raise NotImplementedError("File modify/delete is not implemented in Gitea Assist yet (requires sha)")
            # Gitea expects file content to be base64-encoded
            file["content"] = base64.b64encode(file["content"].encode("utf-8")).decode("utf-8")
        
        res = await self._post("/repos/modify", json={
            "name": name,
            "owner": owner,
            "branch": branch_name,
            "message": commit_message,
            "files": files
        })