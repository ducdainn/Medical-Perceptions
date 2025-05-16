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
                'message': f'Đang xử lý tin nhắn của bạn...',
                'type': 'bot',
                'status': 'received'
            }))
            
            # Save user message to database if session_id exists
            if session_id:
                try:
                    await self.save_message_to_db(session_id, 'user', message)
                except Exception as e:
                    print(f"Error saving user message to database: {str(e)}")
            
            # First try to extract symptoms from the message
            symptoms = await self.extract_symptoms_from_text(message)
            
            # Check if we found any symptoms and if use_gemini is not explicitly True
            if symptoms and not use_gemini:
                # Extract symptom names for display
                symptom_names = [symptom.name for symptom in symptoms]
                print(f"Extracted symptoms: {', '.join(symptom_names)}")
                
                # If we found symptoms, try to find matching diseases
                disease_matches = await self.find_diseases_by_symptoms(symptoms)
                
                if disease_matches:
                    # Get the best matching disease
                    best_match = disease_matches[0]
                    disease = best_match['disease']
                    confidence = best_match['confidence'] * 100  # Convert to percentage
                    
                    # Find medicine recommendations for this disease
                    medicine_recommendations = await self.recommend_medicines_for_disease(disease)
                    
                    # Format medicine recommendations with Markdown
                    medicine_text = ""
                    if medicine_recommendations:
                        medicine_text = "\n\n**Thuốc gợi ý:**\n"
                        for i, med in enumerate(medicine_recommendations[:3], 1):  # Limit to top 3
                            medicine_text += f"{i}. **{med['name']}**: {med['description'][:150]}...\n"
                            
                            # Add more detailed information if available
                            if med.get('type') == 'drug':
                                if 'composition' in med and med['composition']:
                                    medicine_text += f"   - Thành phần: {med['composition'][:100]}\n"
                                if 'usage' in med and med['usage']:
                                    medicine_text += f"   - Cách dùng: {med['usage'][:100]}\n"
                                if 'dosage' in med and med['dosage']:
                                    medicine_text += f"   - Liều dùng: {med['dosage'][:100]}\n"
                                if 'side_effects' in med and med['side_effects']:
                                    medicine_text += f"   - Tác dụng phụ: {med['side_effects'][:100]}\n"
                                if 'contraindications' in med and med['contraindications']:
                                    medicine_text += f"   - Chống chỉ định: {med['contraindications'][:100]}\n"
                            else:
                                # Các thông tin cơ bản cho Medicine
                                if 'price' in med and med['price']:
                                    medicine_text += f"   - Giá tham khảo: {med['price']:,} VND\n"
                            
                            medicine_text += "\n"
                    
                    # Format matching symptoms with Markdown
                    matching_symptoms_text = ""
                    if best_match['matching_symptoms']:
                        matching_symptoms_text = "\n\n**Triệu chứng phù hợp:**\n"
                        for symptom in best_match['matching_symptoms']:
                            matching_symptoms_text += f"- {symptom.name}\n"
                    
                    # Format missing symptoms with Markdown
                    missing_symptoms_text = ""
                    if 'missing_symptoms' in best_match and best_match['missing_symptoms']:
                        important_missing = list(best_match['missing_symptoms'])[:3]  # Limit to 3 important missing symptoms
                        if important_missing:
                            missing_symptoms_text = "\n\n**Triệu chứng cần xác nhận thêm:**\n"
                            for symptom in important_missing:
                                missing_symptoms_text += f"- {symptom.name}\n"
                            
                            # Add suggested questions
                            missing_symptoms_text += "\nBạn có thể chia sẻ thêm về các triệu chứng trên để tôi có thể đánh giá chính xác hơn."
                    
                    # Construct response with database information and Markdown formatting
                    database_response = (
                        f"# Kết quả phân tích triệu chứng\n\n"
                        f"Tôi đã nhận diện được các triệu chứng: **{', '.join(symptom_names)}**.\n\n"
                        f"## Chẩn đoán sơ bộ\n\n"
                        f"Dựa trên các triệu chứng của bạn, tôi nghĩ bạn có thể bị: **{disease.name}** "
                        f"(độ tin cậy: {confidence:.1f}%).\n\n"
                        f"**Thông tin về bệnh:**\n{disease.description}\n\n"
                        f"**Hướng dẫn điều trị:**\n{disease.treatment_guidelines}"
                        f"{matching_symptoms_text}"
                        f"{missing_symptoms_text}"
                        f"{medicine_text}\n\n"
                        f"## Khuyến nghị\n\n"
                        f"**Lưu ý quan trọng:** Đây chỉ là tư vấn sơ bộ dựa trên các triệu chứng bạn cung cấp. "
                        f"Để có chẩn đoán chính xác và phương pháp điều trị phù hợp, vui lòng đến cơ sở y tế để được khám và tư vấn bởi bác sĩ chuyên khoa."
                    )
                    
                    # Add severity-based advice
                    if hasattr(disease, 'severity') and disease.severity:
                        if disease.severity == 'high':
                            database_response += f"\n\n⚠️ **Cảnh báo:** {disease.name} là bệnh nghiêm trọng. Bạn nên đến cơ sở y tế ngay để được khám và điều trị kịp thời."
                        elif disease.severity == 'medium':
                            database_response += f"\n\n⚠️ {disease.name} cần được theo dõi và điều trị phù hợp. Bạn nên đặt lịch khám với bác sĩ trong thời gian sớm nhất."
                    
                    # Get user from session and save diagnosis if possible
                    if session_id:
                        try:
                            user = await self.get_user_from_session(session_id)
                            if user:
                                diagnosis = await self.save_diagnosis_to_db(user, symptoms, disease, confidence)
                                if diagnosis:
                                    database_response += f"\n\nTôi đã lưu chẩn đoán này vào hồ sơ y tế của bạn. Bạn có thể xem lại trong mục 'Lịch sử chẩn đoán'."
                        except Exception as e:
                            print(f"Error saving diagnosis: {str(e)}")
                    
                    # Generate related questions based on the diagnosed disease
                    related_questions = [
                        f"Tôi nên làm gì để phòng ngừa {disease.name}?",
                        f"Các biến chứng của {disease.name} là gì?",
                        f"Bệnh {disease.name} lây truyền qua đường nào?",
                        f"Chế độ ăn uống nào tốt cho người bị {disease.name}?",
                        f"Thời gian điều trị {disease.name} là bao lâu?",
                        f"Có thể điều trị {disease.name} tại nhà không?",
                        f"Bệnh {disease.name} có nguy hiểm không?",
                        f"Cần làm xét nghiệm gì khi nghi ngờ bị {disease.name}?",
                        f"Bệnh {disease.name} có di truyền không?",
                        f"Trẻ em có thể bị {disease.name} không?"
                    ]
                    
                    # Add suggested questions to the end of the response
                    database_response += "\n\n## Câu hỏi gợi ý\n\nBạn có thể quan tâm đến:\n"
                    database_response += "- " + "\n- ".join(random.sample(related_questions, min(3, len(related_questions))))
                    
                    # Save response to database
                    if session_id:
                        try:
                            await self.save_message_to_db(session_id, 'bot', database_response)
                        except Exception as e:
                            print(f"Error saving response to database: {str(e)}")
                    
                    # Send the database-generated response
            await self.send(text_data=json.dumps({
                        'message': database_response,
                'type': 'bot',
                'status': 'success'
            }))
                    return
            
            # If no symptoms found or use_gemini is True, use Gemini AI
            try:
                # Get user context from session if available
                user_context = None
                if session_id:
                    try:
                        user = await self.get_user_from_session(session_id)
                        if user:
                            # Build context from user information
                            user_context = f"Tên: {user.get_full_name() or user.username}\n"
                            
                            # Add diagnosis history if available
                            user_diagnoses = await self.get_user_diagnoses(user)
                            if user_diagnoses:
                                user_context += "Lịch sử chẩn đoán:\n"
                                for diag in user_diagnoses[:3]:  # Limit to 3 most recent diagnoses
                                    user_context += f"- {diag.disease.name} ({diag.created_at.strftime('%d/%m/%Y')})\n"
                    except Exception as e:
                        print(f"Error getting user context: {str(e)}")
                
                # Call Gemini API with user context
                ai_response = await self.call_gemini_api_async(message, user_context)
                
                # Convert any Markdown headers to bold text to avoid rendering issues in some clients
                formatted_response = ai_response
                
                # Format response to include a "Try the diagnosis engine" suggestion if symptoms were detected
                if symptoms and len(symptoms) >= 2:
                    symptom_names = [symptom.name for symptom in symptoms]
                    formatted_response += f"\n\n---\n\n**Gợi ý:** Tôi đã nhận thấy bạn có các triệu chứng: **{', '.join(symptom_names)}**. Bạn có thể nhấn nút 'Chẩn đoán bệnh' để tôi phân tích chi tiết hơn về tình trạng sức khỏe của bạn."
                
                # Save response to database
                if session_id:
                    try:
                        await self.save_message_to_db(session_id, 'bot', formatted_response)
                    except Exception as e:
                        print(f"Error saving Gemini response to database: {str(e)}")
                
                # Send the AI response
            await self.send(text_data=json.dumps({
                    'message': formatted_response,
                    'type': 'bot',
                    'status': 'success'
                }))
                
            except Exception as e:
                error_message = f"Xin lỗi, đã xảy ra lỗi khi tạo phản hồi: {str(e)}"
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

    async def call_gemini_api_async(self, message, context=None):
        """
        Call Gemini API asynchronously to process the message
        """
        try:
            # Prepare system instructions for medical consultation with enhanced medical focus
            system_instructions = """Bạn là trợ lý y tế ảo ReViCARE, một hệ thống chuyên về tư vấn và chẩn đoán y tế sơ bộ.

            Thông tin về hệ thống ReViCARE:
            - ReViCARE là hệ thống quản lý y tế tích hợp cho phép chẩn đoán, tư vấn thuốc và theo dõi bệnh án
            - Hệ thống có cơ sở dữ liệu về các bệnh, triệu chứng và thuốc phổ biến tại Việt Nam
            - Hệ thống có khả năng phân tích triệu chứng để đưa ra chẩn đoán sơ bộ và gợi ý thuốc
            
            Khi tư vấn y tế, hãy làm theo hướng dẫn sau:
            1. Trả lời bằng tiếng Việt với ngôn ngữ chuyên môn y tế nhưng dễ hiểu
            2. Hỏi thêm về các triệu chứng cụ thể như: vị trí, mức độ, thời gian xuất hiện, các yếu tố làm giảm/tăng
            3. Phân tích triệu chứng theo phương pháp y khoa: tần suất, mức độ, thời gian, diễn biến
            4. Đề xuất các xét nghiệm cần thiết nếu bệnh nhân cần thăm khám thêm
            5. Đưa ra các chẩn đoán phân biệt (2-3 khả năng) dựa trên triệu chứng
            6. Giải thích ngắn gọn về cơ chế bệnh sinh có thể có
            7. Đưa ra khuyến nghị về điều trị và phòng ngừa
            8. LUÔN khuyên người dùng đi khám bác sĩ nếu có triệu chứng nghiêm trọng
            9. Định dạng phản hồi của bạn bằng Markdown để dễ đọc (dùng **bold**, *italic*, - cho bullet points)
            
            Các dấu hiệu nguy hiểm cần nhấn mạnh đi khám ngay:
            - Đau ngực dữ dội, khó thở
            - Liệt, yếu hoặc tê một bên cơ thể, nói khó
            - Đau đầu dữ dội, đột ngột
            - Sốt cao kéo dài trên 39°C
            - Chảy máu không kiểm soát được
            - Bất tỉnh hoặc co giật
            - Đau bụng dữ dội và đột ngột
            - Nhìn mờ hoặc thay đổi thị lực đột ngột
            
            Khi đề cập đến thuốc:
            1. Chỉ gợi ý thuốc cho các triệu chứng nhẹ, phổ biến
            2. Nêu rõ liều lượng thông thường cho người lớn
            3. Luôn liệt kê các tác dụng phụ và chống chỉ định chính
            4. Nhấn mạnh rằng việc sử dụng thuốc cần tuân theo chỉ định của bác sĩ
            
            Về mặt chuyên môn y khoa:
            1. Sử dụng kiến thức y khoa hiện đại và cập nhật
            2. Tham khảo các hướng dẫn điều trị chuẩn của Bộ Y tế Việt Nam
            3. Không đưa ra thông tin y học chưa được kiểm chứng
            4. Thừa nhận hạn chế của tư vấn từ xa và chẩn đoán sơ bộ
            
            Đối với các câu hỏi không liên quan đến y tế, chỉ trả lời ngắn gọn và hướng người dùng quay lại chủ đề sức khỏe.
            """
            
            # Add context if available
            if context:
                system_instructions += f"\n\nThông tin bổ sung về bệnh nhân:\n{context}"
            
            # Prepare the API request with enhanced medical context
            api_request = {
                "contents": [
                    {
                        "role": "system",
                        "parts": [{"text": system_instructions}]
                    },
                    {
                        "role": "user",
                        "parts": [{"text": message}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,  # Lower temperature for more focused medical responses
                    "topP": 0.95,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            # Make the async request to Gemini API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json=api_request,
                headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        gemini_response = await response.json()
                bot_message = gemini_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                if not bot_message:
                    bot_message = "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau."
                
                return bot_message
            else:
                        # Enhanced fallback responses if API fails
                        response_text = await response.text()
                        print(f"Gemini API error: {response.status} - {response_text}")
                        
                if "xin chào" in message.lower() or "chào" in message.lower():
                            return "Xin chào! Tôi là trợ lý y tế ảo ReViCARE. Bạn có thể mô tả chi tiết các triệu chứng đang gặp phải hoặc đặt câu hỏi về vấn đề sức khỏe. Tôi sẽ cố gắng đưa ra tư vấn sơ bộ và hướng dẫn phù hợp."
                elif "cảm ơn" in message.lower():
                            return "Không có gì! Hy vọng thông tin tôi cung cấp hữu ích cho bạn. Nếu có bất kỳ câu hỏi nào khác về sức khỏe, đừng ngần ngại hỏi tôi."
                        elif any(symptom in message.lower() for symptom in ["ho", "đau", "sốt", "mệt", "đau đầu", "khó thở"]):
                            return "Từ triệu chứng bạn mô tả, có thể liên quan đến nhiều vấn đề sức khỏe khác nhau. Để đưa ra tư vấn chính xác hơn, bạn có thể chia sẻ thêm: Triệu chứng xuất hiện từ khi nào? Có kèm theo các triệu chứng khác không? Mức độ nghiêm trọng ra sao? Đã dùng thuốc gì chưa? Nếu triệu chứng nghiêm trọng hoặc kéo dài, tôi khuyên bạn nên đến cơ sở y tế để được khám và điều trị phù hợp."
                else:
                            return f"Xin lỗi, hiện tại tôi không thể kết nối đến dịch vụ AI (Lỗi: {response.status}). Để tư vấn y tế chính xác, bạn vui lòng thử lại sau hoặc liên hệ trực tiếp với bác sĩ nếu có vấn đề sức khỏe cần được giải quyết ngay."
                
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return f"Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn: {str(e)}. Vui lòng thử lại sau hoặc liên hệ trực tiếp với bác sĩ nếu cần tư vấn y tế khẩn cấp."
    
    # For backward compatibility
    def call_gemini_api(self, message, context=None):
        """
        Synchronous wrapper around the async API call
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.call_gemini_api_async(message, context))
        finally:
            loop.close()

    @database_sync_to_async
    def save_message_to_db(self, session_id, msg_type, content):
        """
        Save a message to the database
        """
        try:
            # Get the chat session
            session = ChatSession.objects.get(id=session_id)
            
            # Create the message
            message = Message.objects.create(
                session=session,
                type=msg_type,
                content=content
            )
            
            return message
        except Exception as e:
            print(f"Error saving message to database: {str(e)}")
            # Re-raise the exception to be handled by the caller
            raise

    @database_sync_to_async
    def create_chat_session(self):
        return ChatSession.objects.create(user=self.scope["user"])

    @database_sync_to_async
    def end_chat_session(self):
        self.session.status = 'closed'
        self.session.ended_at = timezone.now()
        self.session.save()

    @database_sync_to_async
    def save_message(self, msg_type, content):
        return Message.objects.create(
            session=self.session,
            type=msg_type,
            content=content
        )

    @database_sync_to_async
    def get_response(self, intent_name):
        try:
            intent = Intent.objects.get(name=intent_name)
            responses = Response.objects.filter(intent=intent)
            if responses.exists():
                return random.choice(responses).content
        except Intent.DoesNotExist:
            pass
        return "Xin lỗi, tôi không hiểu ý của bạn. Bạn có thể nói rõ hơn được không?"

    @database_sync_to_async
    def extract_symptoms_from_text(self, text):
        """
        Cải tiến thuật toán tìm kiếm các triệu chứng trong văn bản người dùng nhập vào
        """
        # Lấy tất cả triệu chứng từ cơ sở dữ liệu
        all_symptoms = Symptom.objects.all()
        
        # Danh sách lưu các triệu chứng tìm thấy
        found_symptoms = []
        
        # Chuyển văn bản sang chữ thường để dễ so sánh
        text_lower = text.lower()
        
        # Tiền xử lý văn bản
        # Chuẩn hóa dấu câu và khoảng trắng
        text_normalized = re.sub(r'[.,:;!?]+', ' ', text_lower)
        text_normalized = re.sub(r'\s+', ' ', text_normalized).strip()
        
        # Tách thành câu và từ
        sentences = re.split(r'[.,;!?]+', text_lower)
        words = text_normalized.split()
        
        # Các từ phủ định phổ biến trong tiếng Việt
        negation_words = ['không', 'chẳng', 'ko', 'k', 'chưa', 'không còn', 'không bị', 'chưa từng', 
                         'không hề', 'chẳng có', 'không có', 'không phải', 'phủ nhận']
        
        # Các cụm từ thể hiện mức độ
        intensity_words = {
            'cao': 1.2, 'nặng': 1.2, 'dữ dội': 1.3, 'nghiêm trọng': 1.4, 'trầm trọng': 1.4, 'dữ': 1.3,
            'rất': 1.3, 'cực kỳ': 1.4, 'vô cùng': 1.4,
            'nhẹ': 0.8, 'ít': 0.7, 'thỉnh thoảng': 0.6, 'hơi': 0.8, 'chút ít': 0.7,
            'đôi khi': 0.6, 'thỉnh thoảng': 0.5, 'hiếm khi': 0.4
        }
        
        # Tạo danh sách các cụm từ có thể là triệu chứng với độ dài khác nhau
        phrases = []
        
        # Thêm các câu hoàn chỉnh
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                phrases.append(sentence)
        
        # Thêm các cụm từ n-gram (2-4 từ liên tiếp)
        for i in range(len(words)):
            for n in range(2, min(6, len(words) - i + 1)):  # Tăng từ max 4 lên 5 từ
                phrase = ' '.join(words[i:i+n])
                phrases.append(phrase)
        
        # Dictionary để lưu trữ các triệu chứng tìm thấy và mức độ tin cậy
        symptom_scores = {}
        
        # Xử lý trường hợp đặc biệt: các từ đơn liên quan đến triệu chứng
        common_symptom_words = [
            'đau', 'nhức', 'sốt', 'ho', 'mệt', 'mỏi', 'buồn nôn', 'nôn', 'ói',
            'chóng mặt', 'khó thở', 'đau đầu', 'nhức đầu', 'sưng', 'phát ban',
            'ngứa', 'rát', 'khô', 'tê', 'lạnh', 'nóng', 'run', 'co giật',
            'xuất huyết', 'tiêu chảy', 'táo bón', 'sổ mũi', 'nghẹt mũi', 'hắt hơi',
            'mất ngủ', 'mất cảm giác', 'mất vị giác', 'mất khứu giác', 'mờ mắt',
            'hoa mắt', 'ù tai', 'đau bụng', 'đau ngực', 'đau lưng', 'đau cổ',
            'phù', 'sưng', 'mụn', 'ban đỏ', 'chảy máu', 'chảy mủ', 'viêm',
            'mẩn đỏ', 'mẩn ngứa', 'mụn nước', 'mụn mủ', 'phát ban', 'nổi mề đay',
            'khàn giọng', 'khàn tiếng', 'khô miệng', 'khô họng', 'đổ mồ hôi',
            'ớn lạnh', 'run rẩy', 'tê cứng', 'tê buốt', 'tê liệt', 'yếu',
            'mệt mỏi', 'mệt lả', 'kiệt sức', 'uể oải', 'không có sức'
        ]
        
        for word in common_symptom_words:
            if word in text_normalized:
                # Kiểm tra xem từ này có nằm sau từ phủ định không
                negated = False
                for negation in negation_words:
                    negation_pattern = f"{negation} {word}"
                    if negation_pattern in text_normalized:
                        negated = True
                        break
                    # Kiểm tra mẫu phủ định mở rộng (có thể có từ ở giữa)
                    extended_negation_pattern = f"{negation}\\s+\\w+\\s+{word}"
                    if re.search(extended_negation_pattern, text_normalized):
                        negated = True
                        break
                
                if not negated:
                    # Tìm triệu chứng phù hợp với từ này
                    matching_symptoms = list(Symptom.objects.filter(name__icontains=word))
                    for symptom in matching_symptoms:
                        symptom_id = symptom.id
                        base_score = 0.5  # Điểm cơ bản cho từ đơn
                        
                        # Kiểm tra mức độ
                        intensity_factor = 1.0
                        for intensity, factor in intensity_words.items():
                            if f"{intensity} {word}" in text_normalized:
                                intensity_factor = factor
                                break
                        
                        final_score = base_score * intensity_factor
                        
                        if symptom_id in symptom_scores:
                            symptom_scores[symptom_id] = max(symptom_scores[symptom_id], final_score)
                        else:
                            symptom_scores[symptom_id] = final_score
                            print(f"Found common symptom word: {word} for {symptom.name}, score: {final_score}")
        
        # Kiểm tra từng triệu chứng có trong văn bản không
        for symptom in all_symptoms:
            symptom_name_lower = symptom.name.lower()
            symptom_words = set(symptom_name_lower.split())
            
            # 1. Tìm kiếm trực tiếp - triệu chứng xuất hiện nguyên văn
            if symptom_name_lower in text_normalized:
                # Kiểm tra xem triệu chứng có bị phủ định không
                negated = False
                for negation in negation_words:
                    if f"{negation} {symptom_name_lower}" in text_normalized:
                        negated = True
                        break
                
                if not negated:
                    # Điểm cao nhất cho khớp chính xác
                    symptom_scores[symptom.id] = 1.0
                    print(f"Found symptom (exact match): {symptom.name}")
                continue
            
            # 2. Tìm kiếm cụm từ - triệu chứng xuất hiện trong cụm từ hoặc ngược lại
            for phrase in phrases:
                match_score = 0
                if symptom_name_lower in phrase:
                    match_score = 0.9  # Điểm cao cho triệu chứng nằm trong cụm từ
                elif phrase in symptom_name_lower:
                    match_score = 0.8  # Điểm khá cao nếu cụm từ là một phần của triệu chứng
                
                if match_score > 0:
                    # Kiểm tra phủ định
                    negated = False
                    for negation in negation_words:
                        if f"{negation} {phrase}" in text_normalized:
                            negated = True
                            break
                    
                    if not negated:
                        if symptom.id in symptom_scores:
                            symptom_scores[symptom.id] = max(symptom_scores[symptom.id], match_score)
                        else:
                            symptom_scores[symptom.id] = match_score
                            print(f"Found symptom (phrase): {symptom.name} in '{phrase}', score: {match_score}")
            
            # 3. Tìm kiếm từng từ trong tên triệu chứng - cho triệu chứng có nhiều từ
            if len(symptom_words) > 1 and symptom.id not in symptom_scores:
                text_words = set(words)
                common_words = symptom_words.intersection(text_words)
                
                # Nếu có ít nhất 70% số từ trong tên triệu chứng xuất hiện trong văn bản
                match_ratio = len(common_words) / len(symptom_words)
                if match_ratio >= 0.7:
                    # Kiểm tra phủ định - phức tạp hơn vì chúng ta đang kiểm tra từng từ
                    negated = False
                    for negation in negation_words:
                        for word in common_words:
                            if f"{negation} {word}" in text_normalized:
                                negated = True
                                break
                        if negated:
                            break
                    
                    if not negated:
                        # Điểm dựa trên tỷ lệ từ trùng khớp
                        match_score = 0.6 + (match_ratio * 0.3)  # 0.6-0.9 dựa trên tỷ lệ trùng khớp
                        
                        if symptom.id in symptom_scores:
                            symptom_scores[symptom.id] = max(symptom_scores[symptom.id], match_score)
                        else:
                            symptom_scores[symptom.id] = match_score
                            print(f"Found symptom (word match): {symptom.name}, common words: {common_words}, score: {match_score}")
        
        # Kiểm tra các trường hợp đặc biệt - triệu chứng phổ biến có nhiều cách diễn đạt
        special_cases = {
            'đau': ['nhức', 'đau đớn', 'đau nhức', 'cơn đau', 'bị đau', 'cảm thấy đau', 'rát', 'buốt'],
            'ho': ['ho khan', 'ho có đờm', 'ho nhiều', 'bị ho', 'ho ra máu', 'ho dai dẳng', 'ho liên tục'],
            'sốt': ['nóng', 'sốt cao', 'bị sốt', 'nóng sốt', 'cảm sốt', 'sốt nhẹ', 'lên cơn sốt', 'sốt rét', 'sốt li bì'],
            'mệt': ['mệt mỏi', 'uể oải', 'không có sức', 'kiệt sức', 'mệt lả', 'không có năng lượng', 'mệt lử'],
            'buồn nôn': ['nôn', 'buồn ói', 'muốn nôn', 'ói', 'nôn ói', 'nôn mửa', 'buồn nôn', 'buồn ói'],
            'chóng mặt': ['hoa mắt', 'váng đầu', 'xây xẩm', 'choáng váng', 'quay cuồng', 'tối mắt', 'đầu óc quay cuồng'],
            'khó thở': ['thở khó', 'thở gấp', 'thở hụt hơi', 'thở không được', 'thở dốc', 'thở nặng nhọc', 'thở hổn hển'],
            'đau đầu': ['nhức đầu', 'đầu đau', 'đau nửa đầu', 'đau đầu dữ dội', 'migraine', 'đau đầu âm ỉ', 'đau đầu sau gáy'],
            'tiêu chảy': ['đi ngoài', 'đi lỏng', 'đi nhiều lần', 'phân lỏng', 'tiêu lỏng', 'tiêu nhiều lần', 'đau bụng đi ngoài'],
            'mất ngủ': ['khó ngủ', 'mất giấc', 'trằn trọc', 'thức giấc giữa đêm', 'ngủ không sâu giấc', 'ngủ không ngon'],
            'mệt mỏi': ['mệt', 'không có sức', 'kiệt sức', 'yếu', 'không có năng lượng', 'mệt lử', 'cảm thấy yếu'],
            'đau bụng': ['đau dạ dày', 'đau ruột', 'cơn đau bụng', 'đau thắt bụng', 'bụng đau', 'đau bụng dưới', 'đau bụng trên'],
            'chảy máu cam': ['chảy máu mũi', 'chảy máu ở mũi', 'xuất huyết mũi'],
            'nổi mề đay': ['phát ban', 'nổi sẩn', 'nổi mụn', 'nổi ban đỏ', 'nổi ban'],
            'nổi mẩn': ['phát ban', 'nổi sẩn', 'nổi mụn', 'nổi ban đỏ', 'nổi ban'],
            'đau họng': ['viêm họng', 'rát họng', 'khô họng', 'khàn giọng', 'đau khi nuốt'],
            'nghẹt mũi': ['mũi nghẹt', 'không thở được bằng mũi', 'mũi tắc', 'mũi bít'],
            'sổ mũi': ['chảy nước mũi', 'nước mũi chảy', 'mũi chảy nước', 'mũi chảy', 'mũi có dịch']
        }
        
        for base_symptom, variations in special_cases.items():
            # Tìm xem có biến thể của triệu chứng trong văn bản không
            found_variations = []
            
            # Tìm cả từ gốc
            if base_symptom in text_normalized:
                found_variations.append(base_symptom)
            
            # Tìm các biến thể
            for var in variations:
                if var in text_normalized:
                    # Kiểm tra phủ định
                    negated = False
                    for negation in negation_words:
                        if f"{negation} {var}" in text_normalized:
                            negated = True
                            break
                    
                    if not negated:
                        found_variations.append(var)
            
            # Nếu tìm thấy biến thể không bị phủ định, tìm triệu chứng tương ứng trong cơ sở dữ liệu
            if found_variations:
                try:
                    matching_symptoms = list(Symptom.objects.filter(name__icontains=base_symptom))
                    for symptom in matching_symptoms:
                        # Điểm cho các biến thể cụm từ
                        match_score = 0.85  # Điểm cao cho các biến thể đặc biệt
                        
                        # Tăng điểm nếu tìm thấy nhiều biến thể
                        variation_bonus = min(0.1, 0.02 * len(found_variations))
                        match_score += variation_bonus
                        
                        if symptom.id in symptom_scores:
                            symptom_scores[symptom.id] = max(symptom_scores[symptom.id], match_score)
                        else:
                            symptom_scores[symptom.id] = match_score
                            print(f"Found symptom (special case): {symptom.name}, variations: {found_variations}, score: {match_score}")
                except Exception as e:
                    print(f"Error finding special case symptom: {str(e)}")
        
        # Xử lý các cụm vị trí cơ thể - kết hợp với từ triệu chứng để xác định chính xác hơn
        body_parts = ['đầu', 'cổ', 'vai', 'lưng', 'ngực', 'bụng', 'tay', 'chân', 'mắt', 'tai', 'mũi', 
                      'họng', 'miệng', 'răng', 'lưỡi', 'da', 'khớp', 'cơ', 'xương', 'thận', 'tim', 
                      'phổi', 'gan', 'dạ dày', 'ruột', 'sọ', 'não', 'tủy sống', 'cánh tay', 'bàn tay',
                      'cẳng chân', 'bàn chân', 'mắt cá', 'đầu gối', 'hông', 'khuỷu tay', 'cổ tay',
                      'gáy', 'thái dương', 'trán', 'má', 'cằm', 'lông mày', 'lông mi', 'mí mắt',
                      'lỗ mũi', 'chân mày', 'cuống họng', 'amidan', 'vòm họng', 'thực quản', 'ruột non',
                      'ruột già', 'đại tràng', 'trực tràng', 'hậu môn', 'niêm mạc', 'tuyến mồ hôi']
        
        symptom_verbs = ['đau', 'nhức', 'sưng', 'ngứa', 'đỏ', 'tê', 'yếu', 'cứng', 'mỏi', 'phù', 'nóng',
                         'lạnh', 'viêm', 'rát', 'ngứa', 'khô', 'chảy máu', 'chảy mủ', 'mụn', 'nổi ban',
                         'sưng tấy', 'thâm', 'tím', 'vàng', 'xanh', 'đổi màu', 'tiết dịch', 'khó cử động']
        
        for part in body_parts:
            for verb in symptom_verbs:
                compound = f"{verb} {part}"
                if compound in text_normalized:
                    # Tìm triệu chứng phù hợp nhất
                    try:
                        matches = list(Symptom.objects.filter(name__icontains=part))
                        if matches:
                            closest_match = None
                            max_similarity = 0
                            
                            for match in matches:
                                # Tính độ tương đồng đơn giản
                                if verb in match.name.lower():
                                    similarity = 0.75  # Điểm cao nếu cả động từ và bộ phận cơ thể đều khớp
                                else:
                                    similarity = 0.65  # Điểm thấp hơn nếu chỉ có bộ phận cơ thể khớp
                                
                                # Kiểm tra mức độ
                                for intensity, factor in intensity_words.items():
                                    if f"{intensity} {verb} {part}" in text_normalized:
                                        similarity *= factor
                                        break
                                
                                if similarity > max_similarity:
                                    max_similarity = similarity
                                    closest_match = match
                            
                            if closest_match:
                                if closest_match.id in symptom_scores:
                                    symptom_scores[closest_match.id] = max(symptom_scores[closest_match.id], max_similarity)
                                else:
                                    symptom_scores[closest_match.id] = max_similarity
                                    print(f"Found symptom (body part): {closest_match.name} from '{compound}', score: {max_similarity}")
                    except Exception as e:
                        print(f"Error finding body part symptom: {str(e)}")
        
        # Lọc các triệu chứng có điểm tin cậy trên ngưỡng
        confidence_threshold = 0.5
        reliable_symptoms = []
        
        for symptom_id, score in sorted(symptom_scores.items(), key=lambda x: x[1], reverse=True):
            if score >= confidence_threshold:
                try:
                    symptom = Symptom.objects.get(id=symptom_id)
                    reliable_symptoms.append(symptom)
                    print(f"Added reliable symptom: {symptom.name}, confidence: {score}")
                except Symptom.DoesNotExist:
                    pass
        
        return reliable_symptoms

    @database_sync_to_async
    def find_diseases_by_symptoms(self, symptoms):
        """
        Cải tiến thuật toán tìm kiếm bệnh dựa trên triệu chứng với trọng số và xác suất thống kê
        """
        if not symptoms:
            return []
        
        # Lấy tất cả bệnh có ít nhất một triệu chứng trùng khớp
        diseases = Disease.objects.filter(symptoms__in=symptoms).distinct()
        print(f"Found {len(diseases)} potential diseases based on symptoms")
        
        # Tính số lượng triệu chứng trùng khớp cho mỗi bệnh
        disease_matches = []
        
        # Hệ số trọng số cho các triệu chứng đặc trưng
        # Tính dựa trên độ phổ biến của triệu chứng (triệu chứng hiếm có trọng số cao hơn)
        total_diseases = Disease.objects.count()
        all_symptom_weights = {}
        
        for symptom in symptoms:
            # Đếm số bệnh có triệu chứng này
            symptom_disease_count = Disease.objects.filter(symptoms=symptom).count()
            if symptom_disease_count > 0:
                # Tính trọng số dựa trên công thức IDF (Inverse Document Frequency)
                # Triệu chứng càng hiếm (xuất hiện trong ít bệnh), trọng số càng cao
                all_symptom_weights[symptom.id] = 1.0 + (1.0 * (total_diseases / symptom_disease_count))
            else:
                all_symptom_weights[symptom.id] = 1.0
        
        # In ra trọng số các triệu chứng
        print(f"Symptom weights: {all_symptom_weights}")
        
        for disease in diseases:
            # Lấy tất cả triệu chứng của bệnh
            disease_symptoms = disease.symptoms.all()
            
            # Xác định các triệu chứng trùng khớp
            matching_symptoms = set(disease_symptoms) & set(symptoms)
            
            # Xác định các triệu chứng còn thiếu
            missing_symptoms = set(disease_symptoms) - set(symptoms)
            
            # Xác định các triệu chứng thừa (có ở người dùng nhưng không phải của bệnh này)
            extra_symptoms = set(symptoms) - set(disease_symptoms)
            
            # Không tiếp tục nếu không có triệu chứng trùng khớp
            if not matching_symptoms:
                continue
            
            # Tính điểm trùng khớp theo tỷ lệ trọng số
            weighted_symptom_score = 0
            matching_weight_sum = 0
            
            # 1. Cộng điểm cho các triệu chứng trùng khớp, với trọng số dựa trên độ hiếm
            for symptom in matching_symptoms:
                # Lấy trọng số của triệu chứng (với giá trị mặc định là 1.0)
                weight = all_symptom_weights.get(symptom.id, 1.0)
                weighted_symptom_score += weight
                matching_weight_sum += weight
            
            # 2. Trừ điểm cho các triệu chứng thừa (không thuộc bệnh này)
            # Triệu chứng thừa sẽ làm giảm điểm trùng khớp, nhưng với mức độ nhẹ hơn
            extra_weight_sum = 0
            for symptom in extra_symptoms:
                weight = all_symptom_weights.get(symptom.id, 1.0)
                weighted_symptom_score -= weight * 0.3  # Giảm trọng số cho triệu chứng thừa
                extra_weight_sum += weight * 0.3
            
            # Tính độ tin cậy dựa trên số lượng triệu chứng và trọng số
            total_disease_symptoms = disease_symptoms.count()
            
            # Đếm số lượng triệu chứng quan trọng của bệnh
            important_symptoms_count = 0
            for symptom in disease_symptoms:
                if Disease.objects.filter(symptoms=symptom).count() <= total_diseases * 0.3:
                    important_symptoms_count += 1
            
            # Tính điểm cho các triệu chứng quan trọng đã khớp
            important_matched = 0
            for symptom in matching_symptoms:
                if Disease.objects.filter(symptoms=symptom).count() <= total_diseases * 0.3:
                    important_matched += 1
            
            # Tính độ tin cậy cơ bản: tỷ lệ triệu chứng trùng khớp
            if total_disease_symptoms > 0:
                # Công thức cơ bản: số triệu chứng trùng khớp / tổng số triệu chứng của bệnh
                basic_confidence = len(matching_symptoms) / total_disease_symptoms
                
                # Tăng cường độ tin cậy nếu các triệu chứng quan trọng được khớp
                if important_symptoms_count > 0:
                    important_symptom_confidence = important_matched / important_symptoms_count
                    # Triệu chứng quan trọng có trọng số cao hơn trong công thức
                    basic_confidence = (basic_confidence * 0.7) + (important_symptom_confidence * 0.3)
                
                # Trọng số cho số lượng triệu chứng
                # Bệnh có nhiều triệu chứng, được điều chỉnh để tránh bất lợi
                symptoms_weight = min(1.0, 3.0 / total_disease_symptoms) + 0.4
                
                # Tính điểm độ nghiêm trọng của bệnh (bệnh nặng cần nhiều triệu chứng trùng khớp hơn)
                severity_weight = 1.0
                if hasattr(disease, 'severity'):
                    if disease.severity == 'high':
                        severity_weight = 0.8  # Yêu cầu nhiều triệu chứng trùng khớp hơn cho bệnh nặng
                    elif disease.severity == 'low':
                        severity_weight = 1.2  # Yêu cầu ít triệu chứng trùng khớp hơn cho bệnh nhẹ
                
                # Chỉ số trùng khớp từ trọng số
                if matching_weight_sum > 0:
                    weighted_match_ratio = weighted_symptom_score / (matching_weight_sum + extra_weight_sum)
                else:
                    weighted_match_ratio = 0
                
                # Công thức tính độ tin cậy theo trọng số
                weighted_confidence = (basic_confidence * severity_weight * symptoms_weight)
                
                # Tính độ tin cậy cuối cùng: kết hợp giữa độ tin cậy cơ bản và điểm trùng khớp
                final_confidence = max(0.15, (weighted_confidence * 0.6) + (weighted_match_ratio * 0.4))
                
                # Điều chỉnh theo số lượng triệu chứng còn thiếu
                missing_penalty = 0
                if total_disease_symptoms > 0:
                    missing_ratio = len(missing_symptoms) / total_disease_symptoms
                    # Phạt nhẹ hơn nếu chỉ thiếu một phần nhỏ triệu chứng
                    missing_penalty = missing_ratio * 0.2
                
                # Trừ điểm phạt
                final_confidence = max(0.15, final_confidence - missing_penalty)
                
                # Nếu tất cả triệu chứng của bệnh đều trùng khớp và không có triệu chứng thừa,
                # tăng độ tin cậy lên tối đa 0.95
                if len(matching_symptoms) == total_disease_symptoms and len(extra_symptoms) == 0:
                    final_confidence = min(0.95, final_confidence * 1.5)
                
                # Nếu có hơn 80% triệu chứng trùng khớp, tăng độ tin cậy
                elif len(matching_symptoms) / total_disease_symptoms > 0.8:
                    final_confidence = min(0.9, final_confidence * 1.3)
                
                # Nếu tất cả triệu chứng quan trọng đều khớp, tăng độ tin cậy
                if important_symptoms_count > 0 and important_matched == important_symptoms_count:
                    final_confidence = min(0.95, final_confidence * 1.2)
                
                # Giới hạn độ tin cậy trong khoảng [0, 1]
                final_confidence = max(0, min(1, final_confidence))
                
                # Thêm kết quả vào danh sách
                disease_matches.append({
                    'disease': disease,
                    'matching_symptoms': matching_symptoms,
                    'missing_symptoms': missing_symptoms,
                    'extra_symptoms': extra_symptoms,
                    'weighted_score': weighted_symptom_score,
                    'basic_confidence': basic_confidence,
                    'confidence': final_confidence
                })
                
                print(f"Disease: {disease.name}, Matching: {len(matching_symptoms)}/{total_disease_symptoms}, " 
                      f"Important matched: {important_matched}/{important_symptoms_count}, "
                      f"Confidence: {final_confidence:.2f}, Score: {weighted_symptom_score:.2f}")
        
        # Sắp xếp theo độ tin cậy giảm dần
        sorted_matches = sorted(disease_matches, key=lambda x: x['confidence'], reverse=True)
        
        # Lọc các kết quả có độ tin cậy dưới ngưỡng tối thiểu (20%)
        filtered_matches = [match for match in sorted_matches if match['confidence'] >= 0.2]
        
        return filtered_matches

    @database_sync_to_async
    def get_disease_by_name(self, disease_name):
        """
        Tìm kiếm bệnh theo tên
        """
        try:
            disease = Disease.objects.get(name__icontains=disease_name)
            return disease
        except (Disease.DoesNotExist, Disease.MultipleObjectsReturned):
            return None

    @database_sync_to_async
    def get_all_symptoms(self):
        """
        Lấy danh sách tất cả các triệu chứng trong hệ thống
        """
        from diagnosis.models import Symptom
        symptoms = Symptom.objects.all().order_by('name')
        return list(symptoms)

    @database_sync_to_async
    def get_all_diseases(self):
        """
        Lấy danh sách tất cả các bệnh trong hệ thống
        """
        from diagnosis.models import Disease
        diseases = Disease.objects.all().order_by('name')
        return list(diseases)

    @database_sync_to_async
    def recommend_medicines_for_disease(self, disease):
        """
        Cải tiến thuật toán gợi ý thuốc dựa trên bệnh và triệu chứng với phân tích độ liên quan
        """
        # Các thuốc được gợi ý cho bệnh này
        recommendations = []
        
        try:
            # 1. Tìm kiếm thuốc dựa trên tên bệnh trong mô tả
            medicines_by_name = list(Medicine.objects.filter(description__icontains=disease.name))
            if medicines_by_name:
                print(f"Found {len(medicines_by_name)} medicines by disease name")
            
            # 2. Tìm thuốc dựa trên các từ khóa liên quan đến bệnh
            disease_keywords = disease.name.split()
            # Thêm các từ khóa từ mô tả bệnh (tối đa 5 từ quan trọng)
            if disease.description:
                # Loại bỏ các từ thông dụng
                common_words = ['và', 'hoặc', 'là', 'có', 'được', 'các', 'khi', 'như', 'thì', 'này', 'từ', 'với', 'để', 'của',
                               'trong', 'không', 'cho', 'một', 'đến', 'những', 'theo', 'nhiều', 'bị', 'bởi', 'gây', 'nên',
                               'làm', 'về', 'vì', 'tại', 'do', 'ra', 'vào', 'nếu', 'sẽ', 'mà', 'sau', 'trước', 'khi', 'tuy',
                               'nhưng', 'phải', 'cần', 'nên', 'thường', 'hay', 'cũng', 'đều', 'rất', 'rồi', 'vẫn', 'tất', 'cả']
                
                description_words = [word for word in disease.description.lower().split() 
                                  if len(word) > 3 and word not in common_words]
                # Chọn các từ quan trọng nhất
                disease_keywords.extend(description_words[:7])
            
            # Thêm các triệu chứng của bệnh vào từ khóa tìm kiếm
            symptom_keywords = [symptom.name.lower() for symptom in disease.symptoms.all()]
            disease_keywords.extend(symptom_keywords)
            
            # Chuyển tất cả thành lowercase và loại bỏ trùng lặp
            disease_keywords = list(set([keyword.lower() for keyword in disease_keywords if len(keyword) > 3]))
            
            # Nhóm các từ khóa theo mức độ quan trọng
            primary_keywords = [keyword for keyword in disease_keywords if keyword in disease.name.lower() or keyword in symptom_keywords]
            secondary_keywords = [keyword for keyword in disease_keywords if keyword not in primary_keywords]
            
            # Tìm thuốc dựa trên các từ khóa chính
            medicines_by_primary = []
            for keyword in primary_keywords:
                keyword_medicines = list(Medicine.objects.filter(description__icontains=keyword))
                for med in keyword_medicines:
                    med.relevance_score = 1.0  # Điểm cao nhất cho từ khóa chính
                    medicines_by_primary.append(med)
            
            # Tìm thuốc dựa trên các từ khóa phụ
            medicines_by_secondary = []
            for keyword in secondary_keywords:
                keyword_medicines = list(Medicine.objects.filter(description__icontains=keyword))
                for med in keyword_medicines:
                    med.relevance_score = 0.5  # Điểm thấp hơn cho từ khóa phụ
                    medicines_by_secondary.append(med)
            
            # 3. Tìm thuốc dựa trên các triệu chứng của bệnh
            symptom_medicines = []
            disease_symptoms = list(disease.symptoms.all())
            
            for symptom in disease_symptoms:
                symptom_meds = list(Medicine.objects.filter(description__icontains=symptom.name))
                for med in symptom_meds:
                    med.relevance_score = 0.8  # Điểm khá cao cho triệu chứng
                    symptom_medicines.append(med)
            
            # 4. Tìm Drug model
            drugs_by_name = list(Drug.objects.filter(description__icontains=disease.name))
            for drug in drugs_by_name:
                drug.relevance_score = 1.2  # Điểm cao nhất cho Drug model khớp trực tiếp với tên bệnh
            
            drugs_by_keywords = []
            for keyword in primary_keywords:
                keyword_drugs = list(Drug.objects.filter(description__icontains=keyword))
                for drug in keyword_drugs:
                    drug.relevance_score = 1.0  # Điểm cao cho Drug model khớp với từ khóa chính
                    drugs_by_keywords.append(drug)
            
            for keyword in secondary_keywords:
                keyword_drugs = list(Drug.objects.filter(description__icontains=keyword))
                for drug in keyword_drugs:
                    drug.relevance_score = 0.6  # Điểm thấp hơn cho Drug model khớp với từ khóa phụ
                    drugs_by_keywords.append(drug)
            
            # Kết hợp tất cả các thuốc tìm được
            all_medicines = []
            all_medicines.extend(medicines_by_name)
            all_medicines.extend(medicines_by_primary)
            all_medicines.extend(medicines_by_secondary)
            all_medicines.extend(symptom_medicines)
            
            # Tạo dict để lưu trữ các Medicine với điểm cao nhất
            medicine_scores = {}
            for med in all_medicines:
                if not hasattr(med, 'relevance_score'):
                    med.relevance_score = 0.5  # Giá trị mặc định
                
                # Cập nhật điểm cao nhất cho mỗi thuốc
                if med.id in medicine_scores:
                    medicine_scores[med.id] = max(medicine_scores[med.id], med.relevance_score)
                else:
                    medicine_scores[med.id] = med.relevance_score
            
            # Tạo dict để lưu trữ các Drug với điểm cao nhất
            all_drugs = drugs_by_name + drugs_by_keywords
            drug_scores = {}
            for drug in all_drugs:
                if not hasattr(drug, 'relevance_score'):
                    drug.relevance_score = 0.5  # Giá trị mặc định
                
                # Cập nhật điểm cao nhất cho mỗi thuốc
                if drug.id in drug_scores:
                    drug_scores[drug.id] = max(drug_scores[drug.id], drug.relevance_score)
                else:
                    drug_scores[drug.id] = drug.relevance_score
            
            # Tạo danh sách gợi ý từ Medicine
            for med_id, score in medicine_scores.items():
                try:
                    med = Medicine.objects.get(id=med_id)
                    recommendation = {
                        'name': med.name,
                        'type': 'medicine',
                        'description': med.description,
                        'price': med.price,
                        'score': score
                    }
                    recommendations.append(recommendation)
                except Medicine.DoesNotExist:
                    pass
            
            # Tạo danh sách gợi ý từ Drug (với thông tin chi tiết hơn)
            for drug_id, score in drug_scores.items():
                try:
                    drug = Drug.objects.get(id=drug_id)
                    recommendation = {
            'name': drug.name,
                        'type': 'drug',
            'description': drug.description,
                        'composition': drug.composition,
            'usage': drug.usage,
            'dosage': drug.dosage,
                        'side_effects': drug.side_effects,
                        'contraindications': drug.contraindications,
            'price': drug.price,
                        'manufacturer': drug.manufacturer,
                        'score': score
                    }
                    recommendations.append(recommendation)
                except Drug.DoesNotExist:
                    pass
            
            # Sắp xếp theo điểm giảm dần
            recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
            
            # Loại bỏ trùng lặp dựa trên tên
            unique_recommendations = []
            seen_names = set()
            
            for rec in recommendations:
                if rec['name'].lower() not in seen_names:
                    seen_names.add(rec['name'].lower())
                    unique_recommendations.append(rec)
            
            # Chỉ giữ lại 5 gợi ý tốt nhất
            return unique_recommendations[:5]
            
        except Exception as e:
            print(f"Error in medicine recommendation: {str(e)}")
            return []
        
    @database_sync_to_async
    def recommend_medicines_for_symptoms(self, symptoms):
        """
        Cải tiến thuật toán gợi ý thuốc dựa trên triệu chứng
        """
        if not symptoms:
            return []
        
        # Các thuốc được gợi ý
        recommendations = []
        
        # Dùng dictionary để theo dõi điểm của mỗi thuốc
        medicine_scores = {}
        
        # Lấy danh sách tất cả các thuốc trong Medicine model
        all_medicines = list(Medicine.objects.all())
        
        # Lấy danh sách tất cả các thuốc trong Drug model
        all_drugs = list(Drug.objects.all())
        
        # Lấy danh sách tên triệu chứng
        symptom_names = [symptom.name.lower() for symptom in symptoms]
        
        # Chuẩn bị các từ khóa từ tên triệu chứng
        symptom_keywords = []
        for name in symptom_names:
            words = name.split()
            for word in words:
                if len(word) > 3:  # Chỉ lấy từ có độ dài > 3
                    symptom_keywords.append(word)
        
        # Loại bỏ trùng lặp
        symptom_keywords = list(set(symptom_keywords))
        
        # 1. Tìm kiếm thuốc dựa trên tên triệu chứng
        for symptom in symptoms:
            # Tìm trong Medicine model
            symptom_medicines = list(Medicine.objects.filter(description__icontains=symptom.name))
            
            for medicine in symptom_medicines:
                if medicine.id in medicine_scores:
                    medicine_scores[medicine.id]['score'] += 50  # Tăng điểm cho mỗi triệu chứng trùng khớp
                else:
                    medicine_scores[medicine.id] = {'item': medicine, 'score': 50, 'is_drug': False}
            
            # Tìm trong Drug model
            symptom_drugs = list(Drug.objects.filter(description__icontains=symptom.name))
            
            for drug in symptom_drugs:
                key = f"drug_{drug.id}"
                if key in medicine_scores:
                    medicine_scores[key]['score'] += 50
                else:
                    medicine_scores[key] = {'item': drug, 'score': 50, 'is_drug': True}
        
        # 2. Tìm kiếm thuốc dựa trên từ khóa triệu chứng
        for keyword in symptom_keywords:
            # Tìm trong Medicine model
            keyword_medicines = list(Medicine.objects.filter(description__icontains=keyword))
            
            for medicine in keyword_medicines:
                if medicine.id in medicine_scores:
                    medicine_scores[medicine.id]['score'] += 20
                else:
                    medicine_scores[medicine.id] = {'item': medicine, 'score': 20, 'is_drug': False}
            
            # Tìm trong Drug model
            keyword_drugs = list(Drug.objects.filter(description__icontains=keyword))
            
            for drug in keyword_drugs:
                key = f"drug_{drug.id}"
                if key in medicine_scores:
                    medicine_scores[key]['score'] += 20
                else:
                    medicine_scores[key] = {'item': drug, 'score': 20, 'is_drug': True}
        
        # 3. Phân tích từng thuốc để xác định mức độ phù hợp với các triệu chứng
        for medicine in all_medicines:
            if medicine.id not in medicine_scores:
                # Kiểm tra xem mô tả thuốc có chứa các từ liên quan đến triệu chứng không
                medicine_desc = medicine.description.lower()
                symptom_match_count = 0
                
        for symptom_name in symptom_names:
                    if symptom_name in medicine_desc:
                        symptom_match_count += 1
                
                if symptom_match_count > 0:
                    # Tính điểm dựa trên số lượng triệu chứng trùng khớp
                    score = symptom_match_count * 30
                    medicine_scores[medicine.id] = {'item': medicine, 'score': score, 'is_drug': False}
        
        # Tương tự cho Drug model
        for drug in all_drugs:
            key = f"drug_{drug.id}"
            if key not in medicine_scores:
                drug_desc = drug.description.lower()
                symptom_match_count = 0
                
        for symptom_name in symptom_names:
                    if symptom_name in drug_desc:
                        symptom_match_count += 1
                
                if symptom_match_count > 0:
                    score = symptom_match_count * 30
                    medicine_scores[key] = {'item': drug, 'score': score, 'is_drug': True}
        
        # Chuyển từ điển thành danh sách và sắp xếp theo điểm giảm dần
        scored_items = list(medicine_scores.values())
        scored_items.sort(key=lambda x: x['score'], reverse=True)
        
        # Chỉ lấy các thuốc có điểm > 20
        scored_items = [item for item in scored_items if item['score'] > 20]
        
        # Chuyển các item thành format khuyến nghị
        for item in scored_items:
            if item['is_drug']:
                drug = item['item']
                recommendations.append({
            'name': drug.name,
            'description': drug.description,
            'usage': drug.usage,
            'dosage': drug.dosage,
                    'side_effects': drug.side_effects if hasattr(drug, 'side_effects') else '',
                    'contraindications': drug.contraindications if hasattr(drug, 'contraindications') else '',
            'price': drug.price,
                    'score': item['score'],
            'is_drug': True
                })
            else:
                medicine = item['item']
                recommendations.append({
            'name': medicine.name,
            'description': medicine.description,
            'price': medicine.price,
                    'score': item['score'],
            'is_drug': False
                })
        
        return recommendations

    @database_sync_to_async
    def save_diagnosis_to_db(self, user, symptoms, disease, confidence_score):
        """
        Lưu chẩn đoán vào cơ sở dữ liệu
        """
        try:
            from diagnosis.models import Diagnosis
            
            # Tạo chẩn đoán mới
            diagnosis = Diagnosis.objects.create(
                patient=user,
                disease=disease,
                confidence_score=confidence_score,
                notes=f"Chẩn đoán tự động bởi chatbot với độ tin cậy {confidence_score:.1f}%"
            )
            
            # Thêm các triệu chứng
            diagnosis.symptoms.set(symptoms)
            
            return diagnosis
        except Exception as e:
            print(f"Error saving diagnosis to database: {str(e)}")
            return None

    @database_sync_to_async
    def get_user_from_session(self, session_id):
        """
        Lấy thông tin người dùng từ ID phiên
        """
        from .models import ChatSession
        try:
            session = ChatSession.objects.get(id=session_id)
            return session.user
        except Exception as e:
            print(f"Error getting user from session: {str(e)}")
            return None 
