from fastapi import APIRouter, HTTPException
import pandas as pd
from services.data_analytics import DataAnalyticsService
from models.schemas import DashboardResponse
from utils.logger import logger

# Initialize the router and service
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
data_service = DataAnalyticsService()

@router.get("/metrics", response_model=DashboardResponse)
async def get_campus_metrics():
    """
    Fetch comprehensive sustainability metrics for SPJIMR.
    Includes: 
    1. Joining Facts with Building Dimensions
    2. Running Isolation Forest for Anomaly Detection
    """
    logger.info("Request received: Fetching comprehensive campus metrics.")
    
    try:
        # 1. Retrieve the joined data (Facts + Building Names)
        raw_data = data_service.get_joined_dashboard_data()
        
        if not raw_data:
            logger.warning("No data found in the Excel source.")
            return {"status": "success", "data": []}

        # 2. Convert to DataFrame to run AI/Analytics
        df = pd.DataFrame(raw_data)

        # 3. Apply Anomaly Detection (Isolation Forest)
        # This adds the 'is_anomaly' boolean to our dataset
        df_enriched = data_service.detect_anomalies(df)

        # 4. Final cleaning for JSON response
        final_list = df_enriched.to_dict(orient="records")
        
        logger.info(f"Returning {len(final_list)} rows with anomaly detection applied.")
        return {
            "status": "success",
            "data": final_list
        }
        
    except Exception as e:
        logger.error(f"Failed to process dashboard metrics: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing SPJIMR campus data. Check logs for details."
        )

@router.get("/alerts")
async def get_sustainability_alerts():
    """
    Returns ONLY the anomalies detected in the last cycle.
    Perfect for an 'Alerts' or 'Action Required' panel in Lovable.
    """
    raw_data = data_service.get_joined_dashboard_data()
    if not raw_data:
        return {"status": "success", "alerts": []}

    df = pd.DataFrame(raw_data)
    df_enriched = data_service.detect_anomalies(df)
    
    # Filter for only the anomalies
    alerts = df_enriched[df_enriched['is_anomaly'] == True]
    
    return {
        "status": "success",
        "count": len(alerts),
        "alerts": alerts.to_dict(orient="records")
    }

@router.get("/summary")
async def get_dashboard_summary():
    """
    Returns high-level cards: Total Consumption, Top Consumer, and Efficiency.
    """
    stats = data_service.get_summary_stats()
    return {
        "status": "success",
        "summary": stats
    }