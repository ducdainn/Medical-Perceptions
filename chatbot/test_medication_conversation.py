"""
Test module for medication recommendation followed by inventory queries.
This simulates a conversation flow where a user first asks about medication for a symptom,
then asks if the pharmacy has that medication in stock.
"""

import os
import sys

# Set up environment to run outside Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')

import django
django.setup()

from chatbot.direct_implementation import (
    check_if_medication_recommendation_query,
    extract_symptom_from_medication_query,
    process_medication_recommendation_query,
    extract_medication_names_from_response,
    check_if_inventory_query_about_medicine,
    get_medication_inventory_info
)

def test_conversation_flow():
    """
    Test a complete conversation flow:
    1. User asks about medication for a symptom
    2. System provides medication recommendations
    3. User asks if any of those medications are available
    4. System checks inventory and responds with availability
    """
    print("=== Testing Medication Conversation Flow ===\n")
    
    # Step 1: User asks about medication for a symptom
    user_message1 = "Tôi bị ho, nên uống thuốc gì?"
    print(f"User: {user_message1}")
    
    # Check if this is a medication recommendation query
    is_medication_query = check_if_medication_recommendation_query(user_message1)
    print(f"Detected as medication query: {is_medication_query}")
    
    symptom = None
    if is_medication_query:
        # Extract symptom
        symptom = extract_symptom_from_medication_query(user_message1)
        print(f"Extracted symptom: {symptom}")
        
        # Get medication recommendations
        medication_response = process_medication_recommendation_query(user_message1)
        print(f"\nBot: {medication_response}\n")
        
        # Extract medication names from the response
        medications = extract_medication_names_from_response(medication_response)
        print(f"Extracted medications: {medications}\n")
    else:
        print("Not detected as a medication query")
        return
    
    # Step 2: User asks about medication inventory
    user_message2 = "Nhà thuốc có những loại thuốc này không?"
    print(f"User: {user_message2}")
    
    # Check if this is an inventory query about the mentioned medications
    is_inventory_followup = check_if_inventory_query_about_medicine(user_message2, medications)
    print(f"Detected as inventory followup: {is_inventory_followup}")
    
    if is_inventory_followup:
        # Get inventory information for the medications
        inventory_response = get_medication_inventory_info(medications)
        print(f"\nBot: {inventory_response}\n")
    else:
        print("Not detected as an inventory followup query")
    
    # Step 3: Test with direct medication name in followup
    if medications and len(medications) > 0:
        specific_med = medications[0]
        user_message3 = f"Nhà thuốc có thuốc {specific_med} không?"
        print(f"\nUser: {user_message3}")
        
        is_specific_inventory_query = check_if_inventory_query_about_medicine(user_message3, medications)
        print(f"Detected as specific inventory query: {is_specific_inventory_query}")
        
        if is_specific_inventory_query:
            inventory_response = get_medication_inventory_info([specific_med])
            print(f"\nBot: {inventory_response}\n")

def test_medication_extraction():
    """
    Test the extraction of medication names from AI responses
    """
    print("=== Testing Medication Name Extraction ===\n")
    
    test_responses = [
        """Với triệu chứng ho, một số thuốc bạn có thể cân nhắc:

1. Thuốc ho không kê đơn:
   • Dextromethorphan: Giúp giảm ho khan
   • Guaifenesin: Hỗ trợ làm loãng đờm, dễ khạc
   • Bromhexin: Giúp long đờm

2. Siro ho thảo dược như N-Acetylcysteine, Terpin Hydrate có thể giúp làm loãng đờm.

Lưu ý: Nếu ho kéo dài trên 1 tuần, có đờm màu xanh/vàng, hoặc kèm sốt, bạn nên đi khám bác sĩ.""",
        
        """Đối với đau đầu, bạn có thể sử dụng:

• Paracetamol (Panadol, Tylenol): Giảm đau nhẹ, hạ sốt
• Ibuprofen (Advil): Giảm đau và chống viêm
• Aspirin: Giảm đau, nhưng không nên dùng cho trẻ em

Liều lượng thông thường cho người lớn:
- Paracetamol 500mg, mỗi 4-6 giờ, không quá 4g/ngày
- Ibuprofen 200-400mg, mỗi 4-6 giờ

Hãy tham khảo ý kiến bác sĩ nếu đau đầu kéo dài hoặc nghiêm trọng.""",
        
        """Với triệu chứng sốt, có thể dùng các loại thuốc hạ sốt:

1. Paracetamol (acetaminophen)
2. Ibuprofen (không dùng cho trẻ dưới 6 tháng)

Thuốc đến từ nhóm NSAID như aspirin không được khuyến cáo cho trẻ em do nguy cơ hội chứng Reye."""
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"Test response #{i}:")
        print(f"{response}\n")
        
        extracted = extract_medication_names_from_response(response)
        print(f"Extracted medications: {extracted}\n")
        print("-" * 50)

def main():
    """Main test function"""
    test_medication_extraction()
    print("\n" + "=" * 50 + "\n")
    test_conversation_flow()

if __name__ == "__main__":
    main() 