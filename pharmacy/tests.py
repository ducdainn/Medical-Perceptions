from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Medicine, Prescription, Transaction, PrescriptionItem, TransactionItem
from decimal import Decimal

User = get_user_model()

class PharmacyAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Tạo dữ liệu test
        self.medicine = Medicine.objects.create(
            name='Test Medicine',
            description='Test Description',
            price=Decimal('10.00')
        )
        
        self.prescription = Prescription.objects.create(
            patient_name='Test Patient',
            pharmacist=self.user,
            status='pending'
        )
        
        self.prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medicine=self.medicine,
            quantity=2,
            unit='viên'
        )
        
        self.transaction = Transaction.objects.create(
            prescription=self.prescription,
            transaction_type='sale',
            created_by=self.user
        )
        
        self.transaction_item = TransactionItem.objects.create(
            transaction=self.transaction,
            medicine=self.medicine,
            quantity=2,
            unit='viên',
            unit_price=Decimal('10.00')
        )

    def test_medicine_list(self):
        response = self.client.get(reverse('pharmacy:medicine_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Medicine')

    def test_medicine_detail(self):
        response = self.client.get(reverse('pharmacy:medicine_detail', args=[self.medicine.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Medicine')
        self.assertContains(response, 'Test Description')

    def test_prescription_list(self):
        response = self.client.get(reverse('pharmacy:prescription_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')

    def test_prescription_detail(self):
        response = self.client.get(reverse('pharmacy:prescription_detail', args=[self.prescription.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')
        self.assertContains(response, 'Test Medicine')

    def test_prescription_items_api(self):
        response = self.client.get(reverse('pharmacy:prescription_items_api', args=[self.prescription.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['medicine'], self.medicine.id)
        self.assertEqual(data[0]['quantity'], 2)
        self.assertEqual(data[0]['unit'], 'viên')
        self.assertEqual(Decimal(str(data[0]['medicine_price'])), self.medicine.price)

    def test_transaction_list(self):
        response = self.client.get(reverse('pharmacy:transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bán hàng')

    def test_transaction_detail(self):
        response = self.client.get(reverse('pharmacy:transaction_detail', args=[self.transaction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Medicine')
        self.assertContains(response, '20.00')  # total price = quantity * unit_price

    def test_create_transaction_from_prescription(self):
        data = {
            'transaction_type': 'sale',
            'prescription': self.prescription.id,
            'notes': 'Test transaction',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '1',
            'items-MAX_NUM_FORMS': '10',
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '2',
            'items-0-unit': 'viên',
            'items-0-unit_price': '10.00',
            'items-0-id': '',
            'items-0-transaction': '',
            'items-0-DELETE': ''
        }
        response = self.client.post(reverse('pharmacy:transaction_create'), data)
        
        # In ra nội dung response để debug
        print("Response content:", response.content.decode())
        print("Response status code:", response.status_code)
        
        self.assertEqual(response.status_code, 302)  # redirect after success
        
        # Kiểm tra transaction mới được tạo
        new_transaction = Transaction.objects.latest('id')
        self.assertEqual(new_transaction.prescription, self.prescription)
        self.assertEqual(new_transaction.transaction_type, 'sale')
        self.assertEqual(new_transaction.total_amount, Decimal('20.00'))
        
        # Kiểm tra trạng thái đơn thuốc đã được cập nhật
        self.prescription.refresh_from_db()
        self.assertEqual(self.prescription.status, 'completed')

    def test_create_purchase_transaction_not_update_prescription_status(self):
        data = {
            'transaction_type': 'purchase',  # Giao dịch nhập hàng
            'prescription': '',  # Không cần đơn thuốc
            'notes': 'Test purchase',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '1',
            'items-MAX_NUM_FORMS': '10',
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '2',
            'items-0-unit': 'viên',
            'items-0-unit_price': '10.00',
            'items-0-id': '',
            'items-0-transaction': '',
            'items-0-DELETE': ''
        }
        response = self.client.post(reverse('pharmacy:transaction_create'), data)
        
        # In ra nội dung response để debug
        print("Response content:", response.content.decode())
        print("Response status code:", response.status_code)
        
        self.assertEqual(response.status_code, 302)  # redirect after success
        
        # Kiểm tra trạng thái đơn thuốc không thay đổi
        self.prescription.refresh_from_db()
        self.assertEqual(self.prescription.status, 'pending')
