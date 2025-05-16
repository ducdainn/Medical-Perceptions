from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatSession, Message, BotMessage
from django.utils import timezone
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Max, Q

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
    
    context = {
        'title': 'Bot trò chuyện ReViCARE',
        'bot_messages': bot_messages,
        'is_manager': is_manager(request.user),
        'is_doctor': is_doctor(request.user),
    }
    
    return render(request, 'chatbot/bot_chat.html', context)

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
    API endpoint for sending messages to the chatbot and getting AI-generated responses
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Save user message
        user_msg = BotMessage.objects.create(
            user=request.user,
            type='user',
            content=user_message
        )
        
        # Prepare prompt for Gemini AI
        prompt = f"""Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
        Hãy trả lời câu hỏi sau đây một cách chuyên nghiệp, ngắn gọn và hữu ích.
        Câu hỏi: {user_message}
        
        Lưu ý: Trả lời bằng tiếng Việt, và đảm bảo thông tin y tế chính xác. Nếu không chắc chắn về thông tin,
        hãy đề xuất người dùng tham khảo ý kiến bác sĩ hoặc chuyên gia y tế."""
        
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
        
        if response.status_code != 200:
            return JsonResponse({'error': f'Gemini API error: {response.text}'}, status=500)
        
        response_data = response.json()
        bot_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not bot_response:
            bot_response = "Xin lỗi, tôi không thể xử lý yêu cầu của bạn bây giờ. Vui lòng thử lại sau."
        
        # Save bot response
        bot_msg = BotMessage.objects.create(
            user=request.user,
            type='bot',
            content=bot_response
        )
        
        return JsonResponse({
            'message': bot_response,
            'type': 'bot'
        })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 