"""
Orchestrator Service Entry Point
"""
import os
import sys
sys.path.insert(0, '/app/modules')

from module_3_main_orchestrator import UnjaiOrchestrator

if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Nong Unjai Orchestrator")
    orchestrator = UnjaiOrchestrator()
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "orchestrator"}
    
    @app.post("/process")
    async def process(request: dict):
        return await orchestrator.process_message(
            user_id=request["user_id"],
            message=request["message"],
            session=request.get("session")
        )
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    
    print(f"🚀 Starting Orchestrator on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
