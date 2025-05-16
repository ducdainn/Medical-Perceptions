import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

# Import settings and update ALLOWED_HOSTS
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver', 'localhost']

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from pharmacy.models import Transaction, Medicine, Prescription
from pos.models import Sale

User = get_user_model()

def create_test_data():
    """Create test data for transaction confirmation"""
    # Create a test user if not exists
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_staff=True
        )
    
    # Create a test medicine if not exists
    try:
        medicine = Medicine.objects.get(name='Test Medicine')
    except Medicine.DoesNotExist:
        medicine = Medicine.objects.create(
            name='Test Medicine',
            description='Test Description',
            price=10.00
        )
    
    # Create a test prescription if not exists
    try:
        prescription = Prescription.objects.get(patient_name='Test Patient')
    except Prescription.DoesNotExist:
        prescription = Prescription.objects.create(
            patient_name='Test Patient',
            pharmacist=user,
            status='pending',
            notes='Test prescription'
        )
    
    # Create a test transaction if not exists
    transactions = Transaction.objects.filter(
        transaction_type='sale',
        sales__isnull=True  # Unconfirmed transaction
    )
    
    if not transactions.exists():
        transaction = Transaction.objects.create(
            prescription=prescription,
            transaction_type='sale',
            notes='Test transaction',
            created_by=user
        )
        print(f"Created test transaction with ID: {transaction.id}")
    else:
        transaction = transactions.first()
        print(f"Using existing transaction with ID: {transaction.id}")
    
    return {
        'user': user,
        'medicine': medicine,
        'prescription': prescription,
        'transaction': transaction
    }

def test_transaction_confirmation():
    """Test the transaction confirmation process"""
    test_data = create_test_data()
    user = test_data['user']
    transaction = test_data['transaction']
    
    # Create a test client
    client = Client()
    
    # Login
    logged_in = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {logged_in}")
    
    # Get the transaction confirmation page
    confirmation_url = reverse('pos:confirm_transaction', kwargs={'transaction_id': transaction.id})
    response = client.get(confirmation_url)
    print(f"Confirmation page status code: {response.status_code}")
    
    # Check if the page contains the transaction ID
    transaction_id_present = f'#{transaction.id}' in response.content.decode()
    print(f"Transaction ID present in confirmation page: {transaction_id_present}")
    
    # Extract CSRF token from the page
    csrf_token = response.context['csrf_token']
    print(f"CSRF token extracted: {csrf_token is not None}")
    
    # Prepare form data for POST
    form_data = {
        'csrfmiddlewaretoken': csrf_token,
        'customer_name': 'Test Customer',
        'status': 'pending',
        'notes': 'Test confirmation',
        
        # FormSet data
        'items-TOTAL_FORMS': '1',
        'items-INITIAL_FORMS': '0',
        'items-MIN_NUM_FORMS': '0',
        'items-MAX_NUM_FORMS': '1000',
        'items-0-medicine': test_data['medicine'].id,
        'items-0-quantity': '2',
        'items-0-unit': 'viên',
        'items-0-unit_price': '10.00',
    }
    
    # Submit the form
    response = client.post(confirmation_url, form_data)
    print(f"Form submission status code: {response.status_code}")
    
    # Check if a sale was created
    sale_exists = Sale.objects.filter(transaction=transaction).exists()
    print(f"Sale created: {sale_exists}")
    
    if not sale_exists:
        print("Failed to create sale. There might be an issue with data transmission.")
    
    return response

if __name__ == "__main__":
    print("Starting transaction confirmation test...")
    response = test_transaction_confirmation()
    print("Test completed.") 