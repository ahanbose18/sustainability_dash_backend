import pandas as pd
import numpy as np
from pathlib import Path

# Setup paths
data_dir = Path("data/raw")
data_dir.mkdir(parents=True, exist_ok=True)
output_file = data_dir / "campus_data.xlsx"

# 1. Dimensions: Buildings
buildings_df = pd.DataFrame({
    "BuildingKey": [1, 2],
    "BuildingName": ["SPJIMR ACAD BLOCK", "HOSTEL B30"],
    "Type": ["Academic", "Residential"]
})

# 2. Dimensions: Blocks (Granular Level)
blocks_df = pd.DataFrame({
    "BlockID": [101, 102, 103, 104],
    "BuildingKey": [1, 1, 2, 2],
    "BlockName": ["Admin Wing", "Classrooms", "B30 North", "B30 South"]
})

# 3. Facts: Generation (Now with BlockID)
dates = pd.date_range(start="2026-01-15", periods=30)
fact_data = []

for date in dates:
    for _, block in blocks_df.iterrows():
        b_id = block["BlockID"]
        b_key = block["BuildingKey"]
        
        # Simulated Consumption Value
        val = round(20.0 + np.random.normal(0, 5), 2)
        
        fact_data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "BuildingKey": b_key,
            "BlockID": b_id,      # <--- New Granular Column
            "Value": val,
            "Goal": 25.0,
            "Resource": "Energy",
            "Unit": "kWh",
            "Source": "Grid",
            "CO2_Emissions": round(val * 0.82, 2)
        })

# Save to Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    pd.DataFrame(fact_data).to_excel(writer, sheet_name="Facts", index=False)
    buildings_df.to_excel(writer, sheet_name="DimBuildings", index=False)
    blocks_df.to_excel(writer, sheet_name="DimBlocks", index=False)

print(f"✅ Fresh Excel generated with BlockID at {output_file}")