import os
import django
import json
import uuid
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver', 'localhost']

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from pharmacy.models import Transaction, Medicine, Prescription
from pos.models import Sale, SaleItem

User = get_user_model()

def get_test_user():
    """Get or create a test user with a unique username/email"""
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            password="testpass123",
            email=email,
            is_staff=True
        )
    
    return user, "testpass123"

class TransactionConfirmationTest(TestCase):
    """Test class for transaction confirmation functionality"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        
        # Create test user
        self.user, self.password = get_test_user()
        
        # Create test medicine
        self.medicine = Medicine.objects.create(
            name=f"Test Medicine {uuid.uuid4().hex[:6]}",
            description="Test Description",
            price=10.00
        )
        
        # Create test prescription
        self.prescription = Prescription.objects.create(
            patient_name=f"Test Patient {uuid.uuid4().hex[:6]}",
            pharmacist=self.user,
            status="pending",
            notes="Test prescription"
        )
        
        # Create test transaction
        self.transaction = Transaction.objects.create(
            prescription=self.prescription,
            transaction_type="sale",
            notes="Test transaction",
            created_by=self.user
        )
        
        print(f"Test setup complete. Transaction ID: {self.transaction.id}")
    
    def test_transaction_confirmation_get(self):
        """Test GET request to transaction confirmation view"""
        # Login
        self.client.login(username=self.user.username, password=self.password)
        
        # Get the URL for transaction confirmation
        url = reverse('pos:confirm_transaction', kwargs={'transaction_id': self.transaction.id})
        
        # Send GET request
        response = self.client.get(url)
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check if transaction info is in the response
        self.assertContains(response, f'#{self.transaction.id}')
        self.assertContains(response, "Test transaction")
        
        print("GET request test passed!")
    
    def test_transaction_confirmation_post(self):
        """Test POST request to transaction confirmation view"""
        # Login
        login_success = self.client.login(username=self.user.username, password=self.password)
        print(f"Login successful: {login_success}")
        
        # Get the URL for transaction confirmation
        url = reverse('pos:confirm_transaction', kwargs={'transaction_id': self.transaction.id})
        
        # Get the confirmation page to get CSRF token
        response = self.client.get(url)
        
        # Prepare form data
        form_data = {
            'customer_name': 'Test Customer',
            'status': 'pending',
            'notes': 'Test confirmation',
            
            # FormSet data
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '2',
            'items-0-unit': 'viên',
            'items-0-unit_price': '10.00',
        }
        
        # First try without following redirects
        response = self.client.post(url, form_data, follow=False)
        print(f"POST response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            print(f"Redirected to: {response.url}")
            
            # Now try with following redirects
            try:
                full_response = self.client.post(url, form_data, follow=True)
                print(f"Full response followed, status: {full_response.status_code}")
                if full_response.status_code == 200:
                    print("Successfully followed redirect to the detail page!")
            except Exception as e:
                print(f"Error following redirect: {str(e)}")
        
        # Check if a sale was created
        sale_exists = Sale.objects.filter(transaction=self.transaction).exists()
        print(f"Sale created: {sale_exists}")
        
        if sale_exists:
            sale = Sale.objects.get(transaction=self.transaction)
            print(f"Sale ID: {sale.id}, items count: {sale.items.count()}")
            
            # Check if sale items were created correctly
            for item in sale.items.all():
                print(f"Sale Item: {item.medicine.name}, quantity: {item.quantity}, unit: {item.unit}, price: {item.unit_price}")
        
        # Test assertions
        self.assertTrue(sale_exists, "No sale was created from the transaction")
        
        if sale_exists:
            sale = Sale.objects.get(transaction=self.transaction)
            self.assertEqual(sale.items.count(), 1, "Sale should have 1 item")
            self.assertEqual(sale.customer_name, "Test Customer", "Customer name doesn't match")
            
            # Check sale item details
            sale_item = sale.items.first()
            self.assertEqual(sale_item.medicine.id, self.medicine.id, "Medicine doesn't match")
            self.assertEqual(sale_item.quantity, 2, "Quantity doesn't match")
            self.assertEqual(sale_item.unit, "viên", "Unit doesn't match")
            self.assertEqual(float(sale_item.unit_price), 10.00, "Unit price doesn't match")
        
        print("POST request test passed!")

def run_tests():
    """Run the transaction confirmation tests"""
    test_case = TransactionConfirmationTest()
    test_case.setUp()
    
    print("\nRunning GET request test...")
    test_case.test_transaction_confirmation_get()
    
    print("\nRunning POST request test...")
    try:
        test_case.test_transaction_confirmation_post()
        print("\nAll tests passed! Transaction confirmation is working correctly.")
    except AssertionError as e:
        print(f"\nTest failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting transaction confirmation tests...")
    success = run_tests()
    
    if not success:
        print("\nFIXING: We need to fix the transaction confirmation process.") 