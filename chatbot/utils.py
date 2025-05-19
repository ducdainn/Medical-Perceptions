from django.db.models import Q, Count, Sum, Avg
from diagnosis.models import Symptom, Disease, Diagnosis
from pharmacy.models import Drug, DrugCategory, Medicine, Inventory, Prescription, Transaction
from accounts.models import User
from django.conf import settings
import json

class ChatbotDataAccess:
    """
    Utility class to provide data access functions for the chatbot.
    Provides controlled access to medical data to answer user queries.
    """
    
    @staticmethod
    def search_symptoms(query):
        """
        Search for symptoms based on user query.
        
        Args:
            query (str): Search term for symptoms
            
        Returns:
            list: List of matching symptoms with their details
        """
        symptoms = Symptom.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:10]  # Limit to 10 results
        
        return [
            {
                'id': symptom.id,
                'name': symptom.name,
                'description': symptom.description
            }
            for symptom in symptoms
        ]
    
    @staticmethod
    def get_symptom_details(symptom_id):
        """
        Get detailed information about a specific symptom.
        
        Args:
            symptom_id (int): ID of the symptom
            
        Returns:
            dict: Detailed information about the symptom
        """
        try:
            symptom = Symptom.objects.get(id=symptom_id)
            return {
                'id': symptom.id,
                'name': symptom.name,
                'description': symptom.description,
                'related_diseases': [
                    {'id': disease.id, 'name': disease.name}
                    for disease in symptom.diseases.all()[:5]
                ]
            }
        except Symptom.DoesNotExist:
            return None
    
    @staticmethod
    def search_diseases(query):
        """
        Search for diseases based on user query.
        
        Args:
            query (str): Search term for diseases
            
        Returns:
            list: List of matching diseases with their details
        """
        diseases = Disease.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:10]  # Limit to 10 results
        
        return [
            {
                'id': disease.id,
                'name': disease.name,
                'description': disease.description,
                'severity': disease.get_severity_display()
            }
            for disease in diseases
        ]
    
    @staticmethod
    def get_disease_details(disease_id):
        """
        Get detailed information about a specific disease.
        
        Args:
            disease_id (int): ID of the disease
            
        Returns:
            dict: Detailed information about the disease
        """
        try:
            disease = Disease.objects.get(id=disease_id)
            return {
                'id': disease.id,
                'name': disease.name,
                'description': disease.description,
                'severity': disease.get_severity_display(),
                'treatment_guidelines': disease.treatment_guidelines,
                'symptoms': [
                    {'id': symptom.id, 'name': symptom.name}
                    for symptom in disease.symptoms.all()
                ]
            }
        except Disease.DoesNotExist:
            return None
    
    @staticmethod
    def search_drugs(query):
        """
        Search for drugs based on user query.
        
        Args:
            query (str): Search term for drugs
            
        Returns:
            list: List of matching drugs with their details
        """
        drugs = Drug.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(composition__icontains=query) |
            Q(usage__icontains=query)
        )[:10]  # Limit to 10 results
        
        return [
            {
                'id': drug.id,
                'name': drug.name,
                'category': drug.category.name,
                'description': drug.description,
                'price': str(drug.price),
                'stock': drug.stock,
                'in_stock': drug.stock > 0
            }
            for drug in drugs
        ]
    
    @staticmethod
    def get_drug_details(drug_id):
        """
        Get detailed information about a specific drug.
        
        Args:
            drug_id (int): ID of the drug
            
        Returns:
            dict: Detailed information about the drug
        """
        try:
            drug = Drug.objects.get(id=drug_id)
            return {
                'id': drug.id,
                'name': drug.name,
                'category': drug.category.name,
                'description': drug.description,
                'composition': drug.composition,
                'usage': drug.usage,
                'dosage': drug.dosage,
                'side_effects': drug.side_effects,
                'contraindications': drug.contraindications,
                'price': str(drug.price),
                'manufacturer': drug.manufacturer,
                'stock': drug.stock,
                'in_stock': drug.stock > 0,
                'expiry_date': drug.expiry_date.strftime('%d/%m/%Y') if drug.expiry_date else None
            }
        except Drug.DoesNotExist:
            return None
    
    @staticmethod
    def search_medicines(query):
        """
        Search for medicines based on user query.
        
        Args:
            query (str): Search term for medicines
            
        Returns:
            list: List of matching medicines with their details
        """
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:10]  # Limit to 10 results
        
        return [
            {
                'id': medicine.id,
                'name': medicine.name,
                'description': medicine.description,
                'price': str(medicine.price),
                'inventory': ChatbotDataAccess.get_medicine_inventory(medicine.id)
            }
            for medicine in medicines
        ]
    
    @staticmethod
    def get_medicine_details(medicine_id):
        """
        Get detailed information about a specific medicine.
        
        Args:
            medicine_id (int): ID of the medicine
            
        Returns:
            dict: Detailed information about the medicine
        """
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            inventory = ChatbotDataAccess.get_medicine_inventory(medicine_id)
            
            return {
                'id': medicine.id,
                'name': medicine.name,
                'description': medicine.description,
                'price': str(medicine.price),
                'inventory': inventory
            }
        except Medicine.DoesNotExist:
            return None
    
    @staticmethod
    def get_medicine_inventory(medicine_id):
        """
        Get inventory information for a specific medicine.
        
        Args:
            medicine_id (int): ID of the medicine
            
        Returns:
            dict: Inventory information for the medicine
        """
        try:
            inventory = Inventory.objects.get(medicine_id=medicine_id)
            return {
                'quantity': inventory.quantity,
                'unit': inventory.unit,
                'in_stock': inventory.quantity > 0,
                'low_stock': inventory.quantity <= inventory.min_quantity and inventory.quantity > 0,
                'out_of_stock': inventory.quantity == 0
            }
        except Inventory.DoesNotExist:
            return {
                'quantity': 0,
                'unit': 'viên',
                'in_stock': False,
                'low_stock': False,
                'out_of_stock': True
            }
    
    @staticmethod
    def get_staff_info(query):
        """
        Search for staff members but return only limited information.
        
        Args:
            query (str): Search term for staff members
            
        Returns:
            list: List of staff members with limited information
        """
        staff = User.objects.filter(
            Q(user_type__in=['doctor', 'pharmacist', 'admin', 'web_manager']) &
            (Q(first_name__icontains=query) | 
             Q(last_name__icontains=query) |
             Q(username__icontains=query))
        )[:10]  # Limit to 10 results
        
        return [
            {
                'name': user.get_full_name() or user.username,
                'role': user.get_user_type_display()
            }
            for user in staff
        ]
    
    @staticmethod
    def search_knowledge_base(query):
        """
        Comprehensive search across all medical data.
        
        Args:
            query (str): Search term
            
        Returns:
            dict: Combined search results from different categories
        """
        return {
            'symptoms': ChatbotDataAccess.search_symptoms(query),
            'diseases': ChatbotDataAccess.search_diseases(query),
            'drugs': ChatbotDataAccess.search_drugs(query),
            'medicines': ChatbotDataAccess.search_medicines(query),
            'staff': ChatbotDataAccess.get_staff_info(query) if 'nhân viên' in query.lower() or 'bác sĩ' in query.lower() or 'dược sĩ' in query.lower() else [],
            'inventory': ChatbotDataAccess.search_inventory(query) if any(keyword in query.lower() for keyword in ['tồn kho', 'kho', 'còn hàng', 'hết hàng', 'inventory', 'stock']) else []
        }
    
    @staticmethod
    def get_related_diseases_for_symptoms(symptom_names):
        """
        Find diseases related to a list of symptoms.
        
        Args:
            symptom_names (list): List of symptom names
            
        Returns:
            list: Diseases that match the symptoms
        """
        # Get symptoms that match the provided names
        symptoms = Symptom.objects.filter(name__in=symptom_names)
        
        # Find diseases that have these symptoms
        diseases = Disease.objects.filter(symptoms__in=symptoms).distinct()
        
        return [
            {
                'id': disease.id,
                'name': disease.name,
                'description': disease.description,
                'severity': disease.get_severity_display(),
                'matching_symptoms': [s.name for s in disease.symptoms.filter(name__in=symptom_names)],
                'matching_count': disease.symptoms.filter(name__in=symptom_names).count(),
                'total_symptoms': disease.symptoms.count()
            }
            for disease in diseases
        ]
    
    @staticmethod
    def get_recommended_drugs_for_disease(disease_name):
        """
        Find drugs recommended for a specific disease.
        
        Args:
            disease_name (str): Name of the disease
            
        Returns:
            list: Drugs recommended for the disease
        """
        try:
            # Try to find the disease
            disease = Disease.objects.get(name__icontains=disease_name)
            
            # Look for drugs that might be related to this disease
            # This is a simplified approach - in reality you'd have a more 
            # sophisticated relationship between diseases and drugs
            related_drugs = Drug.objects.filter(
                Q(description__icontains=disease.name) |
                Q(usage__icontains=disease.name)
            )
            
            return [
                {
                    'id': drug.id,
                    'name': drug.name,
                    'description': drug.description,
                    'usage': drug.usage,
                    'dosage': drug.dosage,
                    'price': str(drug.price),
                    'stock': drug.stock,
                    'in_stock': drug.stock > 0
                }
                for drug in related_drugs
            ]
        except Disease.DoesNotExist:
            return []
    
    @staticmethod
    def format_search_results(results):
        """
        Format search results for the chatbot response.
        
        Args:
            results (dict): Search results from different categories
            
        Returns:
            str: Formatted text for the chatbot response
        """
        response_parts = []
        
        # Add symptoms if found
        if results['symptoms']:
            response_parts.append("Triệu chứng:")
            for symptom in results['symptoms'][:3]:  # Limit to 3 for conciseness
                response_parts.append(f"• {symptom['name']}: {symptom['description'][:100]}...")
        
        # Add diseases if found
        if results['diseases']:
            if response_parts:
                response_parts.append("\n")
            response_parts.append("Bệnh liên quan:")
            for disease in results['diseases'][:3]:  # Limit to 3
                response_parts.append(f"• {disease['name']} (Mức độ: {disease['severity']}): {disease['description'][:100]}...")
        
        # Add drugs if found
        if results['drugs']:
            if response_parts:
                response_parts.append("\n")
            response_parts.append("Thuốc liên quan:")
            for drug in results['drugs'][:3]:  # Limit to 3
                in_stock = "Còn hàng" if drug.get('in_stock', False) else "Hết hàng"
                response_parts.append(f"• {drug['name']} ({drug['category']}): {drug['description'][:100]}... - {in_stock}")
        
        # Add medicines if found
        if results['medicines']:
            if response_parts:
                response_parts.append("\n")
            response_parts.append("Thuốc liên quan:")
            for medicine in results['medicines'][:3]:  # Limit to 3
                inventory_status = "Còn hàng" if medicine.get('inventory', {}).get('in_stock', False) else "Hết hàng"
                response_parts.append(f"• {medicine['name']}: {medicine['description'][:100]}... - {inventory_status}")
        
        # Add inventory information if found
        if results.get('inventory'):
            if response_parts:
                response_parts.append("\n")
            response_parts.append("Thông tin tồn kho:")
            for item in results['inventory'][:5]:  # Limit to 5
                status = "Còn hàng" if item['in_stock'] else "Hết hàng"
                response_parts.append(f"• {item['name']}: {item['quantity']} {item['unit']} - {status}")
        
        # Add staff if found
        if results['staff']:
            if response_parts:
                response_parts.append("\n")
            response_parts.append("Nhân viên liên quan:")
            for staff in results['staff']:
                response_parts.append(f"• {staff['name']} - {staff['role']}")
        
        # If no results found
        if not any(results.values()):
            return "Tôi không tìm thấy thông tin liên quan đến yêu cầu của bạn trong cơ sở dữ liệu của chúng tôi."
        
        return "\n".join(response_parts)
        
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
            quantity__lte=models.F('min_quantity')
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
        
        # Find diagnoses that include these symptoms
        diagnoses = Diagnosis.objects.filter(symptoms__in=symptoms).distinct()
        
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
                for item in most_prescribed
            ]
        } 