import re

# Read the current content of urls.py
with open('chatbot/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the import
if 'from .botmessage_handler import enhanced_bot_send_message' not in content:
    content = re.sub(
        r'from \. import views\nfrom \. import inventory_views',
        'from . import views\nfrom . import inventory_views\nfrom .botmessage_handler import enhanced_bot_send_message',
        content
    )

# Update the endpoint to use the enhanced_bot_send_message
content = re.sub(
    r'path\(\'api/bot-send-message/\', views.bot_send_message, name=\'bot_send_message\'\)',
    r'path(\'api/bot-send-message/\', enhanced_bot_send_message, name=\'bot_send_message\')',
    content
)

# Write the updated content back to the file
with open('chatbot/urls.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated urls.py') 