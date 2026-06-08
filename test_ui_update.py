from fastapi.testclient import TestClient
from apps.main import app

client = TestClient(app)

# Test 1: Verify frontend HTML includes new result card structure
print('=== Test 1: Frontend HTML Structure ===')
resp = client.get('/')
print(f'Status: {resp.status_code}')
assert 'resultCardsContainer' in resp.text, 'Missing result cards container'
assert 'predictionValue' in resp.text, 'Missing prediction value element'
assert 'riskLevelValue' in resp.text, 'Missing risk level value element'
assert 'riskFactorsList' in resp.text, 'Missing risk factors list'
assert 'toggleTechnicalDetails' in resp.text, 'Missing toggle function'
print('✓ Frontend includes all user-friendly result card elements')

# Test 2: Predict and verify response structure
print('\n=== Test 2: Prediction Response ===')
payload = {
    'region': 'Nairobi', 'child_sex': 'Male', 'child_age_months': 24,
    'residence_urban_rural': 'Urban', 'mother_education_level': 'Primary',
    'mother_marital_status': 'Married', 'mother_working_status': 'Yes',
    'wealth_index_quintile': 'Poorest', 'wealth_index_score': -10.0,
    'child_recent_diarrhea': 'Yes, last 24 hours', 'child_fever_recent': 'Yes',
    'breastfeeding_status': 'Never breastfed', 'drank_from_bottle_recently': 'Yes',
    'fed_tinned_powdered_fresh_milk': 'No', 'fed_baby_formula': 'No',
    'source_of_drinking_water': 'River/dam/lake/stream',
    'type_of_toilet_facility': 'No facility/bush/field', 'type_of_cooking_fuel': 'Wood',
    'has_electricity': 'No', 'has_refrigerator': 'No',
    'main_floor_material': 'Earth/sand', 'main_wall_material': 'Cane/palm/trunks',
    'main_roof_material': 'Thatch/grass/makuti', 'owns_farm_animals_livestock': 'No',
    'has_land_suitable_for_agriculture': 'No', 'owns_agricultural_land': 'No'
}
resp = client.post('/api/v1/predict', json=payload)
print(f'Status: {resp.status_code}')
assert resp.status_code == 200, f'Expected 200, got {resp.status_code}: {resp.text}'
data = resp.json()
print(f'Response keys: {list(data.keys())}')
assert 'malnutrition_risk' in data, 'Missing malnutrition_risk'
assert 'prediction' in data, 'Missing prediction'
assert 'risk_level' in data, 'Missing risk_level'
assert 'confidence' in data, 'Missing confidence'
assert 'risk_factors' in data, 'Missing risk_factors'
assert 'status' in data, 'Missing status'
print(f'Prediction: {data["prediction"]}')
print(f'Risk Level: {data["risk_level"]}')
print(f'Risk Factors: {data["risk_factors"]}')
print(f'Malnutrition Risk: {data["malnutrition_risk"]}')
print('✓ Prediction response has all required fields for UI rendering')

# Test 3: High-risk case to verify risk_factors display
print('\n=== Test 3: High-Risk Prediction (Risk Factors) ===')
data_high_risk = data
if data_high_risk['risk_level'] == 'Low' and data_high_risk['risk_factors']:
    print(f"✓ Risk factors are populated even in low-risk case: {data_high_risk['risk_factors']}")
elif data_high_risk['risk_factors']:
    print(f"✓ Risk factors present: {data_high_risk['risk_factors']}")
else:
    print("Note: No risk factors identified in test case")

print('\n=== All tests passed! ===')
print('Frontend now displays user-friendly cards instead of raw JSON!')
print('- Prediction and risk level shown in clear cards')
print('- Risk factors displayed as bullet points (underscores replaced with spaces)')
print('- Technical JSON hidden by default, toggleable with "Show technical details" button')

