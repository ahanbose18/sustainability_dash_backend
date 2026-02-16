import pandas as pd
from config.settings import settings
from utils.logger import logger
from sklearn.ensemble import IsolationForest
import numpy as np
class DataAnalyticsService:
    def __init__(self):
        self.file_path = settings.excel_path
    
    def detect_anomalies(self, df):
        """
        Uses Isolation Forest to flag unusual consumption spikes.
        Returns the dataframe with an 'is_anomaly' boolean column.
        """
        if df.empty or len(df) < 5:  # Need a minimum amount of data to find patterns
            df['is_anomaly'] = False
            return df

        # 1. Initialize the Model
        # contamination=0.05 means we expect about 5% of data to be anomalies
        model = IsolationForest(contamination=0.05, random_state=42)

        # 2. Reshape data and Predict
        # We only train the model on the 'Consumption' column
        consumption_values = df[['Consumption']].values
        df['anomaly_score'] = model.fit_predict(consumption_values)

        # 3. Map results (-1 is an anomaly in sklearn, 1 is normal)
        df['is_anomaly'] = df['anomaly_score'].map({1: False, -1: True})
        
        # Clean up temporary score column
        df = df.drop(columns=['anomaly_score'])
        
        return df
    
   
    def get_joined_dashboard_data(self):
        try:
            all_sheets = pd.read_excel(self.file_path, sheet_name=None)
            facts_df = all_sheets["Facts"]
            buildings_df = all_sheets["DimBuildings"]

            # Rename the 'Type' in DimBuildings to 'Category' BEFORE the merge
            # This prevents the Type_x / Type_y conflict
            buildings_df = buildings_df.rename(columns={"Type": "BuildingCategory"})

            # Perform Join
            merged_df = facts_df.merge(buildings_df, on="BuildingKey", how="inner")
            
            # Ensure the Date is clean
            merged_df['Date'] = pd.to_datetime(merged_df['Date']).dt.strftime('%Y-%m-%d')
            
            # Convert to dictionary
            return merged_df.to_dict(orient="records")

        except Exception as e:
            logger.error(f"SERVICE ERROR: {str(e)}")
            return []

        
    def get_summary_stats(self):
        """Optional: Calculate high-level stats for dashboard cards."""
        data = self.get_joined_dashboard_data()
        if not data:
            return {}
            
        df = pd.DataFrame(data)
        return {
            "total_consumption": round(df['Consumption'].sum(), 2),
            "avg_efficiency": round(df['Consumption'].mean(), 2),
            "top_consumer": df.groupby('BuildingName')['Consumption'].sum().idxmax()
        }