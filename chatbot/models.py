from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('closed', 'Đã kết thúc'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions', verbose_name='Người dùng')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField('Thời gian bắt đầu', auto_now_add=True)
    ended_at = models.DateTimeField('Thời gian kết thúc', null=True, blank=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phiên chat'
        verbose_name_plural = 'Phiên chat'
        ordering = ['-started_at']

    def __str__(self):
        return f'Phiên chat với {self.user.get_full_name()} - {self.started_at.strftime("%d/%m/%Y %H:%M")}'

class Message(models.Model):
    TYPE_CHOICES = [
        ('user', 'Người dùng'),
        ('bot', 'Chatbot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='Phiên chat')
    type = models.CharField('Loại tin nhắn', max_length=4, choices=TYPE_CHOICES)
    content = models.TextField('Nội dung')
    sent_at = models.DateTimeField('Thời gian gửi', auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['sent_at']

    def __str__(self):
        return f'{self.get_type_display()} - {self.sent_at.strftime("%H:%M:%S")}'

class BotMessage(models.Model):
    """
    Model for storing AI chatbot messages without a session
    """
    TYPE_CHOICES = [
        ('user', 'Người dùng'),
        ('bot', 'Chatbot'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bot_messages', verbose_name='Người dùng')
    type = models.CharField('Loại tin nhắn', max_length=4, choices=TYPE_CHOICES)
    content = models.TextField('Nội dung')
    sent_at = models.DateTimeField('Thời gian gửi', auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tin nhắn Bot'
        verbose_name_plural = 'Tin nhắn Bot'
        ordering = ['sent_at']

    def __str__(self):
        return f'{self.get_type_display()} - {self.sent_at.strftime("%H:%M:%S")}'

class Intent(models.Model):
    name = models.CharField('Tên ý định', max_length=100)
    description = models.TextField('Mô tả', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ý định'
        verbose_name_plural = 'Ý định'

    def __str__(self):
        return self.name

class TrainingPhrase(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='training_phrases', verbose_name='Ý định')
    text = models.TextField('Câu mẫu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Câu mẫu huấn luyện'
        verbose_name_plural = 'Câu mẫu huấn luyện'

    def __str__(self):
        return f'{self.intent.name} - {self.text[:50]}'

class Response(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='responses', verbose_name='Ý định')
    content = models.TextField('Nội dung phản hồi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phản hồi'
        verbose_name_plural = 'Phản hồi'

    def __str__(self):
        return f'{self.intent.name} - {self.content[:50]}'
