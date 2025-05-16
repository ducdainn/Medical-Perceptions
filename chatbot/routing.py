from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Simple pattern to match both with and without trailing slash
    re_path(r'^ws/chat/?$', consumers.ChatConsumer.as_asgi()),
] 