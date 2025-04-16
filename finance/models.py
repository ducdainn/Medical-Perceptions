from django.db import models
from django.conf import settings
from pharmacy.models import Prescription
from django.contrib.auth import get_user_model
from django.utils import timezone
from pos.models import Sale
from pharmacy.models import Transaction
from decimal import Decimal

User = get_user_model()

class Bill(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('card', 'Thẻ'),
        ('transfer', 'Chuyển khoản'),
        ('insurance', 'Bảo hiểm'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bills', verbose_name='Bệnh nhân')
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='bill', verbose_name='Đơn thuốc')
    total_amount = models.DecimalField('Tổng tiền', max_digits=10, decimal_places=2)
    insurance_amount = models.DecimalField('Số tiền bảo hiểm chi trả', max_digits=10, decimal_places=2, default=0)
    patient_amount = models.DecimalField('Số tiền bệnh nhân phải trả', max_digits=10, decimal_places=2)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField('Phương thức thanh toán', max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_date = models.DateTimeField('Ngày thanh toán', null=True, blank=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hóa đơn'
        verbose_name_plural = 'Hóa đơn'
        ordering = ['-created_at']

    def __str__(self):
        return f'Hóa đơn {self.id} - {self.patient.get_full_name()}'

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Thu'),
        ('expense', 'Chi'),
    ]

    CATEGORY_CHOICES = [
        ('medicine', 'Thuốc'),
        ('service', 'Dịch vụ'),
        ('salary', 'Lương'),
        ('utility', 'Tiện ích'),
        ('other', 'Khác'),
    ]

    type = models.CharField('Loại giao dịch', max_length=10, choices=TYPE_CHOICES)
    category = models.CharField('Danh mục', max_length=10, choices=CATEGORY_CHOICES)
    amount = models.DecimalField('Số tiền', max_digits=10, decimal_places=2)
    description = models.TextField('Mô tả')
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Hóa đơn')
    transaction_date = models.DateTimeField('Ngày giao dịch')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='transactions', verbose_name='Người tạo')
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Giao dịch'
        verbose_name_plural = 'Giao dịch'
        ordering = ['-transaction_date']

    def __str__(self):
        return f'{self.get_type_display()} - {self.amount} - {self.transaction_date.strftime("%d/%m/%Y")}'

class Revenue(models.Model):
    REVENUE_TYPES = [
        ('sale', 'Bán hàng'),
        ('service', 'Dịch vụ'),
        ('other', 'Khác'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Số tiền')
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPES, default='sale', verbose_name='Loại doanh thu')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    date = models.DateTimeField(default=timezone.now, verbose_name='Ngày ghi nhận')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenues', verbose_name='Người ghi nhận')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='revenues', verbose_name='Hóa đơn bán hàng')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='revenues', verbose_name='Giao dịch')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doanh thu'
        verbose_name_plural = 'Doanh thu'
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_revenue_type_display()} - {self.amount} - {self.date.strftime("%d/%m/%Y")}'

    def clean(self):
        if self.amount <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError('Số tiền phải lớn hơn 0')
        return super().clean()

class Expense(models.Model):
    EXPENSE_TYPES = [
        ('inventory', 'Nhập hàng'),
        ('salary', 'Lương nhân viên'),
        ('rent', 'Tiền thuê'),
        ('utility', 'Tiện ích'),
        ('equipment', 'Thiết bị'),
        ('marketing', 'Marketing'),
        ('other', 'Khác'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Số tiền')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES, default='other', verbose_name='Loại chi phí')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    date = models.DateTimeField(default=timezone.now, verbose_name='Ngày ghi nhận')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses', verbose_name='Người ghi nhận')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses', verbose_name='Giao dịch')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chi phí'
        verbose_name_plural = 'Chi phí'
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_expense_type_display()} - {self.amount} - {self.date.strftime("%d/%m/%Y")}'

    def clean(self):
        if self.amount <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError('Số tiền phải lớn hơn 0')
        return super().clean()

class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('quarterly', 'Hàng quý'),
        ('yearly', 'Hàng năm'),
        ('custom', 'Tùy chỉnh'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='monthly', verbose_name='Loại báo cáo')
    start_date = models.DateTimeField(verbose_name='Ngày bắt đầu')
    end_date = models.DateTimeField(verbose_name='Ngày kết thúc')
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Tổng doanh thu')
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Tổng chi phí')
    net_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Thu nhập ròng')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='Người tạo báo cáo')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian tạo báo cáo')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name = 'Báo cáo tài chính'
        verbose_name_plural = 'Báo cáo tài chính'
        ordering = ['-generated_at']

    def __str__(self):
        return f'Báo cáo {self.get_report_type_display()} từ {self.start_date.strftime("%d/%m/%Y")} đến {self.end_date.strftime("%d/%m/%Y")}'

    def save(self, *args, **kwargs):
        # Tính thu nhập ròng
        self.net_income = self.total_revenue - self.total_expense
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date >= self.end_date:
            from django.core.exceptions import ValidationError
            raise ValidationError('Ngày bắt đầu phải trước ngày kết thúc')
        return super().clean()
