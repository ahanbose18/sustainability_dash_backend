import pandas as pd
import os

def transform_all_months(file_path):
    # Load the Excel file object to access all sheets
    xl = pd.ExcelFile(file_path)
    all_dfs = []

    print(f"Processing file: {file_path}")

    for sheet in xl.sheet_names:
        # Step 1: Read the sheet with NO header to find where the table actually starts
        # This prevents the "datetime" or "Unnamed" error you saw earlier
        df_search = pd.read_excel(xl, sheet_name=sheet, header=None)
        
        # Step 2: Find the row index that contains the string "Waste type"
        # We search the entire dataframe for the keyword
        mask = df_search.apply(lambda row: row.astype(str).str.contains('Waste type', case=False).any(), axis=1)
        header_indices = df_search.index[mask].tolist()

        if not header_indices:
            print(f"⚠️ Skipping sheet '{sheet}': Could not find 'Waste type' column.")
            continue
            
        actual_header_row = header_indices[0]
        
        # Step 3: Re-read the sheet using the correctly identified header row
        df_raw = pd.read_excel(xl, sheet_name=sheet, header=actual_header_row)
        
        # Step 4: Clean column names (strip whitespace)
        df_raw.columns = [str(col).strip() for col in df_raw.columns]

        # Step 5: Check if 'Waste type' exists after cleaning
        if "Waste type" not in df_raw.columns:
            print(f"❌ Error in sheet '{sheet}': 'Waste type' not found in columns {df_raw.columns.tolist()}")
            continue

        # Step 6: Perform the Melt
        # We identify value_vars by taking all columns EXCEPT 'Waste type'
        value_columns = [col for col in df_raw.columns if col != "Waste type" and "Unnamed" not in col]
        
        df_melted = df_raw.melt(
            id_vars=["Waste type"],
            value_vars=value_columns,
            var_name="Month",
            value_name="Value"
        )
        
        # Add a column to track which sheet this came from
        df_melted["Source_Sheet"] = sheet
        all_dfs.append(df_melted)
        print(f"✅ Successfully processed sheet: {sheet}")

    if not all_dfs:
        print("No data was collected. Check your Excel formatting.")
        return None

    # Step 7: Consolidate everything into one master dataframe
    consolidated_data = pd.concat(all_dfs, ignore_index=True)
    
    # Step 8: Final Cleanup (remove rows where Value is NaN)
    consolidated_data = consolidated_data.dropna(subset=["Value"])
    
    return consolidated_data

# --- Execution ---
input_file = "data/raw/Waste_Collection_Data_2025.xlsx"

if os.path.exists(input_file):
    final_data = transform_all_months(input_file)
    if final_data is not None:
        # Save the cleaned data
        output_path = "data/processed/Cleaned_Waste_Data_2025.csv"
        os.makedirs("data/processed", exist_ok=True)
        final_data.to_csv(output_path, index=False)
        print(f"\n🚀 Success! Cleaned data saved to: {output_path}")
        print(final_data.head())
else:
    print(f"File not found: {input_file}")