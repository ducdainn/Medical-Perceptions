"""
Advanced data access utilities for the chatbot to handle inventory and diagnosis data.
This extends the functionality provided in utils.py.
"""

from django.db.models import Q, Count, Sum, Avg, F
import re
from diagnosis.models import Symptom, Disease, Diagnosis
from pharmacy.models import Drug, DrugCategory, Medicine, Inventory, Prescription, Transaction, PrescriptionItem
from accounts.models import User
from django.conf import settings
import json

class AdvancedChatbotDataAccess:
    """
    Extended data access utilities for the chatbot.
    Provides additional functionality for inventory and diagnosis data.
    """
    
    @staticmethod
    def check_if_medical_query(message):
        """
        Enhanced check if a message is querying for medical data.
        Includes inventory and prescription related keywords.
        
        Args:
            message (str): The user's message
            
        Returns:
            bool: True if the message is a medical query, False otherwise
        """
        # Keywords for medical queries
        medical_keywords = [
            'triệu chứng', 'symptom', 
            'bệnh', 'disease', 
            'thuốc', 'medicine', 'drug',
            'điều trị', 'treatment',
            'bác sĩ', 'doctor',
            'dược sĩ', 'pharmacist',
            'tác dụng phụ', 'side effect',
            'liều lượng', 'dosage',
            'thành phần', 'composition',
            'tồn kho', 'kho', 'còn hàng', 'hết hàng', 'inventory', 'stock',
            'đơn thuốc', 'kê đơn', 'prescription'
        ]
        
        # Question indicators
        question_indicators = ['?', 'là gì', 'như thế nào', 'thế nào', 'ra sao', 'làm sao', 'cách', 'chữa', 'hỏi', 'tư vấn', 'tìm']
        
        # Check if the message contains both medical keywords and question indicators
        has_medical_keyword = any(keyword in message.lower() for keyword in medical_keywords)
        has_question_indicator = any(indicator in message.lower() for indicator in question_indicators)
        
        # Direct commands to search for information
        direct_commands = ['tìm kiếm', 'tìm thông tin về', 'tra cứu', 'search', 'lookup', 'find', 'thống kê', 'kiểm tra']
        has_direct_command = any(command in message.lower() for command in direct_commands)
        
        return (has_medical_keyword and has_question_indicator) or has_direct_command
    
    @staticmethod
    def search_inventory(query):
        """
        Search for inventory information based on query.
        
        Args:
            query (str): Search term for inventory
            
        Returns:
            list: List of inventory items matching the query
        """
        # Search in Medicine names and descriptions
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:15]
        
        results = []
        
        for medicine in medicines:
            try:
                inventory = Inventory.objects.get(medicine=medicine)
                results.append({
                    'id': medicine.id,
                    'name': medicine.name,
                    'quantity': inventory.quantity,
                    'unit': inventory.unit,
                    'min_quantity': inventory.min_quantity,
                    'in_stock': inventory.quantity > 0,
                    'low_stock': inventory.quantity <= inventory.min_quantity and inventory.quantity > 0,
                    'out_of_stock': inventory.quantity == 0
                })
            except Inventory.DoesNotExist:
                # If no inventory record exists, assume out of stock
                results.append({
                    'id': medicine.id,
                    'name': medicine.name,
                    'quantity': 0,
                    'unit': 'viên',
                    'min_quantity': 0,
                    'in_stock': False,
                    'low_stock': False,
                    'out_of_stock': True
                })
        
        # If no results found in medicines, also search in drugs
        if not results:
            drugs = Drug.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )[:15]
            
            for drug in drugs:
                results.append({
                    'id': drug.id,
                    'name': drug.name,
                    'quantity': drug.stock,
                    'unit': 'đơn vị',
                    'min_quantity': 10,  # Default value
                    'in_stock': drug.stock > 0,
                    'low_stock': drug.stock <= 10 and drug.stock > 0,
                    'out_of_stock': drug.stock == 0
                })
        
        return results
        
    @staticmethod
    def get_inventory_stats():
        """
        Get overall statistics about inventory.
        
        Returns:
            dict: Statistics about inventory
        """
        # Count total medicines
        total_medicines = Medicine.objects.count()
        
        # Count medicines with inventory
        medicines_with_inventory = Inventory.objects.count()
        
        # Count out of stock medicines
        out_of_stock = Inventory.objects.filter(quantity=0).count()
        
        # Count low stock medicines
        low_stock = Inventory.objects.filter(
            quantity__gt=0, 
            quantity__lte=F('min_quantity')
        ).count()
        
        # Get total drugs
        total_drugs = Drug.objects.count()
        
        # Count out of stock drugs
        drugs_out_of_stock = Drug.objects.filter(stock=0).count()
        
        # Count low stock drugs (assuming below 10 is low)
        drugs_low_stock = Drug.objects.filter(stock__gt=0, stock__lte=10).count()
        
        return {
            'total_medicines': total_medicines,
            'medicines_with_inventory': medicines_with_inventory,
            'medicines_out_of_stock': out_of_stock,
            'medicines_low_stock': low_stock,
            'total_drugs': total_drugs,
            'drugs_out_of_stock': drugs_out_of_stock,
            'drugs_low_stock': drugs_low_stock,
        }
        
    @staticmethod
    def get_diagnoses_for_symptoms(symptom_list):
        """
        Get historical diagnoses for a set of symptoms.
        
        Args:
            symptom_list (list): List of symptom names
            
        Returns:
            list: Previous diagnoses matching these symptoms
        """
        # Get symptoms that match the provided names
        symptoms = Symptom.objects.filter(name__in=symptom_list)
        
        if not symptoms.exists():
            return []
            
        # Find diagnoses that include these symptoms
        diagnoses = Diagnosis.objects.filter(symptoms__in=symptoms).distinct()
        
        if not diagnoses.exists():
            return []
            
        # Count diagnoses per disease
        disease_counts = diagnoses.values('disease__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get the top diseases diagnosed with these symptoms
        results = []
        
        for item in disease_counts[:5]:  # Top 5 most common diagnoses
            disease_name = item['disease__name']
            disease = Disease.objects.get(name=disease_name)
            
            # Calculate confidence based on historical diagnoses
            confidence = (item['count'] / diagnoses.count()) * 100
            
            results.append({
                'disease_name': disease_name,
                'description': disease.description,
                'severity': disease.get_severity_display(),
                'confidence': round(confidence, 2),
                'diagnosis_count': item['count'],
                'treatment_guidelines': disease.treatment_guidelines,
            })
        
        return results
        
    @staticmethod
    def get_prescription_stats():
        """
        Get statistics about prescriptions.
        
        Returns:
            dict: Statistics about prescriptions
        """
        # Count total prescriptions
        total_prescriptions = Prescription.objects.count()
        
        # Count prescriptions by status
        pending = Prescription.objects.filter(status='pending').count()
        processing = Prescription.objects.filter(status='processing').count()
        completed = Prescription.objects.filter(status='completed').count()
        
        # Get most prescribed medicines
        most_prescribed = PrescriptionItem.objects.values(
            'medicine__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'total_prescriptions': total_prescriptions,
            'pending_prescriptions': pending,
            'processing_prescriptions': processing,
            'completed_prescriptions': completed,
            'most_prescribed': [
                {'name': item['medicine__name'], 'count': item['count']}
                for item in most_prescribed if item['medicine__name']
            ]
        }
    
    @staticmethod
    def process_inventory_query(message, search_term):
        """
        Process a query about inventory.
        
        Args:
            message (str): The user's message
            search_term (str): Extracted search term
            
        Returns:
            str: Formatted response about inventory
        """
        inventory_results = AdvancedChatbotDataAccess.search_inventory(search_term)
        
        if not inventory_results:
            return f"Không tìm thấy thông tin tồn kho cho '{search_term}'. Vui lòng thử tìm kiếm với từ khóa khác."
        
        # Format inventory results
        response = "Thông tin tồn kho:\n\n"
        for item in inventory_results[:10]:
            status = "Còn hàng" if item['in_stock'] else "Hết hàng"
            low_stock_note = " (Sắp hết)" if item.get('low_stock', False) else ""
            response += f"• {item['name']}: {item['quantity']} {item['unit']} - {status}{low_stock_note}\n"
        
        # Add stats about overall inventory if querying general inventory
        if any(term in message.lower() for term in ['tổng quan', 'tất cả', 'toàn bộ', 'all']):
            try:
                inventory_stats = AdvancedChatbotDataAccess.get_inventory_stats()
                response += f"\nTổng quan tồn kho:\n"
                response += f"• Tổng số thuốc: {inventory_stats['total_medicines'] + inventory_stats['total_drugs']}\n"
                response += f"• Thuốc hết hàng: {inventory_stats['medicines_out_of_stock'] + inventory_stats['drugs_out_of_stock']}\n"
                response += f"• Thuốc sắp hết: {inventory_stats['medicines_low_stock'] + inventory_stats['drugs_low_stock']}\n"
            except Exception as e:
                print(f"Error getting inventory stats: {str(e)}")
        
        response += "\nLưu ý: Thông tin tồn kho được cập nhật theo thời gian thực. Vui lòng liên hệ nhân viên dược phòng để biết thêm chi tiết."
        return response
    
    @staticmethod
    def process_advanced_diagnosis(symptom_list):
        """
        Process a diagnosis with historical data.
        
        Args:
            symptom_list (list): List of symptom names
            
        Returns:
            str: Formatted diagnosis response with historical data
        """
        # Get disease matches from symptoms
        from chatbot.utils import ChatbotDataAccess
        disease_results = ChatbotDataAccess.get_related_diseases_for_symptoms(symptom_list)
        
        if not disease_results:
            return f"Không tìm thấy bệnh nào phù hợp với các triệu chứng bạn đã mô tả: {', '.join(symptom_list)}. Vui lòng mô tả chi tiết hơn hoặc tham khảo ý kiến bác sĩ."
        
        # Sort by number of matching symptoms
        disease_results.sort(key=lambda x: x['matching_count'], reverse=True)
        
        response = "Dựa trên các triệu chứng bạn mô tả, đây là một số bệnh có thể liên quan:\n\n"
        
        for idx, disease in enumerate(disease_results[:3], 1):
            matching_ratio = disease['matching_count'] / disease['total_symptoms']
            confidence = "cao" if matching_ratio > 0.7 else "trung bình" if matching_ratio > 0.4 else "thấp"
            
            response += f"{idx}. {disease['name']} (Độ phù hợp: {confidence})\n"
            response += f"   Mô tả: {disease['description'][:150]}...\n"
            response += f"   Triệu chứng khớp: {', '.join(disease['matching_symptoms'])}\n\n"
        
        # Try to get historical diagnosis data to improve accuracy
        try:
            historical_diagnoses = AdvancedChatbotDataAccess.get_diagnoses_for_symptoms(symptom_list)
            
            if historical_diagnoses:
                response += "Thông tin từ lịch sử chẩn đoán:\n"
                for idx, diagnosis in enumerate(historical_diagnoses[:2], 1):
                    response += f"{idx}. {diagnosis['disease_name']} (Độ tin cậy: {diagnosis['confidence']}%)\n"
                    if diagnosis.get('treatment_guidelines'):
                        response += f"   Hướng dẫn điều trị: {diagnosis['treatment_guidelines'][:150]}...\n\n"
        except Exception as e:
            print(f"Error getting historical diagnoses: {str(e)}")
        
        response += "Lưu ý: Đây chỉ là thông tin tham khảo dựa trên phân tích dữ liệu. Vui lòng tham khảo ý kiến bác sĩ để được chẩn đoán chính xác."
        return response
    
    @staticmethod
    def process_prescription_stats_query():
        """
        Process a query about prescription statistics.
        
        Returns:
            str: Formatted response about prescription statistics
        """
        try:
            prescription_stats = AdvancedChatbotDataAccess.get_prescription_stats()
            
            response = "Thống kê đơn thuốc:\n\n"
            response += f"• Tổng số đơn thuốc: {prescription_stats['total_prescriptions']}\n"
            response += f"• Đơn đang chờ xử lý: {prescription_stats['pending_prescriptions']}\n"
            response += f"• Đơn đang xử lý: {prescription_stats['processing_prescriptions']}\n"
            response += f"• Đơn đã hoàn thành: {prescription_stats['completed_prescriptions']}\n\n"
            
            if prescription_stats.get('most_prescribed'):
                response += "Thuốc được kê đơn nhiều nhất:\n"
                for idx, item in enumerate(prescription_stats['most_prescribed'], 1):
                    response += f"{idx}. {item['name']} - {item['count']} lần\n"
            
            return response
        except Exception as e:
            print(f"Error getting prescription stats: {str(e)}")
            return "Không thể truy xuất thống kê đơn thuốc. Vui lòng thử lại sau."
    
    @staticmethod
    def extract_symptom_list(message):
        """
        Enhanced extraction of symptom list from message.
        
        Args:
            message (str): The user's message
            
        Returns:
            list: List of extracted symptoms
        """
        # Check for listing patterns
        list_patterns = [
            r"(?:có|bị) các? triệu chứng (?:như|gồm|bao gồm|là)? (.*?)(?:\.|$)",
            r"(?:có|bị) (.*?)(?:\.|$)",
            r"(?:triệu chứng|symptoms)(?:: | là | như | bao gồm | gồm )(.*?)(?:\.|$)",
            r"(?:tôi|mình|bệnh nhân) (?:bị|có|đang) (.*?)(?:\?|\.|$)",
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                symptom_text = match.group(1)
                
                # Split by common separators
                separators = [',', ';', 'và', 'and', '\n', '\t', '•', '-']
                for sep in separators:
                    if sep in symptom_text:
                        return [s.strip() for s in symptom_text.split(sep) if s.strip()]
                
                # If no separators found, check for multiple words
                words = symptom_text.split()
                if len(words) > 2:  # If more than 2 words, it might be multiple symptoms
                    return [symptom_text]
        
        # If no patterns match, try to extract from the whole message
        potential_symptoms = []
        symptom_keywords = [
            'đau', 'nhức', 'sốt', 'ho', 'khó thở', 'mệt', 'buồn nôn', 'nôn', 
            'chóng mặt', 'đau đầu', 'tiêu chảy', 'phát ban', 'ngứa', 'sưng'
        ]
        
        for keyword in symptom_keywords:
            if keyword in message.lower():
                # Find the context of the symptom
                parts = message.lower().split('.')
                for part in parts:
                    if keyword in part:
                        # Extract the symptom with context
                        words_around = part.split()
                        keyword_index = next(i for i, word in enumerate(words_around) if keyword in word)
                        
                        # Get a window of words around the keyword
                        start = max(0, keyword_index - 2)
                        end = min(len(words_around), keyword_index + 3)
                        symptom_context = ' '.join(words_around[start:end])
                        
                        potential_symptoms.append(symptom_context.strip())
        
        return list(set(potential_symptoms))

    @staticmethod
    def get_inventory_data_for_chatbot(query=None):
        """
        Get comprehensive inventory data for the chatbot to answer customer questions.
        If query is provided, filter results based on the query.
        
        Args:
            query (str, optional): Optional search term to filter inventory data
            
        Returns:
            list: List of inventory items with detailed information
        """
        inventory_query = Inventory.objects.all()
        
        # If a search query is provided, filter the results
        if query:
            inventory_query = inventory_query.filter(
                Q(medicine__name__icontains=query) | 
                Q(medicine__description__icontains=query)
            )
        
        # Limit results to manage response size
        inventory_items = inventory_query[:25]
        
        results = []
        for item in inventory_items:
            status = "Còn hàng"
            if item.quantity == 0:
                status = "Hết hàng"
            elif item.quantity <= item.min_quantity:
                status = "Sắp hết hàng"
                
            results.append({
                'id': item.id,
                'thuoc': item.medicine.name,
                'so_luong': item.quantity,
                'don_vi': item.unit,
                'so_luong_toi_thieu': item.min_quantity,
                'gia': str(item.medicine.price),
                'trang_thai': status,
                'mo_ta': item.medicine.description or "Không có mô tả",
            })
            
        return results
        
    @staticmethod
    def format_inventory_response(inventory_items):
        """
        Format inventory data into a human-readable response for the chatbot.
        
        Args:
            inventory_items (list): List of inventory items
            
        Returns:
            str: Formatted response for the chatbot
        """
        if not inventory_items:
            return "Không tìm thấy thông tin về thuốc trong kho. Vui lòng thử lại với từ khóa khác."
        
        response = "Đây là thông tin về thuốc trong kho:\n\n"
        
        for item in inventory_items:
            response += f"- {item['thuoc']}:\n"
            response += f"  • Số lượng: {item['so_luong']} {item['don_vi']}\n"
            response += f"  • Giá: {item['gia']} VNĐ\n"
            response += f"  • Trạng thái: {item['trang_thai']}\n"
            if item['mo_ta'] != "Không có mô tả":
                response += f"  • Mô tả: {item['mo_ta']}\n"
            response += "\n"
            
        return response.strip()

    @staticmethod
    def process_inventory_query(message):
        """
        Process a user query about inventory.
        Extract search terms and return relevant inventory data.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: Response with inventory information
        """
        # Keywords that might indicate what medicine the user is asking about
        search_terms = []
        
        # Common search patterns in Vietnamese
        patterns = [
            r'thuốc\s+(.+?)(?:\s+có|trong|\?|$)',  # "thuốc X có..."
            r'có\s+thuốc\s+(.+?)(?:\s+không|\?|$)',  # "có thuốc X không"
            r'thông tin\s+(?:về\s+)?thuốc\s+(.+?)(?:\s+không|\?|$)',  # "thông tin về thuốc X"
            r'tìm\s+(?:thuốc|thông tin)\s+(.+?)(?:\s+không|\?|$)',  # "tìm thuốc X"
            r'kiểm tra\s+(?:thuốc|kho)\s+(.+?)(?:\s+không|\?|$)',  # "kiểm tra thuốc X"
        ]
        
        # Try to extract search terms using patterns
        for pattern in patterns:
            matches = re.findall(pattern, message.lower())
            if matches:
                search_terms.extend(matches)
        
        # If no structured search terms found, extract potential medicine names
        # This is a simple extraction based on word position after keywords
        if not search_terms:
            words = message.lower().split()
            for i, word in enumerate(words):
                if word in ['thuốc', 'medicine', 'drug', 'kho', 'inventory'] and i < len(words) - 1:
                    search_terms.append(words[i+1])
        
        # If still no search terms found, return all inventory items
        if search_terms:
            # Use the first found term for search
            inventory_items = AdvancedChatbotDataAccess.get_inventory_data_for_chatbot(search_terms[0])
        else:
            inventory_items = AdvancedChatbotDataAccess.get_inventory_data_for_chatbot()
            
        return AdvancedChatbotDataAccess.format_inventory_response(inventory_items)

    @staticmethod
    def search_medication_in_inventory(med_name):
        """
        Search for a specific medication in inventory by name.
        Performs an exact search for the medication name.
        
        Args:
            med_name (str): Name of the medication to search for
            
        Returns:
            list: List of inventory items matching the medication name
        """
        results = []
        
        try:
            # Search in Medicine model
            medicines = Medicine.objects.filter(name__icontains=med_name)[:10]
            
            for medicine in medicines:
                try:
                    inventory = Inventory.objects.get(medicine=medicine)
                    expiry_date = "N/A"
                    if hasattr(inventory, 'expiry_date') and inventory.expiry_date:
                        try:
                            expiry_date = inventory.expiry_date.strftime('%d/%m/%Y')
                        except:
                            expiry_date = "N/A"
                        
                    results.append({
                        'id': medicine.id,
                        'name': medicine.name,
                        'quantity': inventory.quantity,
                        'unit': inventory.unit if hasattr(inventory, 'unit') else 'đơn vị',
                        'price': str(medicine.price) if hasattr(medicine, 'price') else 'Không có thông tin',
                        'expiry': expiry_date,
                        'description': medicine.description or ""
                    })
                except Inventory.DoesNotExist:
                    # No inventory record exists
                    results.append({
                        'id': medicine.id,
                        'name': medicine.name,
                        'quantity': 0,
                        'unit': 'đơn vị',
                        'price': str(medicine.price) if hasattr(medicine, 'price') else 'Không có thông tin',
                        'description': medicine.description or ""
                    })
                except Exception as e:
                    print(f"Error processing medicine {medicine.name}: {str(e)}")
        except Exception as e:
            print(f"Error searching medicines: {str(e)}")
        
        # If no results in Medicine, search in Drug model
        if not results:
            try:
                drugs = Drug.objects.filter(name__icontains=med_name)[:10]
                
                for drug in drugs:
                    try:
                        results.append({
                            'id': drug.id,
                            'name': drug.name,
                            'quantity': drug.stock if hasattr(drug, 'stock') else 0,
                            'unit': 'đơn vị',
                            'price': str(drug.price) if hasattr(drug, 'price') else 'Không có thông tin',
                            'description': drug.description or ""
                        })
                    except Exception as e:
                        print(f"Error processing drug {drug.name}: {str(e)}")
            except Exception as e:
                print(f"Error searching drugs: {str(e)}")
        
        return results
    
    @staticmethod
    def fuzzy_search_medication(med_name):
        """
        Perform a fuzzy search for medications in inventory.
        This method is less strict and can find medications even with partial or
        misspelled names, by searching in name, description, and category.
        
        Args:
            med_name (str): Name or partial name of the medication
            
        Returns:
            list: List of inventory items that might match the medication
        """
        results = []
        
        # Break down the med_name into words for more flexible matching
        search_terms = med_name.lower().split()
        
        # Build a query for Medicine model (without category field)
        medicine_query = Q()
        for term in search_terms:
            if len(term) >= 3:  # Only search for terms with at least 3 characters
                medicine_query |= Q(name__icontains=term)
                medicine_query |= Q(description__icontains=term)
                # Note: category field is removed as it's not available in the model
        
        # Search in Medicine model with the query
        if medicine_query:
            try:
                medicines = Medicine.objects.filter(medicine_query).distinct()[:10]
                
                for medicine in medicines:
                    try:
                        inventory = Inventory.objects.get(medicine=medicine)
                        results.append({
                            'id': medicine.id,
                            'name': medicine.name,
                            'quantity': inventory.quantity,
                            'unit': inventory.unit,
                            'price': str(medicine.price),
                            'expiry': inventory.expiry_date.strftime('%d/%m/%Y') if hasattr(inventory, 'expiry_date') and inventory.expiry_date else 'N/A',
                            'description': medicine.description or "",
                            'match_type': 'fuzzy'
                        })
                    except Inventory.DoesNotExist:
                        results.append({
                            'id': medicine.id,
                            'name': medicine.name,
                            'quantity': 0,
                            'unit': 'đơn vị',
                            'price': str(medicine.price),
                            'description': medicine.description or "",
                            'match_type': 'fuzzy'
                        })
            except Exception as e:
                print(f"Error in fuzzy medicine search: {str(e)}")
        
        # Build a query for Drug model (without category field)
        drug_query = Q()
        for term in search_terms:
            if len(term) >= 3:  # Only search for terms with at least 3 characters
                drug_query |= Q(name__icontains=term)
                drug_query |= Q(description__icontains=term)
                # Note: category field is removed as it might not be available
        
        # Search in Drug model with the complex query
        if drug_query and len(results) < 10:
            # Only search drugs if we don't have enough results yet
            try:
                drugs = Drug.objects.filter(drug_query).distinct()[:10]
                
                for drug in drugs:
                    results.append({
                        'id': drug.id,
                        'name': drug.name,
                        'quantity': drug.stock,
                        'unit': 'đơn vị',
                        'price': str(drug.price),
                        'description': drug.description or "",
                        'match_type': 'fuzzy'
                    })
            except Exception as e:
                print(f"Error in fuzzy drug search: {str(e)}")
        
        # Search for similar medication names (without using category)
        if not results:
            # Try to find medications with similar names
            try:
                # First try to find an exact match
                exact_med = Medicine.objects.filter(name__icontains=med_name).first()
                if exact_med:
                    # Find other medications with similar names
                    similar_med_query = Q(name__icontains=med_name.split()[0]) if med_name.split() else Q(name__icontains=med_name)
                    similar_meds = Medicine.objects.filter(similar_med_query).exclude(id=exact_med.id)[:5]
                    
                    for medicine in similar_meds:
                        try:
                            inventory = Inventory.objects.get(medicine=medicine)
                            results.append({
                                'id': medicine.id,
                                'name': medicine.name,
                                'quantity': inventory.quantity,
                                'unit': inventory.unit,
                                'price': str(medicine.price),
                                'description': medicine.description or "",
                                'match_type': 'related'
                            })
                        except Inventory.DoesNotExist:
                            results.append({
                                'id': medicine.id,
                                'name': medicine.name,
                                'quantity': 0,
                                'unit': 'đơn vị',
                                'price': str(medicine.price),
                                'description': medicine.description or "",
                                'match_type': 'related'
                            })
            except Exception as e:
                print(f"Error finding similar medications: {str(e)}")
        
        return results 