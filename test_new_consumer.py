import sys
import os

# Add a new import path for testing
sys.path.insert(0, os.path.abspath('.'))

try:
    print("Setting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
    
    # We only want to check the syntax, not actually run Django code
    # So we'll just check if the file has proper indentation
    
    with open("chatbot/consumers_new.py", "r", encoding="utf-8") as f:
        source_code = f.read()
    
    # If this compiles without IndentationError, it's good
    compile(source_code, "chatbot/consumers_new.py", "exec")
    print("Success! New consumers_new.py file has correct indentation.")
    
    print("Now copying to consumers.py...")
    # Copy the fixed file to replace the original
    with open("chatbot/consumers_new.py", "r", encoding="utf-8") as source:
        with open("chatbot/consumers.py", "w", encoding="utf-8") as destination:
            destination.write(source.read())
    
    print("consumers.py has been replaced with the fixed version.")
except IndentationError as e:
    print(f"Indentation error found: {e}")
    print(f"Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"Other error found: {type(e).__name__}: {e}") 