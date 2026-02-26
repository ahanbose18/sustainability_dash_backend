from pydantic import BaseModel, Field
from typing import List, Optional

# --- Dimension Schemas ---

class BuildingDim(BaseModel):
    """Schema for the DimBuildings sheet."""
    BuildingKey: int
    BuildingName: str
    TotalFloors: int
    BuildingCategory: str  # e.g., Academic, Residential, Amenities

class BlockDim(BaseModel):
    """Schema for the DimBlocks sheet (The SPJIMR wings)."""
    BlockID: int
    BuildingKey: int
    BlockName: str
    Facilities: Optional[str] = None

# --- Fact & Response Schemas ---

# class ValueFact(BaseModel):
#     """Schema for the main Facts sheet."""
#     Date: str
#     BuildingKey: int
#     Value: float
#     Goal: float
#     MetricBuildingCategory: str = "Energy"

class JoinedDashboardData(BaseModel):
    """
    The 'Final' structure we send to Lovable.
    Combines ID numbers with real names like 'SPJIMR ACAD BLOCK'.
    """
    Date: str
    BuildingName: str
    BlockID: int
    BlockName: str
    Value: float
    Goal: float
    BuildingCategory: str
    CO2_Emissions: float
    is_anomaly: bool = False
    anomaly_type: str = "Normal"  # "High (Waste)", "Low (Potential Failure)", or "Normal"

class DashboardSummary(BaseModel):
    """Schema for the top-level summary statistics."""
    total_value: float
    avg_value: float
    total_co2: float
    avg_co2: float
    top_consumer_building: str
    top_consumer_block: str
    low_anomalies: int
    high_anomalies: int

class DashboardResponse(BaseModel):
    """The top-level JSON response for the frontend."""
    status: str = "success"
    data: List[JoinedDashboardData]