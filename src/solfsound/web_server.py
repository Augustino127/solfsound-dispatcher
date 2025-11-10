"""
Web Server for SolfSound Dispatcher

Serves the web interface and API.
"""

import os
import logging
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .web_api import app as api_app

logger = logging.getLogger(__name__)

# Get static files directory
STATIC_DIR = Path(__file__).parent / "web" / "static"

# Mount API
app = FastAPI(title="SolfSound Dispatcher Web Server")
app.mount("/api", api_app)

# Serve static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        """Serve the main index page."""
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "SolfSound Dispatcher Web Server",
            "api": "/api",
            "docs": "/api/docs",
        }


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the web server.

    Args:
        host: Host to bind to (0.0.0.0 for all interfaces)
        port: Port to listen on
        reload: Enable auto-reload for development
    """
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           🎵 SolfSound Dispatcher Web Server 🎵              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

    Server starting...

    📱 Web Interface:    http://localhost:{port}
    🔧 API Docs:         http://localhost:{port}/api/docs
    🌐 Network Access:   http://{host}:{port} (accessible from other devices)

    Press Ctrl+C to stop the server
    """)

    uvicorn.run(
        "solfsound.web_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
