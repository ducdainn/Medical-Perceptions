import re

def fix_indentation(file_path):
    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Create a backup
    backup_path = f"{file_path}.original"
    with open(backup_path, 'w', encoding='utf-8') as backup_file:
        backup_file.writelines(lines)
    
    print(f"Created backup at {backup_path}")
    
    # Fix indentation issues
    fixed_lines = []
    in_try_block = False
    in_connect_method = False
    in_receive_method = False
    fixed_line_added = False
    
    for i, line in enumerate(lines):
        # Track method context
        if "async def connect" in line:
            in_connect_method = True
            in_receive_method = False
        elif "async def receive" in line:
            in_connect_method = False
            in_receive_method = True
        elif "async def" in line and "connect" not in line and "receive" not in line:
            in_connect_method = False
            in_receive_method = False
        
        # Fix indentation in connect method
        if in_connect_method and "await self.send(text_data=json.dumps" in line and line.strip().startswith("await"):
            fixed_line = "            await self.send(text_data=json.dumps" + line.split("await self.send(text_data=json.dumps", 1)[1]
            fixed_lines.append(fixed_line)
            fixed_line_added = True
        # Fix indentation in try block in connect method
        elif in_connect_method and line.strip() == "try:":
            fixed_lines.append(line)
            fixed_line_added = True
            in_try_block = True
        elif in_connect_method and in_try_block and "await self.send(text_data=json.dumps" in line and line.strip().startswith("await"):
            fixed_line = "                await self.send(text_data=json.dumps" + line.split("await self.send(text_data=json.dumps", 1)[1]
            fixed_lines.append(fixed_line)
            fixed_line_added = True
        # Fix indentation in receive method
        elif in_receive_method and "await self.send(text_data=json.dumps" in line and line.strip().startswith("await"):
            fixed_line = "            await self.send(text_data=json.dumps" + line.split("await self.send(text_data=json.dumps", 1)[1]
            fixed_lines.append(fixed_line)
            fixed_line_added = True
        # Fix indentation in try/except blocks in receive method
        elif in_receive_method and "text_data_json = json.loads" in line:
            fixed_line = "            text_data_json = json.loads" + line.split("text_data_json = json.loads", 1)[1]
            fixed_lines.append(fixed_line)
            fixed_line_added = True
        else:
            fixed_lines.append(line)
            fixed_line_added = False
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)
    
    print(f"Fixed indentation issues in {file_path}")

# Path to the file that needs fixing
file_path = 'chatbot/consumers.py'
fix_indentation(file_path) 