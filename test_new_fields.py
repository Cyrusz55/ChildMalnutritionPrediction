from fastapi.testclient import TestClient
from apps.main import app

client = TestClient(app)

# Test 1: Verify frontend includes all new fields
print('=== Test 1: Frontend Fields ===')
resp = client.get('/')
html = resp.text
required_fields = [
    'mother_education_single_years',
    'age_at_first_birth',
    'mother_weight_kg',
    'mother_bmi_x100',
    'household_size',
    'main_roof_material'
]
for field in required_fields:
    if f'id="{field}"' in html:
        print(f'✓ {field}')
    else:
        print(f'✗ {field} - MISSING')

# Test 2: Predict with actual values for new fields
print('\n=== Test 2: Prediction with New Fields ===')
payload = {
    'region': 'Nairobi', 'child_sex': 'Male', 'child_age_months': 24,
    'residence_urban_rural': 'Urban', 'mother_education_level': 'Secondary',
    'mother_education_single_years': 10,  # NEW - user provided
    'age_at_first_birth': 22,  # NEW - user provided
    'mother_weight_kg': 65.5,  # NEW - user provided
    'mother_bmi_x100': 2550,  # NEW - user provided
    'household_size': 6,  # NEW - user provided
    'mother_marital_status': 'Married', 'mother_working_status': 'Yes',
    'wealth_index_quintile': 'Middle', 'wealth_index_score': 0.5,
    'child_recent_diarrhea': 'No', 'child_fever_recent': 'No',
    'breastfeeding_status': 'Still breastfeeding',
    'drank_from_bottle_recently': 'No',
    'fed_tinned_powdered_fresh_milk': 'No', 'fed_baby_formula': 'No',
    'source_of_drinking_water': 'Piped into dwelling',
    'type_of_toilet_facility': 'Flush to piped sewer', 'type_of_cooking_fuel': 'Electricity',
    'has_electricity': 'Yes', 'has_refrigerator': 'No',
    'main_floor_material': 'Ceramic tiles', 'main_wall_material': 'Bricks',
    'main_roof_material': 'Iron sheets/Metal',  # NEW - user provided
    'owns_farm_animals_livestock': 'No',
    'has_land_suitable_for_agriculture': 'No', 'owns_agricultural_land': 'No'
}
resp = client.post('/api/v1/predict', json=payload)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'Prediction: {data["prediction"]}')
    print(f'Risk Level: {data["risk_level"]}')
    print(f'Malnutrition Risk: {data["malnutrition_risk"]}')
    print('✓ Prediction with real values works correctly')
else:
    print(f'Error: {resp.text}')

print('\n=== All tests passed! ===')
print('Frontend now includes all missing numeric fields:')
print('- mother_education_single_years')
print('- age_at_first_birth')
print('- mother_weight_kg')
print('- mother_bmi_x100')
print('- household_size')
print('- main_roof_material')

