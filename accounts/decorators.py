from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """
    Decorator for views that checks if the user is an admin
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
    
def web_manager_required(view_func):
    """
    Decorator for views that checks if the user is a web manager
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_web_manager:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
    
def admin_or_web_manager_required(view_func):
    """
    Decorator for views that checks if the user is either an admin or a web manager
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_admin or request.user.is_web_manager):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
    
def pharmacist_required(view_func):
    """
    Decorator for views that checks if the user is a pharmacist
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_pharmacist:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def patient_view_only(view_func):
    """
    Decorator for diagnosis views that restricts creation to staff 
    but allows patients to view their own diagnoses
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If it's a GET request, allow it regardless of user type
        if request.method == 'GET':
            return view_func(request, *args, **kwargs)
        
        # If it's a POST request, only allow staff members to proceed
        if request.user.is_authenticated and (request.user.is_admin or 
                                             request.user.is_web_manager):
            return view_func(request, *args, **kwargs)
            
        raise PermissionDenied
    return _wrapped_view

def medicine_view_only(view_func):
    """
    Decorator for medicine views that allows only viewing for patients
    but full access for staff
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If it's a GET request, allow it regardless of user type
        if request.method == 'GET':
            return view_func(request, *args, **kwargs)
        
        # If it's a POST request, only allow staff members to proceed
        if request.user.is_authenticated and (request.user.is_admin or 
                                             request.user.is_web_manager or
                                             request.user.is_pharmacist):
            return view_func(request, *args, **kwargs)
            
        raise PermissionDenied
    return _wrapped_view 