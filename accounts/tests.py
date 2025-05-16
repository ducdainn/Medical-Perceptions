from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from accounts.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class UserPermissionsTest(TestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password='password123',
            user_type='admin'
        )
        
        self.web_manager = User.objects.create_user(
            username='webmanager_test',
            email='webmanager@example.com',
            password='password123',
            user_type='web_manager'
        )
        
        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@example.com',
            password='password123',
            user_type='patient'
        )
        
        self.client = Client()
        
    def test_user_types(self):
        """Test that user types are correctly assigned and can be queried"""
        self.assertEqual(self.admin_user.user_type, 'admin')
        self.assertEqual(self.web_manager.user_type, 'web_manager')
        self.assertEqual(self.regular_user.user_type, 'patient')
        
        # Test the is_admin, is_web_manager, and is_user properties (to be implemented)
        self.assertTrue(self.admin_user.is_admin)
        self.assertTrue(self.web_manager.is_web_manager)
        self.assertTrue(self.regular_user.is_patient)
        
    def test_admin_access(self):
        """Test that admin can access admin-only pages"""
        # Login as admin
        self.client.login(username='admin_test', password='password123')
        
        # This would be a URL that only admins can access
        # Will implement this view in the actual code
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Logout and login as non-admin
        self.client.logout()
        self.client.login(username='user_test', password='password123')
        
        # Non-admin should be redirected or get a 403 Forbidden
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertIn(response.status_code, [302, 403])
    
    def test_web_manager_access(self):
        """Test that web manager can access their pages"""
        # Login as web manager
        self.client.login(username='webmanager_test', password='password123')
        
        # This would be a URL that web managers can access
        response = self.client.get(reverse('accounts:web_manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Logout and login as regular user
        self.client.logout()
        self.client.login(username='user_test', password='password123')
        
        # Regular user should be redirected or get a 403 Forbidden
        response = self.client.get(reverse('accounts:web_manager_dashboard'))
        self.assertIn(response.status_code, [302, 403])
    
    def test_regular_user_access(self):
        """Test that regular user can access their pages"""
        # Login as regular user
        self.client.login(username='user_test', password='password123')
        
        # This would be a URL that regular users can access
        response = self.client.get(reverse('accounts:user_dashboard'))
        self.assertEqual(response.status_code, 200)

class ProfileTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        
        # Set up test client
        self.client = Client()
        
    def test_profile_view(self):
        """Test the profile view"""
        # Login the user
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the profile page
        response = self.client.get(reverse('accounts:profile'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
    def test_edit_profile_view(self):
        """Test the edit profile view"""
        # Login the user
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the edit profile page
        response = self.client.get(reverse('accounts:edit_profile'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/edit_profile.html')
        
        # Test updating the profile
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone_number': '0987654321',
            'address': 'Test Address',
            'date_of_birth': '1990-01-01',
            'gender': 'M'
        }
        
        response = self.client.post(reverse('accounts:edit_profile'), updated_data)
        
        # Check that the user is redirected to the profile page
        self.assertRedirects(response, reverse('accounts:profile'))
        
        # Refresh the user from the database
        self.user.refresh_from_db()
        
        # Check that the user's information was updated
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.phone_number, '0987654321')
        self.assertEqual(self.user.address, 'Test Address')
        self.assertEqual(str(self.user.date_of_birth), '1990-01-01')
        self.assertEqual(self.user.gender, 'M')
        
    def test_change_password_view(self):
        """Test the change password view"""
        # Login the user
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the change password page
        response = self.client.get(reverse('accounts:change_password'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/change_password.html')
        
        # Test changing the password
        password_data = {
            'old_password': 'testpassword123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        }
        
        response = self.client.post(reverse('accounts:change_password'), password_data)
        
        # Check that the user is redirected to the profile page
        self.assertRedirects(response, reverse('accounts:profile'))
        
        # Verify the password was changed by logging in with the new password
        self.client.logout()
        login_successful = self.client.login(username='testuser', password='newpassword456')
        self.assertTrue(login_successful)

class StaffManagementTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password='adminpassword123',
            user_type='admin'
        )
        
        # Create a web manager
        self.web_manager = User.objects.create_user(
            username='webmanager_test',
            email='webmanager@example.com',
            password='password123',
            user_type='web_manager'
        )
        
        # Create a doctor
        self.doctor = User.objects.create_user(
            username='doctor_test',
            email='doctor@example.com',
            password='password123',
            user_type='doctor'
        )
        
        self.client = Client()
    
    def test_staff_management_access(self):
        """Test access to staff management page"""
        # Anonymous user should be redirected to login
        response = self.client.get(reverse('accounts:staff_management'))
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Login as admin
        self.client.login(username='admin_test', password='adminpassword123')
        response = self.client.get(reverse('accounts:staff_management'))
        self.assertEqual(response.status_code, 200)
        
        # Check that staff members are shown
        self.assertContains(response, 'webmanager@example.com')
        self.assertContains(response, 'doctor@example.com')
        
        # Logout and login as web manager (who shouldn't have access)
        self.client.logout()
        self.client.login(username='webmanager_test', password='password123')
        response = self.client.get(reverse('accounts:staff_management'))
        self.assertEqual(response.status_code, 403)  # Should be forbidden
    
    def test_toggle_staff_status(self):
        """Test toggling staff active status"""
        # Login as admin
        self.client.login(username='admin_test', password='adminpassword123')
        
        # Initial state should be active
        self.assertTrue(self.doctor.is_active)
        
        # Deactivate doctor
        response = self.client.get(reverse('accounts:toggle_staff_status', args=[self.doctor.id]))
        self.assertRedirects(response, reverse('accounts:staff_management'))
        
        # Refresh user from db and check status
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_active)
        
        # Activate doctor again
        response = self.client.get(reverse('accounts:toggle_staff_status', args=[self.doctor.id]))
        self.assertRedirects(response, reverse('accounts:staff_management'))
        
        # Refresh user from db and check status
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.is_active)
        
        # Try to deactivate yourself (should fail)
        response = self.client.get(reverse('accounts:toggle_staff_status', args=[self.admin_user.id]))
        self.assertRedirects(response, reverse('accounts:staff_management'))
        
        # Admin should still be active
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
    
    def test_add_staff(self):
        """Test adding a new staff member"""
        # Login as admin
        self.client.login(username='admin_test', password='adminpassword123')
        
        # Initial count
        initial_count = User.objects.count()
        
        # Add a new pharmacist
        new_staff_data = {
            'username': 'new_pharmacist',
            'email': 'pharmacist@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
            'first_name': 'New',
            'last_name': 'Pharmacist',
            'user_type': 'pharmacist',
        }
        
        response = self.client.post(reverse('accounts:add_staff'), new_staff_data)
        self.assertRedirects(response, reverse('accounts:staff_management'))
        
        # Check that user was created
        self.assertEqual(User.objects.count(), initial_count + 1)
        
        # Check that user has correct data
        new_user = User.objects.get(username='new_pharmacist')
        self.assertEqual(new_user.email, 'pharmacist@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'Pharmacist')
        self.assertEqual(new_user.user_type, 'pharmacist')
        self.assertTrue(new_user.is_active)
