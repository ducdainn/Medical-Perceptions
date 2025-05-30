from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacy_dashboard, name='dashboard'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/create/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('inventory/', views.inventory_management, name='inventory'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/edit/', views.prescription_edit, name='prescription_edit'),
    path('prescriptions/<int:pk>/delete/', views.prescription_delete, name='prescription_delete'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('api/prescriptions/<int:pk>/items/', views.prescription_items_api, name='prescription_items_api'),
    
    # Các URL mới cho yêu cầu kê đơn thuốc
    path('prescription-requests/', views.prescription_request_list, name='prescription_request_list'),
    path('prescription-requests/create/', views.request_prescription, name='request_prescription'),
    path('prescription-requests/<int:pk>/', views.prescription_request_detail, name='prescription_request_detail'),
    path('prescription-requests/<int:pk>/approve/', views.approve_prescription_request, name='approve_prescription_request'),
    path('prescription-requests/<int:pk>/reject/', views.reject_prescription_request, name='reject_prescription_request'),
    path('prescription-requests/<int:pk>/delete/', views.delete_prescription_request, name='delete_prescription_request'),
    path('pharmacist-requests/', views.pharmacist_prescription_requests, name='pharmacist_requests'),
    path('prescription-requests/help/', views.prescription_request_help, name='prescription_request_help'),
] 