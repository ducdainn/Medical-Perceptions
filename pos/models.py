from django.db import models
from django.conf import settings
from pharmacy.models import Drug, Medicine, Transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('card', 'Thẻ'),
        ('transfer', 'Chuyển khoản'),
    ]

    customer_name = models.CharField(max_length=200, default='Khách vãng lai')
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def get_total(self):
        return self.total_amount
    
    @property
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Hóa đơn bán hàng'
        verbose_name_plural = 'Hóa đơn bán hàng'
        ordering = ['-created_at']

    def __str__(self):
        return f'Hóa đơn {self.id} - {self.created_at.strftime("%d/%m/%Y")}'

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=50, default='Viên')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def total_price(self):
        return Decimal(str(self.quantity)) * self.unit_price
    
    @property
    def get_total(self):
        return self.total_price

    class Meta:
        verbose_name = 'Chi tiết hóa đơn'
        verbose_name_plural = 'Chi tiết hóa đơn'

    def __str__(self):
        return f'{self.medicine.name if self.medicine else "Không có thuốc"} - {self.quantity}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Shift(models.Model):
    STATUS_CHOICES = [
        ('open', 'Đang mở'),
        ('closed', 'Đã đóng'),
    ]

    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shifts', verbose_name='Thu ngân')
    start_time = models.DateTimeField('Thời gian bắt đầu', auto_now_add=True)
    end_time = models.DateTimeField('Thời gian kết thúc', null=True, blank=True)
    starting_cash = models.DecimalField('Tiền đầu ca', max_digits=10, decimal_places=2)
    ending_cash = models.DecimalField('Tiền cuối ca', max_digits=10, decimal_places=2, null=True, blank=True)
    total_sales = models.DecimalField('Tổng doanh thu', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='open')
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ca làm việc'
        verbose_name_plural = 'Ca làm việc'
        ordering = ['-start_time']

    def __str__(self):
        return f'Ca {self.id} - {self.cashier.get_full_name()} - {self.start_time.strftime("%d/%m/%Y")}'

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Tiền mặt'),
        ('card', 'Thẻ'),
        ('transfer', 'Chuyển khoản'),
    ]
    
    sale = models.ForeignKey(Sale, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(default=timezone.now)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f'Thanh toán {self.payment_method} - {self.amount}'
