"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat, recommendations, reservations

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"]
)

api_router.include_router(
    reservations.router,
    prefix="/reservations",
    tags=["reservations"]
)
