from django.urls import path
from . import views

app_name = 'diagnosis'

urlpatterns = [
    path('', views.diagnosis_list, name='list'),
    path('create/', views.diagnosis_create, name='create'),
    path('<int:pk>/', views.diagnosis_detail, name='detail'),
    path('symptoms/', views.symptom_list, name='symptoms'),
    path('symptoms/create/', views.symptom_create, name='symptom_create'),
    path('symptoms/<int:pk>/edit/', views.symptom_edit, name='symptom_edit'),
    path('diseases/', views.disease_list, name='diseases'),
    path('diseases/create/', views.disease_create, name='disease_create'),
    path('diseases/<int:pk>/edit/', views.disease_edit, name='disease_edit'),
    path('recommend-drug/', views.recommend_drug, name='recommend_drug'),
    path('save-recommendation/', views.save_recommendation, name='save_recommendation'),
    path('test-prescription-button/', views.test_prescription_button, name='test_prescription_button'),
] 