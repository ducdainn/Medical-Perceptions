import os
import sys
import requests
import json

# Set up environment to run outside Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')

import django
django.setup()

def test_ai_fallback():
    """
    Interactive test for AI fallback in the chatbot
    """
    print("=== Chatbot AI Fallback Test ===")
    
    # Gemini API configuration from env or use default
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCEua2hrKMgAe_8qcawIXwVGNA7dV39BdA")
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Test health-related queries that might not be in our database
    test_queries = [
        "Tìm thông tin về thuốc paracetamol",
        "Thuốc điều trị cao huyết áp?",
        "Tôi bị đau đầu, sốt và ho. Có thể là bệnh gì?",
        "Triệu chứng của bệnh tiểu đường là gì?"
    ]
    
    system_info = """
    Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
    Hãy trả lời câu hỏi y tế dựa trên kiến thức chuyên môn của bạn.
    Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
    Nếu không chắc chắn về thông tin, hãy cho biết giới hạn và đề xuất người dùng tham khảo ý kiến bác sĩ.
    """
    
    # Test each query
    for idx, query in enumerate(test_queries, 1):
        print(f"\nTest Query {idx}: {query}")
        
        try:
            # Call the Gemini API
            response = requests.post(
                f"{api_url}?key={api_key}",
                json={
                    "contents": [{"parts": [{"text": f"{system_info}\n\nCâu hỏi: {query}"}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1024,
                    }
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                if ai_response:
                    print(f"AI Response: {ai_response[:200]}..." if len(ai_response) > 200 else ai_response)
                    print("✅ Successfully generated response")
                else:
                    print("❌ Failed to get response from AI")
            else:
                print(f"❌ Error: API returned status code {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error calling API: {str(e)}")
            
    print("\nTest complete. Check the responses above to verify AI fallback behavior.")

if __name__ == "__main__":
    test_ai_fallback() 
