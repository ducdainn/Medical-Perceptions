import os
import django
import datetime
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from pharmacy.models import DrugCategory, Drug, Medicine, Inventory

def add_drug_categories():
    """Add diverse drug categories"""
    categories = [
        {
            'name': 'Thuốc kháng sinh',
            'description': 'Nhóm thuốc dùng để điều trị các bệnh nhiễm khuẩn do vi khuẩn gây ra.'
        },
        {
            'name': 'Thuốc giảm đau, hạ sốt',
            'description': 'Nhóm thuốc có tác dụng giảm đau và hạ sốt.'
        },
        {
            'name': 'Thuốc tim mạch',
            'description': 'Nhóm thuốc điều trị các bệnh lý về tim mạch.'
        },
        {
            'name': 'Thuốc tiêu hóa',
            'description': 'Nhóm thuốc tác động lên hệ tiêu hóa để điều trị các triệu chứng hoặc bệnh lý liên quan.'
        },
        {
            'name': 'Thuốc da liễu',
            'description': 'Nhóm thuốc dùng để điều trị các bệnh về da.'
        },
        {
            'name': 'Thuốc hô hấp',
            'description': 'Nhóm thuốc điều trị các bệnh về đường hô hấp.'
        },
        {
            'name': 'Thuốc nội tiết',
            'description': 'Nhóm thuốc tác động lên hệ thống nội tiết.'
        },
        {
            'name': 'Vitamin và khoáng chất',
            'description': 'Bổ sung các vitamin và khoáng chất thiết yếu cho cơ thể.'
        }
    ]
    
    for category_data in categories:
        category, created = DrugCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data['description']}
        )
        if created:
            print(f"  Đã thêm danh mục thuốc: {category.name}")
        else:
            print(f"  Danh mục thuốc đã tồn tại: {category.name}")

def add_drugs():
    """Add diverse drugs to each category"""
    # Get all categories
    categories = DrugCategory.objects.all()
    
    # Drugs for "Thuốc kháng sinh" category
    if categories.filter(name='Thuốc kháng sinh').exists():
        category = categories.get(name='Thuốc kháng sinh')
        drugs_data = [
            {
                'name': 'Amoxicillin',
                'description': 'Kháng sinh beta-lactam phổ rộng',
                'composition': 'Amoxicillin trihydrate tương đương 500mg amoxicillin',
                'usage': 'Uống, 3 lần/ngày sau bữa ăn',
                'dosage': 'Người lớn: 500mg, 3 lần/ngày. Trẻ em: 20-40mg/kg/ngày chia 3 lần',
                'side_effects': 'Buồn nôn, tiêu chảy, phát ban',
                'contraindications': 'Dị ứng với penicillin, suy thận nặng',
                'price': Decimal('35000'),
                'stock': 200,
                'manufacturer': 'Công ty dược phẩm Hà Nội',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Cefuroxime',
                'description': 'Kháng sinh nhóm cephalosporin thế hệ 2',
                'composition': 'Cefuroxime axetil tương đương 500mg cefuroxime',
                'usage': 'Uống, 2 lần/ngày sau bữa ăn',
                'dosage': 'Người lớn: 250-500mg, 2 lần/ngày. Trẻ em: 10-15mg/kg/ngày chia 2 lần',
                'side_effects': 'Buồn nôn, tiêu chảy, đau đầu',
                'contraindications': 'Dị ứng với cephalosporin, suy gan nặng',
                'price': Decimal('60000'),
                'stock': 150,
                'manufacturer': 'GlaxoSmithKline',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Azithromycin',
                'description': 'Kháng sinh nhóm macrolide',
                'composition': 'Azithromycin dihydrate tương đương 500mg azithromycin',
                'usage': 'Uống, 1 lần/ngày trước bữa ăn 1 giờ hoặc sau bữa ăn 2 giờ',
                'dosage': 'Người lớn: 500mg/ngày trong 3 ngày. Trẻ em: 10mg/kg/ngày trong 3 ngày',
                'side_effects': 'Buồn nôn, tiêu chảy, đau bụng',
                'contraindications': 'Dị ứng với macrolide, bệnh gan nặng',
                'price': Decimal('80000'),
                'stock': 120,
                'manufacturer': 'Pfizer',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            }
        ]
        
        for drug_data in drugs_data:
            drug, created = Drug.objects.get_or_create(
                name=drug_data['name'],
                defaults={
                    'category': category,
                    'description': drug_data['description'],
                    'composition': drug_data['composition'],
                    'usage': drug_data['usage'],
                    'dosage': drug_data['dosage'],
                    'side_effects': drug_data['side_effects'],
                    'contraindications': drug_data['contraindications'],
                    'price': drug_data['price'],
                    'stock': drug_data['stock'],
                    'manufacturer': drug_data['manufacturer'],
                    'expiry_date': drug_data['expiry_date']
                }
            )
            if created:
                print(f"  Đã thêm thuốc: {drug.name} (Danh mục: {category.name})")
            else:
                print(f"  Thuốc đã tồn tại: {drug.name}")
    
    # Drugs for "Thuốc giảm đau, hạ sốt" category
    if categories.filter(name='Thuốc giảm đau, hạ sốt').exists():
        category = categories.get(name='Thuốc giảm đau, hạ sốt')
        drugs_data = [
            {
                'name': 'Paracetamol',
                'description': 'Thuốc giảm đau, hạ sốt thông dụng',
                'composition': 'Paracetamol 500mg',
                'usage': 'Uống, cách nhau ít nhất 4 giờ',
                'dosage': 'Người lớn: 500-1000mg, 3-4 lần/ngày. Trẻ em: 10-15mg/kg/lần, 3-4 lần/ngày',
                'side_effects': 'Hiếm gặp: phát ban, độc tính gan khi dùng liều cao',
                'contraindications': 'Suy gan nặng, quá mẫn với paracetamol',
                'price': Decimal('25000'),
                'stock': 300,
                'manufacturer': 'Công ty dược phẩm Đông Dược',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Ibuprofen',
                'description': 'Thuốc kháng viêm không steroid (NSAID)',
                'composition': 'Ibuprofen 400mg',
                'usage': 'Uống sau bữa ăn, cách nhau ít nhất 6 giờ',
                'dosage': 'Người lớn: 200-400mg, 3-4 lần/ngày. Trẻ em: 5-10mg/kg/lần, 3-4 lần/ngày',
                'side_effects': 'Đau dạ dày, buồn nôn, tiêu chảy, chóng mặt',
                'contraindications': 'Loét dạ dày, tiền sử dị ứng với NSAID, suy thận nặng',
                'price': Decimal('45000'),
                'stock': 180,
                'manufacturer': 'Adco',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=640)
            }
        ]
        
        for drug_data in drugs_data:
            drug, created = Drug.objects.get_or_create(
                name=drug_data['name'],
                defaults={
                    'category': category,
                    'description': drug_data['description'],
                    'composition': drug_data['composition'],
                    'usage': drug_data['usage'],
                    'dosage': drug_data['dosage'],
                    'side_effects': drug_data['side_effects'],
                    'contraindications': drug_data['contraindications'],
                    'price': drug_data['price'],
                    'stock': drug_data['stock'],
                    'manufacturer': drug_data['manufacturer'],
                    'expiry_date': drug_data['expiry_date']
                }
            )
            if created:
                print(f"  Đã thêm thuốc: {drug.name} (Danh mục: {category.name})")
            else:
                print(f"  Thuốc đã tồn tại: {drug.name}")
    
    # Drugs for "Thuốc tim mạch" category
    if categories.filter(name='Thuốc tim mạch').exists():
        category = categories.get(name='Thuốc tim mạch')
        drugs_data = [
            {
                'name': 'Amlodipine',
                'description': 'Thuốc chẹn kênh canxi',
                'composition': 'Amlodipine besylate tương đương 5mg amlodipine',
                'usage': 'Uống 1 lần/ngày, có thể dùng bất kể bữa ăn',
                'dosage': 'Người lớn: Bắt đầu 5mg/ngày, có thể tăng lên 10mg/ngày',
                'side_effects': 'Phù mắt cá chân, đau đầu, đỏ mặt',
                'contraindications': 'Hạ huyết áp nặng, sốc tim',
                'price': Decimal('55000'),
                'stock': 150,
                'manufacturer': 'Pfizer',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Atorvastatin',
                'description': 'Thuốc nhóm statin hạ lipid máu',
                'composition': 'Atorvastatin calcium tương đương 20mg atorvastatin',
                'usage': 'Uống 1 lần/ngày, tốt nhất vào buổi tối',
                'dosage': 'Người lớn: 10-80mg/ngày tùy mức độ tăng cholesterol',
                'side_effects': 'Đau cơ, tăng men gan, tiêu chảy',
                'contraindications': 'Bệnh gan hoạt động, phụ nữ mang thai',
                'price': Decimal('85000'),
                'stock': 120,
                'manufacturer': 'Pfizer',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            }
        ]
        
        for drug_data in drugs_data:
            drug, created = Drug.objects.get_or_create(
                name=drug_data['name'],
                defaults={
                    'category': category,
                    'description': drug_data['description'],
                    'composition': drug_data['composition'],
                    'usage': drug_data['usage'],
                    'dosage': drug_data['dosage'],
                    'side_effects': drug_data['side_effects'],
                    'contraindications': drug_data['contraindications'],
                    'price': drug_data['price'],
                    'stock': drug_data['stock'],
                    'manufacturer': drug_data['manufacturer'],
                    'expiry_date': drug_data['expiry_date']
                }
            )
            if created:
                print(f"  Đã thêm thuốc: {drug.name} (Danh mục: {category.name})")
            else:
                print(f"  Thuốc đã tồn tại: {drug.name}")

def add_medicines_and_inventory():
    """Add medicines and inventory for diversity"""
    medicines_data = [
        {
            'name': 'Augmentin 500mg',
            'description': 'Kháng sinh phối hợp amoxicillin và acid clavulanic',
            'price': Decimal('120000'),
            'inventory': {'quantity': 100, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Cefalexin 500mg',
            'description': 'Kháng sinh cephalosporin thế hệ 1',
            'price': Decimal('70000'),
            'inventory': {'quantity': 150, 'unit': 'viên', 'min_quantity': 30}
        },
        {
            'name': 'Meloxicam 7.5mg',
            'description': 'Thuốc chống viêm không steroid',
            'price': Decimal('65000'),
            'inventory': {'quantity': 80, 'unit': 'viên', 'min_quantity': 15}
        },
        {
            'name': 'Loratadin 10mg',
            'description': 'Thuốc kháng histamin H1 thế hệ 2',
            'price': Decimal('45000'),
            'inventory': {'quantity': 120, 'unit': 'viên', 'min_quantity': 25}
        },
        {
            'name': 'Metformin 500mg',
            'description': 'Thuốc uống điều trị đái tháo đường type 2',
            'price': Decimal('55000'),
            'inventory': {'quantity': 200, 'unit': 'viên', 'min_quantity': 40}
        },
        {
            'name': 'Acyclovir 400mg',
            'description': 'Thuốc kháng virus',
            'price': Decimal('80000'),
            'inventory': {'quantity': 60, 'unit': 'viên', 'min_quantity': 10}
        },
        {
            'name': 'Prednisolone 5mg',
            'description': 'Thuốc chống viêm steroid',
            'price': Decimal('50000'),
            'inventory': {'quantity': 90, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Vitamin tổng hợp',
            'description': 'Bổ sung vitamin và khoáng chất',
            'price': Decimal('150000'),
            'inventory': {'quantity': 180, 'unit': 'viên', 'min_quantity': 30}
        },
        {
            'name': 'Calcium 500mg',
            'description': 'Bổ sung canxi',
            'price': Decimal('90000'),
            'inventory': {'quantity': 150, 'unit': 'viên', 'min_quantity': 25}
        },
        {
            'name': 'Cipro 500mg',
            'description': 'Kháng sinh nhóm quinolone',
            'price': Decimal('110000'),
            'inventory': {'quantity': 75, 'unit': 'viên', 'min_quantity': 15}
        },
        {
            'name': 'Ventolin 100mcg',
            'description': 'Thuốc giãn phế quản dạng xịt',
            'price': Decimal('180000'),
            'inventory': {'quantity': 30, 'unit': 'bình xịt', 'min_quantity': 5}
        },
        {
            'name': 'Omeprazole 20mg',
            'description': 'Thuốc ức chế bơm proton',
            'price': Decimal('85000'),
            'inventory': {'quantity': 120, 'unit': 'viên', 'min_quantity': 25}
        },
        {
            'name': 'Glucosamin 500mg',
            'description': 'Hỗ trợ điều trị thoái hóa khớp',
            'price': Decimal('200000'),
            'inventory': {'quantity': 60, 'unit': 'viên', 'min_quantity': 10}
        },
        {
            'name': 'Fluconazole 150mg',
            'description': 'Thuốc chống nấm',
            'price': Decimal('70000'),
            'inventory': {'quantity': 30, 'unit': 'viên', 'min_quantity': 5}
        },
        {
            'name': 'Esomeprazole 40mg',
            'description': 'Thuốc ức chế bơm proton',
            'price': Decimal('95000'),
            'inventory': {'quantity': 90, 'unit': 'viên', 'min_quantity': 15}
        }
    ]
    
    for medicine_data in medicines_data:
        medicine, created = Medicine.objects.get_or_create(
            name=medicine_data['name'],
            defaults={
                'description': medicine_data['description'],
                'price': medicine_data['price']
            }
        )
        
        if created:
            print(f"  Đã thêm thuốc: {medicine.name}")
            
            # Create inventory for new medicine
            inventory_data = medicine_data['inventory']
            inventory = Inventory.objects.create(
                medicine=medicine,
                quantity=inventory_data['quantity'],
                unit=inventory_data['unit'],
                min_quantity=inventory_data['min_quantity']
            )
            print(f"  Đã thêm tồn kho: {inventory.medicine.name} - {inventory.quantity} {inventory.unit}")
        else:
            print(f"  Thuốc đã tồn tại: {medicine.name}")
            
            # Update inventory if it exists, create if it doesn't
            inventory, inv_created = Inventory.objects.get_or_create(
                medicine=medicine,
                defaults={
                    'quantity': medicine_data['inventory']['quantity'],
                    'unit': medicine_data['inventory']['unit'],
                    'min_quantity': medicine_data['inventory']['min_quantity']
                }
            )
            
            if inv_created:
                print(f"  Đã thêm tồn kho: {inventory.medicine.name} - {inventory.quantity} {inventory.unit}")
            else:
                print(f"  Tồn kho đã tồn tại: {inventory.medicine.name} - {inventory.quantity} {inventory.unit}")

if __name__ == '__main__':
    print("Đang thêm danh mục thuốc đa dạng...")
    add_drug_categories()
    
    print("\nĐang thêm thuốc đa dạng...")
    add_drugs()
    
    print("\nĐang thêm thuốc và tồn kho đa dạng...")
    add_medicines_and_inventory()
    
    print("\nHoàn thành việc thêm dữ liệu thuốc và tồn kho!") 