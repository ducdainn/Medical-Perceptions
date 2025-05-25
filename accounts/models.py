from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    ]

    USER_TYPE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('web_manager', 'Quản lý website'),
        ('pharmacist', 'Dược sĩ'),
        ('patient', 'Bệnh nhân'),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    medical_history = models.TextField(blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return self.get_full_name() or self.username
        
    @property
    def is_admin(self):
        """Check if the user is an admin"""
        return self.user_type == 'admin' or self.is_superuser
        
    @property
    def is_web_manager(self):
        """Check if the user is a web manager"""
        return self.user_type == 'web_manager'
        
    @property
    def is_pharmacist(self):
        """Check if the user is a pharmacist"""
        return self.user_type == 'pharmacist'
        
    @property
    def is_patient(self):
        """Check if the user is a patient"""
        return self.user_type == 'patient'
