from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .forms import UserRegistrationForm, UserProfileUpdateForm, CustomPasswordChangeForm
from .decorators import admin_required, web_manager_required
from .models import User

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect users to their role-specific dashboard
        user = self.request.user
        if user.is_admin:
            return reverse_lazy('accounts:admin_dashboard')
        elif user.is_web_manager:
            return reverse_lazy('accounts:web_manager_dashboard')
        else:
            return reverse_lazy('accounts:user_dashboard')

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class()
        
        # Debug info
        print("Form fields:", context['form'].fields.keys())
        print("Form is bound:", context['form'].is_bound)
        print("Form data:", context['form'].data if context['form'].is_bound else None)
        
        return context
    
    def form_valid(self, form):
        user = form.save()
        if user:
            # Set default user type to patient
            user.user_type = 'patient'
            user.save()
            
            login(self.request, user)
            messages.success(self.request, 'Đăng ký tài khoản thành công!')
            return redirect('accounts:user_dashboard')
        return redirect('home')

def logout_view(request):
    """Custom logout view that works with both GET and POST requests"""
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    """View for editing user profile information"""
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thông tin đã được cập nhật thành công.')
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    """View for changing user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session so the user doesn't get logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
    
@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.is_admin:
        return redirect('accounts:admin_dashboard')
    elif request.user.is_web_manager:
        return redirect('accounts:web_manager_dashboard')
    else:
        return redirect('accounts:user_dashboard')

@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    return render(request, 'accounts/admin_dashboard.html')

@admin_required
def staff_management(request):
    """Staff management view for admins"""
    # Get list of staff members (all non-patient users)
    staff_list = User.objects.filter(
        user_type__in=['admin', 'web_manager', 'doctor', 'pharmacist']
    ).order_by('-date_joined')
    
    # Handle search and filters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        staff_list = staff_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if role_filter:
        staff_list = staff_list.filter(user_type=role_filter)
    
    if status_filter:
        is_active = status_filter == 'active'
        staff_list = staff_list.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(staff_list, 10)  # Show 10 staff per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'staff_list': page_obj,
        'staff_count': staff_list.count(),
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
    }
    
    return render(request, 'accounts/staff_management.html', context)

@admin_required
def add_staff(request):
    """Add new staff member"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Ensure staff role is one of the allowed types
            if user.user_type not in ['admin', 'web_manager', 'doctor', 'pharmacist']:
                user.user_type = 'web_manager'  # Default to web manager if invalid type
            user.save()
            messages.success(request, f'Nhân viên {user.username} đã được tạo thành công.')
            return redirect('accounts:staff_management')
        else:
            messages.error(request, 'Có lỗi xảy ra khi tạo nhân viên mới. Vui lòng kiểm tra lại thông tin.')
    
    return redirect('accounts:staff_management')

@admin_required
def toggle_staff_status(request, staff_id):
    """Toggle staff active status"""
    try:
        staff = User.objects.get(id=staff_id)
        # Prevent deactivating yourself
        if staff == request.user:
            messages.error(request, 'Bạn không thể vô hiệu hóa tài khoản của chính mình.')
            return redirect('accounts:staff_management')
        
        staff.is_active = not staff.is_active
        staff.save()
        
        status = "kích hoạt" if staff.is_active else "vô hiệu hóa"
        messages.success(request, f'Nhân viên {staff.username} đã được {status} thành công.')
    except User.DoesNotExist:
        messages.error(request, 'Không tìm thấy nhân viên.')
    
    return redirect('accounts:staff_management')

@admin_required
def delete_staff(request, staff_id):
    """Delete staff member"""
    try:
        staff = User.objects.get(id=staff_id)
        # Prevent deleting yourself
        if staff == request.user:
            messages.error(request, 'Bạn không thể xóa tài khoản của chính mình.')
            return redirect('accounts:staff_management')
        
        username = staff.username
        staff.delete()
        messages.success(request, f'Nhân viên {username} đã được xóa thành công.')
    except User.DoesNotExist:
        messages.error(request, 'Không tìm thấy nhân viên.')
    
    return redirect('accounts:staff_management')

@web_manager_required
def web_manager_dashboard(request):
    """Web manager dashboard view"""
    return render(request, 'accounts/web_manager_dashboard.html')

@login_required
def user_dashboard(request):
    """Regular user dashboard view"""
    # Get user information
    user = request.user
    context = {
        'username': user.username,
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone': user.phone_number,
        'address': user.address,
        'date_joined': user.date_joined,
        'profile_complete': bool(user.first_name and user.last_name and user.phone_number)
    }
    return render(request, 'accounts/user_dashboard.html', context)

@admin_required
def user_management(request):
    """User management view for admins"""
    # Get sorting parameter
    sort_by = request.GET.get('sort', '-date_joined')  # Default: newest first
    
    # Get list of all users with sorting
    if sort_by == 'date_joined':
        user_list = User.objects.all().order_by('date_joined')  # Oldest first
    else:
        user_list = User.objects.all().order_by('-date_joined')  # Newest first
    
    # Get user statistics
    user_stats = {
        'total': user_list.count(),
        'admin': user_list.filter(user_type='admin').count(),
        'web_manager': user_list.filter(user_type='web_manager').count(),
        'pharmacist': user_list.filter(user_type='pharmacist').count(),
        'patient': user_list.filter(user_type='patient').count(),
    }
    
    # Handle search and filters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        user_list = user_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if role_filter:
        user_list = user_list.filter(user_type=role_filter)
    
    if status_filter:
        is_active = status_filter == 'active'
        user_list = user_list.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(user_list, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user_list': page_obj,
        'user_count': user_list.count(),
        'user_stats': user_stats,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'accounts/user_management.html', context)

@admin_required
def add_user(request):
    """Add new user"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set user_type from form data
            user_type = form.cleaned_data.get('user_type', 'patient')
            user.user_type = user_type
            user.save()
            
            # Get display name for user type
            user_type_display = dict(form.fields['user_type'].choices).get(user_type, user_type)
            messages.success(request, f'Người dùng {user.username} đã được tạo thành công với vai trò {user_type_display}.')
            return redirect('accounts:user_management')
        else:
            # Add detailed form errors to messages
            for field, errors in form.errors.items():
                field_label = form.fields.get(field, {}).label or field
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')
    
    return redirect('accounts:user_management')

@admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    try:
        user = User.objects.get(id=user_id)
        # Prevent deactivating yourself
        if user == request.user:
            messages.error(request, 'Bạn không thể vô hiệu hóa tài khoản của chính mình.')
            return redirect('accounts:user_management')
        
        user.is_active = not user.is_active
        user.save()
        
        status = "kích hoạt" if user.is_active else "vô hiệu hóa"
        messages.success(request, f'Người dùng {user.username} đã được {status} thành công.')
    except User.DoesNotExist:
        messages.error(request, 'Không tìm thấy người dùng.')
    
    return redirect('accounts:user_management')

@admin_required
def delete_user(request, user_id):
    """Delete user"""
    try:
        user = User.objects.get(id=user_id)
        # Prevent deleting yourself
        if user == request.user:
            messages.error(request, 'Bạn không thể xóa tài khoản của chính mình.')
            return redirect('accounts:user_management')
        
        username = user.username
        user.delete()
        messages.success(request, f'Người dùng {username} đã được xóa thành công.')
    except User.DoesNotExist:
        messages.error(request, 'Không tìm thấy người dùng.')
    
    return redirect('accounts:user_management')

def register(request):
    """Function-based view for user registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        print("POST data received:", request.POST)
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set user type to patient by default for new registrations
            user.user_type = 'patient'
            user.save()
            
            login(request, user)
            messages.success(request, 'Đăng ký tài khoản thành công!')
            return redirect('accounts:user_dashboard')
        else:
            print(f"Form errors: {form.errors}")
            # Show error message
            messages.error(request, 'Đăng ký không thành công. Vui lòng sửa các lỗi bên dưới.')
    else:
        form = UserRegistrationForm()
    
    # Check if we're using the new URL pattern
    if 'register-new' in request.path:
        template_name = 'accounts/register_new.html'
    else:
        template_name = 'accounts/register.html'
    
    # Enable debug mode to see form fields
    context = {
        'form': form,
        'debug': True  # Enable debug info display
    }
    
    return render(request, template_name, context)

def register_test(request):
    """Test view for minimal registration form"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'patient'
            user.save()
            
            login(request, user)
            messages.success(request, 'Đăng ký tài khoản thành công!')
            return redirect('accounts:user_dashboard')
        else:
            print(f"Form errors in test: {form.errors}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register_test.html', {'form': form})
