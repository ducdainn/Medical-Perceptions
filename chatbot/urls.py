from django.urls import path, re_path
from . import views
from . import inventory_views
from .botmessage_handler import enhanced_bot_send_message

app_name = 'chatbot'

urlpatterns = [
    # User-facing URLs
    path('', views.chat_view, name='chat'),
    path('bot/', views.bot_chat_view, name='bot_chat'),
    path('history/', views.chat_history, name='chat_history'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/bot-send-message/', enhanced_bot_send_message, name='bot_send_message'),
    path('api/reset-chat-context/', views.reset_chat_context, name='reset_chat_context'),
    path('api/end-session/<int:session_id>/', views.end_session, name='end_session'),
    path('websocket-test/', views.websocket_test, name='websocket_test'),
    
    # Admin/Staff management URLs
    path('admin/chats/', views.admin_chat_list, name='admin_chat_list'),
    path('admin/chats/closed/', views.admin_closed_sessions, name='admin_closed_sessions'),
    path('admin/chats/session/<int:session_id>/', views.admin_session_detail, name='admin_session_detail'),
    path('admin/api/send-message/', views.admin_send_message, name='admin_send_message'),
    path('admin/api/end-session/<int:session_id>/', views.admin_end_session, name='admin_end_session'),
    
    # Test endpoints for development
    path('api/test/inventory/', inventory_views.test_inventory_access, name='test_inventory_access'),
    
    # WebSocket endpoint fallback (for HTTP requests)
    re_path(r'^ws/chat/$', views.websocket_http_fallback, name='ws_chat_http'),
    re_path(r'ws/chat/$', views.websocket_http_fallback, name='ws_chat_http_alt'),
]
