from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Sale, SaleItem, Payment

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'status', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'customer_name': 'Tên khách hàng',
            'status': 'Trạng thái',
            'notes': 'Ghi chú',
        }

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['medicine', 'quantity', 'unit', 'unit_price']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control medicine-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'min': '1'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
        }
        labels = {
            'medicine': 'Thuốc',
            'quantity': 'Số lượng',
            'unit': 'Đơn vị',
            'unit_price': 'Đơn giá',
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError('Số lượng phải lớn hơn 0')
        return quantity
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price and unit_price <= 0:
            raise ValidationError('Đơn giá phải lớn hơn 0')
        return unit_price

# Tạo formset cho SaleItem
SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem, form=SaleItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'amount': 'Số tiền',
            'payment_method': 'Phương thức thanh toán',
            'reference_number': 'Số tham chiếu',
            'notes': 'Ghi chú',
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError('Số tiền phải lớn hơn 0')
        return amount 