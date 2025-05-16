file_path = 'chatbot/consumers.py'
fixed_file_path = 'chatbot/consumers_fixed2.py'

with open(file_path, 'r', encoding='utf-8') as file:
    content = file.readlines()

# Find the receive method
in_receive_method = False
in_try_block = False
fixed_content = []

for line in content:
    # Check if we're in the receive method
    if 'async def receive(self, text_data):' in line:
        in_receive_method = True
    
    # Check if we're in the try block
    if in_receive_method and 'try:' in line:
        in_try_block = True
    
    # Fix the indentation of text_data_json line
    if in_try_block and 'text_data_json = json.loads(text_data)' in line:
        # Add proper indentation (4 spaces after try block)
        fixed_line = '            text_data_json = json.loads(text_data)\n'
        fixed_content.append(fixed_line)
    else:
        fixed_content.append(line)
    
    # Check if we're out of the receive method
    if in_receive_method and line.strip() == '' and not line.startswith(' '):
        in_receive_method = False
        in_try_block = False

with open(fixed_file_path, 'w', encoding='utf-8') as file:
    file.writelines(fixed_content)

print(f"Fixed file created at {fixed_file_path}")
print("Please review the fixed file and replace consumers.py if it looks correct.") 