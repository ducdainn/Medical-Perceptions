from django import forms
from .models import Medicine, Prescription, Transaction, PrescriptionItem, TransactionItem
from django.forms import inlineformset_factory

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên thuốc',
            'description': 'Mô tả',
            'price': 'Giá (VNĐ)',
        }

class PrescriptionForm(forms.ModelForm):
    patient_name = forms.CharField(label='Tên bệnh nhân', max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(label='Ghi chú', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = Prescription
        fields = ['patient_name', 'status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Trạng thái',
        }

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'quantity', 'unit', 'instructions']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'medicine': 'Thuốc',
            'quantity': 'Số lượng',
            'unit': 'Đơn vị',
            'instructions': 'Hướng dẫn',
        }

PrescriptionItemFormSet = inlineformset_factory(
    Prescription, PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True
)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'prescription', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'prescription': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'transaction_type': 'Loại giao dịch',
            'prescription': 'Đơn thuốc',
            'notes': 'Ghi chú',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prescription'].required = False

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        prescription = cleaned_data.get('prescription')
        
        if transaction_type == 'sale':
            if not prescription:
                self.add_error('prescription', 'Vui lòng chọn đơn thuốc cho giao dịch bán hàng.')
        
        return cleaned_data

class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ['medicine', 'quantity', 'unit', 'unit_price']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
        labels = {
            'medicine': 'Thuốc',
            'quantity': 'Số lượng',
            'unit': 'Đơn vị',
            'unit_price': 'Đơn giá',
        }

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if medicine:
            if not quantity or quantity <= 0:
                self.add_error('quantity', 'Số lượng phải lớn hơn 0.')
            
            if not unit_price or unit_price <= 0:
                self.add_error('unit_price', 'Đơn giá phải lớn hơn 0.')
        
        return cleaned_data

TransactionItemFormSet = inlineformset_factory(
    Transaction, TransactionItem,
    form=TransactionItemForm,
    extra=1,
    can_delete=True,
    validate_min=True,
    min_num=1,
    validate_max=True,
    max_num=10,
    absolute_max=10
)

def get_transaction_item_formset():
    return TransactionItemFormSet 