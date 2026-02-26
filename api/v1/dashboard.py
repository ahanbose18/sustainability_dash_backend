from fastapi import APIRouter, HTTPException
import pandas as pd
from services.data_analytics import DataAnalyticsService
from models.schemas import DashboardResponse
from utils.logger import logger

# Initialize the router and service
# The prefix /dashboard ensures URLs like http://127.0.0.1:8000/dashboard/metrics
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
data_service = DataAnalyticsService()

@router.get("/metrics", response_model=DashboardResponse)
async def get_campus_metrics():
    """
    Fetch comprehensive sustainability metrics for SPJIMR.
    The Service layer now handles:
    1. Joining Facts + Blocks + Buildings (Snowflake Join)
    2. Isolation Forest Anomaly Detection
    3. Cleaning NaNs and Renaming columns to match the Response Model
    """
    logger.info("Request received: Fetching comprehensive campus metrics.")
    
    try:
        # Retrieve the fully processed and enriched data from the service
        final_list = data_service.get_joined_dashboard_data()
        
        if not final_list:
            logger.warning("No data found or processed from the Excel source.")
            return {"status": "success", "data": []}

        logger.info(f"Successfully returning {len(final_list)} rows of validated ESG data.")
        
        # Return the clean dictionary list directly to the Pydantic validator
        return {
            "status": "success",
            "data": final_list
        }
        
    except Exception as e:
        logger.error(f"Failed to process dashboard metrics: {e}")
        # Raising a 500 here if Pydantic validation fails or data is missing
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/alerts")
async def get_sustainability_alerts():
    """
    Returns ONLY the anomalies detected in the last cycle.
    Filters the enriched data for rows where 'is_anomaly' is True.
    """
    try:
        data = data_service.get_joined_dashboard_data()
        if not data:
            return {"status": "success", "alerts": []}

        # Filter for only the anomalies using list comprehension
        alerts = [row for row in data if row.get('is_anomaly') is True]
        
        return {
            "status": "success",
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        logger.error(f"Alerts endpoint failed: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/summary")
async def get_dashboard_summary():
    """
    Returns high-level summary statistics (Total Energy, Water, CO2).
    """
    try:
        stats = data_service.get_summary_stats()
        return {
            "status": "success",
            "summary": stats
        }
    except Exception as e:
        logger.error(f"Summary endpoint failed: {e}")
        return {"status": "error", "summary": {}}