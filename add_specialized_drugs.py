import os
import django
import datetime
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from pharmacy.models import DrugCategory, Drug, Medicine, Inventory

def add_specialized_category():
    """Add specialized drug categories"""
    categories = [
        {
            'name': 'Thuốc đường tiết niệu',
            'description': 'Nhóm thuốc điều trị các bệnh lý về đường tiết niệu và sinh dục.'
        },
        {
            'name': 'Thuốc nhỏ mắt',
            'description': 'Nhóm thuốc dùng điều trị các bệnh về mắt.'
        },
        {
            'name': 'Thuốc kháng virus',
            'description': 'Nhóm thuốc kháng virus dùng điều trị các bệnh nhiễm virus.'
        },
        {
            'name': 'Thuốc tiêm và truyền',
            'description': 'Nhóm thuốc dùng đường tiêm và truyền tĩnh mạch.'
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

def add_specialized_drugs():
    """Add specialized drugs to categories"""
    categories = DrugCategory.objects.all()
    
    # Drugs for "Thuốc đường tiết niệu" category
    if categories.filter(name='Thuốc đường tiết niệu').exists():
        category = categories.get(name='Thuốc đường tiết niệu')
        drugs_data = [
            {
                'name': 'Tamsulosin',
                'description': 'Thuốc điều trị phì đại lành tính tuyến tiền liệt',
                'composition': 'Tamsulosin hydrochloride 0.4mg',
                'usage': 'Uống 1 lần/ngày sau bữa ăn sáng',
                'dosage': 'Người lớn: 0.4mg/ngày',
                'side_effects': 'Chóng mặt, đau đầu, xuất tinh bất thường',
                'contraindications': 'Quá mẫn với tamsulosin, hạ huyết áp nặng',
                'price': Decimal('120000'),
                'stock': 60,
                'manufacturer': 'Astellas Pharma',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Ciprofloxacin',
                'description': 'Kháng sinh nhóm quinolone điều trị nhiễm khuẩn đường tiết niệu',
                'composition': 'Ciprofloxacin hydrochloride tương đương 500mg ciprofloxacin',
                'usage': 'Uống 2 lần/ngày, trước hoặc giữa các bữa ăn',
                'dosage': 'Người lớn: 250-750mg, 2 lần/ngày tùy theo mức độ nhiễm khuẩn',
                'side_effects': 'Buồn nôn, tiêu chảy, đau bụng, đau đầu',
                'contraindications': 'Quá mẫn với ciprofloxacin hoặc quinolones khác',
                'price': Decimal('85000'),
                'stock': 90,
                'manufacturer': 'Bayer',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Doxazosin',
                'description': 'Thuốc điều trị tăng huyết áp và phì đại tuyến tiền liệt',
                'composition': 'Doxazosin mesylate tương đương 4mg doxazosin',
                'usage': 'Uống 1 lần/ngày vào buổi sáng hoặc tối',
                'dosage': 'Khởi đầu 1mg/ngày, tăng dần đến 4-8mg/ngày',
                'side_effects': 'Chóng mặt, mệt mỏi, đau đầu, hạ huyết áp tư thế',
                'contraindications': 'Quá mẫn với doxazosin hoặc quinazolines khác',
                'price': Decimal('95000'),
                'stock': 70,
                'manufacturer': 'Pfizer',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
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
    
    # Drugs for "Thuốc nhỏ mắt" category
    if categories.filter(name='Thuốc nhỏ mắt').exists():
        category = categories.get(name='Thuốc nhỏ mắt')
        drugs_data = [
            {
                'name': 'Timolol',
                'description': 'Thuốc nhỏ mắt điều trị glaucoma (tăng nhãn áp)',
                'composition': 'Timolol maleate 0.5% (5mg/ml)',
                'usage': 'Nhỏ 1 giọt vào mắt bị bệnh, 2 lần/ngày',
                'dosage': '1 giọt vào mắt bị bệnh, 2 lần/ngày (sáng và tối)',
                'side_effects': 'Rát mắt, mờ mắt tạm thời, nhức đầu',
                'contraindications': 'Bệnh nhân hen suyễn, suy tim, nhịp tim chậm',
                'price': Decimal('90000'),
                'stock': 40,
                'manufacturer': 'Merck',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Tobramycin',
                'description': 'Thuốc nhỏ mắt kháng sinh điều trị nhiễm khuẩn mắt',
                'composition': 'Tobramycin 0.3% (3mg/ml)',
                'usage': 'Nhỏ 1-2 giọt vào mắt bị bệnh, 4-6 lần/ngày',
                'dosage': 'Nhiễm khuẩn nặng: 1-2 giọt mỗi 1 giờ, giảm dần khi cải thiện',
                'side_effects': 'Kích ứng mắt, ngứa, rát, mờ mắt tạm thời',
                'contraindications': 'Quá mẫn với tobramycin hoặc bất kỳ aminoglycoside nào',
                'price': Decimal('75000'),
                'stock': 50,
                'manufacturer': 'Novartis',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Artificial Tears',
                'description': 'Dung dịch nhỏ mắt nhân tạo điều trị khô mắt',
                'composition': 'Hypromellose 0.3%, Dextran 70 0.1%',
                'usage': 'Nhỏ 1-2 giọt vào mắt khi cần thiết',
                'dosage': '1-2 giọt vào mắt khi cần, có thể dùng nhiều lần trong ngày',
                'side_effects': 'Hiếm gặp: mờ mắt tạm thời, cảm giác rát nhẹ',
                'contraindications': 'Quá mẫn với bất kỳ thành phần nào của thuốc',
                'price': Decimal('65000'),
                'stock': 100,
                'manufacturer': 'Alcon',
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
                
    # Drugs for "Thuốc kháng virus" category
    if categories.filter(name='Thuốc kháng virus').exists():
        category = categories.get(name='Thuốc kháng virus')
        drugs_data = [
            {
                'name': 'Oseltamivir',
                'description': 'Thuốc kháng virus điều trị và dự phòng cúm A và B',
                'composition': 'Oseltamivir phosphate tương đương 75mg oseltamivir',
                'usage': 'Uống 2 lần/ngày cùng thức ăn trong 5 ngày',
                'dosage': 'Điều trị: 75mg, 2 lần/ngày trong 5 ngày. Dự phòng: 75mg, 1 lần/ngày trong 10 ngày',
                'side_effects': 'Buồn nôn, nôn, đau đầu, mệt mỏi',
                'contraindications': 'Quá mẫn với oseltamivir hoặc bất kỳ thành phần nào của thuốc',
                'price': Decimal('150000'),
                'stock': 40,
                'manufacturer': 'Roche',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Acyclovir',
                'description': 'Thuốc kháng virus herpes',
                'composition': 'Acyclovir 200mg',
                'usage': 'Uống 5 lần/ngày, cách nhau 4 giờ (bỏ liều ban đêm)',
                'dosage': 'Herpes sinh dục: 200mg, 5 lần/ngày trong 10 ngày',
                'side_effects': 'Buồn nôn, nôn, tiêu chảy, đau đầu',
                'contraindications': 'Quá mẫn với acyclovir hoặc valacyclovir',
                'price': Decimal('80000'),
                'stock': 60,
                'manufacturer': 'GlaxoSmithKline',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Valganciclovir',
                'description': 'Thuốc kháng virus điều trị nhiễm cytomegalovirus (CMV)',
                'composition': 'Valganciclovir hydrochloride tương đương 450mg valganciclovir',
                'usage': 'Uống 2 lần/ngày cùng thức ăn',
                'dosage': 'Điều trị: 900mg, 2 lần/ngày trong 21 ngày. Dự phòng: 900mg, 1 lần/ngày',
                'side_effects': 'Giảm bạch cầu, thiếu máu, tiêu chảy, buồn nôn',
                'contraindications': 'Quá mẫn với valganciclovir hoặc ganciclovir',
                'price': Decimal('300000'),
                'stock': 20,
                'manufacturer': 'Roche',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
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
                
    # Drugs for "Thuốc tiêm và truyền" category
    if categories.filter(name='Thuốc tiêm và truyền').exists():
        category = categories.get(name='Thuốc tiêm và truyền')
        drugs_data = [
            {
                'name': 'Ceftriaxone',
                'description': 'Kháng sinh cephalosporin thế hệ 3 dạng tiêm',
                'composition': 'Ceftriaxone sodium tương đương 1g ceftriaxone',
                'usage': 'Tiêm bắp hoặc tiêm tĩnh mạch, 1-2 lần/ngày',
                'dosage': 'Người lớn: 1-2g/ngày, chia 1-2 lần tùy theo mức độ nhiễm khuẩn',
                'side_effects': 'Buồn nôn, tiêu chảy, phản ứng tại chỗ tiêm',
                'contraindications': 'Quá mẫn với cephalosporin, trẻ sơ sinh vàng da',
                'price': Decimal('85000'),
                'stock': 40,
                'manufacturer': 'Roche',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Furosemide',
                'description': 'Thuốc lợi tiểu quai dạng tiêm',
                'composition': 'Furosemide 20mg/2ml',
                'usage': 'Tiêm tĩnh mạch hoặc tiêm bắp',
                'dosage': 'Người lớn: 20-40mg/lần, có thể lặp lại sau 2 giờ nếu cần',
                'side_effects': 'Hạ kali máu, hạ huyết áp, mất nước và điện giải',
                'contraindications': 'Vô niệu, quá mẫn với furosemide, mất nước nặng',
                'price': Decimal('40000'),
                'stock': 80,
                'manufacturer': 'Sanofi',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Dextrose 5%',
                'description': 'Dung dịch truyền tĩnh mạch cung cấp nước và năng lượng',
                'composition': 'Dextrose 5% trong nước cất pha tiêm, 500ml',
                'usage': 'Truyền tĩnh mạch với tốc độ phù hợp',
                'dosage': 'Tùy theo tình trạng bệnh nhân và chỉ định của bác sĩ',
                'side_effects': 'Nhiễm khuẩn tại chỗ tiêm, tăng đường huyết nếu truyền nhanh',
                'contraindications': 'Hôn mê do tăng đường huyết, xuất huyết nội sọ cấp',
                'price': Decimal('35000'),
                'stock': 100,
                'manufacturer': 'B.Braun',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
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

def add_specialized_medicines_and_inventory():
    """Add specialized medicines and inventory"""
    medicines_data = [
        {
            'name': 'Clobetasol 0.05%',
            'description': 'Kem bôi corticosteroid mạnh điều trị bệnh vẩy nến, viêm da',
            'price': Decimal('110000'),
            'inventory': {'quantity': 30, 'unit': 'tuýp', 'min_quantity': 5}
        },
        {
            'name': 'Betamethasone 0.05%',
            'description': 'Kem bôi corticosteroid điều trị viêm da, chàm',
            'price': Decimal('95000'),
            'inventory': {'quantity': 40, 'unit': 'tuýp', 'min_quantity': 8}
        },
        {
            'name': 'Insulin NPH 100UI/ml',
            'description': 'Insulin tác dụng trung bình điều trị đái tháo đường',
            'price': Decimal('260000'),
            'inventory': {'quantity': 20, 'unit': 'lọ', 'min_quantity': 5}
        },
        {
            'name': 'Methylprednisolone 16mg',
            'description': 'Thuốc chống viêm steroid',
            'price': Decimal('70000'),
            'inventory': {'quantity': 60, 'unit': 'viên', 'min_quantity': 12}
        },
        {
            'name': 'Methylprednisolone 40mg/ml',
            'description': 'Thuốc chống viêm steroid dạng tiêm',
            'price': Decimal('130000'),
            'inventory': {'quantity': 25, 'unit': 'lọ', 'min_quantity': 5}
        },
        {
            'name': 'Ciprofloxacin 0.3%',
            'description': 'Dung dịch nhỏ tai kháng sinh',
            'price': Decimal('50000'),
            'inventory': {'quantity': 40, 'unit': 'lọ', 'min_quantity': 8}
        },
        {
            'name': 'NaCl 0.9%',
            'description': 'Dung dịch truyền tĩnh mạch cung cấp nước và điện giải',
            'price': Decimal('25000'),
            'inventory': {'quantity': 120, 'unit': 'chai', 'min_quantity': 20}
        },
        {
            'name': 'Atropine 1mg/ml',
            'description': 'Thuốc tiêm kháng cholinergic',
            'price': Decimal('45000'),
            'inventory': {'quantity': 30, 'unit': 'ống', 'min_quantity': 10}
        },
        {
            'name': 'Adrenaline 1mg/ml',
            'description': 'Thuốc tiêm cấp cứu phản vệ, ngừng tim',
            'price': Decimal('40000'),
            'inventory': {'quantity': 50, 'unit': 'ống', 'min_quantity': 15}
        },
        {
            'name': 'Lidocaine 2%',
            'description': 'Thuốc gây tê tại chỗ',
            'price': Decimal('35000'),
            'inventory': {'quantity': 40, 'unit': 'ống', 'min_quantity': 10}
        },
        {
            'name': 'Povidone Iodine 10%',
            'description': 'Dung dịch sát khuẩn',
            'price': Decimal('30000'),
            'inventory': {'quantity': 60, 'unit': 'chai', 'min_quantity': 10}
        },
        {
            'name': 'Mupirocin 2%',
            'description': 'Kem kháng sinh bôi ngoài da',
            'price': Decimal('65000'),
            'inventory': {'quantity': 35, 'unit': 'tuýp', 'min_quantity': 7}
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
    print("Đang thêm danh mục thuốc chuyên biệt...")
    add_specialized_category()
    
    print("\nĐang thêm thuốc chuyên biệt vào các danh mục...")
    add_specialized_drugs()
    
    print("\nĐang thêm thuốc và tồn kho chuyên biệt...")
    add_specialized_medicines_and_inventory()
    
    print("\nHoàn thành việc thêm dữ liệu thuốc và tồn kho chuyên biệt!") 