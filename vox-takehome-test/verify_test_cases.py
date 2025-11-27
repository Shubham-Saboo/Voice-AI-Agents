#!/usr/bin/env python3
"""
Script to verify the test case answers by programmatically querying the provider data.
"""

import json
from typing import List, Dict, Any

def load_providers() -> List[Dict[str, Any]]:
    """Load providers from JSON file."""
    with open('data/providerlist.json', 'r') as f:
        return json.load(f)

def test_case_1(providers: List[Dict[str, Any]]) -> float:
    """Test Case 1: Multi-criteria filtering with aggregation"""
    matches = []
    for p in providers:
        if (p['specialty'] == 'Cardiology' and
            p['address']['state'] == 'TX' and
            p['board_certified'] is True and
            p['years_experience'] >= 15 and
            'Spanish' in p['languages'] and
            'Aetna' in p['insurance_accepted'] and
            'Medicare' in p['insurance_accepted']):
            matches.append(p)
    
    if not matches:
        return None
    return sum(p['rating'] for p in matches) / len(matches)

def test_case_2(providers: List[Dict[str, Any]]) -> int:
    """Test Case 2: Complex insurance intersection query"""
    count = 0
    for p in providers:
        if (p['address']['state'] == 'CA' and
            p['accepting_new_patients'] is True and
            p['rating'] > 4.0 and
            'Blue Cross Blue Shield' in p['insurance_accepted'] and
            'Cigna' in p['insurance_accepted'] and
            'Medicaid' in p['insurance_accepted']):
            count += 1
    return count

def test_case_3(providers: List[Dict[str, Any]]) -> Dict[str, float]:
    """Test Case 3: Statistical analysis with conditional logic"""
    board_certified = []
    non_board_certified = []
    
    for p in providers:
        if p['specialty'] == 'Internal Medicine' and p['years_experience'] > 10:
            if p['board_certified']:
                board_certified.append(p['rating'])
            else:
                non_board_certified.append(p['rating'])
    
    result = {}
    if board_certified:
        result['board_certified_avg'] = sum(board_certified) / len(board_certified)
    if non_board_certified:
        result['non_board_certified_avg'] = sum(non_board_certified) / len(non_board_certified)
    
    return result

def test_case_4(providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test Case 4: Geographic distribution with multiple conditions"""
    city_providers = {}
    
    for p in providers:
        if (p['address']['state'] == 'CA' and
            p['specialty'] == 'Pediatrics' and
            p['rating'] > 4.0 and
            'Kaiser Permanente' in p['insurance_accepted']):
            city = p['address']['city']
            if city not in city_providers:
                city_providers[city] = []
            city_providers[city].append(p)
    
    # Filter cities with at least 2 providers
    result_cities = {city: len(provs) for city, provs in city_providers.items() if len(provs) >= 2}
    total_count = sum(len(provs) for provs in city_providers.values())
    
    return {
        'cities': result_cities,
        'total_count': total_count
    }

def test_case_5(providers: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Test Case 5: Multi-language filtering with experience threshold"""
    matches = []
    for p in providers:
        if ('Russian' in p['languages'] and
            'Portuguese' in p['languages'] and
            p['years_experience'] > 20 and
            p['board_certified'] is True and
            p['accepting_new_patients'] is True):
            matches.append({
                'name': p['full_name'],
                'specialty': p['specialty']
            })
    return matches

def test_case_6(providers: List[Dict[str, Any]]) -> int:
    """Test Case 6: State pattern matching with rating range"""
    count = 0
    for p in providers:
        if (p['address']['state'] in ['CA', 'CO'] and
            3.8 <= p['rating'] <= 4.2 and
            p['board_certified'] is True and
            'Medicare' in p['insurance_accepted'] and
            'Medicaid' in p['insurance_accepted']):
            count += 1
    return count

def test_case_7(providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test Case 7: Experience vs rating anomaly detection"""
    matches = []
    for p in providers:
        if (p['years_experience'] < 10 and
            p['rating'] > 4.5 and
            p['accepting_new_patients'] is True):
            matches.append(p)
    
    if not matches:
        return {'count': 0, 'avg_experience': None}
    
    avg_exp = sum(p['years_experience'] for p in matches) / len(matches)
    return {
        'count': len(matches),
        'avg_experience': avg_exp,
        'providers': [p['full_name'] for p in matches]
    }

def test_case_8(providers: List[Dict[str, Any]]) -> Dict[str, float]:
    """Test Case 8: Specialty distribution with aggregation"""
    specialty_data = {}
    
    for p in providers:
        if p['board_certified'] and p['accepting_new_patients']:
            specialty = p['specialty']
            if specialty not in specialty_data:
                specialty_data[specialty] = []
            specialty_data[specialty].append(p['years_experience'])
    
    # Filter specialties with at least 3 providers
    result = {}
    for specialty, experiences in specialty_data.items():
        if len(experiences) >= 3:
            result[specialty] = sum(experiences) / len(experiences)
    
    return result

def test_case_9(providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Test Case 9: Complex ranking with multiple criteria"""
    matches = []
    for p in providers:
        if (p['board_certified'] and
            len(p['languages']) >= 2):
            matches.append({
                'name': p['full_name'],
                'rating': p['rating'],
                'insurance_count': len(p['insurance_accepted'])
            })
    
    # Sort by rating (desc), then by insurance count (desc)
    matches.sort(key=lambda x: (x['rating'], x['insurance_count']), reverse=True)
    return matches[:3]

def test_case_10(providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test Case 10: Multi-step conditional logic with exclusion"""
    matches = []
    for p in providers:
        if p['address']['state'] == 'TX' and p['address']['city'] != 'Houston':
            condition_a = (p['rating'] > 4.5 and 'Aetna' in p['insurance_accepted'])
            condition_b = (p['years_experience'] > 25 and 'Kaiser Permanente' in p['insurance_accepted'])
            
            if condition_a or condition_b:
                matches.append(p)
    
    if not matches:
        return {'count': 0, 'avg_rating': None}
    
    avg_rating = sum(p['rating'] for p in matches) / len(matches)
    return {
        'count': len(matches),
        'avg_rating': avg_rating,
        'providers': [p['full_name'] for p in matches]
    }

def main():
    providers = load_providers()
    
    print("=" * 80)
    print("TEST CASE VERIFICATION RESULTS")
    print("=" * 80)
    
    print("\n1. Multi-Criteria Filtering with Aggregation:")
    result = test_case_1(providers)
    print(f"   Average rating: {result}")
    
    print("\n2. Complex Insurance Intersection Query:")
    result = test_case_2(providers)
    print(f"   Count: {result}")
    
    print("\n3. Statistical Analysis with Conditional Logic:")
    result = test_case_3(providers)
    print(f"   Board-certified avg: {result.get('board_certified_avg')}")
    print(f"   Non-board-certified avg: {result.get('non_board_certified_avg')}")
    
    print("\n4. Geographic Distribution with Multiple Conditions:")
    result = test_case_4(providers)
    print(f"   Cities with >=2 providers: {result['cities']}")
    print(f"   Total count: {result['total_count']}")
    
    print("\n5. Multi-Language Filtering with Experience Threshold:")
    result = test_case_5(providers)
    for match in result:
        print(f"   {match['name']} - {match['specialty']}")
    
    print("\n6. State Pattern Matching with Rating Range:")
    result = test_case_6(providers)
    print(f"   Count: {result}")
    
    print("\n7. Experience vs Rating Anomaly Detection:")
    result = test_case_7(providers)
    print(f"   Count: {result['count']}")
    print(f"   Average experience: {result['avg_experience']}")
    if result.get('providers'):
        print(f"   Providers: {', '.join(result['providers'])}")
    
    print("\n8. Specialty Distribution with Aggregation:")
    result = test_case_8(providers)
    if result:
        max_specialty = max(result.items(), key=lambda x: x[1])
        print(f"   Highest average: {max_specialty[0]} ({max_specialty[1]:.2f} years)")
        print(f"   All specialties: {result}")
    
    print("\n9. Complex Ranking with Multiple Criteria:")
    result = test_case_9(providers)
    for i, match in enumerate(result, 1):
        print(f"   {i}. {match['name']} - Rating: {match['rating']}, Insurance types: {match['insurance_count']}")
    
    print("\n10. Multi-Step Conditional Logic with Exclusion:")
    result = test_case_10(providers)
    print(f"   Count: {result['count']}")
    print(f"   Average rating: {result['avg_rating']:.2f}")
    if result.get('providers'):
        print(f"   Providers: {', '.join(result['providers'])}")

if __name__ == '__main__':
    main()

