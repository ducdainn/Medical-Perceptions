#!/usr/bin/env python
"""
Quick test script for chatbot improvements
"""

import os
import django
import json
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from django.contrib.auth import get_user_model
from chatbot.models import BotMessage, ChatMemory

User = get_user_model()

def quick_test():
    """Quick test with a few questions"""
    
    # Create or get test user
    test_user, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'test2@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User2'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
    
    # Test questions
    test_questions = [
        "Xin chào!",
        "Đau đầu",
        "Thuốc",
        "Bệnh cúm có triệu chứng gì?",
        "Làm thế nào để phòng ngừa cảm cúm?",
        "Cảm ơn bạn",
    ]
    
    print("=" * 50)
    print("QUICK CHATBOT TEST")
    print("=" * 50)
    
    # Create Django test client
    client = Client()
    client.force_login(test_user)
    
    # Clear previous chat history
    BotMessage.objects.filter(user=test_user).delete()
    ChatMemory.objects.filter(user=test_user).delete()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. QUESTION: {question}")
        print("-" * 30)
        
        try:
            response = client.post('/chatbot/api/bot-send-message/', 
                data=json.dumps({'message': question}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('message', 'No response')
                query_type = data.get('query_type', 'unknown')
                
                print(f"TYPE: {query_type}")
                print(f"RESPONSE: {bot_response[:200]}{'...' if len(bot_response) > 200 else ''}")
                
                # Check improvements
                if query_type == 'greeting' and i == 1:
                    print("✅ GREETING improved!")
                elif query_type == 'expanded' and i in [2, 3]:
                    print("✅ SHORT QUERY expanded!")
                elif query_type == 'prevention' and i == 5:
                    print("✅ PREVENTION handled!")
                elif query_type == 'medical' and i == 4:
                    print("✅ MEDICAL database working!")
                elif query_type == 'greeting' and i == 6:
                    print("✅ THANKS handled!")
                
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 50)
    print("QUICK TEST COMPLETED")
    print("=" * 50)

if __name__ == '__main__':
    quick_test() 