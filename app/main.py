"""
Main FastAPI application for the Guest Recommendation Generation API.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
from datetime import datetime

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and logging errors."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error processing request: {e}")
            error_response = {
                "error": "Internal server error",
                "detail": str(e),
                "path": str(request.url)
            }
            return HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Guest Recommendation Generation API...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"Google Cloud configured:")
    logger.info(f"  - Project: {'[OK] ' + settings.GOOGLE_CLOUD_PROJECT if settings.GOOGLE_CLOUD_PROJECT else '[ERROR]'}")
    logger.info(f"  - Location: {settings.GOOGLE_CLOUD_LOCATION}")
    logger.info(f"  - Service Account: {'[OK]' if settings.USE_SERVICE_ACCOUNT else '[WARNING]'}")
    
    logger.info(f"Optional API Keys:")
    logger.info(f"  - Google Places: {'[OK]' if settings.GOOGLE_PLACES_API_KEY else '[WARNING]'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Guest Recommendation Generation API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test basic functionality
        from app.services.recommendation_service import RecommendationService
        
        # Initialize service to test model connection
        service = RecommendationService()
        model_status = await service.test_model_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "operational",
                "vertex_ai_model": "operational" if model_status else "degraded",
                "reservations_api": "operational"
            },
            "model_info": {
                "name": settings.GEMINI_MODEL,
                "project": settings.GOOGLE_CLOUD_PROJECT,
                "location": settings.GOOGLE_CLOUD_LOCATION,
                "connection": "working" if model_status else "failed"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Root endpoint that serves the UI
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Gemini Agent API</title></head>
            <body>
                <h1>🤖 Gemini Agent API</h1>
                <p>API is running successfully!</p>
                <ul>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/docs">API Documentation</a> (if DEBUG enabled)</li>
                    <li><a href="/api/v1">API Endpoints</a></li>
                </ul>
                <p><strong>Note:</strong> UI not found. Make sure static/index.html exists.</p>
            </body>
        </html>
        """)

# Test Google Places API endpoint
@app.get("/test-google-places")
async def test_google_places():
    """Test if Google Places API is working."""
    if not settings.GOOGLE_PLACES_API_KEY:
        return {
            "status": "error",
            "message": "Google Places API key is not configured",
            "solution": "Set GOOGLE_PLACES_API_KEY environment variable or add to .env file"
        }
    
    try:
        # Test with a simple search
        import requests
        test_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": "Aura New Haven Hotel",
            "key": settings.GOOGLE_PLACES_API_KEY
        }
        
        response = requests.get(test_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return {
                    "status": "success",
                    "message": "Google Places API is working correctly",
                    "api_status": data.get("status"),
                    "results_count": len(data.get("results", []))
                }
            else:
                return {
                    "status": "error",
                    "message": f"Google Places API returned status: {data.get('status')}",
                    "error_message": data.get("error_message", "No error message provided")
                }
        else:
            return {
                "status": "error",
                "message": f"Google Places API request failed with status code: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Google Places API: {str(e)}"
        }
