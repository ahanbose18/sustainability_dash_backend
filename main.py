import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.dashboard import router as dashboard_router
from config.settings import settings
from utils.logger import logger

# 1. Initialize FastAPI with metadata
app = FastAPI(
    title=settings.app_name,
    description="Backend API for SPJIMR Sustainability Dashboard",
    version="1.0.0-mvp"
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
# This is CRITICAL for Lovable to be able to talk to your local machine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include Versioned API Routes
# All dashboard routes will now start with /api/v1/dashboard
app.include_router(dashboard_router, prefix="/api/v1")

# 4. Health Check Endpoint
@app.get("/", tags=["Health"])
async def health_check():
    """Verifies the API is online and the logger is working."""
    logger.info("Health check pinged.")
    return {
        "status": "online",
        "environment": "development",
        "campus": "SPJIMR Mumbai"
    }

# 5. Execution Logic
if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} on http://0.0.0.0:8000")
    # reload=True automatically restarts the server when you save code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)