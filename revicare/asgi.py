"""
ASGI config for revicare project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')

# Setup Django first
django.setup()

# Import websocket URLpatterns after Django setup
from chatbot.routing import websocket_urlpatterns

# Create the ASGI application
application = ProtocolTypeRouter({
    # Django's ASGI application for handling HTTP requests
    "http": get_asgi_application(),
    
    # WebSocket handler with authorization and security
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
