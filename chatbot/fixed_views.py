from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatSession, Message, BotMessage, ChatMemory
from django.utils import timezone
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Max, Q
from .utils import ChatbotDataAccess
from .advanced_data_access import AdvancedChatbotDataAccess

import json
import requests
import os
import re

# Load environment variables
load_dotenv()

# Function to clean markdown formatting
def clean_markdown(text):
    # Remove asterisks for bold/italic formatting
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    # Remove other markdown formatting if needed
    text = re.sub(r'\*\s+', '• ', text)  # Replace "* " with bullet points
    text = re.sub(r'\*{2,}', '', text)  # Remove remaining asterisks
    return text

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCEua2hrKMgAe_8qcawIXwVGNA7dV39BdA")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Check if user is a web manager or admin
def is_manager(user):
    return user.is_web_manager or user.is_staff

# Check if user is a doctor
def is_doctor(user):
    return user.is_doctor 