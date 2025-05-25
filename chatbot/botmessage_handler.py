from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import BotMessage, ChatMemory
from .utils import ChatbotDataAccess
from .advanced_data_access import AdvancedChatbotDataAccess
import json
import requests
import os
import re

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCEua2hrKMgAe_8qcawIXwVGNA7dV39BdA")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Function to clean markdown formatting
def clean_markdown(text):
    # Remove asterisks for bold/italic formatting
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    # Remove other markdown formatting if needed
    text = re.sub(r'\*\s+', '• ', text)
    return text

# Helper functions for medical queries
def check_if_medical_query(message):
    medical_keywords = ['triệu chứng', 'bệnh', 'chứng', 'symptom', 'disease', 'illness', 'condition', 'điều trị', 'treatment']
    return any(keyword in message.lower() for keyword in medical_keywords)

def extract_search_term(message):
    # Extract search term from message
    patterns = [
        r'về\s+(.+?)(?:\s+là|\s+có|\?|$)',
        r'của\s+(.+?)(?:\s+là|\s+có|\?|$)',
        r'bệnh\s+(.+?)(?:\s+là|\s+có|\?|$)',
        r'triệu chứng\s+(.+?)(?:\s+là|\s+có|\?|$)',
        r'triệu chứng\s+của\s+(.+?)(?:\s+là|\s+có|\?|$)',
    ]
    
    # Direct extraction for common patterns
    if "tiểu đường" in message.lower():
        return "tiểu đường"
    if "cúm" in message.lower():
        return "cúm"
    if "covid" in message.lower() or "covid-19" in message.lower():
        return "covid-19"
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # If no specific pattern matches, use a simple approach
    words = message.split()
    if len(words) > 2:
        return ' '.join(words[2:])
    return None

def process_medical_query(message):
    # Process medical query using database
    search_term = extract_search_term(message)
    print(f"Extracted search term: {search_term}")
    if search_term:
        print(f"Searching knowledge base for: {search_term}")
        try:
            # First try the ChatbotDataAccess method
            results = ChatbotDataAccess.search_knowledge_base(search_term)
            print(f"Search results from ChatbotDataAccess: {results}")
            
            # If empty results, try our direct search method
            if not results or (not results.get('disease') and not results.get('symptom')):
                print("No results from ChatbotDataAccess, trying direct search")
                direct_results = direct_search_knowledge_base(search_term)
                if direct_results:
                    results = direct_results
                    print(f"Direct search results: {direct_results}")
            
            if results and (results.get('disease') or results.get('symptom')):
                if results.get('disease'):
                    disease = results['disease'][0]
                    response = f"Thông tin về {disease['name']}:\n"
                    if disease.get('description'):
                        response += f"Mô tả: {disease['description']}\n"
                    if disease.get('symptoms'):
                        response += f"Triệu chứng: {disease['symptoms']}\n"
                    if disease.get('treatments'):
                        response += f"Điều trị: {disease['treatments']}\n"
                    return response
                elif results.get('symptom'):
                    symptom = results['symptom'][0]
                    response = f"Thông tin về triệu chứng {symptom['name']}:\n"
                    if symptom.get('description'):
                        response += f"Mô tả: {symptom['description']}\n"
                    if symptom.get('associated_diseases'):
                        response += f"Bệnh liên quan: {symptom['associated_diseases']}\n"
                    return response
            else:
                print("No results found in knowledge base")
        except Exception as e:
            print(f"Error searching knowledge base: {str(e)}")
    return "Không tìm thấy thông tin liên quan"

def extract_symptom_list(message):
    # Extract list of symptoms from message
    symptom_patterns = [
        r'triệu chứng\s+(.+?)(?:\s+và|\s+hoặc|\s+or|\?|$)',
        r'có\s+(.+?)(?:\s+và|\s+hoặc|\s+or|\?|$)',
        r'bị\s+(.+?)(?:\s+và|\s+hoặc|\s+or|\?|$)',
    ]
    
    symptoms = []
    
    # Direct extraction for specific symptoms in the message
    if "đau đầu" in message.lower():
        symptoms.append("đau đầu")
    if "sốt" in message.lower():
        symptoms.append("sốt")
    if "ho" in message.lower():
        symptoms.append("ho")
    if "nhức" in message.lower():
        symptoms.append("nhức")
    if "mệt" in message.lower():
        symptoms.append("mệt")
    if "chóng mặt" in message.lower():
        symptoms.append("chóng mặt")
    if "buồn nôn" in message.lower():
        symptoms.append("buồn nôn")
    if "nôn" in message.lower() and "buồn nôn" not in message.lower():
        symptoms.append("nôn")
    if "tiêu chảy" in message.lower():
        symptoms.append("tiêu chảy")
    
    # If we already found symptoms directly, return them
    if len(symptoms) >= 2:
        return symptoms
    
    # Otherwise try the patterns
    for pattern in symptom_patterns:
        matches = re.finditer(pattern, message, re.IGNORECASE)
        for match in matches:
            symptom_text = match.group(1).strip()
            # Split by common separators
            for symptom in re.split(r',|\s+và\s+|\s+cùng\s+với\s+|\s+kèm\s+|\s+kèm\s+theo\s+', symptom_text):
                if symptom.strip():
                    symptoms.append(symptom.strip())
    
    return symptoms

def direct_search_knowledge_base(search_term):
    """
    Directly search the knowledge base for medical information
    This is a fallback in case ChatbotDataAccess.search_knowledge_base returns empty results
    """
    try:
        # Import Django models directly
        from diagnosis.models import Disease, Symptom
        
        # Search for diseases
        diseases = Disease.objects.filter(name__icontains=search_term)
        
        # Search for symptoms
        symptoms = Symptom.objects.filter(name__icontains=search_term)
        
        # Format results
        results = {}
        
        if diseases.exists():
            disease_list = []
            for disease in diseases:
                disease_dict = {
                    'name': disease.name,
                    'description': disease.description,
                }
                if hasattr(disease, 'symptoms'):
                    disease_dict['symptoms'] = ', '.join([s.name for s in disease.symptoms.all()])
                if hasattr(disease, 'treatments'):
                    disease_dict['treatments'] = ', '.join([t.name for t in disease.treatments.all()])
                disease_list.append(disease_dict)
            results['disease'] = disease_list
            
        if symptoms.exists():
            symptom_list = []
            for symptom in symptoms:
                symptom_dict = {
                    'name': symptom.name,
                    'description': symptom.description if hasattr(symptom, 'description') else '',
                }
                if hasattr(symptom, 'associated_diseases'):
                    symptom_dict['associated_diseases'] = ', '.join([d.name for d in symptom.associated_diseases.all()])
                symptom_list.append(symptom_dict)
            results['symptom'] = symptom_list
            
        return results
    except Exception as e:
        print(f"Error in direct search: {str(e)}")
        return None

def check_if_prevention_query(message):
    """Check if the message is asking about prevention"""
    prevention_keywords = [
        'phòng ngừa', 'phòng bệnh', 'ngăn ngừa', 'ngăn chặn', 'đề phòng',
        'cách phòng', 'làm thế nào để phòng', 'làm sao để phòng', 'tránh bị'
    ]
    
    return any(keyword in message.lower() for keyword in prevention_keywords)

def check_if_medication_recommendation_query(message):
    """Check if the message is asking for medication recommendations"""
    medication_recommendation_patterns = [
        r'(nên|cần) uống (thuốc|loại thuốc) (gì|nào)',
        r'(nên|cần) dùng (thuốc|loại thuốc) (gì|nào)',
        r'thuốc (gì|nào) (để|trị|chữa)',
        r'dùng (thuốc|loại thuốc) (gì|nào) (để|khi|chữa)',
        r'uống (thuốc|loại thuốc) (gì|nào) (để|khi|chữa)',
        r'thuốc (nào|gì) tốt',
        r'thuốc (cho|trị) (bệnh|triệu chứng)'
    ]
    
    for pattern in medication_recommendation_patterns:
        if re.search(pattern, message.lower()):
            return True
    
    return False

def extract_symptom_from_medication_query(message):
    """Extract symptom or condition from a medication recommendation query"""
    # Directly check for common symptoms first (this takes precedence)
    common_symptoms = {
        'ho': 'ho',
        'sốt': 'sốt',
        'nhức đầu': 'nhức đầu',
        'đau đầu': 'đau đầu',
        'đau bụng': 'đau bụng',
        'tiêu chảy': 'tiêu chảy',
        'mất ngủ': 'mất ngủ',
        'cảm': 'cảm',
        'cảm cúm': 'cảm cúm',
        'cảm lạnh': 'cảm lạnh',
        'viêm họng': 'viêm họng',
        'viêm mũi': 'viêm mũi',
        'đau răng': 'đau răng',
        'nhức răng': 'nhức răng',
        'viêm xoang': 'viêm xoang',
        'dị ứng': 'dị ứng',
        'đau lưng': 'đau lưng'
    }
    
    for symptom_text, symptom_name in common_symptoms.items():
        if symptom_text in message.lower():
            return symptom_name
    
    # If no common symptom found, try pattern matching
    symptom_patterns = [
        r'bị\s+([\w\s]+?)(?:\s+(?:thì|nên|cần)|$)',
        r'có\s+([\w\s]+?)(?:,|\s+(?:cần|nên))',
        r'(?:thuốc|điều trị|chữa|trị)\s+([\w\s]+?)(?:\s+(?:tốt|hiệu quả)|$)',
        r'(?:khi|lúc)\s+bị\s+([\w\s]+?)(?:,|\s+(?:thì|nên|cần)|$)'
    ]
    
    for pattern in symptom_patterns:
        match = re.search(pattern, message.lower())
        if match:
            extracted = match.group(1).strip()
            # Don't return words that are likely part of question structure
            if extracted in ["gì", "nào", "loại", "thuốc"]:
                continue
            return extracted
    
    return None

def process_medication_recommendation_query(message):
    """Process query asking for medication recommendations"""
    symptom = extract_symptom_from_medication_query(message)
    
    if symptom:
        # Call Gemini API for medication recommendations based on symptom
        system_info = """
        Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám. 
        Hãy đưa ra gợi ý về thuốc có thể sử dụng cho các triệu chứng được đề cập.
        Luôn đưa ra các lời khuyên an toàn và lưu ý về việc cần tham khảo ý kiến bác sĩ 
        trước khi sử dụng bất kỳ loại thuốc nào.
        Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
        
        Chú ý: KHÔNG sử dụng ký tự * trong câu trả lời của bạn. Thay vì dùng dấu * để đánh dấu điểm, hãy dùng dấu • hoặc -.
        """
        
        prompt = f"{system_info}\n\nTôi bị {symptom}, tôi nên uống thuốc gì?"
        
        try:
            # Call the Gemini API
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
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
                    # Clean any markdown formatting
                    return clean_markdown(ai_response)
        except Exception as e:
            print(f"Error calling Gemini API for medication recommendation: {str(e)}")
    
    return "Tôi không thể đưa ra khuyến nghị thuốc cụ thể cho tình trạng của bạn. Vui lòng tham khảo ý kiến bác sĩ để được tư vấn phù hợp."

@csrf_exempt
@login_required
def enhanced_bot_send_message(request):
    """
    Enhanced API endpoint for sending messages to the chatbot
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        reset_context = data.get('reset_context', False)
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create user's memory object for context
        chat_memory, created = ChatMemory.objects.get_or_create(user=request.user)
        
        # Reset context if requested
        if reset_context:
            chat_memory.clear_context()
        
        # Save user message
        user_msg = BotMessage.objects.create(
            user=request.user,
            type='user',
            content=user_message
        )
        
        # Add to memory context
        chat_memory.add_message('user', user_message)
        
        # Handle simple greetings and thanks
        if is_greeting_or_thanks(user_message):
            response = handle_greeting_or_thanks(user_message)
            bot_msg = BotMessage.objects.create(
                user=request.user,
                type='bot',
                content=response
            )
            chat_memory.add_message('bot', response)
            return JsonResponse({
                'message': response,
                'type': 'bot',
                'query_type': 'greeting'
            })
        
        # Handle very short queries with expansion
        if len(user_message.split()) <= 2:
            expanded_response = handle_short_query(user_message)
            if expanded_response:
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=expanded_response
                )
                chat_memory.add_message('bot', expanded_response)
                return JsonResponse({
                    'message': expanded_response,
                    'type': 'bot',
                    'query_type': 'expanded'
                })
        
        # Check for inventory queries first
        if any(keyword in user_message.lower() for keyword in ['thuốc', 'kho', 'tồn kho', 'inventory', 'còn hàng', 'hết hàng']):
            inventory_response = AdvancedChatbotDataAccess.process_inventory_query(user_message)
            if inventory_response and "Không tìm thấy thông tin" not in inventory_response:
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=inventory_response
                )
                chat_memory.add_message('bot', inventory_response)
                return JsonResponse({
                    'message': inventory_response,
                    'type': 'bot',
                    'query_type': 'inventory'
                })
        
        # Check for medication recommendation queries
        if check_if_medication_recommendation_query(user_message):
            medication_response = process_medication_recommendation_query(user_message)
            if medication_response:
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=medication_response
                )
                chat_memory.add_message('bot', medication_response)
                return JsonResponse({
                    'message': medication_response,
                    'type': 'bot',
                    'query_type': 'medication'
                })
        
        # Check for prevention queries
        if check_if_prevention_query(user_message):
            prevention_response = process_prevention_query(user_message)
            if prevention_response:
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=prevention_response
                )
                chat_memory.add_message('bot', prevention_response)
                return JsonResponse({
                    'message': prevention_response,
                    'type': 'bot',
                    'query_type': 'prevention'
                })
        
        # Check for medical knowledge queries (symptoms, diseases)
        if check_if_medical_query(user_message):
            search_term = extract_search_term(user_message)
            if search_term:
                database_response = process_medical_query(user_message)
                if database_response and "Không tìm thấy thông tin liên quan" not in database_response:
                    bot_msg = BotMessage.objects.create(
                        user=request.user,
                        type='bot',
                        content=database_response
                    )
                    chat_memory.add_message('bot', database_response)
                    return JsonResponse({
                        'message': database_response,
                        'type': 'bot',
                        'query_type': 'medical'
                    })
        
        # Check for symptom diagnosis query
        symptom_list = extract_symptom_list(user_message)
        if len(symptom_list) >= 2:
            diagnosis_response = AdvancedChatbotDataAccess.process_advanced_diagnosis(symptom_list)
            if diagnosis_response and "Không tìm thấy bệnh" not in diagnosis_response:
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=diagnosis_response
                )
                chat_memory.add_message('bot', diagnosis_response)
                return JsonResponse({
                    'message': diagnosis_response,
                    'type': 'bot',
                    'query_type': 'diagnosis'
                })
        
        # If we've got here, try using Gemini API for general knowledge response
        if GEMINI_API_KEY:
            conversation_context = chat_memory.get_context_for_prompt()
            
            system_info = """
            Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
            Hãy trả lời câu hỏi y tế dựa trên kiến thức chuyên môn của bạn.
            Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
            Nếu không chắc chắn về thông tin, hãy cho biết giới hạn của mình và đề xuất người dùng 
            tham khảo ý kiến bác sĩ hoặc chuyên gia y tế.
            
            Chú ý: KHÔNG sử dụng ký tự * trong câu trả lời của bạn. Thay vì dùng dấu * để đánh dấu điểm, hãy dùng dấu • hoặc -.
            
            Nếu câu hỏi không liên quan đến y tế hoặc sức khỏe, hãy lịch sự từ chối và giải thích rằng bạn chỉ hỗ trợ các vấn đề y tế.
            """
            
            prompt = f"{system_info}\n\n{conversation_context}\n\nCâu hỏi: {user_message}"
            
            try:
                response = requests.post(
                    f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 1024,
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    
                    if ai_response:
                        ai_response = clean_markdown(ai_response)
                        
                        bot_msg = BotMessage.objects.create(
                            user=request.user,
                            type='bot',
                            content=ai_response
                        )
                        chat_memory.add_message('bot', ai_response)
                        
                        return JsonResponse({
                            'message': ai_response,
                            'type': 'bot',
                            'query_type': 'ai'
                        })
                else:
                    print(f"Gemini API error: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error calling Gemini API: {str(e)}")
        
        # Enhanced fallback response based on query type
        fallback_response = get_intelligent_fallback_response(user_message)
        
        bot_msg = BotMessage.objects.create(
            user=request.user,
            type='bot',
            content=fallback_response
        )
        chat_memory.add_message('bot', fallback_response)
        
        return JsonResponse({
            'message': fallback_response,
            'type': 'bot',
            'query_type': 'fallback'
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def process_prevention_query(message):
    """Process prevention-related queries"""
    # Common prevention topics
    prevention_responses = {
        'cúm': """Để phòng ngừa cúm, bạn có thể:
• Tiêm vắc-xin cúm hàng năm
• Rửa tay thường xuyên với xà phòng
• Tránh tiếp xúc gần với người bệnh
• Che miệng khi ho, hắt hơi
• Tăng cường sức đề kháng bằng ăn uống đầy đủ
• Giữ vệ sinh môi trường sống và làm việc""",
        
        'covid': """Để phòng ngừa COVID-19:
• Đeo khẩu trang nơi đông người
• Rửa tay thường xuyên hoặc dùng nước rửa tay
• Giữ khoảng cách an toàn với người khác
• Tiêm vắc-xin COVID-19 đầy đủ
• Tránh những nơi đông đúc, kín gió
• Tăng cường sức khỏe bằng chế độ ăn uống lành mạnh""",
        
        'cảm lạnh': """Để phòng ngừa cảm lạnh:
• Rửa tay thường xuyên
• Tránh chạm tay vào mặt
• Giữ ấm cơ thể khi thời tiết thay đổi
• Ăn uống đầy đủ chất dinh dưỡng
• Ngủ đủ giấc
• Tập thể dục đều đặn để tăng sức đề kháng"""
    }
    
    message_lower = message.lower()
    for disease, response in prevention_responses.items():
        if disease in message_lower:
            return response
    
    # Generic prevention advice
    return """Để phòng ngừa bệnh tật nói chung:
• Rửa tay thường xuyên
• Ăn uống lành mạnh, đa dạng
• Tập thể dục đều đặn
• Ngủ đủ giấc
• Tiêm vắc-xin theo lịch
• Khám sức khỏe định kỳ
• Tránh stress, giữ tinh thần thoải mái"""

def is_greeting_or_thanks(message):
    """Check if message is a greeting or thanks"""
    greetings = ['xin chào', 'chào', 'hello', 'hi', 'cảm ơn', 'thanks', 'thank you', 'tạm biệt', 'bye']
    return any(greeting in message.lower() for greeting in greetings)

def handle_greeting_or_thanks(message):
    """Handle greeting and thanks messages"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['cảm ơn', 'thanks', 'thank you']):
        return "Rất vui được hỗ trợ bạn! Nếu có thêm câu hỏi nào về sức khỏe, đừng ngại hỏi nhé."
    
    if any(word in message_lower for word in ['tạm biệt', 'bye']):
        return "Tạm biệt! Chúc bạn có một ngày tốt lành và luôn khỏe mạnh!"
    
    # Default greeting
    return "Xin chào! Tôi là trợ lý chăm sóc sức khỏe tự động của ReViCARE. Tôi có thể giúp bạn tìm hiểu về các vấn đề y tế, thuốc men, và sức khỏe. Bạn có câu hỏi gì cho tôi không?"

def handle_short_query(message):
    """Handle very short queries by expanding them"""
    message_lower = message.lower().strip()
    
    # Handle single word medical queries
    short_responses = {
        'đau đầu': """Đau đầu có thể có nhiều nguyên nhân:
• Căng thẳng, stress
• Thiếu ngủ
• Khô cơ thể (thiếu nước)
• Áp lực công việc
• Viêm xoang
• Migraine

Bạn có thể cho biết thêm: đau đầu có kèm theo triệu chứng nào khác không? Đau bao lâu rồi?""",
        
        'đau bụng': """Đau bụng có thể do:
• Khó tiêu
• Đầy hơi
• Ăn uống không phù hợp
• Viêm dạ dày
• Táo bón

Bạn có thể mô tả thêm: đau ở vị trí nào? Đau như thế nào? Có kèm theo triệu chứng khác không?""",
        
        'sốt': """Sốt thường là dấu hiệu cơ thể đang chống lại nhiễm trùng:
• Nhiệt độ trên 37.5°C
• Có thể kèm mệt mỏi, ớn lạnh
• Thường do virus hoặc vi khuẩn gây ra

Bạn có thể cho biết: sốt bao nhiều độ? Sốt bao lâu rồi? Có triệu chứng nào khác không?""",
        
        'ho': """Ho có thể chia thành:
• Ho khô: thường do kích ứng
• Ho có đờm: thường do nhiễm trùng
• Ho kéo dài: cần khám để tìm nguyên nhân

Bạn có thể mô tả: ho khô hay có đờm? Ho bao lâu rồi? Có kèm sốt không?""",
        
        'thuốc': """Bạn muốn hỏi về thuốc gì cụ thể?
• Tìm kiếm thông tin thuốc cụ thể
• Kiểm tra tồn kho thuốc
• Hỏi về tác dụng của thuốc
• Hỏi về liều dùng

Vui lòng nêu rõ tên thuốc hoặc câu hỏi cụ thể nhé!""",
        
        'bệnh': """Bạn muốn hỏi về bệnh gì?
• Triệu chứng của một bệnh cụ thể
• Cách điều trị
• Cách phòng ngừa
• Chẩn đoán từ triệu chứng

Vui lòng nêu rõ tên bệnh hoặc triệu chứng bạn quan tâm!""",
    }
    
    # Check for exact matches
    if message_lower in short_responses:
        return short_responses[message_lower]
    
    # Check for partial matches
    for key, response in short_responses.items():
        if key in message_lower:
            return response
    
    # Handle very generic queries
    if message_lower in ['không khỏe', 'bệnh', 'đau']:
        return """Tôi hiểu bạn đang không cảm thấy khỏe. Để có thể hỗ trợ tốt hơn, bạn có thể mô tả cụ thể hơn:
• Bạn có triệu chứng gì?
• Triệu chứng xuất hiện bao lâu rồi?
• Có điều gì khiến bạn cảm thấy tốt hơn hoặc tệ hơn không?

Thông tin chi tiết sẽ giúp tôi tư vấn chính xác hơn."""
    
    return None

def get_intelligent_fallback_response(message):
    """Provide intelligent fallback response based on message content"""
    message_lower = message.lower()
    
    # Check if it's health-related
    health_keywords = ['đau', 'bệnh', 'triệu chứng', 'thuốc', 'điều trị', 'khỏe', 'sức khỏe']
    is_health_related = any(keyword in message_lower for keyword in health_keywords)
    
    if is_health_related:
        return """Tôi hiểu bạn đang hỏi về vấn đề sức khỏe. Tuy nhiên, tôi cần thêm thông tin chi tiết để có thể hỗ trợ tốt hơn.

Bạn có thể:
• Mô tả rõ hơn triệu chứng hoặc vấn đề
• Nêu cụ thể tên thuốc hoặc bệnh bạn quan tâm
• Liên hệ trực tiếp với bác sĩ hoặc dược sĩ để được tư vấn chính xác

Lưu ý: Tôi chỉ cung cấp thông tin tham khảo, không thay thế cho ý kiến chuyên gia y tế."""
    
    # For non-health questions
    return """Tôi là trợ lý chăm sóc sức khỏe của ReViCARE, chuyên hỗ trợ các vấn đề y tế và sức khỏe.

Tôi có thể giúp bạn:
• Tìm hiểu về triệu chứng bệnh
• Thông tin về thuốc men
• Tư vấn sức khỏe cơ bản
• Kiểm tra tồn kho thuốc

Nếu bạn có câu hỏi về chủ đề khác, vui lòng tìm kiếm trên các nguồn thông tin phù hợp khác.""" 