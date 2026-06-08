from pydantic import BaseModel, Field, model_validator
from typing import Literal


class ChildMalnutritionInput(BaseModel):

    # Demographic
    region: Literal[
        'Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita Taveta',
        'Garissa', 'Wajir', 'Mandera', 'Marsabit', 'Isiolo', 'Meru',
        'Tharaka Nithi', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua',
        'Nyeri', 'Kirinyaga', "Murang'a", 'Kiambu', 'Turkana', 'West Pokot',
        'Samburu', 'Trans Nzoia', 'Uasin Gishu', 'Elgeyo Marakwet', 'Nandi',
        'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Kericho',
        'Bomet', 'Kakamega', 'Vihiga', 'Bungoma', 'Busia', 'Siaya',
        'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi'
    ] = Field(..., description="Region/County in Kenya")

    child_sex: Literal['Male', 'Female'] = Field(..., description="Child's sex")

    child_age_months: int = Field(..., description="Child's age in months", ge=0, le=60)

    residence_urban_rural: Literal['Urban', 'Rural'] = Field(..., description="Urban or rural residence")

    # Mother's characteristics
    mother_education_level: Literal['No Education', 'Primary', 'Secondary', 'Higher'] = Field(
        ..., description="Mother's education level"
    )

    mother_marital_status: Literal[
        'Never in union', 'Married', 'Living with partner', 'Widowed', 'Divorced', 'Separated'
    ] = Field(..., description="Mother's marital status")

    mother_working_status: Literal['No', 'Yes'] = Field(..., description="Is mother working?")

    # Wealth
    wealth_index_quintile: Literal['Poorest', 'Poorer', 'Middle', 'Richer', 'Richest'] = Field(
        ..., description="Household wealth index quintile"
    )

    wealth_index_score: float = Field(..., description="Wealth index score", ge=-10, le=10)

    # Child health
    child_recent_diarrhea: Literal['No', 'Yes, last 24 hours', 'Yes, last two weeks', "Don't know"] = Field(
        ..., description="Child had recent diarrhea?"
    )

    child_fever_recent: Literal['No', 'Yes', "Don't know"] = Field(..., description="Child had recent fever?")

    # Feeding
    breastfeeding_status: Literal[
        'Ever breastfed, not currently', 'Never breastfed', 'Still breastfeeding',
        'Breastfed until died', 'Inconsistent', "Don't know"
    ] = Field(..., description="Breastfeeding status")

    drank_from_bottle_recently: Literal['No', 'Yes', "Don't know"] = Field(
        ..., description="Child drank from bottle recently?"
    )

    fed_tinned_powdered_fresh_milk: Literal['No', 'Yes', "Don't know"] = Field(
        ..., description="Child fed tinned/powdered/fresh milk recently?"
    )

    fed_baby_formula: Literal['No', 'Yes', "Don't know"] = Field(
        ..., description="Child fed baby formula recently?"
    )

    # Water & sanitation
    source_of_drinking_water: Literal[
        'Piped into dwelling', 'Piped to yard/plot', 'Piped to neighbor', 'Public tap/standpipe',
        'Tube well or borehole', 'Protected well', 'Unprotected well', 'Protected spring',
        'Unprotected spring', 'River/dam/lake/stream', 'Rainwater', 'Tanker truck',
        'Cart with small tank', 'Bottled water', 'Other'
    ] = Field(..., description="Source of drinking water")

    type_of_toilet_facility: Literal[
        'Flush to piped sewer', 'Flush to septic tank', 'Flush to pit latrine', 'Flush to somewhere else',
        'Flush, unknown destination', 'VIP latrine', 'Pit latrine with slab', 'Pit latrine without slab',
        'No facility/bush/field', 'Composting toilet', 'Bucket toilet', 'Hanging toilet/latrine', 'Other'
    ] = Field(..., description="Type of toilet facility")

    # Housing
    type_of_cooking_fuel: Literal[
        'Electricity', 'LPG', 'Natural gas', 'Biogas', 'Kerosene', 'Coal/lignite', 'Charcoal',
        'Wood', 'Straw/shrubs/grass', 'Agricultural crop', 'Animal dung', 'Alcohol/ethanol',
        'Gasoline/diesel', 'Solar power', 'No food cooked in house', 'Other'
    ] = Field(..., description="Type of cooking fuel")

    has_electricity: Literal['No', 'Yes'] = Field(..., description="Household has electricity?")

    has_refrigerator: Literal['No', 'Yes'] = Field(..., description="Household has refrigerator?")

    main_floor_material: Literal[
        'Earth/sand', 'Dung', 'Wood planks', 'Palm/bamboo', 'Parquet or polished wood',
        'Vinyl or asphalt strips', 'Ceramic tiles', 'Cement', 'Carpet', 'Other'
    ] = Field(..., description="Main floor material")

    main_wall_material: Literal[
        'No walls', 'Cane/palm/trunks', 'Dirt', 'Bamboo with mud', 'Stone with mud', 'Uncovered adobe',
        'Plywood', 'Cardboard', 'Reused wood', 'Iron sheets', 'Cement', 'Stone with lime/cement',
        'Bricks', 'Cement blocks', 'Covered adobe', 'Wood planks/shingles', 'Other'
    ] = Field(..., description="Main wall material")

    main_roof_material: Literal[
        'No roof', 'Thatch/grass/makuti', 'Sod/mud/dung', 'Rustic mat', 'Palm/bamboo', 'Wood planks',
        'Cardboard', 'Tin cans', 'Iron sheets/Metal', 'Wood', 'Calamine/cement fiber', 'Ceramic tiles',
        'Cement', 'Roofing shingles', 'Asbestos sheet', 'Other'
    ] = Field(..., description="Main roof material")

    # Agriculture & livestock
    owns_farm_animals_livestock: Literal['No', 'Yes'] = Field(
        ..., description="Household owns farm animals/livestock?"
    )

    has_land_suitable_for_agriculture: Literal['No', 'Yes'] = Field(
        ..., description="Household has land suitable for agriculture?"
    )

    owns_agricultural_land: Literal['No', 'Yes'] = Field(
        ..., description="Household owns agricultural land?"
    )

    # Engineered features (auto-computed)
    poverty_indicator: int = Field(default=0, description="Is household in poorest/poorer quintile?")
    poor_sanitation: int = Field(default=0, description="Does household have poor sanitation?")
    poor_water: int = Field(default=0, description="Does household have poor water source?")
    unsafe_housing: int = Field(default=0, description="Does household have unsafe housing?")
    mother_vulnerable: int = Field(default=0, description="Is mother uneducated and not working?")
    child_health_risk: int = Field(default=0, description="Does child have recent diarrhea or fever?")
    poverty_sanitation_risk: int = Field(default=0, description="Interaction: poverty × poor sanitation")

    @model_validator(mode='after')
    def compute_engineered_features(self):
        """Auto-compute engineered features from raw inputs"""
        # Poverty indicator: poorest or poorer quintile
        self.poverty_indicator = 1 if self.wealth_index_quintile in ['Poorest', 'Poorer'] else 0

        # Poor sanitation: no facility/bush/field or pit latrine without slab
        self.poor_sanitation = 1 if self.type_of_toilet_facility in [
            'No facility/bush/field', 'Pit latrine without slab'
        ] else 0

        # Poor water: unprotected well, river/stream, or unprotected spring
        self.poor_water = 1 if self.source_of_drinking_water in [
            'Unprotected well', 'River/dam/lake/stream', 'Unprotected spring'
        ] else 0

        # Unsafe housing: earth/sand floor or cane/palm/trunks walls
        self.unsafe_housing = 1 if (
                self.main_floor_material == 'Earth/sand' or
                self.main_wall_material == 'Cane/palm/trunks'
        ) else 0

        # Mother vulnerable: no education and not working
        self.mother_vulnerable = 1 if (
                self.mother_education_level == 'No Education' and
                self.mother_working_status == 'No'
        ) else 0

        # Child health risk: diarrhea in last 24 hours or recent fever
        self.child_health_risk = 1 if (
                self.child_recent_diarrhea == 'Yes, last 24 hours' or
                self.child_fever_recent == 'Yes'
        ) else 0

        # Interaction term: poverty × sanitation
        self.poverty_sanitation_risk = self.poverty_indicator * self.poor_sanitation

        return self

    class Config:
        schema_extra = {
            "example": {
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
                "owns_agricultural_land": "No",
            }
        }


class MalnutritionPredictionResponse(BaseModel):

    malnutrition_risk: float = Field(
        ..., description="Probability of malnutrition (0.0 to 1.0)", ge=0.0, le=1.0
    )

    prediction: Literal['Malnourished', 'Not malnourished'] = Field(
        ..., description="Binary malnutrition prediction"
    )

    risk_level: Literal['Low', 'Medium', 'High'] = Field(
        ..., description="Risk level category (Low: <0.3, Medium: 0.3-0.6, High: >0.6)"
    )

    confidence: float = Field(
        ..., description="Model confidence in prediction (0.0 to 1.0)", ge=0.0, le=1.0
    )

    risk_factors: list[str] = Field(
        default=[], description="List of identified risk factors (engineered features = 1)"
    )

    status: str = Field(default="success", description="Response status")

    class Config:
        schema_extra = {
            "example": {
                "malnutrition_risk": 0.32,
                "prediction": "Not malnourished",
                "risk_level": "Medium",
                "confidence": 0.68,
                "risk_factors": ["poor_water", "unsafe_housing"],
                "status": "success"
            }
        }