from pydantic import BaseModel, Field
from typing import List, Optional

# --- Dimension Schemas ---

class BuildingDim(BaseModel):
    """Schema for the DimBuildings sheet."""
    BuildingKey: int
    BuildingName: str
    TotalFloors: int
    Type: str  # e.g., Academic, Residential, Amenities

class BlockDim(BaseModel):
    """Schema for the DimBlocks sheet (The SPJIMR wings)."""
    BlockID: int
    BuildingKey: int
    BlockName: str
    Facilities: Optional[str] = None

# --- Fact & Response Schemas ---

class ConsumptionFact(BaseModel):
    """Schema for the main Facts sheet."""
    Date: str
    BuildingKey: int
    Consumption: float
    Goal: float
    MetricType: str = "Energy"

class JoinedDashboardData(BaseModel):
    """
    The 'Final' structure we send to Lovable.
    Combines ID numbers with real names like 'SPJIMR ACAD BLOCK'.
    """
    Date: str
    BuildingName: str
    Consumption: float
    Goal: float
    Type: str
    is_anomaly: bool = False

class DashboardResponse(BaseModel):
    """The top-level JSON response for the frontend."""
    status: str = "success"
    data: List[JoinedDashboardData]