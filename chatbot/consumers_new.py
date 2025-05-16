import json
import requests
import asyncio
import aiohttp
import random
import re
import os
from dotenv import load_dotenv
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatSession, Message, Intent, Response
from diagnosis.models import Symptom, Disease, Diagnosis
from pharmacy.models import Medicine, Drug

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCEua2hrKMgAe_8qcawIXwVGNA7dV39BdA")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established
        """
        print(f"WebSocket connection attempt from: {self.scope['client']}")
        print(f"WebSocket scope: {self.scope}")
        
        try:
            # Accept the connection
            await self.accept()
            print(f"WebSocket connection accepted from: {self.scope['client']}")
            
            # Send a welcome message
            await self.send(text_data=json.dumps({
                'message': 'Chào mừng bạn đến với trợ lý y tế ảo ReViCARE! Kết nối WebSocket đã thành công. Bạn có thể bắt đầu trò chuyện.',
                'type': 'bot'
            }))
            print(f"Welcome message sent to: {self.scope['client']}")
        except Exception as e:
            print(f"Error during WebSocket connection: {str(e)}")
            print(f"Connection scope: {self.scope}")
            try:
                await self.send(text_data=json.dumps({
                    'message': f'Lỗi kết nối: {str(e)}',
                    'type': 'error'
                }))
            except Exception as inner_e:
                print(f"Error sending error message: {str(inner_e)}")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes
        """
        print(f"WebSocket connection closed with code: {close_code} from: {self.scope['client']}")

    async def receive(self, text_data):
        """
        Called when we receive a message from the client
        """
        print(f"Received raw message from client {self.scope['client']}: {text_data[:100]}...")
        
        try:
            # Parse the JSON message
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            session_id = text_data_json.get('session_id')
            use_gemini = text_data_json.get('use_gemini', False)
            
            if not message:
                await self.send(text_data=json.dumps({
                    'message': 'Tin nhắn trống, vui lòng gửi nội dung.',
                    'type': 'bot',
                    'status': 'error'
                }))
                return
            
            # Log the received message
            print(f"Processing message: {message}")
            
            # Send an acknowledgment
            await self.send(text_data=json.dumps({
                'message': f'Tin nhắn của bạn đã được ghi nhận. Nhân viên quản lý sẽ phản hồi trong thời gian sớm nhất.',
                'type': 'bot',
                'status': 'received'
            }))
            
            # Save user message to database if session_id exists
            if session_id:
                try:
                    await self.save_message_to_db(session_id, 'user', message)
                except Exception as e:
                    print(f"Error saving user message to database: {str(e)}")
                    
            # Instead of AI processing, we'll save a notification message for web managers to respond
            if session_id:
                try:
                    response_message = "Tin nhắn của bạn đã được ghi nhận. Nhân viên quản lý sẽ phản hồi trong thời gian sớm nhất. Cảm ơn bạn đã sử dụng dịch vụ tư vấn của ReViCARE."
                    await self.save_message_to_db(session_id, 'bot', response_message)
                    
                    # Send response to client
                    await self.send(text_data=json.dumps({
                        'message': response_message,
                        'type': 'bot',
                        'status': 'success'
                    }))
                except Exception as e:
                    error_message = f"Xin lỗi, đã xảy ra lỗi khi lưu tin nhắn: {str(e)}"
                    print(error_message)
                    await self.send(text_data=json.dumps({
                        'message': error_message,
                        'type': 'bot',
                        'status': 'error'
                    }))
            
        except Exception as e:
            error_message = f"Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn: {str(e)}"
            print(error_message)
            await self.send(text_data=json.dumps({
                'message': error_message,
                'type': 'bot',
                'status': 'error'
            }))
    
    @database_sync_to_async
    def get_user_diagnoses(self, user):
        """
        Get recent diagnoses for a user
        """
        from diagnosis.models import Diagnosis
        return list(Diagnosis.objects.filter(user=user).order_by('-created_at')[:5])

    # Add the rest of your methods here... 