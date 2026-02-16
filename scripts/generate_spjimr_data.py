import pandas as pd
import numpy as np
from pathlib import Path

# 1. Setup paths
data_dir = Path("data/raw")
data_dir.mkdir(parents=True, exist_ok=True)
output_file = data_dir / "campus_data.xlsx"

# 2. Define Building Dimensions (The landmarks)
buildings = {
    "BuildingKey": [1, 2, 3, 4, 5, 6],
    "BuildingName": [
        "SPJIMR ACAD BLOCK", 
        "HOSTEL B30", 
        "HOSTEL B27", 
        "HOSTEL B26", 
        "HOSTEL B25", 
        "REC CENTER"
    ],
    "Floors": [4, 14, 10, 10, 12, 4],
    "Type": ["Academic", "Residential", "Residential", "Residential", "Residential", "Amenities"]
}

# 3. Define Block Dimensions (The internal SPJIMR detail)
blocks = {
    "BlockID": [101, 102, 103, 104, 105, 106],
    "BuildingKey": [1, 1, 1, 1, 3, 6],
    "BlockName": ["Block A", "Block B", "Block C", "Block D", "Night Canteen", "Gym & Mess"],
    "Facilities": [
        "Admin, Accounts, Deans Office",
        "Classrooms, Faculty, Wise Tech Lab",
        "Sim Lab, DT Lab, Group Work",
        "Reading Room, Classrooms",
        "Dining",
        "Fitness, Dining"
    ]
}

# 4. Generate 30 days of "Fact" data
# We ensure every row has a Goal and a Type to satisfy Pydantic
dates = pd.date_range(start="2026-01-15", periods=30)
fact_data = []

for date in dates:
    for key in buildings["BuildingKey"]:
        # Assign realistic base consumption values
        # Hostels (2,3,4,5) consume more than Acad Blocks (1) or Rec Center (6)
        if key in [2, 3, 4, 5]:
            base_goal = 250.0
        else:
            base_goal = 120.0
            
        # Add some random variance to consumption
        actual_consumption = round(base_goal + np.random.normal(0, 25), 2)
        
        fact_data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "BuildingKey": key,
            "Consumption": max(0, actual_consumption), # No negative energy!
            "Goal": base_goal,
            "Type": "Energy"
        })

# 5. Save to Multi-Sheet Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    pd.DataFrame(fact_data).to_excel(writer, sheet_name="Facts", index=False)
    pd.DataFrame(buildings).to_excel(writer, sheet_name="DimBuildings", index=False)
    pd.DataFrame(blocks).to_excel(writer, sheet_name="DimBlocks", index=False)

print(f"✅ SPJIMR Master Data generated successfully at: {output_file}")