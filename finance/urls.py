from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("", views.finance_dashboard, name="finance_dashboard"),
    
    # Doanh thu
    path("revenue/", views.revenue_list, name="revenue_list"),
    path("revenue/create/", views.revenue_create, name="revenue_create"),
    path("revenue/<int:pk>/edit/", views.revenue_edit, name="revenue_edit"),
    path("revenue/<int:pk>/delete/", views.revenue_delete, name="revenue_delete"),
    
    # Chi phí
    path("expense/", views.expense_list, name="expense_list"),
    path("expense/create/", views.expense_create, name="expense_create"),
    path("expense/<int:pk>/edit/", views.expense_edit, name="expense_edit"),
    path("expense/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    
    # Báo cáo tài chính
    path("report/", views.report_list, name="report_list"),
    path("report/create/", views.report_create, name="report_create"),
    path("report/<int:pk>/", views.report_detail, name="report_detail"),
    path("report/<int:pk>/edit/", views.report_edit, name="report_edit"),
    path("report/<int:pk>/delete/", views.report_delete, name="report_delete"),
    
    # Temporary fix for transaction_list URL
    path("transaction/", views.transaction_list, name="transaction_list"),
    
    # Temporary fix for bill_list URL
    path("bill/", views.bill_list, name="bill_list"),
    
    # Test URL pattern
    path('test/', views.test_template, name='test'),
] 