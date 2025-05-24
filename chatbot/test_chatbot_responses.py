import requests
import json
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from chatbot.advanced_data_access import AdvancedChatbotDataAccess

def test_inventory_query():
    """Test the chatbot's ability to answer inventory queries"""
    print("\n=== Testing Inventory Queries ===")
    
    # Test direct database access
    query = "paracetamol"
    print(f"Direct query for: {query}")
    inventory_results = AdvancedChatbotDataAccess.search_inventory(query)
    print(f"Results: {len(inventory_results)} items found")
    
    # If there are results, print some details
    if inventory_results:
        print(f"First item: {inventory_results[0]['name']}, Quantity: {inventory_results[0]['quantity']}")
    else:
        print("No items found. Database may be empty or query returned no results.")
    
    # Test formatted response
    print("\nTesting formatted inventory query response:")
    response = AdvancedChatbotDataAccess.process_inventory_query("Tìm thuốc paracetamol")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    return len(inventory_results) > 0

def test_symptom_disease_query():
    """Test the chatbot's ability to answer medical knowledge queries"""
    print("\n=== Testing Medical Knowledge Queries ===")
    
    # Test symptoms query
    symptoms = ["sốt", "đau đầu", "ho"]
    print(f"Searching for diseases with symptoms: {', '.join(symptoms)}")
    
    try:
        from chatbot.utils import ChatbotDataAccess
        disease_results = ChatbotDataAccess.get_related_diseases_for_symptoms(symptoms)
        print(f"Results: {len(disease_results)} diseases found")
        
        if disease_results:
            print(f"Top disease: {disease_results[0]['name']}")
            print(f"Matching symptoms: {', '.join(disease_results[0]['matching_symptoms'])}")
        else:
            print("No diseases found for these symptoms.")
        
        return len(disease_results) > 0
    except Exception as e:
        print(f"Error querying medical knowledge: {str(e)}")
        return False

def test_api_inventory_endpoint():
    """Test the inventory API endpoint"""
    print("\n=== Testing Inventory API Endpoint ===")
    
    try:
        client = Client()
        response = client.get('/chatbot/api/test/inventory/?query=paracetamol')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"API Response: {data['success']}")
            print(f"Items found: {len(data['data'])}")
            print(f"Sample response: {data['formatted_response'][:200]}..." if len(data['formatted_response']) > 200 else data['formatted_response'])
            return True
        else:
            print(f"Error: API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error calling API: {str(e)}")
        return False

def test_websocket_response(message):
    """Test the chatbot's WebSocket response to a specific message"""
    print(f"\n=== Testing WebSocket Response to: {message} ===")
    print("Note: This test requires a running server with WebSockets enabled.")
    print("Skipping live WebSocket test. For manual testing, use the chat interface.")
    return None

def run_all_tests():
    """Run all chatbot tests"""
    print("=== Starting Chatbot Response Tests ===")
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Inventory query
    if test_inventory_query():
        print("✅ Inventory query test passed")
        tests_passed += 1
    else:
        print("❌ Inventory query test failed")
    
    # Test 2: Symptom/disease query
    if test_symptom_disease_query():
        print("✅ Symptom/disease query test passed")
        tests_passed += 1
    else:
        print("❌ Symptom/disease query test failed")
    
    # Test 3: API endpoint
    if test_api_inventory_endpoint():
        print("✅ API endpoint test passed")
        tests_passed += 1
    else:
        print("❌ API endpoint test failed")
    
    # Summary
    print(f"\n=== Test Summary: {tests_passed}/{tests_total} tests passed ===")

if __name__ == "__main__":
    run_all_tests() 