import os
import django
import datetime
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from pharmacy.models import DrugCategory, Drug, Medicine, Inventory

def add_missing_drug_categories():
    """Add missing drug categories"""
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

def add_missing_drugs():
    """Add missing drugs to each category"""
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
                
    # Drugs for "Thuốc hô hấp" category
    if categories.filter(name='Thuốc hô hấp').exists():
        category = categories.get(name='Thuốc hô hấp')
        drugs_data = [
            {
                'name': 'Salbutamol',
                'description': 'Thuốc giãn phế quản',
                'composition': 'Salbutamol sulfate tương đương 2mg salbutamol',
                'usage': 'Uống 3-4 lần/ngày hoặc dùng dạng xịt khi cần',
                'dosage': 'Người lớn: 2-4mg, 3-4 lần/ngày. Dạng xịt: 100-200mcg khi cần',
                'side_effects': 'Tim đập nhanh, run tay, đau đầu',
                'contraindications': 'Quá mẫn với salbutamol, rối loạn nhịp tim',
                'price': Decimal('65000'),
                'stock': 100,
                'manufacturer': 'GlaxoSmithKline',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Montelukast',
                'description': 'Thuốc điều trị hen suyễn và viêm mũi dị ứng',
                'composition': 'Montelukast sodium tương đương 10mg montelukast',
                'usage': 'Uống 1 lần/ngày vào buổi tối',
                'dosage': 'Người lớn: 10mg/ngày. Trẻ em: 4-5mg/ngày tùy tuổi',
                'side_effects': 'Đau đầu, mệt mỏi, rối loạn giấc ngủ',
                'contraindications': 'Quá mẫn với montelukast',
                'price': Decimal('95000'),
                'stock': 90,
                'manufacturer': 'Merck',
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

def add_medicines_inventory():
    """Update medicines with prices and inventory"""
    medicines = Medicine.objects.all()
    
    # Update Augmentin's inventory if it exists
    augmentin = medicines.filter(name='Augmentin 500mg').first()
    if augmentin:
        if not Inventory.objects.filter(medicine=augmentin).exists():
            Inventory.objects.create(
                medicine=augmentin,
                quantity=100,
                unit='viên',
                min_quantity=20
            )
            print(f"  Đã thêm tồn kho: {augmentin.name} - 100 viên")
        
        # Update price if it's 0
        if augmentin.price == 0:
            augmentin.price = Decimal('120000')
            augmentin.save()
            print(f"  Đã cập nhật giá: {augmentin.name} - {augmentin.price}")
    
    # Update Paracetamol's price and inventory if it exists
    paracetamol = medicines.filter(name='Paracetamol').first()
    if paracetamol:
        if not Inventory.objects.filter(medicine=paracetamol).exists():
            Inventory.objects.create(
                medicine=paracetamol,
                quantity=250,
                unit='viên',
                min_quantity=50
            )
            print(f"  Đã thêm tồn kho: {paracetamol.name} - 250 viên")
        
        # Update price if it's 0
        if paracetamol.price == 0:
            paracetamol.price = Decimal('25000')
            paracetamol.save()
            print(f"  Đã cập nhật giá: {paracetamol.name} - {paracetamol.price}")

if __name__ == '__main__':
    print("Đang thêm danh mục thuốc còn thiếu...")
    add_missing_drug_categories()
    
    print("\nĐang thêm thuốc còn thiếu...")
    add_missing_drugs()
    
    print("\nĐang cập nhật giá và tồn kho...")
    add_medicines_inventory()
    
    print("\nHoàn thành việc thêm dữ liệu!") 