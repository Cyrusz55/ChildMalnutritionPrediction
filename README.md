# Child Malnutrition Prediction

A machine learning system that predicts child malnutrition risk from household, maternal, and child health features. Built with a Random Forest classifier served via a FastAPI REST API with an interactive web frontend.

> **Dataset:** Kenya Demographic and Health Survey (KDHS) — children under 5 years
>
> **Target:** `has_malnutrition` — binary classification (stunted / not stunted)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Pipeline](#pipeline)
- [Models & Performance](#models--performance)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Feature Engineering](#feature-engineering)
- [API](#api)
- [Frontend](#frontend)
- [Scheduled Retraining](#scheduled-retraining)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Deployment](#deployment)

---

## Project Overview

Child malnutrition is a critical public health challenge in Kenya. This project builds a predictive model using data from the Kenya Demographic and Health Survey (KDHS) to identify children at risk of malnutrition from commonly collected household survey variables.

**Key features:**

- **Random Forest Classifier** with hyperparameter tuning
- **7 engineered risk features** derived from raw survey responses (poverty, sanitation, water, housing, maternal vulnerability, child health risk, and their interactions)
- **SMOTETomek resampling** to handle class imbalance
- **FastAPI** REST API with interactive Swagger docs
- **Two frontends** — a full-featured web form and a compact dark-mode UI
- **Weekly automated retraining** via APScheduler
- **Cross-validated model comparison** across 10+ classifiers

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Project Root                      │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │  scripts/ │  │  data/   │  │  machine_learning/ │ │
│  │ load.py   │  │ raw/     │  │  machine_learning  │ │
│  │ clean.py  │  │ clean/   │  │  .py               │ │
│  │ ingest.py │  │          │  │                    │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                                                      │
│  ┌──────────────────┐  ┌──────────────────┐          │
│  │     apps/        │  │   database/      │          │
│  │  main.py         │  │  db_connection   │          │
│  │  routes.py       │  │  .py             │          │
│  │  schemas.py      │  │  models.py       │          │
│  │  model_loader.py │  │                  │          │
│  └──────────────────┘  └──────────────────┘          │
│                                                      │
│  ┌──────────────────┐  ┌──────────────────┐          │
│  │   frontend/      │  │    notebook/     │          │
│  │  index.html      │  │  book1.ipynb     │          │
│  │  v1/index.html   │  │  book2.ipynb     │          │
│  └──────────────────┘  └──────────────────┘          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │
│  │ models/  │  │  plots/  │  │ scheduler.py │       │
│  └──────────┘  └──────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────┘
```

**Data flow:**

1. Raw CSV → PostgreSQL (`raw_children_data` table)
2. Feature selection & cleaning → CSV (`data/clean/cleaned_children_data.csv`)
3. Cleaned data → PostgreSQL (`cleaned_children_data` table)
4. Cleaned data → ML pipeline training → serialized model (`models/child_malnutrition.joblib`)
5. FastAPI app loads the model at startup (with Hugging Face Hub fallback)
6. Web frontend sends input → `/api/v1/predict` → prediction result displayed

---

## Pipeline

### Data Ingestion & Cleaning

| Script | Purpose |
|--------|---------|
| `scripts/ingest.py` | Reads raw CSV, drops rows with missing targets, loads into PostgreSQL |
| `scripts/clean.py` | Selects relevant features from raw data, drops rows missing the target label |
| `scripts/load.py` | Loads cleaned data into PostgreSQL for serving |

### ML Pipeline Steps

```
Raw data
  │
  ▼
Feature selection (29 columns kept)
  │
  ▼
train_test_split (80/20, stratified)
  │
  ├───► Training set
  │      │
  │      ▼
  │   Preprocessing:
  │     • Numeric → median imputer + StandardScaler
  │     • High-cardinality categorical → TargetEncoder
  │     • Low-cardinality categorical → OneHotEncoder
  │      │
  │      ▼
  │   SMOTETomek resampling (handles class imbalance)
  │      │
  │      ▼
  │   Random Forest Classifier
  │   (n_estimators=150, max_depth=20, class_weight='balanced_subsample')
  │      │
  │      ▼
  │   Cross-validation (5-fold stratified)
  │      │
  │      ▼
  │   Hyperparameter tuning via RandomizedSearchCV
  │
  ├───► Test set → final evaluation metrics
  │
  ▼
Serialized model → models/child_malnutrition.joblib
```

### Feature Engineering

Domain-driven derived features computed automatically from raw survey responses:

| Engineered Feature | Derivation |
|---|---|
| `poverty_indicator` | Wealth quintile is "Poorest" or "Poorer" |
| `poor_sanitation` | Toilet is "No facility/bush/field" or "Pit latrine without slab" |
| `poor_water` | Drinking water is "Unprotected well", "River/dam/lake/stream", or "Unprotected spring" |
| `unsafe_housing` | Floor is "Earth/sand" or walls are "Cane/palm/trunks" |
| `mother_vulnerable` | Mother has "No Education" AND is not working |
| `child_health_risk` | Child had diarrhea in last 24 hours OR recent fever |
| `poverty_sanitation_risk` | Interaction term: `poverty_indicator × poor_sanitation` |

These are auto-computed both during training and at prediction time (via a Pydantic `model_validator` in the API schema), ensuring consistency between training and inference.

---

## Models & Performance

### Models Evaluated

The notebook (`notebook/book2.ipynb`) compares 10+ classifiers using 5-fold stratified cross-validation with SMOTETom ek resampling:

- Logistic Regression
- K-Nearest Neighbors
- Decision Tree
- **Random Forest** (best performer)
- Gradient Boosting
- AdaBoost
- XGBoost
- LightGBM
- Support Vector Machine
- Gaussian Naive Bayes

### Random Forest — Final Tuned Parameters

| Parameter | Value |
|---|---|
| `n_estimators` | 150 |
| `max_depth` | 20 |
| `max_features` | `sqrt` |
| `min_samples_leaf` | 7 |
| `min_samples_split` | 4 |
| `class_weight` | `balanced_subsample` |

### Visualizations

![Top 3 Models — Confusion Matrices](plots/top_3_models.png)
*Confusion matrices for the top 3 models ranked by cross-validated F1 score.*

![ROC Curves — All Models](plots/roc_curve.png)
*ROC curves comparing all trained models on the test set. The Random Forest achieves strong AUC.*

![Cross-Validated Metrics Comparison](plots/cv_model_comparison.png)
*Left: CV accuracy, precision, recall, F1, and ROC-AUC across all models. Right: Training time comparison.*

![Top 15 Feature Importances](plots/top_15_features.png)
*The most influential features for the Random Forest model. Child health risk, wealth, and maternal education dominate.*

---

## Exploratory Data Analysis

![EDA Plots](plots/eda_plots.png)
*Distribution of malnutrition status, regional variation, wealth index by status, and age distribution.*

![Correlation Matrix](plots/correlation_matrix.png)
*Correlation heatmap of numeric features showing relationships between wealth, maternal age, education, and malnutrition.*

Key EDA findings:

- **Malnutrition prevalence varies significantly by region** — some counties (Turkana, West Pokot, Samburu) show rates well above the national average
- **Wealth gradient** is steep — children in the poorest households have substantially higher malnutrition rates
- **Maternal education** is one of the strongest protective factors
- **Child age** shows a nonlinear relationship — risk increases in the 12–24 month window

---

## API

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the main frontend |
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/predict` | Predict malnutrition risk |
| `GET` | `/api/v1/model-info` | Returns loaded model metadata |

### Predict Endpoint

**Request:**

```json
{
  "region": "Nairobi",
  "child_sex": "Male",
  "child_age_months": 24,
  "residence_urban_rural": "Urban",
  "mother_education_level": "Primary",
  "mother_marital_status": "Married",
  "mother_working_status": "Yes",
  "wealth_index_quintile": "Middle",
  "wealth_index_score": 0.5,
  "child_recent_diarrhea": "No",
  "child_fever_recent": "No",
  "breastfeeding_status": "Still breastfeeding",
  "drank_from_bottle_recently": "No",
  "fed_tinned_powdered_fresh_milk": "Yes",
  "fed_baby_formula": "No",
  "source_of_drinking_water": "Piped into dwelling",
  "type_of_toilet_facility": "Flush to piped sewer",
  "type_of_cooking_fuel": "Electricity",
  "has_electricity": "Yes",
  "has_refrigerator": "Yes",
  "main_floor_material": "Ceramic tiles",
  "main_wall_material": "Cement",
  "main_roof_material": "Iron sheets/Metal",
  "owns_farm_animals_livestock": "No",
  "has_land_suitable_for_agriculture": "No",
  "owns_agricultural_land": "No"
}
```

**Response:**

```json
{
  "malnutrition_risk": 0.32,
  "prediction": "Not malnourished",
  "risk_level": "Medium",
  "confidence": 0.68,
  "risk_factors": ["poor_water", "unsafe_housing"],
  "status": "success"
}
```

### Risk Categories

| Risk Level | Probability Range |
|---|---|
| Low | < 0.3 |
| Medium | 0.3 – 0.6 |
| High | > 0.6 |

Interactive API docs available at `/docs` when the server is running.

---

## Frontend

Two frontends are included:

### `frontend/index.html` (main)

A full-featured form with clean, accessible design:

- Fields grouped by section (Child Profile, Maternal Profile, Household & Living Conditions, Child Health & Feeding, Water, Sanitation & Housing)
- Wealth score slider (converts 0–100% to model's -10 to 10 range)
- Real-time results with risk level color coding (green/yellow/red)
- Identified risk factors displayed in a highlighted list
- Expandable technical JSON details
- Responsive layout (desktop sidebar, mobile single-column)
- Skip-to-content navigation and reduced-motion support

### `frontend/v1/index.html` (compact)

A minimal dark-mode alternative with the same prediction logic, suited for embedded use or quick testing.

---

## Scheduled Retraining

The `scheduler.py` module uses APScheduler to automatically retrain the model every **Saturday at 12:00 noon**.

```python
scheduler.add_job(
    retrain_job,
    trigger=CronTrigger(day_of_week="sat", hour=12, minute=0),
    id="weekly_retrain",
    replace_existing=True,
)
```

The scheduler starts automatically with the FastAPI application (`on_event("startup")`).

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (or Supabase — the project uses a Supabase PostgreSQL instance)
- Git LFS (for model versioning — optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/cyrusnx/ChildMalnutritionPrediction.git
cd ChildMalnutritionPrediction

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL="postgresql://user:password@host:port/database"
HF_TOKEN="hf_your_huggingface_token"  # optional, for model hub fallback
```

### Running Locally

**Step 1 — Ingest & clean the data:**

```bash
python scripts/ingest.py
python scripts/clean.py
python scripts/load.py
```

**Step 2 — Train the model:**

```bash
python machine_learning/machine_learning.py
```

**Step 3 — Start the API:**

```bash
uvicorn apps.main:app --reload
```

Visit: `http://localhost:8000` for the frontend, or `http://localhost:8000/docs` for the interactive API documentation.

### Running the Notebook

To re-run the full analysis pipeline (EDA, model comparison, tuning):

```bash
jupyter notebook notebook/book2.ipynb
```

---

## Project Structure

```
ChildMalnutritionPrediction/
├── .env                          # Environment variables (DB URL, HF token)
├── .gitignore
├── README.md
│
├── apps/                         # FastAPI application
│   ├── main.py                   # App entry point, CORS, startup event
│   ├── routes.py                 # API endpoints (/predict, /health, /model-info)
│   ├── schemas.py                # Pydantic input/output models with validation
│   └── model_loader.py           # Singleton model loader (cached)
│
├── database/                     # PostgreSQL integration
│   ├── db_connection.py          # SQLAlchemy engine factory
│   └── models.py                 # ORM model for cleaned data
│
├── machine_learning/             # ML training & inference
│   └── machine_learning.py       # Pipeline building, training, prediction, model loading
│
├── scripts/                      # Data pipeline scripts
│   ├── ingest.py                 # Raw CSV → PostgreSQL (raw_children_data)
│   ├── clean.py                  # Feature selection & cleaning
│   └── load.py                   # Cleaned CSV → PostgreSQL (cleaned_children_data)
│
├── data/
│   ├── raw/children_processed.csv        # Raw survey data
│   └── clean/cleaned_children_data.csv    # Cleaned, feature-selected data
│
├── models/
│   └── child_malnutrition.joblib          # Trained model artifact (19 MB)
│
├── notebook/
│   ├── book1.ipynb               # Initial data inspection & load
│   └── book2.ipynb               # EDA, feature engineering, model comparison, tuning
│
├── plots/                        # Visualization outputs
│   ├── eda_plots.png             # EDA: target distribution, regional rates, wealth, age
│   ├── correlation_matrix.png    # Numeric feature correlation heatmap
│   ├── top_3_models.png          # Confusion matrices for top 3 classifiers
│   ├── roc_curve.png             # ROC curves for all models
│   ├── cv_model_comparison.png   # CV metrics & training time comparison
│   └── top_15_features.png       # Feature importance bar chart
│
├── frontend/                     # Web user interfaces
│   ├── index.html                # Main frontend (light theme, full form)
│   └── v1/index.html             # Compact frontend (dark theme)
│
├── scheduler.py                  # Weekly retraining scheduler (APScheduler)
├── test_new_fields.py            # Field validation test script
└── test_ui_update.py             # UI update test script
```

---

## Deployment

### Hugging Face Hub

The trained model can be uploaded to the Hugging Face Hub for versioning and remote serving:

```bash
# Prerequisites
pip install huggingface_hub
huggingface-cli login

# Create a repo (one-time)
huggingface-cli repo create cyrusnx/malnutrition-model --public

# Push using git + git-lfs
cd models
git init
git remote add origin https://huggingface.co/cyrusnx/malnutrition-model
git lfs track "*.joblib"
git add .gitattributes child_malnutrition.joblib
git commit -m "Add trained model artifact"
git push origin main
```

### Render (or similar PaaS)

The FastAPI app is configured for deployment and was tested on Render. The frontend auto-detects the API base URL:

```javascript
// In frontend/index.html — auto-detection logic
const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : window.location.origin;
```

**CORS** is configured to allow requests from:
- `http://localhost`
- `http://localhost:8000`
- `https://malnutrition-api-ivc9.onrender.com`

---

## License

MIT

---

*Built with scikit-learn, FastAPI, and PostgreSQL. Data: Kenya Demographic and Health Survey (KDHS).*
