import os
import django
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

class TransactionCompletionTest(TestCase):
    """Test class for transaction completion functionality"""
    
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
        
        # Create a test sale from the transaction
        self.sale = Sale.objects.create(
            customer_name="Test Customer",
            cashier=self.user,
            transaction=self.transaction,
            status="pending",
            notes="Test sale confirmation"
        )
        
        # Create a test sale item
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            medicine=self.medicine,
            quantity=2,
            unit="viên",
            unit_price=10.00
        )
        
        print(f"Test setup complete. Transaction ID: {self.transaction.id}, Sale ID: {self.sale.id}")
    
    def test_sale_completion(self):
        """Test completing a sale after transaction confirmation"""
        # Login
        login_success = self.client.login(username=self.user.username, password=self.password)
        print(f"Login successful: {login_success}")
        
        # Get the URL for sale completion
        url = reverse('pos:sale_edit', kwargs={'pk': self.sale.id})
        
        # Prepare form data for completion
        form_data = {
            'status': 'completed',
        }
        
        # Send POST request
        response = self.client.post(url, form_data, follow=False)
        print(f"POST response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            print(f"Redirected to: {response.url}")
        
        # Refresh sale from database
        self.sale.refresh_from_db()
        print(f"Sale status after update: {self.sale.status}")
        
        # Test assertions
        self.assertEqual(self.sale.status, 'completed', "Sale status was not updated to 'completed'")
        print("Sale completion test passed!")

def run_tests():
    """Run the transaction completion tests"""
    test_case = TransactionCompletionTest()
    test_case.setUp()
    
    print("\nRunning sale completion test...")
    try:
        test_case.test_sale_completion()
        print("\nAll tests passed! Transaction completion is working correctly.")
        return True
    except AssertionError as e:
        print(f"\nTest failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting transaction completion tests...")
    success = run_tests()
    
    if not success:
        print("\nFIXING: We need to fix the transaction completion process.") 