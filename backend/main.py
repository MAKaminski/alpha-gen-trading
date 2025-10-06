from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the path to import alphagen modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers import auth, market_data, websocket
from services.schwab_client import SchwabWebSocketService
from models.schemas import WebSocketMessage, MarketDataResponse

app = FastAPI(
    title="Alpha-Gen API",
    description="API for Alpha-Gen trading system with real-time market data",
    version="1.0.0"
)

# CORS middleware - Railway production configuration
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://alpha-gen.vercel.app",  # Vercel frontend
    "https://alpha-gen-git-main.vercel.app",  # Vercel preview
]

# Add Railway domain when available
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    allowed_origins.append(f"https://{railway_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Global WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_data_service = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def start_market_data_stream(self):
        """Start the market data streaming service."""
        if not self.market_data_service:
            self.market_data_service = SchwabWebSocketService(self.broadcast)
            await self.market_data_service.start()

    async def stop_market_data_stream(self):
        """Stop the market data streaming service."""
        if self.market_data_service:
            await self.market_data_service.stop()
            self.market_data_service = None

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Alpha-Gen API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections)
    }

@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "start_stream":
                await manager.start_market_data_stream()
                await manager.send_personal_message(
                    json.dumps({"type": "stream_status", "data": {"active": True}}),
                    websocket
                )
            elif message.get("type") == "stop_stream":
                await manager.stop_market_data_stream()
                await manager.send_personal_message(
                    json.dumps({"type": "stream_status", "data": {"active": False}}),
                    websocket
                )
            elif message.get("type") == "change_time_scale":
                # Handle time scale change
                scale = message.get("scale", "1min")
                await manager.send_personal_message(
                    json.dumps({"type": "time_scale_changed", "data": {"scale": scale}}),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
