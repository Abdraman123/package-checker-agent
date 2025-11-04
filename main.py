from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from models import JSONRPCRequest, JSONRPCResponse
from services import process_package_query

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="An AI agent that checks package versions from PyPI and npm",
    version=settings.version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "Check package versions from PyPI and npm",
        "endpoints": {
            "a2a": "/a2a/package",
            "health": "/health"
        },
        "usage": {
            "examples": [
                "Check fastapi",
                "Latest version of express",
                "npm package react",
                "python package django"
            ]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "package-checker",
        "version": settings.version
    }

@app.post("/a2a/package")
async def a2a_endpoint(request: Request):
    """Main A2A endpoint for package checker agent"""
    body = None
    try:
        # Parse request body
        body = await request.json()
        
        # Check if body is empty
        if not body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: Empty request body"
                    }
                }
            )
        
        # Validate JSON-RPC request
        if body.get("jsonrpc") != "2.0":
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0'"
                    }
                }
            )
        
        if "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: id is required"
                    }
                }
            )
        
        # Parse and validate with Pydantic
        rpc_request = JSONRPCRequest(**body)
        
        # Extract messages and configuration
        messages = []
        context_id = None
        task_id = None
        config = None
        
        if rpc_request.method == "message/send":
            messages = [rpc_request.params.message]
            config = rpc_request.params.configuration
        elif rpc_request.method == "execute":
            messages = rpc_request.params.messages
            context_id = rpc_request.params.contextId
            task_id = rpc_request.params.taskId
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {rpc_request.method}"
                    }
                }
            )
        
        # Process with package checker service
        result = await process_package_query(
            messages=messages,
            context_id=context_id,
            task_id=task_id,
            config=config
        )
        
        # Build response
        response = JSONRPCResponse(
            id=rpc_request.id,
            result=result
        )
        
        return response.model_dump()
    
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if body else None,
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {"details": str(e)}
                }
            }
        )
    
    except Exception as e:
        # Handle JSON parsing errors
        error_msg = str(e)
        if "Expecting value" in error_msg or "JSON" in error_msg:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON in request body",
                        "data": {"details": "Please provide a valid JSON-RPC 2.0 request"}
                    }
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if body else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"details": error_msg}
                }
            }
        )

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting {settings.app_name} on port {settings.port}")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)