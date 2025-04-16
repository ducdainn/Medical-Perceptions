from django import forms
from .models import Revenue, Expense, FinancialReport
from django.core.exceptions import ValidationError

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['revenue_type', 'amount', 'date', 'description', 'sale', 'transaction']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sale'].required = False
        self.fields['transaction'].required = False
        # Chuyển đổi định dạng ngày tháng nếu instance đã tồn tại
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['date'].initial = kwargs['instance'].date.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        
        if amount and amount <= 0:
            raise ValidationError('Số tiền phải lớn hơn 0')
            
        return cleaned_data

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'date', 'description', 'transaction']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction'].required = False
        # Chuyển đổi định dạng ngày tháng nếu instance đã tồn tại
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['date'].initial = kwargs['instance'].date.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        
        if amount and amount <= 0:
            raise ValidationError('Số tiền phải lớn hơn 0')
            
        return cleaned_data

class FinancialReportForm(forms.ModelForm):
    class Meta:
        model = FinancialReport
        fields = ['report_type', 'start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chuyển đổi định dạng ngày tháng nếu instance đã tồn tại
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['start_date'].initial = kwargs['instance'].start_date.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_date'].initial = kwargs['instance'].end_date.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError('Ngày bắt đầu phải trước ngày kết thúc')
            
        return cleaned_data 