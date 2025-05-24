import json
import requests
import asyncio
import aiohttp
import random
import re
import os
import logging
from dotenv import load_dotenv
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db.models import Q
from .models import ChatSession, Message, Intent, Response
from diagnosis.models import Symptom, Disease, Diagnosis
from pharmacy.models import Medicine, Drug, Inventory
from .advanced_data_access import AdvancedChatbotDataAccess
from .utils import ChatbotDataAccess

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCEua2hrKMgAe_8qcawIXwVGNA7dV39BdA")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established
        """
        print(f"WebSocket connection attempt from: {self.scope['client']}")
        
        try:
            # Accept the connection
            await self.accept()
            print(f"WebSocket connection accepted from: {self.scope['client']}")
            
            # Send a welcome message
            await self.send(text_data=json.dumps({
                'message': 'Chào mừng bạn đến với hệ thống tin nhắn ReViCARE! Kết nối WebSocket đã thành công.',
                'type': 'bot'
            }))
        except Exception as e:
            print(f"Error during WebSocket connection: {str(e)}")
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
        print(f"Received message from client {self.scope['client']}")
        
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
            
            # Save user message to database if session_id exists
            if session_id:
                try:
                    await self.save_message_to_db(session_id, 'user', message)
                except Exception as e:
                    print(f"Error saving user message to database: {str(e)}")
            
            # Process the message and determine the appropriate response method
            query_type, response_message = await self.determine_query_type_and_respond(message)
            
            # Save bot response to database if session exists
            if session_id:
                try:
                    await self.save_message_to_db(session_id, 'bot', response_message)
                except Exception as e:
                    print(f"Error saving bot response to database: {str(e)}")
                    
            # Send response to client
            await self.send(text_data=json.dumps({
                'message': response_message,
                'type': 'bot',
                'status': 'success',
                'query_type': query_type
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
    def determine_query_type_and_respond(self, message):
        """
        Determine the type of query and provide the appropriate response
        Returns a tuple of (query_type, response_message)
        """
        # Check for inventory related queries first
        if self.check_if_inventory_query_sync(message):
            return "inventory", AdvancedChatbotDataAccess.process_inventory_query(message)
            
        # Check for medical knowledge queries (symptoms, diseases)
        if self.check_if_medical_knowledge_query(message):
            medical_response = self.process_medical_knowledge_query(message)
            if medical_response and medical_response != "Không tìm thấy thông tin liên quan":
                return "medical", medical_response
                
        # Check for symptom diagnosis query
        symptom_list = AdvancedChatbotDataAccess.extract_symptom_list(message)
        if len(symptom_list) >= 2:
            diagnosis_response = AdvancedChatbotDataAccess.process_advanced_diagnosis(symptom_list)
            if diagnosis_response and "Không tìm thấy bệnh" not in diagnosis_response:
                return "diagnosis", diagnosis_response
        
        # If we've got here, we couldn't handle the query with database knowledge
        # Try using Gemini API for general knowledge response
        if GEMINI_API_KEY:
            # Prepare context for the AI
            system_info = """
            Bạn là trợ lý chăm sóc sức khỏe tự động của ReViCARE - một hệ thống quản lý phòng khám.
            Hãy trả lời câu hỏi y tế dựa trên kiến thức chuyên môn của bạn.
            Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
            Nếu không chắc chắn về thông tin, hãy cho biết giới hạn của mình và đề xuất người dùng 
            tham khảo ý kiến bác sĩ hoặc chuyên gia y tế.
            
            Chú ý: KHÔNG sử dụng ký tự * trong câu trả lời. Thay vì dùng dấu * để đánh dấu điểm, hãy dùng dấu • hoặc -.
            """
            
            try:
                # Call the Gemini API
                response = requests.post(
                    f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                    json={
                        "contents": [{"parts": [{"text": f"{system_info}\n\nCâu hỏi: {message}"}]}],
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
                        ai_response = self.clean_markdown(ai_response)
                        return "ai", ai_response
            except Exception as e:
                print(f"Error calling Gemini API: {str(e)}")
        
        # If all else fails, return a generic response
        return "generic", "Tôi không tìm thấy thông tin liên quan đến yêu cầu của bạn. Vui lòng hỏi rõ hơn hoặc liên hệ với nhân viên y tế để được hỗ trợ trực tiếp."
    
    def clean_markdown(self, text):
        """
        Clean markdown formatting from text
        """
        # Remove asterisks for bold/italic formatting
        text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
        # Replace "* " with bullet points
        text = re.sub(r'\*\s+', '• ', text)
        # Remove remaining asterisks
        text = re.sub(r'\*{2,}', '', text)
        return text
        
    def check_if_inventory_query_sync(self, message):
        """
        Synchronous version of check_if_inventory_query
        """
        inventory_keywords = [
            'thuốc', 'medicine', 'drug', 'kho', 'inventory', 
            'còn hàng', 'hết hàng', 'số lượng', 'đơn vị',
            'trạng thái', 'tồn kho', 'danh sách thuốc', 'danh mục thuốc',
            'tìm thuốc', 'kiểm tra thuốc', 'tra cứu thuốc'
        ]
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Check if any inventory keyword is in the message
        return any(keyword in message_lower for keyword in inventory_keywords)
    
    def check_if_medical_knowledge_query(self, message):
        """
        Check if the message is asking about medical knowledge
        """
        medical_keywords = [
            'triệu chứng', 'symptom', 
            'bệnh', 'disease', 
            'điều trị', 'treatment',
            'chữa', 'cure',
            'nguyên nhân', 'cause',
            'phòng ngừa', 'prevention'
        ]
        
        # Question indicators
        question_indicators = ['?', 'là gì', 'như thế nào', 'thế nào', 'ra sao', 'làm sao', 'cách', 'hỏi', 'tư vấn']
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Check for medical keywords and question indicators
        has_medical_keyword = any(keyword in message_lower for keyword in medical_keywords)
        has_question = any(indicator in message_lower for indicator in question_indicators)
        
        return has_medical_keyword and has_question
    
    def process_medical_knowledge_query(self, message):
        """
        Process a query about medical knowledge
        """
        try:
            # Extract search terms
            search_term = self.extract_search_term(message)
            
            if not search_term:
                return "Tôi hiểu bạn đang hỏi về thông tin y tế, nhưng tôi cần từ khóa cụ thể để tìm kiếm."
            
            # First, try to find symptoms matching the search term
            symptoms = ChatbotDataAccess.search_symptoms(search_term)
            
            if symptoms:
                response = f"Thông tin về triệu chứng '{search_term}':\n\n"
                for symptom in symptoms[:3]:  # Limit to top 3 results
                    response += f"• {symptom['name']}: {symptom['description'][:100]}...\n\n"
                return response
            
            # If no symptoms found, try diseases
            diseases = ChatbotDataAccess.search_diseases(search_term)
            
            if diseases:
                response = f"Thông tin về bệnh '{search_term}':\n\n"
                for disease in diseases[:3]:  # Limit to top 3 results
                    response += f"• {disease['name']} (Mức độ: {disease['severity']}):\n"
                    response += f"  {disease['description'][:150]}...\n\n"
                return response
                
            # If no diseases found, try medicines
            medicines = ChatbotDataAccess.search_medicines(search_term)
            
            if medicines:
                response = f"Thông tin về thuốc '{search_term}':\n\n"
                for medicine in medicines[:3]:  # Limit to top 3 results
                    response += f"• {medicine['name']}:\n"
                    response += f"  {medicine['description'][:150]}...\n"
                    
                    # Add inventory information if available
                    if medicine.get('inventory'):
                        inv = medicine['inventory']
                        status = "Còn hàng" if inv.get('in_stock', False) else "Hết hàng"
                        response += f"  Tình trạng: {status}\n"
                        if inv.get('quantity') is not None:
                            response += f"  Số lượng: {inv['quantity']} {inv.get('unit', 'đơn vị')}\n"
                    
                    response += "\n"
                return response
            
            # If no results in any category
            return "Không tìm thấy thông tin liên quan"
            
        except Exception as e:
            print(f"Error processing medical knowledge query: {str(e)}")
            return None
    
    def extract_search_term(self, message):
        """
        Extract the main search term from a medical query
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

    @database_sync_to_async
    def check_if_inventory_query(self, message):
        """
        Check if the message is querying inventory data
        """
        return self.check_if_inventory_query_sync(message)
        
    @database_sync_to_async
    def process_inventory_query(self, message):
        """
        Process a query about inventory data
        """
        try:
            # Use the advanced data access method to process inventory queries
            return AdvancedChatbotDataAccess.process_inventory_query(message)
        except Exception as e:
            return f"Xin lỗi, đã có lỗi khi truy vấn dữ liệu kho thuốc: {str(e)}"
    
    @database_sync_to_async
    def save_message_to_db(self, session_id, message_type, content):
        """
        Save a message to the database
        """
        try:
            session = ChatSession.objects.get(id=session_id)
            Message.objects.create(
                session=session,
                type=message_type,
                content=content
            )
            return True
        except Exception as e:
            print(f"Error saving message to DB: {str(e)}")
            raise e

    @database_sync_to_async
    def get_user_diagnoses(self, user):
        """
        Get recent diagnoses for a user
        """
        from diagnosis.models import Diagnosis
        return list(Diagnosis.objects.filter(user=user).order_by('-created_at')[:5]) 

