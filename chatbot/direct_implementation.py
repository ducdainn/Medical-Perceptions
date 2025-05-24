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

def extract_medication_names_from_response(response_text):
    """
    Extract medication names from a response text
    Returns a list of medication names mentioned in the response
    """
    # Common medication names in Vietnamese and international
    common_medications = [
        'paracetamol', 'ibuprofen', 'aspirin', 'acetaminophen', 'dextromethorphan',
        'guaifenesin', 'bromhexin', 'ambroxol', 'acetylcysteine', 'n-acetylcysteine', 'terpin hydrate',
        'codein', 'loratadin', 'cetirizin', 'desloratadin', 'diphenhydramine',
        'amoxicillin', 'azithromycin', 'vitamin', 'kháng sinh', 'kháng viêm',
        'panadol', 'tylenol', 'advil', 'nsaid', 'salbutamol', 'ventolin'
    ]
    
    # Pattern to extract medication names with bullet points
    medication_patterns = [
        r'[•\-\*]\s+([\w\s\-\(\)]+?)(?::|;|$)',  # Bullet point patterns
        r'(?:thuốc|dùng|sử dụng)\s+([\w\s\-]+)(?:\s+để|\s+giúp|:|\.|,)',  # Words after "thuốc" 
        r'(?:như|gồm|bao gồm)\s+([\w\s\-]+)(?:\.|,|\s+có)',  # Words after "như/gồm"
        r'(\w+)\s+\(\w+\)',  # Words followed by parentheses
        r'\d\.\s+([\w\s\-]+?)(?::|;|$)',  # Numbered list items
    ]
    
    medications = []
    
    # First, look for common known medications
    for med in common_medications:
        if med.lower() in response_text.lower():
            # Find the full medication name with proper capitalization
            start_index = response_text.lower().find(med.lower())
            
            # Get some context around the medication name
            start = max(0, start_index - 10)
            end = min(len(response_text), start_index + len(med) + 30)
            context = response_text[start:end]
            
            # Find the exact word boundaries
            med_pattern = re.compile(r'\b' + re.escape(med) + r'\b', re.IGNORECASE)
            match = med_pattern.search(context)
            if match:
                exact_med = match.group(0)
                # Check if it's part of a branded name or has additional information
                word_context = context[max(0, match.start() - 15):min(len(context), match.end() + 15)]
                branded_pattern = re.compile(r'([A-Z][a-z]+\s*)?' + re.escape(exact_med) + r'(\s*\([^)]+\))?', re.IGNORECASE)
                branded_match = branded_pattern.search(word_context)
                if branded_match and branded_match.group(0) != exact_med:
                    medications.append(branded_match.group(0).strip())
                else:
                    medications.append(exact_med)
    
    # Then use patterns to find other potential medications
    lines = response_text.split('\n')
    for line in lines:
        # Skip very short lines
        if len(line.strip()) < 3:
            continue
            
        # Check if the line is probably mentioning a medication
        has_medication_keyword = any(keyword in line.lower() for keyword in ['thuốc', 'dùng', 'uống', 'sử dụng', 'mg', 'liều', 'dose'])
        
        if has_medication_keyword or '•' in line or '-' in line or ':' in line:
            # Apply all patterns to this line
            for pattern in medication_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    med_name = match.group(1).strip()
                    # Avoid very common words and non-medication terms
                    common_words = ['thuốc', 'loại', 'như', 'này', 'đó', 'có thể', 'nên', 'không', 'và', 'hoặc', 'cần', 'phải', 'là']
                    if (
                        med_name and 
                        len(med_name) > 3 and 
                        not any(word == med_name.lower() for word in common_words) and
                        not med_name.startswith('không') and
                        not med_name.lower().startswith('nên')
                    ):
                        medications.append(med_name)
    
    # Clean up and deduplicate
    unique_medications = []
    seen = set()
    for med in medications:
        med_clean = med.strip()
        med_lower = med_clean.lower()
        
        # Skip items that are likely not medications
        if med_lower in ['cho trẻ em', 'người lớn', 'liều lượng', 'không quá', 'đừng sử dụng']:
            continue
            
        if med_lower not in seen and len(med_clean) > 2:
            seen.add(med_lower)
            unique_medications.append(med_clean)
    
    return unique_medications

def check_if_inventory_query_about_medicine(message, context_medications):
    """
    Check if the message is asking about medication inventory
    context_medications is a list of medications previously mentioned in conversation
    """
    # If no medications were previously discussed, this can't be a follow-up inventory query
    if not context_medications:
        return False
    
    # Check if the message contains inventory keywords
    inventory_keywords = [
        'kho', 'tồn kho', 'inventory', 'còn hàng', 'hết hàng', 'còn không', 
        'có bán', 'giá', 'bán', 'mua', 'bao nhiêu', 'nhà thuốc', 'pharmacy'
    ]
    has_inventory_keyword = any(keyword in message.lower() for keyword in inventory_keywords)
    
    if not has_inventory_keyword:
        return False
    
    # Check if any previously mentioned medication is in this message
    for medication in context_medications:
        # Clean medication name for comparison
        med_clean = medication.lower()
        med_words = med_clean.split()
        
        # Skip very common words that might cause false positives
        if len(med_words) == 1 and len(med_clean) <= 3:
            continue
            
        if med_clean in message.lower():
            return True
        
        # For longer medication names, check if main part is mentioned
        if len(med_words) > 1:
            main_word = max(med_words, key=len)  # Get longest word in the medication name
            if len(main_word) > 3 and main_word in message.lower():
                return True
    
    # Check if the message contains generic references to previously mentioned medications
    reference_patterns = [
        r'(thuốc|loại thuốc|medicine) (đó|này|kia|những|trên|vừa|mới|đã)',
        r'những (thuốc|loại thuốc) (này|vừa|trên|mới|rồi)',
        r'(có|còn|hết|bán|mua) (không|được không|được chưa)',
        r'(giá|giá tiền|giá cả) (thuốc|của thuốc)',
        r'(nhà thuốc|pharmacy|cửa hàng) có',
        r'(những|các) loại (thuốc|dược phẩm)'
    ]
    
    for pattern in reference_patterns:
        if re.search(pattern, message.lower()):
            return True
            
    # Additional check: if asking about "inventory" and there are medications mentioned previously
    general_inventory_patterns = [
        r'(nhà thuốc|pharmacy|cửa hàng|bán|mua|tồn kho)',
    ]
    
    # If medications were mentioned AND the query is general about pharmacy/inventory
    if len(context_medications) > 1:  # Multiple medications discussed previously
        for pattern in general_inventory_patterns:
            if re.search(pattern, message.lower()):
                # More likely to be a followup if multiple medications were previously discussed
                return True
    
    return False

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

def get_medication_inventory_info(medication_names):
    """
    Get inventory information for medications
    Returns a formatted string with inventory information
    """
    if not medication_names:
        return "Không tìm thấy thông tin về thuốc trong kho."
    
    inventory_info = []
    seen_medicines = set()  # Track medicines we've already processed
    
    # Limit to top 5 medication names to avoid overwhelming responses
    for med_name in medication_names[:5]:
        try:
            # Skip very generic terms
            if med_name.lower() in ['thuốc', 'loại thuốc', 'đơn vị', 'giá', 'kho', 'tôi', 'bạn', 'nhà thuốc']:
                continue
                
            # Check if we've already seen this medication (case-insensitive)
            if med_name.lower() in seen_medicines:
                continue
            
            # Add to seen set
            seen_medicines.add(med_name.lower())
            
            # Query the pharmacy inventory for this medication
            results = AdvancedChatbotDataAccess.search_medication_in_inventory(med_name)
            
            if results and len(results) > 0:
                # Limit to top 3 results per medication to avoid overwhelming response
                for item in results[:3]:
                    info = f"• {item['name']}: "
                    if 'quantity' in item:
                        if item['quantity'] > 0:
                            info += f"Còn {item['quantity']} {item.get('unit', 'đơn vị')} trong kho. "
                        else:
                            info += "Hết hàng. "
                    if 'price' in item:
                        info += f"Giá: {item['price']} VNĐ. "
                    if 'expiry' in item:
                        info += f"Hạn sử dụng: {item['expiry']}."
                    inventory_info.append(info)
            else:
                # If nothing was found by exact name, try a more flexible search
                fuzzy_results = AdvancedChatbotDataAccess.fuzzy_search_medication(med_name)
                if fuzzy_results and len(fuzzy_results) > 0:
                    # Limit to top 3 fuzzy results per medication
                    for item in fuzzy_results[:3]:
                        if item['name'].lower() in seen_medicines:
                            continue
                        seen_medicines.add(item['name'].lower())
                        
                        info = f"• {item['name']}: "
                        if 'quantity' in item:
                            if item['quantity'] > 0:
                                info += f"Còn {item['quantity']} {item.get('unit', 'đơn vị')} trong kho. "
                            else:
                                info += "Hết hàng. "
                        if 'price' in item:
                            info += f"Giá: {item['price']} VNĐ. "
                        if 'expiry' in item:
                            info += f"Hạn sử dụng: {item['expiry']}."
                        inventory_info.append(info)
                else:
                    inventory_info.append(f"• {med_name}: Không tìm thấy trong kho.")
        except Exception as e:
            print(f"Error searching inventory for {med_name}: {str(e)}")
            inventory_info.append(f"• {med_name}: Không thể kiểm tra kho hàng.")
    
    if not inventory_info:
        return "Không tìm thấy thông tin về thuốc trong kho."
    
    # Limit to at most 10 items in the final response
    if len(inventory_info) > 10:
        inventory_info = inventory_info[:10]
        inventory_info.append("• ... và các loại thuốc khác.")
    
    return "Thông tin thuốc trong kho:\n\n" + "\n".join(inventory_info)

@csrf_exempt
@login_required
def direct_bot_send_message(request):
    """
    Enhanced API endpoint for sending messages to the chatbot with flexible medication query handling
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
            # Initialize medication context if it's been reset
            if not chat_memory.conversation_context.get('medication_context'):
                chat_memory.conversation_context['medication_context'] = {
                    'last_mentioned_medications': [],
                    'last_symptom': None
                }
                chat_memory.save()
        
        # Initialize medication context if it doesn't exist yet
        if not chat_memory.conversation_context.get('medication_context'):
            chat_memory.conversation_context['medication_context'] = {
                'last_mentioned_medications': [],
                'last_symptom': None
            }
            chat_memory.save()
        
        # Extract current medication context
        medication_context = chat_memory.conversation_context.get('medication_context', {})
        last_mentioned_medications = medication_context.get('last_mentioned_medications', [])
        last_symptom = medication_context.get('last_symptom')
        
        # Save user message
        user_msg = BotMessage.objects.create(
            user=request.user,
            type='user',
            content=user_message
        )
        
        # Add to memory context
        chat_memory.add_message('user', user_message)
        
        # Check if this is a follow-up inventory query about previously mentioned medications
        is_inventory_followup = check_if_inventory_query_about_medicine(user_message, last_mentioned_medications)
        
        if is_inventory_followup:
            # Process as inventory query but use the context medications
            inventory_response = get_medication_inventory_info(last_mentioned_medications)
            
            # Save bot response
            bot_msg = BotMessage.objects.create(
                user=request.user,
                type='bot',
                content=inventory_response
            )
            # Add to memory
            chat_memory.add_message('bot', inventory_response)
            return JsonResponse({
                'message': inventory_response,
                'type': 'bot',
                'query_type': 'inventory'
            })
        
        # Check if this is a medication recommendation query
        if check_if_medication_recommendation_query(user_message):
            medication_response = process_medication_recommendation_query(user_message)
            
            if medication_response:
                # Extract medication names from the response for future context
                extracted_medications = extract_medication_names_from_response(medication_response)
                symptom = extract_symptom_from_medication_query(user_message)
                
                # Update the medication context
                chat_memory.conversation_context['medication_context'] = {
                    'last_mentioned_medications': extracted_medications,
                    'last_symptom': symptom
                }
                chat_memory.save()
                
                # Save bot response
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=medication_response
                )
                # Add to memory
                chat_memory.add_message('bot', medication_response)
                return JsonResponse({
                    'message': medication_response,
                    'type': 'bot',
                    'query_type': 'medication'
                })
        
        # Check if this is a regular inventory query (but not a medication recommendation)
        inventory_keywords = ['kho', 'tồn kho', 'inventory', 'còn hàng', 'hết hàng']
        if (any(keyword in user_message.lower() for keyword in inventory_keywords) or
            ('thuốc' in user_message.lower() and not check_if_medication_recommendation_query(user_message))):
            # Extract medication name from the query if possible
            med_search_terms = [term for term in user_message.lower().split() 
                              if term not in inventory_keywords and len(term) > 3]
            
            # If we have a specific medication name, use it; otherwise use the general inventory query
            inventory_response = AdvancedChatbotDataAccess.process_inventory_query(user_message)
            if inventory_response:
                # Save bot response
                bot_msg = BotMessage.objects.create(
                    user=request.user,
                    type='bot',
                    content=inventory_response
                )
                # Add to memory
                chat_memory.add_message('bot', inventory_response)
                return JsonResponse({
                    'message': inventory_response,
                    'type': 'bot',
                    'query_type': 'inventory'
                })
        
        # Check if this is a prevention query (always use AI for these)
        if check_if_prevention_query(user_message):
            # Skip database lookup and go straight to AI
            pass
        else:
            # Check for symptom diagnosis query first (multiple symptoms)
            symptom_list = extract_symptom_list(user_message)
            if len(symptom_list) >= 2:
                diagnosis_response = AdvancedChatbotDataAccess.process_advanced_diagnosis(symptom_list)
                if diagnosis_response and "Không tìm thấy bệnh" not in diagnosis_response:
                    # Save bot response
                    bot_msg = BotMessage.objects.create(
                        user=request.user,
                        type='bot',
                        content=diagnosis_response
                    )
                    # Add to memory
                    chat_memory.add_message('bot', diagnosis_response)
                    return JsonResponse({
                        'message': diagnosis_response,
                        'type': 'bot',
                        'query_type': 'diagnosis'
                    })
        
        # Check for medical knowledge queries (symptoms, diseases)
        if check_if_medical_query(user_message):
            # Extract search terms
            search_term = extract_search_term(user_message)
            if search_term:
                database_response = process_medical_query(user_message)
                if database_response and "Không tìm thấy thông tin liên quan" not in database_response:
                    # Save bot response
                    bot_msg = BotMessage.objects.create(
                        user=request.user,
                        type='bot',
                        content=database_response
                    )
                    # Add to memory
                    chat_memory.add_message('bot', database_response)
                    return JsonResponse({
                        'message': database_response,
                        'type': 'bot',
                        'query_type': 'medical'
                    })
        
        # If we've got here, we couldn't handle the query with database knowledge
        # Try using Gemini API for general knowledge response
        if GEMINI_API_KEY:
            # Get conversation context for AI prompt
            conversation_context = chat_memory.get_context_for_prompt()
            
            # Prepare context for the AI
            system_info = """
            Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
            Hãy trả lời câu hỏi y tế dựa trên kiến thức chuyên môn của bạn.
            Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
            Nếu không chắc chắn về thông tin, hãy cho biết giới hạn của mình và đề xuất người dùng 
            tham khảo ý kiến bác sĩ hoặc chuyên gia y tế.
            
            Chú ý: KHÔNG sử dụng ký tự * trong câu trả lời của bạn. Thay vì dùng dấu * để đánh dấu điểm, hãy dùng dấu • hoặc -.
            """
            
            # Prepare prompt for Gemini AI
            prompt = f"{system_info}\n\n{conversation_context}\n\nCâu hỏi: {user_message}"
            
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
                        ai_response = clean_markdown(ai_response)
                        
                        # Save bot response
                        bot_msg = BotMessage.objects.create(
                            user=request.user,
                            type='bot',
                            content=ai_response
                        )
                        
                        # Add to memory context
                        chat_memory.add_message('bot', ai_response)
                        
                        # Determine the query type based on the message content
                        query_type = 'ai'
                        
                        # If this is a prevention query, always use 'ai' type
                        if check_if_prevention_query(user_message):
                            query_type = 'ai'
                        # If the message is about symptoms diagnosis but we're using AI
                        elif len(symptom_list) >= 2:
                            query_type = 'diagnosis'
                        # If the message is about medical knowledge but we're using AI
                        elif check_if_medical_query(user_message):
                            query_type = 'medical'
                        
                        # Check if there are medications mentioned in the AI response and save them
                        extracted_medications = extract_medication_names_from_response(ai_response)
                        if extracted_medications:
                            chat_memory.conversation_context['medication_context']['last_mentioned_medications'] = extracted_medications
                            chat_memory.save()
                        
                        return JsonResponse({
                            'message': ai_response,
                            'type': 'bot',
                            'query_type': query_type
                        })
                else:
                    print(f"Gemini API error: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error calling Gemini API: {str(e)}")
        
        # If all else fails or API error occurred, return a generic response
        generic_response = "Tôi không tìm thấy thông tin liên quan đến yêu cầu của bạn. Vui lòng hỏi rõ hơn hoặc liên hệ với nhân viên y tế để được hỗ trợ trực tiếp."
        
        # Save bot response
        bot_msg = BotMessage.objects.create(
            user=request.user,
            type='bot',
            content=generic_response
        )
        
        # Add to memory context
        chat_memory.add_message('bot', generic_response)
        
        return JsonResponse({
            'message': generic_response,
            'type': 'bot',
            'query_type': 'generic'
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 