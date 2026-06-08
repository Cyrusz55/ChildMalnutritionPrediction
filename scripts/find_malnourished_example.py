import json
import pandas as pd
from fastapi.testclient import TestClient

from apps.main import app

DATA_PATH = "data/clean/cleaned_children_data.csv"


def pick(value, allowed, default):
    if pd.isna(value):
        return default
    value = str(value)
    return value if value in allowed else default


def build_payload(row):
    # Allowed values from apps/schemas.py
    region_allowed = {
        'Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita Taveta',
        'Garissa', 'Wajir', 'Mandera', 'Marsabit', 'Isiolo', 'Meru',
        'Tharaka Nithi', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua',
        'Nyeri', 'Kirinyaga', "Murang'a", 'Kiambu', 'Turkana', 'West Pokot',
        'Samburu', 'Trans Nzoia', 'Uasin Gishu', 'Elgeyo Marakwet', 'Nandi',
        'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Kericho',
        'Bomet', 'Kakamega', 'Vihiga', 'Bungoma', 'Busia', 'Siaya',
        'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi'
    }

    payload = {
        "region": pick(row.get("region"), region_allowed, "Nairobi"),
        "child_sex": pick(row.get("child_sex"), {"Male", "Female"}, "Male"),
        "child_age_months": int(float(row.get("child_age_months", 24)) if not pd.isna(row.get("child_age_months")) else 24),
        "residence_urban_rural": pick(row.get("residence_urban_rural"), {"Urban", "Rural"}, "Rural"),
        "mother_education_level": pick(row.get("mother_education_level"), {"No Education", "Primary", "Secondary", "Higher"}, "No Education"),
        "mother_marital_status": "Married",
        "mother_working_status": pick(row.get("mother_working_status"), {"No", "Yes"}, "No"),
        "wealth_index_quintile": pick(row.get("wealth_index_quintile"), {"Poorest", "Poorer", "Middle", "Richer", "Richest"}, "Poorest"),
        "wealth_index_score": float(row.get("wealth_index_score", -5.0)) if not pd.isna(row.get("wealth_index_score")) else -5.0,
        "child_recent_diarrhea": pick(row.get("child_recent_diarrhea"), {"No", "Yes, last 24 hours", "Yes, last two weeks", "Don't know"}, "No"),
        "child_fever_recent": pick(row.get("child_fever_recent"), {"No", "Yes", "Don't know"}, "No"),
        "breastfeeding_status": "Never breastfed",
        "drank_from_bottle_recently": pick(row.get("drank_from_bottle_recently"), {"No", "Yes", "Don't know"}, "No"),
        "fed_tinned_powdered_fresh_milk": pick(row.get("fed_tinned_powdered_fresh_milk"), {"No", "Yes", "Don't know"}, "No"),
        "fed_baby_formula": "No",
        "source_of_drinking_water": pick(
            row.get("source_of_drinking_water"),
            {
                'Piped into dwelling', 'Piped to yard/plot', 'Piped to neighbor', 'Public tap/standpipe',
                'Tube well or borehole', 'Protected well', 'Unprotected well', 'Protected spring',
                'Unprotected spring', 'River/dam/lake/stream', 'Rainwater', 'Tanker truck',
                'Cart with small tank', 'Bottled water', 'Other'
            },
            'Unprotected well',
        ),
        "type_of_toilet_facility": pick(
            row.get("type_of_toilet_facility"),
            {
                'Flush to piped sewer', 'Flush to septic tank', 'Flush to pit latrine', 'Flush to somewhere else',
                'Flush, unknown destination', 'VIP latrine', 'Pit latrine with slab', 'Pit latrine without slab',
                'No facility/bush/field', 'Composting toilet', 'Bucket toilet', 'Hanging toilet/latrine', 'Other'
            },
            'No facility/bush/field',
        ),
        "type_of_cooking_fuel": pick(
            row.get("type_of_cooking_fuel"),
            {
                'Electricity', 'LPG', 'Natural gas', 'Biogas', 'Kerosene', 'Coal/lignite', 'Charcoal',
                'Wood', 'Straw/shrubs/grass', 'Agricultural crop', 'Animal dung', 'Alcohol/ethanol',
                'Gasoline/diesel', 'Solar power', 'No food cooked in house', 'Other'
            },
            'Wood',
        ),
        "has_electricity": pick(row.get("has_electricity"), {"No", "Yes"}, "No"),
        "has_refrigerator": pick(row.get("has_refrigerator"), {"No", "Yes"}, "No"),
        "main_floor_material": pick(
            row.get("main_floor_material"),
            {'Earth/sand', 'Dung', 'Wood planks', 'Palm/bamboo', 'Parquet or polished wood',
             'Vinyl or asphalt strips', 'Ceramic tiles', 'Cement', 'Carpet', 'Other'},
            'Earth/sand',
        ),
        "main_wall_material": pick(
            row.get("main_wall_material"),
            {'No walls', 'Cane/palm/trunks', 'Dirt', 'Bamboo with mud', 'Stone with mud', 'Uncovered adobe',
             'Plywood', 'Cardboard', 'Reused wood', 'Iron sheets', 'Cement', 'Stone with lime/cement',
             'Bricks', 'Cement blocks', 'Covered adobe', 'Wood planks/shingles', 'Other'},
            'Cane/palm/trunks',
        ),
        "main_roof_material": pick(
            row.get("main_roof_material"),
            {'No roof', 'Thatch/grass/makuti', 'Sod/mud/dung', 'Rustic mat', 'Palm/bamboo', 'Wood planks',
             'Cardboard', 'Tin cans', 'Iron sheets/Metal', 'Wood', 'Calamine/cement fiber', 'Ceramic tiles',
             'Cement', 'Roofing shingles', 'Asbestos sheet', 'Other'},
            'Thatch/grass/makuti',
        ),
        "owns_farm_animals_livestock": pick(row.get("owns_farm_animals_livestock"), {"No", "Yes"}, "No"),
        "has_land_suitable_for_agriculture": pick(row.get("has_land_suitable_for_agriculture"), {"No", "Yes"}, "No"),
        "owns_agricultural_land": "No",
        "mother_education_single_years": float(row.get("mother_education_single_years", 0)) if not pd.isna(row.get("mother_education_single_years")) else 0.0,
        "age_at_first_birth": float(row.get("age_at_first_birth", 20)) if not pd.isna(row.get("age_at_first_birth")) else 20.0,
        "mother_weight_kg": float(row.get("mother_weight_kg", 55)) if not pd.isna(row.get("mother_weight_kg")) else 55.0,
        "mother_bmi_x100": float(row.get("mother_bmi_x100", 2200)) if not pd.isna(row.get("mother_bmi_x100")) else 2200.0,
        "household_size": int(float(row.get("household_size", 5)) if not pd.isna(row.get("household_size")) else 5),
    }

    # keep child age within schema bounds
    payload["child_age_months"] = max(0, min(60, payload["child_age_months"]))

    return payload


def main():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    if "has_malnutrition" not in df.columns:
        raise RuntimeError("has_malnutrition column not found in cleaned dataset")

    positives = df[df["has_malnutrition"] == 1].reset_index(drop=True)
    print(f"positive rows in cleaned data: {len(positives)}")

    client = TestClient(app)

    found = None
    for i in range(min(len(positives), 1500)):
        payload = build_payload(positives.iloc[i])
        r = client.post("/api/v1/predict", json=payload)
        if r.status_code != 200:
            continue
        data = r.json()
        if data.get("prediction") == "Malnourished":
            found = {"idx": i, "payload": payload, "response": data}
            break

    if not found:
        print("No payload predicted as 'Malnourished' found in scanned positives.")
        return

    print("\nFound payload predicted as 'Malnourished':")
    print(json.dumps(found["payload"], indent=2))
    print("\nAPI response:")
    print(json.dumps(found["response"], indent=2))


if __name__ == "__main__":
    main()

