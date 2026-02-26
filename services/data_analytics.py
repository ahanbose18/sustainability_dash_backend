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
        Uses Isolation Forest to flag unusual Value levels.
        Categorizes anomalies as 'High (Waste)' or 'Low (Potential Failure)'.
        """
        if df.empty or len(df) < 5:
            df['is_anomaly'] = False
            df['anomaly_type'] = "Normal"
            return df

        # 1. Initialize the Model
        model = IsolationForest(contamination=0.05, random_state=42)

        # 2. Reshape data and Predict
        Value_values = df[['Value']].values
        df['anomaly_score'] = model.fit_predict(Value_values)

        # 3. Map results (1 is normal, -1 is anomaly)
        df['is_anomaly'] = df['anomaly_score'].map({1: False, -1: True})
        
        # 4. CATEGORIZATION LOGIC: Distinguish High vs Low
        # We compare Value to Goal to determine the 'direction' of the anomaly
        df['anomaly_type'] = "Normal"
        
        # High Anomaly (Value significantly exceeds Goal)
        df.loc[(df['is_anomaly']) & (df['Value'] > df['Goal']), 'anomaly_type'] = "High (Waste)"
        
        # Low Anomaly (Value is significantly below Goal)
        df.loc[(df['is_anomaly']) & (df['Value'] <= df['Goal']), 'anomaly_type'] = "Low (Potential Failure)"
        
        # Clean up temporary score column
        df = df.drop(columns=['anomaly_score'])
        
        return df
    
    def get_joined_dashboard_data(self):
        try:
            all_sheets = pd.read_excel(self.file_path, sheet_name=None)
            facts_df = all_sheets["Facts"]
            buildings_df = all_sheets["DimBuildings"]
            blocks_df = all_sheets["DimBlocks"]

            # Prevent Type_x conflict
            buildings_df = buildings_df.rename(columns={"Type": "BuildingCategory"})

            #First Join: Facts + Buildings (to get BuildingName and Category)
            merged_df = facts_df.merge(blocks_df[['BlockID', 'BlockName', 'BuildingKey']], 
            on="BlockID", 
            how="inner")         
            # Perform Join
            
            merged_df = facts_df.merge(buildings_df[['BuildingKey', 'BuildingName', 'BuildingCategory']], 
            on="BuildingKey", 
            how="inner")
            
            #Second Join: merged_df + Blocks (to get BlockName)
            merged_df = merged_df.merge(blocks_df, on="BlockID", how="inner")

            # RUN ANOMALY DETECTION on the merged dataframe
            # This ensures 'Goal' is available for the High/Low comparison logic
            merged_df = self.detect_anomalies(merged_df)
            
            # Ensure the Date is clean
            merged_df['Date'] = pd.to_datetime(merged_df['Date']).dt.strftime('%Y-%m-%d')
            

            # Convert to dictionary
            return merged_df.to_dict(orient="records")

        except Exception as e:
            logger.error(f"SERVICE ERROR: {str(e)}")
            return []

    def get_summary_stats(self):
        data = self.get_joined_dashboard_data()
        if not data:
            return {}
            
        df = pd.DataFrame(data)
        
        # Add anomaly counts to stats
        low_count = len(df[df['anomaly_type'] == "Low (Potential Failure)"])
        high_count = len(df[df['anomaly_type'] == "High (Waste)"])
        stats = {
            "total_value": round(df['Value'].sum(), 2),
            "avg_value": round(df['Value'].mean(), 2),
            
            # --- NEW CO2 METRICS ---
            "total_co2": round(df['CO2_Emissions'].sum(), 2) if 'CO2_Emissions' in df.columns else 0,
            "avg_co2": round(df['CO2_Emissions'].mean(), 2) if 'CO2_Emissions' in df.columns else 0,
            
            # Leaderboard & Admin Insights
            "top_consumer_building": df.groupby('BuildingName')['Value'].sum().idxmax(),
            "top_consumer_block": df.groupby('BlockName')['Value'].sum().idxmax() if 'BlockName' in df.columns else "N/A",
            
            "low_anomalies": low_count,
            "high_anomalies": high_count
        }
        return stats