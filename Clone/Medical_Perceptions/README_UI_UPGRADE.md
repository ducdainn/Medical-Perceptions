# ReViCARE UI Upgrade - Authentication Pages

This upgrade focuses on improving the user interface for the authentication pages (login and registration) of the ReViCARE medical management system.

## Changes Made

1. **Modernized UI Design**:
   - Added visually appealing login and registration pages
   - Implemented responsive design for all device sizes
   - Added animations and transitions for better user experience

2. **Streamlined Registration Process**:
   - Combined two-step registration into a single step
   - Added better form validation and error handling
   - Improved user experience with clearer instructions

3. **Enhanced Login Experience**:
   - Added "Remember Me" functionality
   - Improved error messaging
   - Added social media login UI (functionality can be implemented in the future)

4. **Automated Testing**:
   - Added Selenium-based testing scripts to verify functionality
   - Tests cover registration and login flows

## Requirements

- Python 3.8+
- Django 5.0.2+
- Selenium 4.17.2+ (for tests)
- Chrome browser (for tests)

## Running the Server

### Windows

1. Double-click the `run_server.bat` file, or
2. Open a command prompt and run:
   ```
   .venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver
   ```

### macOS/Linux

1. Open a terminal and run:
   ```
   chmod +x run_server.sh
   ./run_server.sh
   ```
   
   or
   
   ```
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py runserver
   ```

## Running the Tests

### Windows

1. Double-click the `run_tests.bat` file, or
2. Open a command prompt and run:
   ```
   .venv\Scripts\activate
   pip install -r requirements.txt
   python test_login_register.py
   ```

### macOS/Linux

1. Open a terminal and run:
   ```
   chmod +x run_tests.sh
   ./run_tests.sh
   ```
   
   or
   
   ```
   source .venv/bin/activate
   pip install -r requirements.txt
   python test_login_register.py
   ```

## Testing Credentials

For manual testing, you can use these credentials:

**Username**: admin  
**Password**: admin123

## Notes

- Social login functionality is not implemented yet, only the UI is in place
- If you encounter any issues with the tests, make sure the server is running and accessible at http://localhost:8000 