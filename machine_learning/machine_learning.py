import os
import joblib
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from sklearn.ensemble import RandomForestClassifier


MODEL_PATH = "models/child_malnutrition.joblib"
TARGET_COL = "has_malnutrition"
NUM_COLS = ['child_health_risk', 'mother_age_years', 'child_age_months', 'age_at_first_birth', 'poverty_sanitation_risk', 'mother_education_single_years', 'mother_weight_kg', 'mother_bmi_x100', 'wealth_index_score', 'household_size']
CAT_COLS = ['owns_farm_animals_livestock', 'residence_urban_rural', 'has_land_suitable_for_agriculture', 'main_roof_material', 'drank_from_bottle_recently', 'has_electricity', 'type_of_cooking_fuel', 'has_refrigerator', 'child_sex', 'region', 'fed_tinned_powdered_fresh_milk']

high_card_cols = ['main_roof_material', 'region', 'type_of_cooking_fuel']
low_card_cols = [col for col in CAT_COLS if col not in high_card_cols]

def get_X_y(df: pd.DataFrame):
    # Ensure engineered features required for training exist in the dataframe.
    # This will add missing derived columns (safe no-op if they already exist).
    ensure_engineered_features(df)

    X = df[NUM_COLS + CAT_COLS]
    y = df[TARGET_COL]
    return X, y


def ensure_engineered_features(df: pd.DataFrame):
    """Create hand-crafted / derived features used by the training pipeline.

    This function is idempotent and will not fail if source columns are missing;
    it will create sensible default values instead so training can proceed.
    """
    # helper to return a safe Series for possibly-missing columns
    def s(name):
        return df[name] if name in df.columns else pd.Series([None] * len(df), index=df.index)

    # poverty indicator: True for poorest/poorer
    wealth = s('wealth_index_quintile')
    df['poverty_indicator'] = wealth.isin(['Poorest', 'Poorer']).fillna(False).astype(int)

    # poor sanitation
    toilet = s('type_of_toilet_facility')
    poor_sanitation_vals = ['No facility/bush/field', 'Pit latrine without slab']
    df['poor_sanitation'] = toilet.isin(poor_sanitation_vals).fillna(False).astype(int)

    # poor water
    water = s('source_of_drinking_water')
    poor_water_vals = ['Unprotected well', 'River/dam/lake/stream', 'Unprotected spring']
    df['poor_water'] = water.isin(poor_water_vals).fillna(False).astype(int)

    # unsafe housing
    floor = s('main_floor_material')
    wall = s('main_wall_material')
    df['unsafe_housing'] = ((floor == 'Earth/sand') | (wall == 'Cane/palm/trunks')).fillna(False).astype(int)

    # mother vulnerable
    med = s('mother_education_level')
    work = s('mother_working_status')
    df['mother_vulnerable'] = ((med == 'No Education') & (work == 'No')).fillna(False).astype(int)

    # child health risk: recent diarrhea or fever
    diarrhea = s('child_recent_diarrhea')
    fever = s('child_fever_recent')
    df['child_health_risk'] = (((diarrhea == 'Yes, last 24 hours') | (fever == 'Yes'))).fillna(False).astype(int)

    # poor feeding (best effort): if breastfeeding_status present
    bf = s('breastfeeding_status')
    df['poor_feeding'] = bf.isin(["Never breastfed", "Don't know"]).fillna(False).astype(int)

    # interaction: poverty + poor sanitation
    df['poverty_sanitation_risk'] = (df['poverty_indicator'].fillna(0).astype(int) * df['poor_sanitation'].fillna(0).astype(int)).astype(int)

    # Ensure numeric columns referenced in NUM_COLS exist (create defaults if missing)
    for col in ['mother_age_years', 'child_age_months', 'age_at_first_birth', 'mother_education_single_years', 'mother_weight_kg', 'mother_bmi_x100', 'wealth_index_score', 'household_size']:
        if col not in df.columns:
            df[col] = 0


def build_pipeline():
    num_pipeline = Pipeline(
        steps = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
        ]
    )
    high_card_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
    ])
    low_card_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])
    preprocessor = ColumnTransformer([
        ('num', num_pipeline, NUM_COLS),
        ('high_card', high_card_pipeline, high_card_cols),
        ('low_card', low_card_pipeline, low_card_cols)
        ]
    )
    model = Pipeline(
        steps = [
            ('preprocessor', preprocessor),
            ("Random Forest", RandomForestClassifier(
                n_estimators=150,
                max_depth=20,
                max_features='sqrt',
                min_samples_leaf=7,
                min_samples_split=4,
                class_weight='balanced_subsample',
                n_jobs=-1,
                random_state=42,
             ))
        ]
    )
    return model

def train_model(df: pd.DataFrame):
    """Train the classification pipeline and print classification metrics.

    Uses engineered features created by `ensure_engineered_features` via `get_X_y`.
    """
    X, y = get_X_y(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = build_pipeline()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    # Try to obtain predicted probabilities for ROC AUC when available
    y_proba = None
    try:
        y_proba = model.predict_proba(X_test)[:, 1]
    except Exception:
        pass

    # Classification metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, roc_auc_score

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    if y_proba is not None:
        try:
            roc = roc_auc_score(y_test, y_proba)
            print(f"ROC AUC: {roc:.4f}")
        except Exception:
            pass

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model, X_test, y_test

def predict_malnutrition(model, new_data: pd.DataFrame):
    # Make sure engineered features and any numeric defaults exist before predicting
    try:
        ensure_engineered_features(new_data)
    except Exception:
        # If anything goes wrong, continue and let the pipeline raise a clear error
        pass
    return model.predict(new_data)

def load_model():
    from pathlib import Path

    # Try local first
    local_path = Path(MODEL_PATH)
    if local_path.exists():
        try:
            return joblib.load(local_path)
        except Exception as e:
            # If loading fails (corrupt model or incompatible pickle), attempt a safe
            # fallback: retrain a model from the cleaned CSV if available.
            print(f"[load_model] Failed to load model from {local_path}: {e}")
            try:
                df = pd.read_csv("data/clean/cleaned_children_data.csv")
                print("[load_model] Retraining model from cleaned dataset as fallback...")
                model, _, _ = train_model(df)
                return model
            except Exception as e2:
                print(f"[load_model] Retrain fallback failed: {e2}")
                # Re-raise original exception to let caller handle it
                raise

    # Try Huggingface cache
    cache_path = Path("models/models--cyrusnx--salary-model/snapshots")
    if cache_path.exists():
        # Get the latest snapshot
        snapshots = list(cache_path.glob("*/malnutrition_model.joblib"))
        if snapshots:
            return joblib.load(snapshots[0])

    raise FileNotFoundError(f"Model not found in local path {MODEL_PATH} or Huggingface cache.")

def predict_single(input_data: dict):
    model = load_model()
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)[0]
    return prediction[0]


if __name__ == "__main__":
    # fallback for running this module directly — use the cleaned dataset produced by scripts/clean.py
    df = pd.read_csv("data/clean/cleaned_children_data.csv")
    train_model(df)


