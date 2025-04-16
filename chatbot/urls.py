from django.urls import path

app_name = 'chatbot'

urlpatterns = [
    path('', lambda request: None, name='chat'),
] 