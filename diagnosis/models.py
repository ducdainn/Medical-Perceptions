from django.db import models
from django.conf import settings

class Symptom(models.Model):
    name = models.CharField('Tên triệu chứng', max_length=100)
    description = models.TextField('Mô tả', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Triệu chứng'
        verbose_name_plural = 'Triệu chứng'

    def __str__(self):
        return self.name

class Disease(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Nhẹ'),
        ('medium', 'Trung bình'),
        ('high', 'Nặng'),
    ]

    name = models.CharField('Tên bệnh', max_length=100)
    description = models.TextField('Mô tả')
    symptoms = models.ManyToManyField(Symptom, related_name='diseases', verbose_name='Triệu chứng')
    severity = models.CharField('Mức độ nghiêm trọng', max_length=10, choices=SEVERITY_CHOICES, default='medium')
    treatment_guidelines = models.TextField('Hướng dẫn điều trị', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bệnh'
        verbose_name_plural = 'Bệnh'

    def __str__(self):
        return self.name

class Diagnosis(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnoses', verbose_name='Bệnh nhân')
    symptoms = models.ManyToManyField(Symptom, related_name='diagnoses', verbose_name='Triệu chứng')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='diagnoses', verbose_name='Bệnh được chẩn đoán')
    notes = models.TextField('Ghi chú', blank=True)
    confidence_score = models.FloatField('Độ tin cậy', default=0.0)
    diagnosis_date = models.DateTimeField('Ngày chẩn đoán', auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chẩn đoán'
        verbose_name_plural = 'Chẩn đoán'
        ordering = ['-diagnosis_date']

    def __str__(self):
        return f'Chẩn đoán cho {self.patient.get_full_name()} - {self.disease.name}'
