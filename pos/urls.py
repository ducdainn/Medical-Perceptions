from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_dashboard, name='pos_dashboard'),
    path('sales/', views.sale_list, name='sale_list'),
    path('transactions/confirm/<int:transaction_id>/', views.confirm_transaction, name='confirm_transaction'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/edit/', views.sale_edit, name='sale_edit'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    path('sales/<int:pk>/update-status/', views.update_sale_status, name='update_sale_status'),
    path('api/medicine-price/', views.medicine_price_api, name='medicine_price_api'),
    path('transactions/', views.transaction_list, name='transaction_list'),
] 