import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatSession, Message, Intent, Response
import random

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()
            self.session = await self.create_chat_session()

    async def disconnect(self, close_code):
        if hasattr(self, 'session'):
            await self.end_chat_session()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Lưu tin nhắn của người dùng
        await self.save_message('user', message)

        # Xử lý tin nhắn và tạo phản hồi
        response = await self.process_message(message)

        # Lưu và gửi phản hồi
        await self.save_message('bot', response)
        await self.send(text_data=json.dumps({
            'message': response,
            'type': 'bot'
        }))

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

    async def process_message(self, message):
        # TODO: Implement NLP processing here
        # Tạm thời trả về câu trả lời mặc định
        return await self.get_response('default') 