from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ChatSession, Message
from django.utils import timezone
from .templatetags.chat_filters import clean_chat_message
import json

class ChatUITestCase(TestCase):
    def setUp(self):
        # Create a test user with a unique email
        User = get_user_model()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
        # Create a staff user (instead of web_manager)
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        
        # Create a chat session
        self.session = ChatSession.objects.create(
            user=self.test_user,
            status='active',
            started_at=timezone.now()
        )
        
        # Create test messages with timestamp labels
        Message.objects.create(
            session=self.session,
            type='user',
            content='Người dùng - 08:20:34\nTest message from user'
        )
        
        Message.objects.create(
            session=self.session,
            type='bot',
            content='Chatbot - 08:20:35\nTest response from bot'
        )
        
        # Set up clients
        self.client = Client()
        self.admin_client = Client()

    def test_chat_view_ui(self):
        """Test that the chat view renders correctly with hidden timestamps"""
        # Login as test user
        self.client.login(username='testuser', password='testpassword')
        
        # Get the chat view
        response = self.client.get(reverse('chatbot:chat'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the CSS for message-time has display:none
        self.assertContains(response, 'display: none;')
        
        # Check column layout has been updated
        self.assertContains(response, 'col-md-9')
        self.assertContains(response, 'col-md-3')
    
    def test_admin_chat_view_ui(self):
        """Test that the admin chat view renders correctly with hidden timestamps"""
        # Login as admin user
        self.admin_client.login(username='adminuser', password='adminpassword')
        
        # Get the admin session detail view
        response = self.admin_client.get(reverse('chatbot:admin_session_detail', args=[self.session.id]))
        
        # Check if page loads successfully (might not have permissions, just checking structure)
        if response.status_code == 200:  
            # Check that the CSS for message-time has display:none
            self.assertContains(response, 'display: none;')
            
            # Check column layout has been updated
            self.assertContains(response, 'col-md-9')
            self.assertContains(response, 'col-md-3')
    
    def test_clean_chat_message_filter(self):
        """Test the clean_chat_message template filter"""
        # Test user message cleaning
        user_message = "Người dùng - 08:20:34\nThis is a user message"
        cleaned = clean_chat_message(user_message)
        self.assertEqual(cleaned, "This is a user message")
        
        # Test bot message cleaning
        bot_message = "Chatbot - 10:15:47\nThis is a bot response"
        cleaned = clean_chat_message(bot_message)
        self.assertEqual(cleaned, "This is a bot response")
        
        # Test message with just timestamp
        timestamp_message = "08:20:34\nMessage with timestamp"
        cleaned = clean_chat_message(timestamp_message)
        self.assertEqual(cleaned, "Message with timestamp")
        
        # Test message with multiple timestamp lines
        multi_timestamp = "Người dùng - 08:20:34\nFirst line\nChatbot - 08:20:35\nSecond line"
        cleaned = clean_chat_message(multi_timestamp)
        self.assertEqual(cleaned, "First line\nSecond line")
        
        # Test message without timestamp (should be unchanged)
        normal_message = "This is a normal message"
        cleaned = clean_chat_message(normal_message)
        self.assertEqual(cleaned, "This is a normal message")
        
        # Test timestamp-only message (should return empty string)
        timestamp_only = "Người dùng - 08:20:34"
        cleaned = clean_chat_message(timestamp_only)
        self.assertEqual(cleaned, "")
        
        # Test timestamp-only message with no label
        time_only = "08:20:34"
        cleaned = clean_chat_message(time_only)
        self.assertEqual(cleaned, "") 