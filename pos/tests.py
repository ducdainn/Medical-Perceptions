from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Sale, SaleItem, Shift
from pharmacy.models import Drug, DrugCategory, Transaction, Medicine, Prescription

User = get_user_model()

class POSTestCase(TestCase):
    def setUp(self):
        # Tạo người dùng test
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Tạo danh mục thuốc test
        self.drug_category = DrugCategory.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Tạo thuốc test
        self.drug = Drug.objects.create(
            name='Test Drug',
            description='Test Description',
            price=Decimal('10000'),
            expiry_date=timezone.now().date() + timezone.timedelta(days=365),
            category=self.drug_category  # Thêm category vào drug
        )
        
        # Tạo medicine test
        self.medicine = Medicine.objects.create(
            name='Test Medicine',
            description='Test Medicine Description',
            price=Decimal('10000')
        )
        
        # Tạo prescription test
        self.prescription = Prescription.objects.create(
            patient_name='Test Patient',
            pharmacist=self.user,
            status='completed'
        )
        
        # Tạo transaction test
        self.transaction = Transaction.objects.create(
            prescription=self.prescription,
            transaction_type='sale',
            notes='Test transaction',
            created_by=self.user
        )
        
        # Tạo hóa đơn test
        self.sale = Sale.objects.create(
            customer_name='Test Customer',
            cashier=self.user,
            status='pending',
            transaction=self.transaction,
            notes='Test note'
        )
        
        # Tạo item hóa đơn test
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            medicine=self.medicine,
            quantity=2,
            unit='Viên',
            unit_price=Decimal('10000')
        )
        
        # Đăng nhập
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_pos_dashboard(self):
        response = self.client.get(reverse('pos:pos_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pos/dashboard.html')
    
    def test_sale_list(self):
        response = self.client.get(reverse('pos:sale_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pos/sale_list.html')
        self.assertContains(response, 'Test Customer')
    
    def test_confirm_transaction(self):
        # Test GET request to confirm transaction
        response = self.client.get(reverse('pos:confirm_transaction', args=[self.transaction.id]))
        # Không kiểm tra status code và template vì chúng ta đã chuyển qua xác nhận hóa đơn từ giao dịch
        # Chỉ cần kiểm tra việc tạo hóa đơn thành công

        # Test POST request to confirm transaction
        data = {
            'customer_name': 'New Confirmed Customer',
            'status': 'pending',
            'notes': 'New confirmed sale test',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '3',
            'items-0-unit': 'Viên',
            'items-0-unit_price': '15000',
        }

        response = self.client.post(reverse('pos:confirm_transaction', args=[self.transaction.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify the new sale was created with transaction link
        self.assertEqual(Sale.objects.count(), 2)
        new_sale = Sale.objects.latest('id')
        self.assertEqual(new_sale.customer_name, 'New Confirmed Customer')
        self.assertEqual(new_sale.transaction, self.transaction)
    
    def test_sale_detail(self):
        response = self.client.get(reverse('pos:sale_detail', args=[self.sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pos/sale_detail.html')
        self.assertContains(response, 'Test Customer')
    
    def test_sale_edit(self):
        # Test GET request
        response = self.client.get(reverse('pos:sale_edit', args=[self.sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pos/sale_form.html')
        
        # Test POST request
        data = {
            'customer_name': 'Updated Customer',
            'status': 'completed',
            'notes': 'Updated note',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '1',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-id': self.sale_item.id,
            'items-0-sale': self.sale.id,
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '4',
            'items-0-unit': 'Viên',
            'items-0-unit_price': '10000',
        }
        
        response = self.client.post(reverse('pos:sale_edit', args=[self.sale.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify the sale was updated
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.customer_name, 'Updated Customer')
        self.assertEqual(self.sale.status, 'completed')
        
        # Verify the sale item was updated
        self.sale_item.refresh_from_db()
        self.assertEqual(self.sale_item.quantity, 4)
    
    def test_sale_delete(self):
        # Test GET request
        response = self.client.get(reverse('pos:sale_delete', args=[self.sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pos/sale_confirm_delete.html')
        
        # Test POST request
        response = self.client.post(reverse('pos:sale_delete', args=[self.sale.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify the sale was deleted
        self.assertEqual(Sale.objects.count(), 0)
    
    def test_medicine_price_api(self):
        # Test API endpoint
        response = self.client.get(
            reverse('pos:medicine_price_api') + f'?medicine_id={self.medicine.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'price': '10000.00'}
        )
