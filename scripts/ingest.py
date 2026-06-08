from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from database.db_connection import get_engine

RAW_CSV_PATH = PROJECT_ROOT/ "data/raw/children_processed.csv"
TARGET_TABLE = "raw_children_data"
RAW_COLUMNS = [
    'region',
    'child_sex',
    'residence_urban_rural',
    'fed_tinned_powdered_fresh_milk',
    'mother_age_years',
    'mother_education_level',
    'mother_marital_status',
    'mother_working_status',
    'wealth_index_quintile',
    'child_recent_diarrhea',
    'child_fever_recent',
    'breastfeeding_status',
    'source_of_drinking_water',
    'type_of_toilet_facility',
    'type_of_cooking_fuel',
    'has_electricity',
    'has_refrigerator',
    'main_floor_material',
    'main_wall_material',
    'main_roof_material',
    'owns_farm_animals_livestock',
    'has_land_suitable_for_agriculture',
    'owns_agricultural_land',

    'child_age_months',
    'wealth_index_score',
    'children_ever_born',
    'birth_order',
    'mother_height_cm',

    'has_malnutrition',
]
def ingest_raw_data():
    engine = get_engine()
    df = pd.read_csv(RAW_CSV_PATH, usecols = RAW_COLUMNS, low_memory=False)
    df = df.dropna(subset = ['has_malnutrition'])
    print(f"[ingest] Loaded {len(df)} rows from {RAW_CSV_PATH}")
    print(f"[ingest] Columns: {list(df.columns)}")

    with engine.begin() as conn:
        conn.exec_driver_sql(f"DROP TABLE IF EXISTS {TARGET_TABLE} CASCADE")

    df.to_sql(
        TARGET_TABLE,
        con = engine,
        if_exists = 'replace',
        index=False,
        chunksize = 1000,
        method = 'multi',
    )
    print("[ingest] Raw data loaded inton raw_children_data table")
if __name__ == "__main__":
    ingest_raw_data()
