from pathlib import Path

import pandas as pd
PROJECT_ROOT  = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT /'data'/'raw'/ 'children_processed.csv'
CLEAN_PATH = PROJECT_ROOT /'data'/'clean'/ 'cleaned_children_data.csv'

target_col = 'has_malnutrition'

def clean_data(df: pd.DataFrame) ->pd.DataFrame:
    print(f"[clean] Starting shape: {df.shape}")

    # drop unncessary columns
    features = ['child_sex', 'child_age_months', 'mother_age_years', 'region',
       'residence_urban_rural', 'mother_education_level',
       'mother_education_single_years', 'mother_working_status',
       'wealth_index_quintile', 'wealth_index_score', 'age_at_first_birth',
       'mother_weight_kg', 'mother_bmi_x100', 'child_recent_diarrhea',
       'child_fever_recent', 'drank_from_bottle_recently',
       'fed_tinned_powdered_fresh_milk', 'has_malnutrition',
       'source_of_drinking_water', 'type_of_toilet_facility',
       'type_of_cooking_fuel', 'household_size', 'has_electricity',
       'has_refrigerator', 'main_floor_material', 'main_wall_material',
       'main_roof_material', 'owns_farm_animals_livestock',
       'has_land_suitable_for_agriculture']
    df_cleaned = df[features + ['has_malnutrition']].copy()

    df_cleaned = df_cleaned.dropna(subset=[target_col])
    print(f"[clean] Final shape: {df_cleaned.shape}")

    return df_cleaned

if __name__ == "__main__":
    df_raw = pd.read_csv(RAW_PATH)
    df_clean = clean_data(df_raw)
    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"[clean] Cleaned data saved to {CLEAN_PATH}")