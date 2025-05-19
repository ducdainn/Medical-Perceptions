import os
import random
import string
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def random_username(prefix="test_user_", length=6):
    """Generate a random username"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}{random_string}"

def random_email(username=None):
    """Generate a random email"""
    if not username:
        username = random_username(prefix="", length=8)
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    domain = random.choice(domains)
    return f"{username}@{domain}"

def run_tests(base_url):
    # Create Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Uncomment the line below to run headless (no browser UI)
    # chrome_options.add_argument("--headless")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Test variables
        username = random_username()
        email = random_email(username)
        password = "TestPassword123"
        first_name = "Test"
        last_name = "User"
        phone_number = "0123456789"
        
        print(f"Testing with username: {username}, email: {email}")
        
        # Registration test
        print("\n--- Testing Registration ---")
        test_registration(driver, base_url, username, email, password, first_name, last_name, phone_number)
        
        # Login test
        print("\n--- Testing Login ---")
        test_login(driver, base_url, username, password)
        
        # Print success
        print("\n✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    finally:
        # Close the browser
        driver.quit()

def test_registration(driver, base_url, username, email, password, first_name, last_name, phone_number):
    """Test the registration process"""
    # Navigate to the registration page
    driver.get(f"{base_url}/accounts/register/")
    print("Navigated to registration page")
    
    # Fill in the form
    driver.find_element(By.ID, "id_username").send_keys(username)
    driver.find_element(By.ID, "id_email").send_keys(email)
    driver.find_element(By.ID, "id_first_name").send_keys(first_name)
    driver.find_element(By.ID, "id_last_name").send_keys(last_name)
    driver.find_element(By.ID, "id_phone_number").send_keys(phone_number)
    driver.find_element(By.ID, "id_password1").send_keys(password)
    driver.find_element(By.ID, "id_password2").send_keys(password)
    print("Filled in the registration form")
    
    # Check the terms checkbox
    terms_checkbox = driver.find_element(By.ID, "agreeTerms")
    driver.execute_script("arguments[0].click();", terms_checkbox)
    print("Checked the terms and conditions")
    
    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].click();", submit_button)
    print("Submitted the registration form")
    
    # Wait for redirect to dashboard
    try:
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard/")
        )
        print("Successfully registered and redirected to dashboard")
    except TimeoutException:
        # Check if there are any error messages
        try:
            error_messages = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .text-danger")
            errors = [error.text for error in error_messages if error.text.strip()]
            if errors:
                print(f"Registration failed with errors: {', '.join(errors)}")
                raise Exception(f"Registration failed with errors: {', '.join(errors)}")
        except NoSuchElementException:
            pass
        
        raise Exception("Failed to redirect to dashboard after registration")

def test_login(driver, base_url, username, password):
    """Test the login process"""
    # Navigate to the login page
    driver.get(f"{base_url}/accounts/logout/")  # Logout first
    time.sleep(1)
    driver.get(f"{base_url}/accounts/login/")
    print("Navigated to login page")
    
    # Fill in the form
    driver.find_element(By.ID, "id_username").send_keys(username)
    driver.find_element(By.ID, "id_password").send_keys(password)
    print("Filled in the login form")
    
    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].click();", submit_button)
    print("Submitted the login form")
    
    # Wait for redirect to dashboard
    try:
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard/")
        )
        print("Successfully logged in and redirected to dashboard")
    except TimeoutException:
        # Check if there are any error messages
        try:
            error_messages = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .text-danger")
            errors = [error.text for error in error_messages if error.text.strip()]
            if errors:
                print(f"Login failed with errors: {', '.join(errors)}")
                raise Exception(f"Login failed with errors: {', '.join(errors)}")
        except NoSuchElementException:
            pass
        
        raise Exception("Failed to redirect to dashboard after login")

if __name__ == "__main__":
    # Check for base URL argument
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
        
    # Run the tests
    run_tests(base_url) 