from django import template
import re

register = template.Library()

@register.filter
def clean_chat_message(message_content):
    """
    Remove user labels and timestamps from message content.
    Examples:
    "Người dùng - 08:20:34\nActual message" -> "Actual message"
    "Chatbot - 08:20:35\nResponse text" -> "Response text"
    """
    # If the message is empty, return empty string
    if not message_content or not message_content.strip():
        return ""
        
    # Define patterns for timestamp labels
    user_time_pattern = r'(Người dùng|Chatbot|User|Bot)\s*-\s*\d{1,2}:\d{1,2}(:\d{1,2})?'
    time_only_pattern = r'\d{1,2}:\d{1,2}(:\d{1,2})?'
    
    # Check if the entire message content is just a timestamp label with no additional content
    if re.match(f'^{user_time_pattern}$', message_content.strip()):
        return ""  # Return empty string if it's just a timestamp label
    
    # If it's a standalone timestamp
    if re.match(f'^{time_only_pattern}$', message_content.strip()):
        return ""
        
    # Remove standalone timestamp labels at the beginning of the message
    message_content = re.sub(f'^{user_time_pattern}\s*\n?', '', message_content)
    
    # Remove standalone timestamps at the beginning
    message_content = re.sub(f'^{time_only_pattern}\s*\n?', '', message_content)
    
    # Process line by line for more complex cases
    lines = message_content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        # Skip lines that are just timestamp labels
        if re.match(f'^{user_time_pattern}$', line.strip()) or re.match(f'^{time_only_pattern}$', line.strip()):
            continue
        
        # Remove timestamp prefix from lines if it exists
        line = re.sub(f'^{user_time_pattern}:\s*', '', line)
        
        # Keep all other lines
        cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines).strip()
    return result

@register.filter
def user_type_color(user_type):
    """
    Returns the appropriate Bootstrap color class for different user types.
    Example:
    'admin' -> 'danger'
    'doctor' -> 'info'
    """
    colors = {
        'admin': 'danger',
        'web_manager': 'success',
        'doctor': 'info',
        'pharmacist': 'warning',
        'patient': 'primary',
    }
    
    return colors.get(user_type, 'secondary')