import os
import time
import django
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from django.contrib.auth import get_user_model
from pharmacy.models import Transaction, Medicine

User = get_user_model()

def test_transaction_confirmation():
    # Get an unconfirmed transaction from the database
    try:
        transaction = Transaction.objects.filter(
            transaction_type='sale',
            sales__isnull=True
        ).first()
        
        if not transaction:
            print("No unconfirmed transactions found. Please create one first.")
            return
            
        print(f"Found unconfirmed transaction ID: {transaction.id}")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Login first
            print("Logging in...")
            driver.get("http://localhost:8000/accounts/login/")
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "id_username"))
            )
            
            # Fill login form
            driver.find_element(By.ID, "id_username").send_keys("admin")
            driver.find_element(By.ID, "id_password").send_keys("admin")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Go to the transaction list page
            print("Going to transaction list...")
            driver.get("http://localhost:8000/pos/transactions/")
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
            
            # Take a screenshot of the transaction list
            driver.save_screenshot("transaction_list.png")
            print("Saved screenshot of transaction list")
            
            # Click on the confirm button for our transaction
            confirm_button = driver.find_element(By.CSS_SELECTOR, f"a[href='/pos/transactions/confirm/{transaction.id}/']")
            confirm_button.click()
            
            # Wait for the confirmation page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "add-form"))
            )
            
            # Take a screenshot of the confirm page
            driver.save_screenshot("transaction_confirm.png")
            print("Saved screenshot of transaction confirmation page")
            
            # Check if there are any medicines available
            medicines = Medicine.objects.all()
            if not medicines.exists():
                print("No medicines found in the database. Please add some medicines first.")
                return
                
            # Click the "Add product" button
            add_button = driver.find_element(By.ID, "add-form")
            add_button.click()
            
            # Wait for the new form item to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".formset-item:not(.empty-form)"))
            )
            
            # Select a medicine, set quantity and price
            medicine_select = driver.find_element(By.CSS_SELECTOR, "select[name$='-medicine']")
            medicine_select.click()
            
            # Select the first option
            option = driver.find_element(By.CSS_SELECTOR, "select[name$='-medicine'] option:nth-child(2)")
            option.click()
            
            # Set quantity
            quantity_input = driver.find_element(By.CSS_SELECTOR, "input[name$='-quantity']")
            quantity_input.clear()
            quantity_input.send_keys("2")
            
            # Submit the form
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Take a screenshot of the result
            time.sleep(2)  # Wait for redirect
            driver.save_screenshot("confirmation_result.png")
            print("Saved screenshot of confirmation result")
            
            # Check if we were redirected to the sale detail page
            if "sale_detail" in driver.current_url:
                print("Success! Transaction confirmed and redirected to sale detail page.")
            else:
                print("Failed to confirm transaction.")
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error testing transaction confirmation: {str(e)}")

if __name__ == "__main__":
    print("Starting transaction confirmation test...")
    test_transaction_confirmation()
    print("Test completed.") 