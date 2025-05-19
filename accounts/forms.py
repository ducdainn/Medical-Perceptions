from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên đăng nhập'}),
        help_text="Yêu cầu 150 ký tự hoặc ít hơn. Chỉ được phép dùng chữ cái, số và ký tự @/./+/-/_."
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập địa chỉ email'}),
        help_text="Vui lòng nhập một địa chỉ email hợp lệ."
    )
    
    first_name = forms.CharField(
        label="Tên",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên của bạn'}),
        required=False
    )
    
    last_name = forms.CharField(
        label="Họ",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ của bạn'}),
        required=False
    )
    
    phone_number = forms.CharField(
        label="Số điện thoại",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại của bạn'}),
        required=False
    )
    
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mật khẩu'}),
        help_text="Mật khẩu phải chứa ít nhất 8 ký tự và không được chứa toàn số."
    )
    
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'}),
        help_text="Nhập lại mật khẩu để xác nhận."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 
                 'address', 'date_of_birth', 'gender', 'avatar']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        # Make avatar field not required
        self.fields['avatar'].required = False
        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 