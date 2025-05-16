try:
    print("Attempting to import consumers module...")
    from chatbot import consumers
    print("Success! Consumers module imported without errors.")
except IndentationError as e:
    print(f"Indentation error found: {e}")
    print(f"Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"Other error found: {type(e).__name__}: {e}") 