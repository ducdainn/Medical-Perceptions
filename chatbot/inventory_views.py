from django.http import JsonResponse
from django.db.models import Q
from pharmacy.models import Inventory, Medicine
from .advanced_data_access import AdvancedChatbotDataAccess

def test_inventory_access(request):
    """
    Test endpoint to verify inventory data access for chatbot
    This is for debugging and development purposes only
    
    Usage: /chatbot/api/test/inventory/?query=your_search_term
    If no query is provided, returns all inventory items
    """
    query = request.GET.get('query', '')
    try:
        if query:
            inventory_data = AdvancedChatbotDataAccess.get_inventory_data_for_chatbot(query)
            response = AdvancedChatbotDataAccess.format_inventory_response(inventory_data)
        else:
            inventory_data = AdvancedChatbotDataAccess.get_inventory_data_for_chatbot()
            response = AdvancedChatbotDataAccess.format_inventory_response(inventory_data)
            
        return JsonResponse({
            'success': True,
            'data': inventory_data,
            'formatted_response': response
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 