#!/usr/bin/env python
"""
Test script for chatbot functionality
Tests various types of questions to ensure comprehensive responses
"""

import os
import django
import json
import requests
from django.test import Client
from django.contrib.auth import authenticate

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from django.contrib.auth import get_user_model
from chatbot.models import BotMessage, ChatMemory

User = get_user_model()

def test_chatbot_questions():
    """
    Test chatbot with various types of questions
    """
    
    # Create or get test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
    
    # Test questions of different types
    test_questions = [
        # Medical questions with specific data
        "Triệu chứng đau đầu là gì?",
        "Bệnh cúm có triệu chứng gì?",
        "Thuốc paracetamol dùng để làm gì?",
        
        # Inventory questions
        "Thuốc paracetamol còn bao nhiêu trong kho?",
        "Kiểm tra tồn kho thuốc aspirin",
        "Thuốc nào đang sắp hết hàng?",
        
        # General health questions (should use Gemini API)
        "Làm thế nào để phòng ngừa cảm cúm?",
        "Ăn gì để tăng cường miễn dịch?",
        "Tác hại của việc thức khuya là gì?",
        
        # Non-medical questions (should use Gemini API)
        "Hôm nay thời tiết thế nào?",
        "Cách nấu phở ngon?",
        "Python là gì?",
        
        # Complex medical questions
        "Tôi bị đau đầu và sốt, có thể là bệnh gì?",
        "Thuốc nào tốt cho người bị cao huyết áp?",
        "Triệu chứng của bệnh tiểu đường type 2?",
        
        # Questions without enough detail
        "Đau bụng",
        "Thuốc",
        "Bệnh",
        "Tôi không khỏe",
        
        # Conversational questions
        "Xin chào!",
        "Bạn là ai?",
        "Bạn có thể giúp gì cho tôi?",
        "Cảm ơn bạn",
    ]
    
    print("=" * 60)
    print("CHATBOT TESTING")
    print("=" * 60)
    
    # Create Django test client
    client = Client()
    
    # Login test user
    client.force_login(test_user)
    
    # Clear previous chat history
    BotMessage.objects.filter(user=test_user).delete()
    ChatMemory.objects.filter(user=test_user).delete()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. QUESTION: {question}")
        print("-" * 50)
        
        # Send question to chatbot
        try:
            response = client.post('/chatbot/api/bot-send-message/', 
                data=json.dumps({'message': question}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('message', 'No response')
                query_type = data.get('query_type', 'unknown')
                
                print(f"RESPONSE TYPE: {query_type}")
                print(f"BOT RESPONSE: {bot_response}")
                
                # Analyze response quality
                response_length = len(bot_response.split())
                if response_length < 5:
                    print("⚠️  WARNING: Response seems too short")
                elif "Không tìm thấy thông tin" in bot_response and query_type != 'ai':
                    print("ℹ️  INFO: No database info found, should use AI fallback")
                elif query_type == 'ai':
                    print("✅ SUCCESS: Using AI for general/complex questions")
                elif query_type in ['medical', 'inventory', 'diagnosis']:
                    print("✅ SUCCESS: Using database for specific queries")
                
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.content}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETED")
    print("=" * 60)

def test_api_availability():
    """
    Test if Gemini API is properly configured
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ WARNING: GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✅ Gemini API Key found: {api_key[:10]}...{api_key[-5:]}")
    
    # Test API call
    try:
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        response = requests.post(
            f"{api_url}?key={api_key}",
            json={
                "contents": [{"parts": [{"text": "Hello, this is a test."}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100,
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Gemini API is working correctly")
            return True
        else:
            print(f"❌ Gemini API error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing API availability...")
    api_working = test_api_availability()
    
    print("\nTesting chatbot responses...")
    test_chatbot_questions()
    
    if not api_working:
        print("\n⚠️  WARNING: Gemini API is not working. Some responses may be limited.") 