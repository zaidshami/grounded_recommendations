#!/usr/bin/env python3
"""
Startup script for the Guest Recommendation Generation API
Production-grade FastAPI application
"""

import uvicorn
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings

def main():
    """Start the FastAPI server"""
    # Display configuration
    print(f" Configuration:")
    print(f"   App Name: {settings.APP_NAME}")
    print(f"   Version: {settings.APP_VERSION}")
    print(f"   Host: {settings.HOST}")
    print(f"   Port: {settings.PORT}")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   Reload: {settings.RELOAD}")
    print(f"   Vertex AI Model: {settings.GEMINI_MODEL}")
    print(f"   Max Recommendations: {settings.DEFAULT_MAX_RECOMMENDATIONS}")
    
    # Check Google Cloud configuration
    print(f"\n  Google Cloud Configuration:")
    print(f"   Project: {'[OK] ' + settings.GOOGLE_CLOUD_PROJECT if settings.GOOGLE_CLOUD_PROJECT else '[ERROR] Not set'}")
    print(f"   Location: {settings.GOOGLE_CLOUD_LOCATION}")
    print(f"   Service Account: {'[OK] Enabled' if settings.USE_SERVICE_ACCOUNT else '[WARNING] Disabled'}")
    
    # Check optional API keys
    print(f"\n Optional API Keys:")
    print(f"   Google Places: {'[OK] Set' if settings.GOOGLE_PLACES_API_KEY else '[WARNING] Optional (not set)'}")
    
    # Check required configuration
    if not settings.GOOGLE_CLOUD_PROJECT or settings.GOOGLE_CLOUD_PROJECT == "your_google_cloud_project_id":
        print("\n ERROR: Google Cloud Project ID is required!")
        print("   Set GOOGLE_CLOUD_PROJECT environment variable or update .env file")
        sys.exit(1)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
