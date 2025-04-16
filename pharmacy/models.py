from django.db import models
from django.conf import settings
from diagnosis.models import Disease
from django.contrib.auth import get_user_model

User = get_user_model()

class DrugCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=100)
    description = models.TextField('Mô tả', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Danh mục thuốc'
        verbose_name_plural = 'Danh mục thuốc'

    def __str__(self):
        return self.name

class Drug(models.Model):
    name = models.CharField('Tên thuốc', max_length=100)
    category = models.ForeignKey(DrugCategory, on_delete=models.CASCADE, related_name='drugs', verbose_name='Danh mục')
    description = models.TextField('Mô tả')
    composition = models.TextField('Thành phần')
    usage = models.TextField('Cách dùng')
    dosage = models.TextField('Liều lượng')
    side_effects = models.TextField('Tác dụng phụ', blank=True)
    contraindications = models.TextField('Chống chỉ định', blank=True)
    price = models.DecimalField('Giá', max_digits=10, decimal_places=2)
    stock = models.IntegerField('Số lượng tồn kho', default=0)
    manufacturer = models.CharField('Nhà sản xuất', max_length=100)
    expiry_date = models.DateField('Ngày hết hạn')
    image = models.ImageField('Hình ảnh', upload_to='drugs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thuốc'
        verbose_name_plural = 'Thuốc'

    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default='viên')
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} {self.unit}"

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
    ]

    patient_name = models.CharField(max_length=200, default='Bệnh nhân')
    pharmacist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pharmacist_prescriptions', null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Đơn thuốc #{self.id} - {self.patient_name}"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=50, default='viên')
    instructions = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} {self.unit}"

    @property
    def total_price(self):
        return self.quantity * self.medicine.price if self.medicine else 0

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('sale', 'Bán hàng'),
        ('purchase', 'Nhập hàng'),
        ('return', 'Trả hàng'),
    ]

    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='sale')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} #{self.id}"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=50, default='viên')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} {self.unit}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price
