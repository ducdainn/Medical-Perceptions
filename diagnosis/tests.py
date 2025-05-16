from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Symptom, Disease, Diagnosis
from django.contrib.messages import get_messages

class DrugRecommendationTests(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test symptoms
        self.symptom1 = Symptom.objects.create(name='đau khớp', description='Đau ở các khớp')
        self.symptom2 = Symptom.objects.create(name='khó vận động', description='Khó khăn khi di chuyển')
        self.symptom3 = Symptom.objects.create(name='yếu cơ', description='Cảm giác yếu ở các cơ')
        
        # Create two similar diseases - this will test the fix for the multiple disease issue
        self.disease1 = Disease.objects.create(
            name='Viêm khớp',
            description='Bệnh viêm khớp thông thường',
            severity='medium'
        )
        
        self.disease2 = Disease.objects.create(
            name='Viêm khớp dạng thấp',
            description='Bệnh viêm khớp dạng thấp mãn tính',
            severity='high'
        )
        
        # Create a client for making requests
        self.client = Client()
        
    def test_save_recommendation_with_multiple_similar_diseases(self):
        """
        Test saving a drug recommendation when there are multiple diseases with similar names
        This should use the first matching disease without errors
        """
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare the data for saving recommendation
        post_data = {
            'symptoms': f'{self.symptom1.id},{self.symptom2.id},{self.symptom3.id}',
            'disease': 'arthritis',  # This will be mapped to 'Viêm khớp' in Vietnamese
            'recommended_drug': 'NSAIDs, Corticosteroids'
        }
        
        # Make the request to save recommendation
        response = self.client.post(reverse('diagnosis:save_recommendation'), post_data)
        
        # Check that the request was successful (302 is redirect status code)
        self.assertEqual(response.status_code, 302)
        
        # Verify no error messages
        messages = list(get_messages(response.wsgi_request))
        has_error = any('error' in str(message).lower() for message in messages)
        self.assertFalse(has_error, "There should be no error messages")
        
        # Verify the diagnosis was created
        self.assertTrue(Diagnosis.objects.exists(), "A diagnosis should have been created")
        
        # Get the created diagnosis
        diagnosis = Diagnosis.objects.first()
        
        # Verify the correct disease was associated (should be the first matching one)
        self.assertEqual(diagnosis.disease.id, self.disease1.id, 
                        "The first matching disease should be used for the diagnosis")
        
        # Verify the symptoms were correctly associated
        self.assertEqual(diagnosis.symptoms.count(), 3)
        self.assertTrue(diagnosis.symptoms.filter(id=self.symptom1.id).exists())
        self.assertTrue(diagnosis.symptoms.filter(id=self.symptom2.id).exists())
        self.assertTrue(diagnosis.symptoms.filter(id=self.symptom3.id).exists())
        
        # Verify the drug recommendation was correctly saved in the notes
        self.assertIn('NSAIDs, Corticosteroids', diagnosis.notes)
