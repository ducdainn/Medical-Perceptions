import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sys
import random
import string

def random_string(length=6):
    """Generate a random string of fixed length"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class PrescriptionWorkflowTest(unittest.TestCase):
    """Test the prescription workflow from drug recommendation to prescription request"""
    
    def setUp(self):
        """Set up test environment"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        # Uncomment the line below to run headless (no browser UI)
        # chrome_options.add_argument("--headless")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = "http://localhost:8000"
        
        # Create a random username and password for testing
        self.username = f"test_user_{random_string()}"
        self.password = "Test@123456"
        self.email = f"{self.username}@example.com"
        
    def tearDown(self):
        """Clean up after test"""
        self.driver.quit()
        
    def test_prescription_workflow(self):
        """Test the complete prescription workflow"""
        # 1. Register a test user
        self.register_user()
        
        # 2. Navigate to drug recommendation page
        self.driver.get(f"{self.base_url}/diagnosis/recommend-drug/")
        
        # 3. Fill the recommendation form
        self.fill_recommendation_form()
        
        # 4. Request a prescription
        self.request_prescription()
        
        # 5. Verify request was created
        self.verify_prescription_request()
        
    def register_user(self):
        """Register a new test user"""
        self.driver.get(f"{self.base_url}/accounts/register/")
        print(f"Registering user: {self.username}")
        
        # Fill in the registration form
        self.driver.find_element(By.ID, "id_username").send_keys(self.username)
        self.driver.find_element(By.ID, "id_email").send_keys(self.email)
        self.driver.find_element(By.ID, "id_first_name").send_keys("Test")
        self.driver.find_element(By.ID, "id_last_name").send_keys("User")
        self.driver.find_element(By.ID, "id_phone_number").send_keys("1234567890")
        self.driver.find_element(By.ID, "id_password1").send_keys(self.password)
        self.driver.find_element(By.ID, "id_password2").send_keys(self.password)
        
        # Check the terms checkbox
        terms_checkbox = self.driver.find_element(By.ID, "agreeTerms")
        self.driver.execute_script("arguments[0].click();", terms_checkbox)
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Wait for successful registration (redirect to dashboard)
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard/")
        )
        print("User registered successfully")
        
    def fill_recommendation_form(self):
        """Fill the drug recommendation form"""
        print("Filling drug recommendation form")
        
        # Select age group (30-45)
        age_radio = self.driver.find_element(By.CSS_SELECTOR, "input[name='age'][value='30-45']")
        self.driver.execute_script("arguments[0].click();", age_radio)
        
        # Select gender (male)
        gender_radio = self.driver.find_element(By.CSS_SELECTOR, "input[name='gender'][value='male']")
        self.driver.execute_script("arguments[0].click();", gender_radio)
        
        # Select severity (medium)
        severity_radio = self.driver.find_element(By.CSS_SELECTOR, "input[name='severity'][value='medium']")
        self.driver.execute_script("arguments[0].click();", severity_radio)
        
        # Select symptoms (anxiety-related symptoms)
        # Find symptom checkboxes related to anxiety
        symptoms = ["lo âu", "thay đổi tâm trạng", "mất ngủ"]
        for symptom in symptoms:
            try:
                # Try to find an exact match
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                for checkbox in checkboxes:
                    label = self.driver.find_element(By.XPATH, f"//label[@for='{checkbox.get_attribute('id')}']")
                    if symptom.lower() in label.text.lower():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print(f"Selected symptom: {label.text}")
                        break
            except Exception as e:
                print(f"Could not select symptom '{symptom}': {e}")
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Wait for the results page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".card-header.bg-success"))
        )
        print("Drug recommendation received")
        
    def request_prescription(self):
        """Request a prescription based on recommendation"""
        print("Requesting prescription")
        
        # Find and click the prescription request button
        try:
            # Wait for the button to be available
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "requestPrescriptionBtn"))
            )
            
            # Click the button
            request_btn = self.driver.find_element(By.ID, "requestPrescriptionBtn")
            self.driver.execute_script("arguments[0].click();", request_btn)
            print("Clicked prescription request button")
            
            # Wait for redirect to prescription request detail page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/prescription-requests/")
            )
            print("Redirected to prescription request detail page")
            
        except Exception as e:
            self.fail(f"Failed to request prescription: {e}")
    
    def verify_prescription_request(self):
        """Verify that the prescription request was created successfully"""
        print("Verifying prescription request creation")
        
        try:
            # Check if we're on the prescription request page
            self.assertTrue("/prescription-requests/" in self.driver.current_url, 
                           "Not on prescription request detail page")
            
            # Check for success message
            success_messages = self.driver.find_elements(By.CSS_SELECTOR, ".alert-success")
            has_success = any("thành công" in msg.text for msg in success_messages)
            self.assertTrue(has_success or len(success_messages) > 0, 
                           "No success message found")
            
            # Check for pending status
            status_badge = self.driver.find_element(By.CSS_SELECTOR, ".badge.bg-warning")
            self.assertTrue("Chờ xử lý" in status_badge.text, 
                           f"Unexpected status: {status_badge.text}")
            
            print("Prescription request verified successfully")
            
        except Exception as e:
            self.fail(f"Verification failed: {e}")

if __name__ == "__main__":
    # Run the test
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n✅ All tests completed!") 