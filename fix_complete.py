import re

def fix_consumers_file():
    file_path = 'chatbot/consumers.py'
    
    # Create a backup first
    backup_path = f"{file_path}.backup"
    with open(file_path, 'r', encoding='utf-8') as src:
        with open(backup_path, 'w', encoding='utf-8') as dest:
            dest.write(src.read())
    print(f"Backup created at {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix known indentation issues in the connect method
    connect_pattern = r'async def connect\(self\):(.*?)async def disconnect\('
    try:
        connect_match = re.search(connect_pattern, content, re.DOTALL)
        if connect_match:
            connect_block = connect_match.group(1)
            
            # Fix awaits directly under connect
            fixed_connect = re.sub(
                r'(\s+)(await self\.send\(text_data=json\.dumps\()',
                r'            \2',
                connect_block
            )
            
            # Fix await inside the try block
            fixed_connect = re.sub(
                r'(\s+try:.*?)(\s+)(await self\.send\(text_data=json\.dumps\()',
                r'\1\n                \3',
                fixed_connect,
                flags=re.DOTALL
            )
            
            # Replace in original content
            content = content.replace(connect_match.group(1), fixed_connect)
    except Exception as e:
        print(f"Error fixing connect method: {e}")
    
    # Fix the receive method
    receive_pattern = r'async def receive\(self, text_data\):(.*?)@database_sync_to_async'
    try:
        receive_match = re.search(receive_pattern, content, re.DOTALL)
        if receive_match:
            receive_block = receive_match.group(1)
            
            # Fix text_data_json line under try
            fixed_receive = re.sub(
                r'(\s+try:.*?)(\s*)(text_data_json = json\.loads\(text_data\))',
                r'\1\n            \3',
                receive_block,
                flags=re.DOTALL
            )
            
            # Fix awaits directly under receive
            fixed_receive = re.sub(
                r'(\s+)(await self\.send\(text_data=json\.dumps\()',
                r'            \2',
                fixed_receive
            )
            
            # Replace in original content
            content = content.replace(receive_match.group(1), fixed_receive)
    except Exception as e:
        print(f"Error fixing receive method: {e}")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed indentation issues in {file_path}")

if __name__ == "__main__":
    fix_consumers_file() 