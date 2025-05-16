import re

# Path to the file that needs fixing
file_path = 'chatbot/consumers.py'

# Read the content of the file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# The pattern that needs to be fixed (the line that starts the block after try:)
pattern = r'try:\s+# Parse the JSON message\s+text_data_json = json.loads\(text_data\)'

# Replace with properly indented code
fixed_content = re.sub(pattern, 'try:\n            # Parse the JSON message\n            text_data_json = json.loads(text_data)', content)

# Also fix the indentation of the final await in the except block if needed
pattern2 = r'await self\.send\(text_data=json\.dumps\({'
fixed_content = re.sub(pattern2, '            await self.send(text_data=json.dumps({', fixed_content)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print(f"Fixed indentation in {file_path}") 