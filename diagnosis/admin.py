from django.contrib import admin
from .models import Symptom, Disease, Diagnosis

class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')

class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_symptoms', 'severity', 'created_at', 'updated_at')
    list_filter = ('severity', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'treatment_guidelines')
    filter_horizontal = ('symptoms',)
    
    def get_symptoms(self, obj):
        return ", ".join([symptom.name for symptom in obj.symptoms.all()])
    get_symptoms.short_description = 'Triệu chứng'

class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('patient', 'disease', 'get_symptoms', 'diagnosis_date')
    list_filter = ('diagnosis_date', 'created_at', 'updated_at')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'disease__name', 'notes')
    filter_horizontal = ('symptoms',)
    
    def get_symptoms(self, obj):
        return ", ".join([symptom.name for symptom in obj.symptoms.all()])
    get_symptoms.short_description = 'Triệu chứng'

admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(Diagnosis, DiagnosisAdmin)
