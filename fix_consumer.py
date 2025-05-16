import re

# Path to file
file_path = 'chatbot/consumers.py'

# Create a backup
with open(file_path, 'r', encoding='utf-8') as file:
    original_content = file.read()

with open(f"{file_path}.bak", 'w', encoding='utf-8') as file:
    file.write(original_content)

# The pattern captures the method definition and the try statement,
# and then the problematic unindented line
pattern = r'(async def receive\(self, text_data\):.*?try:.*?\n)(\s*)text_data_json'
replacement = r'\1            text_data_json'

# Apply the fix with re.DOTALL to match across multiple lines
fixed_content = re.sub(pattern, replacement, original_content, flags=re.DOTALL)

# Also fix indentation of the await statement in the except block if needed
pattern2 = r'(except Exception as e:.*?\n)(\s*)await self\.send'
replacement2 = r'\1            await self.send'
fixed_content = re.sub(pattern2, replacement2, fixed_content, flags=re.DOTALL)

# Write the fixed content to a new file for verification
with open(f"{file_path}_fixed", 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print(f"Fixed content written to {file_path}_fixed")
print("Please verify the fix and then rename/copy to the original file.") 