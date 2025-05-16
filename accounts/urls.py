from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('register/information/', views.register_information, name='register_information'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('web-manager-dashboard/', views.web_manager_dashboard, name='web_manager_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    # Staff Management URLs
    path('staff-management/', views.staff_management, name='staff_management'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/toggle-status/<int:staff_id>/', views.toggle_staff_status, name='toggle_staff_status'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    # User Management URLs
    path('user-management/', views.user_management, name='user_management'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
] 