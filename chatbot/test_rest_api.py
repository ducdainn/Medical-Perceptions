import os
import sys
import requests
import json

# Set up environment to run outside Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.test import RequestFactory

User = get_user_model()

def test_bot_send_message_api():
    """
    Test the bot_send_message API endpoint with various medical queries
    """
    print("=== Testing Bot Send Message REST API ===")
    
    # Create a test user
    username = "test_user"
    password = "testpass123"
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password)
    
    # Create a client and log in
    client = Client()
    success = client.login(username=username, password=password)
    
    if not success:
        print("Failed to log in")
        return
    
    # Test queries
    test_queries = [
        ("Tìm thuốc paracetamol", "inventory"),
        ("Tôi bị đau đầu, sốt và ho. Có thể là bệnh gì?", "diagnosis"),
        ("Triệu chứng của bệnh tiểu đường là gì?", "medical"),
        ("Làm thế nào để phòng ngừa bệnh cúm?", "ai")
    ]
    
    for query, expected_type in test_queries:
        print(f"\nTesting query: {query}")
        print(f"Expected response type: {expected_type}")
        
        # Send the request to the API
        response = client.post(
            '/chatbot/api/bot-send-message/',
            data=json.dumps({"message": query}),
            content_type="application/json"
        )
        
        # Check the response
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['message'][:100]}..." if len(data['message']) > 100 else data['message'])
            
            query_type = data.get('query_type', 'unknown')
            print(f"Query type: {query_type}")
            
            if query_type == expected_type:
                print("✅ Correct response type")
            else:
                print(f"❌ Wrong response type: expected {expected_type}, got {query_type}")
                
            # Check if the response actually has content
            if "Tôi không tìm thấy thông tin liên quan" in data['message'] and expected_type != 'generic':
                print("❌ Got generic response when expecting specific information")
            else:
                print("✅ Response has useful content")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.content)
            
    print("\nTest complete. Check the responses above.")

if __name__ == "__main__":
    test_bot_send_message_api() 