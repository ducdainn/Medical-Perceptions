from django import forms
from .models import Diagnosis, Symptom, Disease

class DiagnosisForm(forms.ModelForm):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    disease = forms.ModelChoiceField(
        queryset=Disease.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )
    
    class Meta:
        model = Diagnosis
        fields = ['symptoms', 'disease', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'symptoms':  # Exclude symptoms as it uses CheckboxSelectMultiple
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class SymptomForm(forms.ModelForm):
    class Meta:
        model = Symptom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DiseaseForm(forms.ModelForm):
    SEVERITY_CHOICES = [
        ('low', 'Nhẹ'),
        ('medium', 'Trung bình'),
        ('high', 'Nặng'),
    ]
    
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text='Chọn một hoặc nhiều triệu chứng'
    )
    
    severity = forms.ChoiceField(
        choices=SEVERITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        initial='medium'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
    
    class Meta:
        model = Disease
        fields = ['name', 'description', 'symptoms', 'severity', 'treatment_guidelines']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'treatment_guidelines': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        
    def clean_severity(self):
        severity = self.cleaned_data.get('severity', '').lower()
        if severity not in [choice[0] for choice in self.SEVERITY_CHOICES]:
            raise forms.ValidationError(f"Giá trị '{severity}' không hợp lệ. Vui lòng chọn một trong các giá trị: {', '.join([choice[0] for choice in self.SEVERITY_CHOICES])}")
        return severity 