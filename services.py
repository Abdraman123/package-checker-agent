import httpx
from uuid import uuid4
from typing import List, Optional, Dict, Any
from config import get_settings

from models import (
    A2AMessage, TaskResult, TaskStatus, Artifact,
    MessagePart, MessageConfiguration
)

settings = get_settings()

# ⬇️ ADD THIS NEW FUNCTION HERE ⬇️
async def send_to_webhook(webhook_url: str, token: str, result: TaskResult):
    """Send the final result to Telex webhook"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Telex expects the full JSON-RPC response format
    payload = {
        "jsonrpc": "2.0",
        "method": "task/update",
        "params": {
            "taskId": result.id,
            "contextId": result.contextId,
            "status": {
                "state": result.status.state,
                "message": result.status.message.model_dump()
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"✅ Webhook notification sent successfully")
    except Exception as e:
        print(f"❌ Failed to send webhook notification: {e}")
# ⬆️ END OF NEW FUNCTION ⬆️

class PackageChecker:
    """Service for checking package versions from PyPI and npm"""
    
    def __init__(self):
        self.pypi_timeout = settings.pypi_timeout
        self.npm_timeout = settings.npm_timeout
        
    def parse_query(self, query: str) -> tuple[str, Optional[str]]:
        """Parse user query to extract package name and type"""
        query_lower = query.lower()
        
        # Remove common prefixes
        query_lower = query_lower.replace("check ", "")
        query_lower = query_lower.replace("version of ", "")
        query_lower = query_lower.replace("latest ", "")
        query_lower = query_lower.replace("info for ", "")
        query_lower = query_lower.replace("about ", "")
        
        # Detect package type
        package_type = None
        if "npm" in query_lower or "javascript" in query_lower or "node" in query_lower:
            package_type = "npm"
            query_lower = query_lower.replace("npm", "").replace("javascript", "").replace("node", "")
        elif "pip" in query_lower or "python" in query_lower or "pypi" in query_lower:
            package_type = "pypi"
            query_lower = query_lower.replace("pip", "").replace("python", "").replace("pypi", "")
        
        package_name = query_lower.strip()
        return package_name, package_type
    
    async def get_pypi_package(self, package_name: str) -> Dict[str, Any]:
        """Fetch package info from PyPI"""
        url = f"https://pypi.org/pypi/{package_name}/json"
        
        try:
            async with httpx.AsyncClient(timeout=self.pypi_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                info = data.get("info", {})
                return {
                    "found": True,
                    "source": "PyPI",
                    "name": info.get("name", package_name),
                    "version": info.get("version", "Unknown"),
                    "description": info.get("summary", "No description"),
                    "author": info.get("author", "Unknown"),
                    "license": info.get("license", "Unknown"),
                    "homepage": info.get("home_page") or info.get("project_url", ""),
                    "requires_python": info.get("requires_python", "Any"),
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"found": False, "source": "PyPI", "name": package_name, "error": "Package not found"}
            return {"found": False, "source": "PyPI", "name": package_name, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"found": False, "source": "PyPI", "name": package_name, "error": str(e)}
    
    async def get_npm_package(self, package_name: str) -> Dict[str, Any]:
        """Fetch package info from npm"""
        url = f"https://registry.npmjs.org/{package_name}"
        
        try:
            async with httpx.AsyncClient(timeout=self.npm_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                latest_version = data.get("dist-tags", {}).get("latest", "Unknown")
                
                return {
                    "found": True,
                    "source": "npm",
                    "name": data.get("name", package_name),
                    "version": latest_version,
                    "description": data.get("description", "No description"),
                    "author": data.get("author", {}).get("name", "Unknown") if isinstance(data.get("author"), dict) else str(data.get("author", "Unknown")),
                    "license": data.get("license", "Unknown"),
                    "homepage": data.get("homepage", ""),
                    "repository": data.get("repository", {}).get("url", "") if isinstance(data.get("repository"), dict) else str(data.get("repository", "")),
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"found": False, "source": "npm", "name": package_name, "error": "Package not found"}
            return {"found": False, "source": "npm", "name": package_name, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"found": False, "source": "npm", "name": package_name, "error": str(e)}
    
    async def get_package_smart(self, package_name: str) -> Dict[str, Any]:
        """Try both PyPI and npm, return the first successful result"""
        
        # Try PyPI first (backend internship)
        pypi_result = await self.get_pypi_package(package_name)
        if pypi_result.get("found"):
            return pypi_result
        
        # Try npm if PyPI fails
        npm_result = await self.get_npm_package(package_name)
        if npm_result.get("found"):
            return npm_result
        
        # Both failed
        return {
            "found": False,
            "name": package_name,
            "error": "Package not found in PyPI or npm"
        }
    
    def format_response(self, package_info: Dict[str, Any], package_name: str) -> str:
        """Format package info into a readable response"""
        
        if not package_info.get("found"):
            error_msg = package_info.get("error", "Unknown error")
            return f"❌ Could not find package '{package_name}'\n\nError: {error_msg}"
        
        source = package_info.get("source", "Unknown")
        name = package_info.get("name", package_name)
        version = package_info.get("version", "Unknown")
        description = package_info.get("description", "No description")
        author = package_info.get("author", "Unknown")
        license_info = package_info.get("license", "Unknown")
        homepage = package_info.get("homepage", "")
        
        response = f"📦 {name} (from {source})\n\n"
        response += f"Version: {version}\n"
        response += f"Description: {description}\n"
        response += f"Author: {author}\n"
        response += f"License: {license_info}\n"
        
        if homepage:
            response += f"Homepage: {homepage}\n"
        
        if source == "PyPI":
            requires_python = package_info.get("requires_python", "Any")
            response += f"Requires Python: {requires_python}\n"
            response += f"\nInstall: `pip install {name}`"
        elif source == "npm":
            repository = package_info.get("repository", "")
            if repository:
                response += f"Repository: {repository}\n"
            response += f"\nInstall: `npm install {name}`"
        
        return response

async def process_package_query(
    messages: List[A2AMessage],
    context_id: Optional[str] = None,
    task_id: Optional[str] = None,
    config: Optional[MessageConfiguration] = None
) -> TaskResult:
    """Process incoming messages and check package versions"""
    
    # Generate IDs if not provided
    context_id = context_id or str(uuid4())
    task_id = task_id or str(uuid4())
    
    # Extract last user message
    user_message = messages[-1] if messages else None
    if not user_message:
        raise ValueError("No message provided")
    
    # Extract query from message
    query_text = ""
    for part in user_message.parts:
        if part.kind == "text":
            query_text = part.text.strip()
            break
    
    if not query_text:
        raise ValueError("No text content in message")
    
    # Initialize checker
    checker = PackageChecker()
    
    # Parse the query
    package_name, package_type = checker.parse_query(query_text)
    
    # Fetch package information
    if package_type == "pypi":
        package_info = await checker.get_pypi_package(package_name)
    elif package_type == "npm":
        package_info = await checker.get_npm_package(package_name)
    else:
        # Try both
        package_info = await checker.get_package_smart(package_name)
    
    # Build response message
    response_text = checker.format_response(package_info, package_name)
    
    response_message = A2AMessage(
        role="agent",
        parts=[MessagePart(kind="text", text=response_text)],
        taskId=task_id
    )
    
    # Build artifacts
    artifacts = [
        Artifact(
            name="package_info",
            parts=[MessagePart(kind="data", data=package_info)]
        )
    ]
    
    # Build history
    history = messages + [response_message]
    
    return TaskResult(
        id=task_id,
        contextId=context_id,
        status=TaskStatus(
            state="completed",
            message=response_message
        ),
        artifacts=artifacts,
        history=history
    )