import os
import sys

# Set up environment to run outside Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')

import django
django.setup()

from chatbot.direct_implementation import (
    check_if_medication_recommendation_query,
    extract_symptom_from_medication_query,
    process_medication_recommendation_query
)

def main():
    print("=== Testing Medication Recommendation Detection ===")
    
    # Test cases and expected results
    test_cases = [
        ("Tôi bị ho thì nên uống thuốc gì", True),
        ("Tôi có cảm cúm, cần dùng loại thuốc nào", True),
        ("Thuốc nào trị đau đầu tốt nhất", True),
        ("Khi bị sốt, nên uống thuốc gì", True),
        ("Tôi muốn mua thuốc paracetamol", False),
        ("Thuốc trong kho còn bao nhiêu", False),
        ("Tôi bị sốt", False),
    ]
    
    for query, expected in test_cases:
        result = check_if_medication_recommendation_query(query)
        if result == expected:
            status = "✓"
        else:
            status = "✗"
        
        print(f"{status} Query: '{query}' -> Detected as medication query: {result} (Expected: {expected})")
    
    print("\n=== Testing Symptom Extraction from Medication Queries ===")
    
    # Test cases and expected results
    test_cases = [
        ("Tôi bị ho thì nên uống thuốc gì", "ho"),
        ("Tôi có cảm cúm, cần dùng loại thuốc nào", "cảm cúm"),
        ("Thuốc nào trị đau đầu tốt nhất", "đau đầu"),
        ("Khi bị sốt, nên uống thuốc gì", "sốt"),
        ("Tôi nên dùng thuốc gì để chữa đau bụng", "đau bụng"),
        ("Tôi mất ngủ, nên uống thuốc gì?", "mất ngủ"),
    ]
    
    for query, expected in test_cases:
        result = extract_symptom_from_medication_query(query)
        if result == expected:
            status = "✓"
        else:
            status = "✗"
        
        print(f"{status} Query: '{query}' -> Extracted symptom: '{result}' (Expected: '{expected}')")
    
    print("\n=== Testing Medication Recommendations ===")
    
    # Test with a real query
    query = "Tôi bị ho thì nên uống thuốc gì?"
    print(f"Processing query: '{query}'")
    
    response = process_medication_recommendation_query(query)
    print(f"Response: {response}\n")
    
    print("Test complete.")

if __name__ == "__main__":
    main() 