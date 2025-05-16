from django.shortcuts import render, redirect
from django.urls import reverse

def home(request):
    # If user is authenticated, redirect to their dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    return render(request, 'home.html', {}) 