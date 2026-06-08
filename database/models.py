from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CleanedChildrenData(Base):
    __tablename__ = "cleaned_children_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Columns aligned to cleaned CSV header
    child_sex = Column(String, nullable=True)
    child_age_months = Column(Float, nullable=True)
    mother_age_years = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    residence_urban_rural = Column(String, nullable=True)
    mother_education_level = Column(String, nullable=True)
    mother_education_single_years = Column(Float, nullable=True)
    mother_working_status = Column(String, nullable=True)
    wealth_index_quintile = Column(String, nullable=True)
    wealth_index_score = Column(Float, nullable=True)
    age_at_first_birth = Column(Float, nullable=True)
    mother_weight_kg = Column(Float, nullable=True)
    mother_bmi_x100 = Column(Float, nullable=True)
    child_recent_diarrhea = Column(String, nullable=True)
    child_fever_recent = Column(String, nullable=True)
    drank_from_bottle_recently = Column(String, nullable=True)
    fed_tinned_powdered_fresh_milk = Column(String, nullable=True)
    has_malnutrition = Column(Integer, nullable=True)
    source_of_drinking_water = Column(String, nullable=True)
    type_of_toilet_facility = Column(String, nullable=True)
    type_of_cooking_fuel = Column(String, nullable=True)
    household_size = Column(Integer, nullable=True)
    has_electricity = Column(String, nullable=True)
    has_refrigerator = Column(String, nullable=True)
    main_floor_material = Column(String, nullable=True)
    main_wall_material = Column(String, nullable=True)
    main_roof_material = Column(String, nullable=True)
    owns_farm_animals_livestock = Column(String, nullable=True)
    has_land_suitable_for_agriculture = Column(String, nullable=True)

def create_tables(engine):
    Base.metadata.create_all(engine)
    print("[db] Tables created")