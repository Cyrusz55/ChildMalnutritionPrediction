from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from database.db_connection import get_engine
from database.models import create_tables
from scripts.clean import CLEAN_PATH

def load_clean_data():
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql('DROP TABLE IF EXISTS cleaned_children_data;')

    create_tables(engine)

    df = pd.read_csv(CLEAN_PATH, low_memory=False)
    # pandas may mangle duplicate header names by adding suffixes like '.1'.
    # If that happened (e.g., 'has_malnutrition' and 'has_malnutrition.1'),
    # drop the suffixed duplicates and keep the original.
    import re
    suffixed = [col for col in df.columns if re.match(r"^(.+)\.\d+$", col)]
    to_drop = []
    for col in suffixed:
        base = re.sub(r"\.\d+$", "", col)
        if base in df.columns:
            to_drop.append(col)
    if to_drop:
        print(f"[load] Dropping suffixed duplicate columns from CSV: {to_drop}")
        df = df.drop(columns=to_drop)
    df.to_sql(
        "cleaned_children_data",
        engine,
        if_exists = 'append',
        index = False,
        method = 'multi',
        chunksize = 500
    )
    print('[load] Cleaned data loaded into cleaned_children_data table')

if __name__ == "__main__":
    load_clean_data()