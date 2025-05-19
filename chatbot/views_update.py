from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatSession, Message, BotMessage, ChatMemory
from django.utils import timezone
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Max, Q
from .utils import ChatbotDataAccess
import re

import json
import requests
import os

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBM_DZ2uSW-SYBzJlIoOOmMpNtRfrFzk7c")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Check if user is a web manager or admin
def is_manager(user):
    return user.is_web_manager or user.is_staff

# Check if user is a doctor
def is_doctor(user):
    return user.is_doctor

@login_required
def chat_view(request):
    # Get or create an active session for the user
    active_session = ChatSession.objects.filter(
        user=request.user, 
        status='active'
    ).first()
    
    if not active_session:
        active_session = ChatSession.objects.create(
            user=request.user,
            status='active'
        )
    
    # Get previous messages for the active session
    messages = Message.objects.filter(session=active_session)
    
    # WebSocket configuration
    websocket_protocol = 'wss://' if request.is_secure() else 'ws://'
    websocket_host = request.get_host()
    
    context = {
        'title': 'Tin nhắn ReViCARE',
        'session': active_session,
        'messages': messages,
        'websocket_url': f"{websocket_protocol}{websocket_host}/ws/chat/",
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
    }
    
    return render(request, 'chatbot/chat.html', context)

@login_required
def bot_chat_view(request):
    """
    View for the chatbot interface using Gemini AI
    """
    # Get previous bot messages for the user
    bot_messages = BotMessage.objects.filter(user=request.user).order_by('sent_at')
    
    # Get or create the user's memory object
    chat_memory, created = ChatMemory.objects.get_or_create(user=request.user)
    
    # Get the current context length
    context_length = 0
    if chat_memory.conversation_context.get('messages'):
        context_length = len(chat_memory.conversation_context.get('messages', []))
    
    context = {
        'title': 'Bot trò chuyện ReViCARE',
        'bot_messages': bot_messages,
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
        'chat_memory': chat_memory,
        'context_length': context_length,
        'max_context_length': chat_memory.max_context_length,
    }
    
    return render(request, 'chatbot/bot_chat.html', context)

@login_required
def reset_chat_context(request):
    """
    Reset the conversation context for the current user
    """
    try:
        chat_memory, created = ChatMemory.objects.get_or_create(user=request.user)
        chat_memory.clear_context()
        return JsonResponse({'success': True, 'message': 'Đã xóa ngữ cảnh trò chuyện'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def chat_history(request):
    # Get all chat sessions for the user
    if is_manager(request.user) or is_doctor(request.user):
        # Managers and doctors can see all sessions
        if is_manager(request.user):
            sessions = ChatSession.objects.all().order_by('-started_at')
        else:  # is_doctor
            # Doctors can only see sessions from patients
            User = get_user_model()
            patient_ids = User.objects.filter(user_type='patient').values_list('id', flat=True)
            sessions = ChatSession.objects.filter(user_id__in=patient_ids).order_by('-started_at')
    else:
        # Regular users can only see their own sessions
        sessions = ChatSession.objects.filter(user=request.user).order_by('-started_at')
    
    context = {
        'title': 'Lịch sử tin nhắn',
        'sessions': sessions,
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
    }
    
    return render(request, 'chatbot/chat_history.html', context)

@login_required
def session_detail(request, session_id):
    # Get the chat session and its messages
    if is_manager(request.user) or is_doctor(request.user):
        # Managers and doctors can view any session
        session = get_object_or_404(ChatSession, id=session_id)
    else:
        # Regular users can only view their own sessions
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    messages = Message.objects.filter(session=session)
    
    context = {
        'title': f'Chi tiết phiên tin nhắn #{session.id}',
        'session': session,
        'messages': messages,
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
    }
    
    return render(request, 'chatbot/session_detail.html', context)

@csrf_exempt
@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get the chat session
        session = ChatSession.objects.get(id=session_id, user=request.user)
        
        # Save user message
        Message.objects.create(
            session=session,
            type='user',
            content=user_message
        )
        
        # Count existing messages to determine if this is the first message
        message_count = Message.objects.filter(session=session).count()
        
        # If this is the first or second message (considering we just added one), send an automated response
        if message_count <= 2:
            response_message = "Tin nhắn của bạn đã được ghi nhận. Nhân viên quản lý sẽ phản hồi trong thời gian sớm nhất. Cảm ơn bạn đã sử dụng dịch vụ tin nhắn của ReViCARE."
            
            # Save response message
            bot_message = Message.objects.create(
                session=session,
                type='bot',
                content=response_message
            )
            
            return JsonResponse({
                'message': response_message,
                'type': 'bot'
            })
        else:
            # For subsequent messages, just acknowledge receipt
            return JsonResponse({
                'message': 'Đã gửi tin nhắn',
                'type': 'success'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def end_session(request, session_id):
    try:
        if is_manager(request.user):
            # Managers can end any session
            session = get_object_or_404(ChatSession, id=session_id)
        else:
            # Regular users can only end their own sessions
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        
        session.status = 'closed'
        session.ended_at = timezone.now()
        session.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def websocket_test(request):
    """
    View for testing WebSocket connections
    """
    return render(request, 'chatbot/websocket_test.html', {
        'title': 'WebSocket Test'
    })

def websocket_view(request):
    """
    Handle direct HTTP requests to the WebSocket URL.
    This will redirect users to the chat page.
    """
    return HttpResponse(
        "WebSocket endpoint. This URL is meant for WebSocket connections, not HTTP requests. "
        "Please go to <a href='/chatbot/'>the chat page</a> to use the chatbot.",
        content_type="text/html"
    )

# Alias for compatibility with urls.py
websocket_http_fallback = websocket_view

# Views for web manager functionality
@login_required
@user_passes_test(is_manager)
def admin_chat_list(request):
    """
    Admin view to list all active chat sessions
    """
    # Get sessions with counts of unread messages
    active_sessions = ChatSession.objects.filter(status='active').order_by('-started_at')
    
    # Annotate with latest message time and count
    sessions_with_data = active_sessions.annotate(
        last_message_time=Max('messages__sent_at'),
        message_count=Count('messages')
    )
    
    # Filter to only include sessions with at least one message
    sessions_with_messages = sessions_with_data.filter(message_count__gt=0)
    
    context = {
        'title': 'Quản lý Tin nhắn',
        'sessions': sessions_with_messages,
    }
    
    return render(request, 'chatbot/admin_chat_list.html', context)

@login_required
@user_passes_test(lambda u: is_manager(u) or is_doctor(u))
def admin_session_detail(request, session_id):
    """
    Admin/Doctor view to see the details of a chat session
    """
    # Get the session regardless of the user (admin/doctor can see all sessions)
    session = get_object_or_404(ChatSession, id=session_id)
    messages = Message.objects.filter(session=session).order_by('sent_at')
    
    context = {
        'title': f'Phản hồi phiên tin nhắn #{session.id}',
        'session': session,
        'messages': messages,
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
    }
    
    return render(request, 'chatbot/admin_session_detail.html', context)

@csrf_exempt
@login_required
@user_passes_test(lambda u: is_manager(u) or is_doctor(u))
def admin_send_message(request):
    """
    API endpoint for admin/doctor to send messages in a chat session
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        admin_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not admin_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get the chat session (admin/doctor can access any session)
        session = ChatSession.objects.get(id=session_id)
        
        # Save admin/doctor message as "bot" type
        Message.objects.create(
            session=session,
            type='bot',
            content=admin_message
        )
        
        return JsonResponse({
            'success': True,
            'message': admin_message,
            'type': 'bot',
            'timestamp': timezone.now().strftime('%H:%M:%S')
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: is_manager(u) or is_doctor(u))
def admin_end_session(request, session_id):
    """
    API endpoint for admin/doctor to end a chat session
    """
    try:
        session = ChatSession.objects.get(id=session_id)
        session.status = 'closed'
        session.ended_at = timezone.now()
        session.save()
        
        # Add a system message indicating the session was closed by staff
        closer_type = "bác sĩ" if is_doctor(request.user) else "nhân viên quản lý"
        Message.objects.create(
            session=session,
            type='bot',
            content=f"Phiên tin nhắn đã được kết thúc bởi {closer_type}."
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_manager)
def admin_closed_sessions(request):
    """
    Admin view to list all closed chat sessions
    """
    # Get closed sessions
    closed_sessions = ChatSession.objects.filter(status='closed').order_by('-ended_at')
    
    context = {
        'title': 'Phiên tin nhắn đã kết thúc',
        'sessions': closed_sessions,
    }
    
    return render(request, 'chatbot/admin_closed_sessions.html', context)

@csrf_exempt
@login_required
def bot_send_message(request):
    """
    Handle sending messages to the AI chatbot and receiving responses
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        reset_context = data.get('reset_context', False)
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create the user's memory object
        chat_memory, created = ChatMemory.objects.get_or_create(user=request.user)
        
        # Reset context if requested
        if reset_context:
            chat_memory.clear_context()
        
        # Save user message to bot messages
        user_bot_message = BotMessage.objects.create(
            user=request.user,
            type='user',
            content=user_message
        )
        
        # Add to memory
        chat_memory.add_message('user', user_message)
        
        # Check if the message is a query about medical data
        is_medical_query = check_if_medical_query(user_message)
        
        # Process the message differently based on its type
        if is_medical_query:
            # Handle medical data query
            database_response = process_medical_query(user_message)
            
            # Save bot response
            bot_bot_message = BotMessage.objects.create(
                user=request.user,
                type='bot',
                content=database_response
            )
            
            # Add to memory
            chat_memory.add_message('bot', database_response)
            
            return JsonResponse({
                'message': database_response,
                'type': 'bot'
            })
        else:
            # Get conversation context for AI prompt
            conversation_context = chat_memory.get_context_for_prompt()
            
            # Add system information about available data access
            system_info = """
            Bạn có thể tìm kiếm thông tin từ cơ sở dữ liệu của ReViCARE về:
            - Triệu chứng bệnh
            - Thông tin bệnh
            - Thuốc và thông tin về thuốc
            - Thông tin cơ bản về nhân viên y tế (chỉ tên và vai trò)
            
            Nếu người dùng hỏi về những thông tin trên, hãy cho họ biết rằng bạn có thể giúp tìm kiếm 
            thông tin cụ thể trong cơ sở dữ liệu bằng cách họ cung cấp từ khóa rõ ràng.
            """
            
            # Prepare prompt for Gemini AI
            prompt = f"{system_info}\n\n{conversation_context}\n\nVui lòng trả lời câu hỏi/yêu cầu sau đây của người dùng một cách chính xác và hữu ích:\n{user_message}"
            
            # Prepare the request data
            gemini_data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            # Call the Gemini API
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json=gemini_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Extract the text from the response
                try:
                    bot_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Save bot response
                    bot_bot_message = BotMessage.objects.create(
                        user=request.user,
                        type='bot',
                        content=bot_response
                    )
                    
                    # Add to memory
                    chat_memory.add_message('bot', bot_response)
                    
                    return JsonResponse({
                        'message': bot_response,
                        'type': 'bot'
                    })
                except (KeyError, IndexError) as e:
                    return JsonResponse({'error': f'Error parsing Gemini response: {str(e)}'}, status=500)
            else:
                return JsonResponse({'error': f'Gemini API error: {response.text}'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def check_if_medical_query(message):
    """
    Check if a message is querying for medical data.
    
    Args:
        message (str): The user's message
        
    Returns:
        bool: True if the message is a medical query, False otherwise
    """
    # Keywords for medical queries
    medical_keywords = [
        'triệu chứng', 'symptom', 
        'bệnh', 'disease', 
        'thuốc', 'medicine', 'drug',
        'điều trị', 'treatment',
        'bác sĩ', 'doctor',
        'dược sĩ', 'pharmacist',
        'tác dụng phụ', 'side effect',
        'liều lượng', 'dosage',
        'thành phần', 'composition'
    ]
    
    # Question indicators
    question_indicators = ['?', 'là gì', 'như thế nào', 'thế nào', 'ra sao', 'làm sao', 'cách', 'chữa', 'hỏi', 'tư vấn', 'tìm']
    
    # Check if the message contains both medical keywords and question indicators
    has_medical_keyword = any(keyword in message.lower() for keyword in medical_keywords)
    has_question_indicator = any(indicator in message.lower() for indicator in question_indicators)
    
    # Direct commands to search for information
    direct_commands = ['tìm kiếm', 'tìm thông tin về', 'tra cứu', 'search', 'lookup', 'find']
    has_direct_command = any(command in message.lower() for command in direct_commands)
    
    return (has_medical_keyword and has_question_indicator) or has_direct_command

def process_medical_query(message):
    """
    Process a medical query and return relevant information.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: Response with relevant medical information
    """
    # Extract main search term
    search_term = extract_search_term(message)
    
    if not search_term:
        return "Tôi hiểu bạn đang tìm thông tin y tế, nhưng tôi cần từ khóa cụ thể để tìm kiếm. Vui lòng cung cấp tên bệnh, triệu chứng, hoặc thuốc mà bạn quan tâm."
    
    # Search the knowledge base
    results = ChatbotDataAccess.search_knowledge_base(search_term)
    
    # Check for symptom lists for potential diagnosis
    symptom_list = extract_symptom_list(message)
    
    if symptom_list and len(symptom_list) >= 2:
        # User might be listing symptoms for diagnosis
        disease_results = ChatbotDataAccess.get_related_diseases_for_symptoms(symptom_list)
        
        if disease_results:
            # Sort by number of matching symptoms
            disease_results.sort(key=lambda x: x['matching_count'], reverse=True)
            
            response = "Dựa trên các triệu chứng bạn mô tả, đây là một số bệnh có thể liên quan:\n\n"
            
            for idx, disease in enumerate(disease_results[:3], 1):
                matching_ratio = disease['matching_count'] / disease['total_symptoms']
                confidence = "cao" if matching_ratio > 0.7 else "trung bình" if matching_ratio > 0.4 else "thấp"
                
                response += f"{idx}. {disease['name']} (Độ phù hợp: {confidence})\n"
                response += f"   Mô tả: {disease['description'][:150]}...\n"
                response += f"   Triệu chứng khớp: {', '.join(disease['matching_symptoms'])}\n\n"
            
            response += "Lưu ý: Đây chỉ là thông tin tham khảo. Vui lòng tham khảo ý kiến bác sĩ để được chẩn đoán chính xác."
            return response
    
    # Check for disease-specific drug recommendations
    disease_match = re.search(r"thuốc.*(cho|trị|điều trị|chữa).*?([a-zA-ZÀ-ỹ\s]+)(?:\?|$)", message, re.IGNORECASE)
    
    if disease_match:
        disease_name = disease_match.group(2).strip()
        drug_recommendations = ChatbotDataAccess.get_recommended_drugs_for_disease(disease_name)
        
        if drug_recommendations:
            response = f"Các thuốc thường dùng để điều trị {disease_name}:\n\n"
            
            for idx, drug in enumerate(drug_recommendations[:5], 1):
                response += f"{idx}. {drug['name']}\n"
                response += f"   Mô tả: {drug['description'][:100]}...\n"
                response += f"   Liều dùng: {drug['dosage'][:100]}...\n\n"
            
            response += "Lưu ý: Vui lòng tham khảo ý kiến bác sĩ hoặc dược sĩ trước khi sử dụng bất kỳ loại thuốc nào."
            return response
    
    # Format and return general search results
    return ChatbotDataAccess.format_search_results(results)

def extract_search_term(message):
    """
    Extract the main search term from a message.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: The main search term
    """
    # Patterns to extract search terms
    patterns = [
        r"tìm (?:kiếm|thông tin về) (.*?)(?:\?|$)",  # "tìm kiếm X" or "tìm thông tin về X"
        r"(?:thông tin|tư vấn) về (.*?)(?:\?|$)",    # "thông tin về X" or "tư vấn về X"
        r"(?:bệnh|thuốc|triệu chứng|tác dụng) (?:của |là |gì |như thế nào |)?(.*?)(?:\?|$)",  # Various medical terms
        r"(.*?) là (?:bệnh|thuốc|triệu chứng) gì",   # "X là bệnh gì"
        r"(?:chữa|điều trị) (.*?)(?:\?|$)",          # "chữa X" or "điều trị X"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # If no pattern matches, use the whole message but limit to first N words
    words = message.split()
    if len(words) > 5:
        return ' '.join(words[:5])
    
    return message

def extract_symptom_list(message):
    """
    Extract a list of symptoms from a message.
    
    Args:
        message (str): The user's message
        
    Returns:
        list: List of potential symptom names
    """
    # Check for listing patterns
    list_patterns = [
        r"(?:có|bị) các? triệu chứng (?:như|gồm|bao gồm|là)? (.*?)(?:\.|$)",
        r"(?:có|bị) (.*?)(?:\.|$)",
        r"(?:triệu chứng|symptoms)(?:: | là | như | bao gồm | gồm )(.*?)(?:\.|$)",
    ]
    
    for pattern in list_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            symptom_text = match.group(1)
            
            # Split by common separators
            separators = [',', ';', 'và', 'and', '\n', '\t', '•', '-']
            for sep in separators:
                if sep in symptom_text:
                    return [s.strip() for s in symptom_text.split(sep) if s.strip()]
            
            # If no separators found, check for multiple words
            words = symptom_text.split()
            if len(words) > 2:  # If more than 2 words, it might be multiple symptoms
                return [symptom_text]
    
    return [] 