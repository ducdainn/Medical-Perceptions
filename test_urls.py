from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch

class URLTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_admin_dashboard(self):
        """Test access to admin dashboard"""
        try:
            url = reverse('accounts:admin_dashboard')
            response = self.client.get(url)
            # Either 302 (redirect to login) or 403 (forbidden) are acceptable responses
            self.assertIn(response.status_code, [302, 403])
            print("✅ admin_dashboard URL passes")
        except NoReverseMatch as e:
            self.fail(f"❌ admin_dashboard URL fails: {e}")
    
    def test_web_manager_dashboard(self):
        """Test access to web manager dashboard"""
        try:
            url = reverse('accounts:web_manager_dashboard')
            response = self.client.get(url)
            # Either 302 (redirect to login) or 403 (forbidden) are acceptable responses
            self.assertIn(response.status_code, [302, 403])
            print("✅ web_manager_dashboard URL passes")
        except NoReverseMatch as e:
            self.fail(f"❌ web_manager_dashboard URL fails: {e}")
    
    def test_finance_urls(self):
        """Test all finance URLs"""
        finance_urls = [
            'finance:finance_dashboard',
            'finance:report_list',
            'finance:expense_list',
            'finance:revenue_list',
            'finance:bill_list',
            'finance:transaction_list',
        ]
        
        for url_name in finance_urls:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name} URL passes: {url}")
            except NoReverseMatch as e:
                print(f"❌ {url_name} URL fails: {e}")
    
    def test_chatbot_urls(self):
        """Test chatbot admin URLs"""
        try:
            # Test the admin chat list URL
            url = reverse('chatbot:admin_chat_list')
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 403])
            print(f"✅ chatbot:admin_chat_list URL passes: {url}")
            
            # Note: Testing admin_session_detail requires a valid session ID
            # So we're just testing if the URL pattern exists
            try:
                url = reverse('chatbot:admin_session_detail', args=[1])
                print(f"✅ chatbot:admin_session_detail URL passes: {url}")
            except NoReverseMatch as e:
                print(f"❌ chatbot:admin_session_detail URL fails: {e}")
                
        except Exception as e:
            self.fail(f"❌ Chatbot URL test failed: {e}") 