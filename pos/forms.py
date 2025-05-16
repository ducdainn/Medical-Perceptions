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
            'medicine': forms.Select(attrs={'class': 'form-control medicine-select', 'required': 'required'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'min': '1', 'required': 'required'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01', 'min': '0.01', 'required': 'required'}),
        }
        labels = {
            'medicine': 'Thuốc',
            'quantity': 'Số lượng',
            'unit': 'Đơn vị',
            'unit_price': 'Đơn giá',
        }
    
    def clean_medicine(self):
        medicine = self.cleaned_data.get('medicine')
        if not medicine:
            raise ValidationError('Vui lòng chọn thuốc')
        return medicine
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise ValidationError('Vui lòng nhập số lượng')
        if quantity <= 0:
            raise ValidationError('Số lượng phải lớn hơn 0')
        return quantity
    
    def clean_unit(self):
        unit = self.cleaned_data.get('unit')
        if not unit:
            raise ValidationError('Vui lòng nhập đơn vị tính')
        return unit
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is None:
            raise ValidationError('Vui lòng nhập đơn giá')
        if unit_price <= 0:
            raise ValidationError('Đơn giá phải lớn hơn 0')
        return unit_price

# Tạo formset cho SaleItem
SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem, form=SaleItemForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)

# Add additional formset validation
class BaseSaleItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Check if there's at least one valid form that's not deleted
        if not any(form.is_valid() and not self._should_delete_form(form) for form in self.forms):
            raise ValidationError('Vui lòng thêm ít nhất một sản phẩm vào hóa đơn.')
        
        # Validate that all non-deleted forms have valid data
        for form in self.forms:
            if not self._should_delete_form(form):
                # Skip empty forms that will be ignored by the formset
                if not form.has_changed():
                    continue
                
                # Check required fields
                if not form.cleaned_data.get('medicine'):
                    raise ValidationError('Vui lòng chọn thuốc cho tất cả các mặt hàng.')
                
                if not form.cleaned_data.get('quantity') or form.cleaned_data.get('quantity') <= 0:
                    raise ValidationError('Số lượng phải lớn hơn 0 cho tất cả các mặt hàng.')
                
                if not form.cleaned_data.get('unit'):
                    raise ValidationError('Vui lòng nhập đơn vị tính cho tất cả các mặt hàng.')
                
                if not form.cleaned_data.get('unit_price') or form.cleaned_data.get('unit_price') <= 0:
                    raise ValidationError('Đơn giá phải lớn hơn 0 cho tất cả các mặt hàng.')

# Update the formset with custom validation
SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem, form=SaleItemForm,
    formset=BaseSaleItemFormSet,
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