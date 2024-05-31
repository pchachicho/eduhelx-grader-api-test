from typing import List, Optional
from enum import Enum
from io import BytesIO
from pydantic import BaseModel
from app.core.config import settings
from app.core.utils.header import parse_content_disposition_header
import httpx
import base64

class FileOperationType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class FileOperation(BaseModel):
    content: str
    path: str
    from_path: Optional[str] = None
    operation: FileOperationType

class CollaboratorPermission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

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
    
    async def _put(self, endpoint: str, **kwargs):
        return await self._make_request("PUT", endpoint, **kwargs)
    
    async def _patch(self, endpoint: str, **kwargs):
        return await self._make_request("PATCH", endpoint, **kwargs)
    
    async def _delete(self, endpoint: str, **kwargs):
        return await self._make_request("DELETE", endpoint, **kwargs)
    
    async def create_organization(
        self,
        organization_name: str
    ) -> None:
        await self._post("/orgs", json={
            "org_name": organization_name
        })
    
    async def add_user_to_organization(
        self,
        organization_name: str,
        onyen: str
    ) -> None:
        await self._put(f"/orgs/{organization_name}/members/{onyen}")

    async def add_collaborator_to_repo(
        self,
        name: str,
        owner: str,
        collaborator_name: str,
        # Gitea will use WRITE by default if None.
        # NOTE: case-sensitive.
        permission: CollaboratorPermission | None = CollaboratorPermission.WRITE
    ) -> None:
        await self._put("/repos/collaborators", json={
            "name": name,
            "owner": owner,
            "collaborator_name": collaborator_name,
            "permission": permission
        })

    async def remove_collaborator_from_repo(
        self,
        name: str,
        owner: str,
        collaborator_name: str
    ) -> None:
        await self._delete("/repos/collaborators", json={
            "name": name,
            "owner": owner,
            "collaborator_name": collaborator_name
        })
        

    async def create_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> None:
        await self._post("/users", json={
            "username": username,
            "email": email,
            "password": password
        })

    async def delete_user(
        self,
        username: str,
        purge: bool=False
    ) -> None:
        await self._delete("/users", json={
            "username": username,
            "purge": purge
        })
    
    """ Returns the remote URL of the repository. """
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
        remote_url = res.text
        return remote_url
    
    """ Returns the remote URL of the repository. """
    async def fork_repository(
        self,
        name: str,
        owner: str,
        new_owner: str
    ) -> str:
        res = await self._post("/forks", json={
            "repo": name,
            "owner": owner,
            "newOwner": new_owner
        })
        remote_url = res.text
        return remote_url
    
    """ Returns the remote URL of the repository (the remote URL is subject to change if repository is renamed). """
    async def modify_repository(
        self,
        name: str,
        owner: str,
        new_name: str | None = None,
        new_description: str | None = None,
        new_private: bool | None = None
    ) -> str:
        data = {}
        if new_name is not None: data["name"] = new_name
        if new_description is not None: data["description"] = new_description
        if new_private is not None: data["private"] = new_private
        res = await self._patch("/repos", params={
            "name": name,
            "owner": owner
        }, json=data)
        new_remote_url = res.text
        return new_remote_url
    
    """ Returns a zipped archive of the branch/commit as a byte stream """
    async def download_repository(
        self,
        name: str,
        owner: str,
        treeish_id: str,
        path: str | None = None
    ) -> BytesIO:
        res = await self._get("/repos/download", params={
            "name": name,
            "owner": owner,
            "treeish_id": treeish_id,
            "path": path
        })
        content_disposition = res.headers.get("Content-Disposition")
        file_name = parse_content_disposition_header(content_disposition)[1].get("filename")
        file_stream = BytesIO(res.content)
        file_stream.name = file_name
        return file_stream
    
    async def modify_repository_files(
        self,
        name: str,
        owner: str,
        branch_name: str,
        commit_message: str,
        files: List[FileOperation]
    ):
        for file in files:
            if file.operation == FileOperationType.UPDATE or file.operation == FileOperationType.DELETE:
                raise NotImplementedError("File modify/delete is not implemented in Gitea Assist yet (requires sha)")
            # Gitea expects file content to be base64-encoded
            file.content = base64.b64encode(file.content.encode("utf-8")).decode("utf-8")
        
        res = await self._post("/repos/modify", json={
            "name": name,
            "owner": owner,
            "branch": branch_name,
            "message": commit_message,
            "files": files
        })
    
    async def set_ssh_key(
        self,
        username: str,
        name: str,
        key: str
    ):
        res = await self._post("/users/ssh", json={
            "key_name": name,
            "key": key,
            "username": username
        })
    
    async def remove_ssh_key(
        self,
        username: str,
        key_name: str
    ):
        res = await self._delete("/users/ssh", json={
            "key_name": key_name,
            "username": username
        })