import os
import django
import datetime
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from pharmacy.models import DrugCategory, Drug, Medicine, Inventory

def add_special_categories():
    """Add specialized drug categories"""
    categories = [
        {
            'name': 'Thuốc điều trị ung thư',
            'description': 'Nhóm thuốc dùng trong điều trị các bệnh ung thư.'
        },
        {
            'name': 'Thuốc điều trị thần kinh',
            'description': 'Nhóm thuốc tác động lên hệ thần kinh để điều trị các rối loạn thần kinh.'
        },
        {
            'name': 'Thuốc điều trị xương khớp',
            'description': 'Nhóm thuốc dùng điều trị các bệnh về xương và khớp.'
        },
        {
            'name': 'Thuốc điều trị bệnh tự miễn',
            'description': 'Nhóm thuốc dùng điều trị các bệnh tự miễn.'
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

def add_special_drugs():
    """Add specialized drugs to categories"""
    categories = DrugCategory.objects.all()
    
    # Drugs for "Thuốc điều trị ung thư" category
    if categories.filter(name='Thuốc điều trị ung thư').exists():
        category = categories.get(name='Thuốc điều trị ung thư')
        drugs_data = [
            {
                'name': 'Tamoxifen',
                'description': 'Thuốc điều trị ung thư vú, chống estrogen',
                'composition': 'Tamoxifen citrate tương đương 20mg tamoxifen',
                'usage': 'Uống 1-2 lần/ngày',
                'dosage': 'Điều trị ung thư vú: 20mg/ngày trong 5 năm',
                'side_effects': 'Bốc hỏa, rối loạn kinh nguyệt, tăng nguy cơ huyết khối',
                'contraindications': 'Thai kỳ, tiền sử huyết khối tĩnh mạch sâu',
                'price': Decimal('250000'),
                'stock': 30,
                'manufacturer': 'AstraZeneca',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Cyclophosphamide',
                'description': 'Thuốc hóa trị nhóm alkyl hóa',
                'composition': 'Cyclophosphamide 50mg',
                'usage': 'Uống theo chỉ định của bác sĩ chuyên khoa',
                'dosage': 'Liều lượng tùy theo phác đồ điều trị, thông thường 100-200mg/ngày',
                'side_effects': 'Ức chế tủy xương, buồn nôn, nôn, rụng tóc, viêm bàng quang',
                'contraindications': 'Suy tủy xương nặng, mang thai, cho con bú',
                'price': Decimal('180000'),
                'stock': 20,
                'manufacturer': 'Baxter Oncology',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Methotrexate',
                'description': 'Thuốc chống chuyển hóa nhóm kháng folate',
                'composition': 'Methotrexate 2.5mg',
                'usage': 'Uống theo chỉ định của bác sĩ chuyên khoa',
                'dosage': 'Liều lượng tùy theo bệnh lý và phác đồ điều trị',
                'side_effects': 'Ức chế tủy xương, loét miệng, rối loạn tiêu hóa, độc tính gan',
                'contraindications': 'Suy gan, suy thận, mang thai, cho con bú',
                'price': Decimal('120000'),
                'stock': 25,
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
    
    # Drugs for "Thuốc điều trị thần kinh" category
    if categories.filter(name='Thuốc điều trị thần kinh').exists():
        category = categories.get(name='Thuốc điều trị thần kinh')
        drugs_data = [
            {
                'name': 'Escitalopram',
                'description': 'Thuốc chống trầm cảm nhóm SSRI',
                'composition': 'Escitalopram oxalate tương đương 10mg escitalopram',
                'usage': 'Uống 1 lần/ngày, sáng hoặc tối',
                'dosage': 'Điều trị trầm cảm: 10mg/ngày, có thể tăng lên 20mg/ngày sau 1 tuần',
                'side_effects': 'Buồn nôn, mất ngủ, tăng tiết mồ hôi, rối loạn tình dục',
                'contraindications': 'Đồng thời dùng với MAOI, kéo dài QT',
                'price': Decimal('150000'),
                'stock': 60,
                'manufacturer': 'Lundbeck',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Risperidone',
                'description': 'Thuốc chống loạn thần thế hệ 2',
                'composition': 'Risperidone 2mg',
                'usage': 'Uống 1-2 lần/ngày',
                'dosage': 'Tâm thần phân liệt: 4-6mg/ngày chia 1-2 lần',
                'side_effects': 'Khó ngủ, bồn chồn, tăng prolactin, tăng cân',
                'contraindications': 'Quá mẫn với risperidone',
                'price': Decimal('95000'),
                'stock': 40,
                'manufacturer': 'Janssen',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Valproic Acid',
                'description': 'Thuốc chống động kinh',
                'composition': 'Valproic acid 500mg',
                'usage': 'Uống 2-3 lần/ngày cùng bữa ăn',
                'dosage': 'Liều lượng cá nhân hóa, thường bắt đầu 500mg/ngày và tăng dần',
                'side_effects': 'Buồn nôn, run tay, tăng cân, rụng tóc, rối loạn gan',
                'contraindications': 'Bệnh gan, rối loạn chu trình urê, mang thai',
                'price': Decimal('120000'),
                'stock': 50,
                'manufacturer': 'Sanofi',
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
                
    # Drugs for "Thuốc điều trị xương khớp" category
    if categories.filter(name='Thuốc điều trị xương khớp').exists():
        category = categories.get(name='Thuốc điều trị xương khớp')
        drugs_data = [
            {
                'name': 'Alendronat',
                'description': 'Thuốc điều trị loãng xương nhóm bisphosphonate',
                'composition': 'Alendronate sodium tương đương 70mg alendronic acid',
                'usage': 'Uống 1 lần/tuần vào buổi sáng khi thức dậy, trước khi ăn 30 phút',
                'dosage': 'Điều trị loãng xương: 70mg mỗi tuần 1 lần',
                'side_effects': 'Đau cơ, đau khớp, ợ nóng, khó tiêu',
                'contraindications': 'Hẹp thực quản, không thể đứng hoặc ngồi thẳng ít nhất 30 phút',
                'price': Decimal('180000'),
                'stock': 40,
                'manufacturer': 'Merck',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Chondroitin Sulfate',
                'description': 'Thuốc điều trị thoái hóa khớp',
                'composition': 'Chondroitin sulfate 400mg',
                'usage': 'Uống 1-3 lần/ngày',
                'dosage': 'Điều trị thoái hóa khớp: 800-1200mg/ngày',
                'side_effects': 'Nhẹ: buồn nôn, đau bụng, tiêu chảy',
                'contraindications': 'Quá mẫn với chondroitin',
                'price': Decimal('220000'),
                'stock': 60,
                'manufacturer': 'Bioiberica',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Celecoxib',
                'description': 'Thuốc chống viêm không steroid chọn lọc COX-2',
                'composition': 'Celecoxib 200mg',
                'usage': 'Uống 1-2 lần/ngày',
                'dosage': 'Viêm khớp dạng thấp: 100-200mg, 2 lần/ngày',
                'side_effects': 'Đau bụng, khó tiêu, tăng nguy cơ tim mạch',
                'contraindications': 'Dị ứng với sulfonamide, bệnh tim mạch nặng',
                'price': Decimal('150000'),
                'stock': 45,
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
                
    # Drugs for "Thuốc điều trị bệnh tự miễn" category
    if categories.filter(name='Thuốc điều trị bệnh tự miễn').exists():
        category = categories.get(name='Thuốc điều trị bệnh tự miễn')
        drugs_data = [
            {
                'name': 'Adalimumab',
                'description': 'Thuốc sinh học kháng TNF-alpha điều trị bệnh tự miễn',
                'composition': 'Adalimumab 40mg/0.8ml',
                'usage': 'Tiêm dưới da 2 tuần/lần',
                'dosage': 'Viêm khớp dạng thấp: 40mg, 2 tuần/lần',
                'side_effects': 'Phản ứng tại chỗ tiêm, nhiễm trùng, suy giảm miễn dịch',
                'contraindications': 'Lao hoạt động, nhiễm trùng nặng, suy tim độ III-IV',
                'price': Decimal('7500000'),
                'stock': 10,
                'manufacturer': 'AbbVie',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Hydroxychloroquine',
                'description': 'Thuốc điều trị lupus ban đỏ và viêm khớp dạng thấp',
                'composition': 'Hydroxychloroquine sulfate 200mg',
                'usage': 'Uống 1-2 lần/ngày cùng bữa ăn',
                'dosage': 'Lupus ban đỏ: 200-400mg/ngày',
                'side_effects': 'Buồn nôn, tiêu chảy, đau đầu, tổn thương võng mạc',
                'contraindications': 'Bệnh lý võng mạc, quá mẫn với 4-aminoquinoline',
                'price': Decimal('180000'),
                'stock': 35,
                'manufacturer': 'Sanofi',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Azathioprine',
                'description': 'Thuốc ức chế miễn dịch điều trị bệnh tự miễn',
                'composition': 'Azathioprine 50mg',
                'usage': 'Uống 1-2 lần/ngày cùng bữa ăn',
                'dosage': 'Liều khởi đầu 1mg/kg/ngày, có thể tăng lên 2-2.5mg/kg/ngày',
                'side_effects': 'Ức chế tủy xương, buồn nôn, nôn, tiêu chảy',
                'contraindications': 'Quá mẫn với azathioprine, mang thai, cho con bú',
                'price': Decimal('160000'),
                'stock': 25,
                'manufacturer': 'GlaxoSmithKline',
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

def add_final_medicines_and_inventory():
    """Add final medicines and inventory"""
    medicines_data = [
        {
            'name': 'Infliximab 100mg',
            'description': 'Thuốc sinh học kháng TNF-alpha, dạng truyền tĩnh mạch',
            'price': Decimal('9000000'),
            'inventory': {'quantity': 5, 'unit': 'lọ', 'min_quantity': 2}
        },
        {
            'name': 'Tacrolimus 1mg',
            'description': 'Thuốc ức chế miễn dịch dùng sau ghép tạng',
            'price': Decimal('320000'),
            'inventory': {'quantity': 20, 'unit': 'viên', 'min_quantity': 5}
        },
        {
            'name': 'Levetiracetam 500mg',
            'description': 'Thuốc chống động kinh thế hệ mới',
            'price': Decimal('280000'),
            'inventory': {'quantity': 40, 'unit': 'viên', 'min_quantity': 10}
        },
        {
            'name': 'Interferon beta-1a',
            'description': 'Thuốc điều trị xơ cứng rải rác (MS)',
            'price': Decimal('4500000'),
            'inventory': {'quantity': 8, 'unit': 'bơm tiêm', 'min_quantity': 2}
        },
        {
            'name': 'Pregabalin 75mg',
            'description': 'Thuốc điều trị đau thần kinh và động kinh',
            'price': Decimal('200000'),
            'inventory': {'quantity': 30, 'unit': 'viên', 'min_quantity': 10}
        },
        {
            'name': 'Phenytoin 100mg',
            'description': 'Thuốc chống động kinh cổ điển',
            'price': Decimal('85000'),
            'inventory': {'quantity': 50, 'unit': 'viên', 'min_quantity': 15}
        },
        {
            'name': 'Vắc-xin phế cầu',
            'description': 'Vắc-xin phòng ngừa nhiễm khuẩn phế cầu',
            'price': Decimal('850000'),
            'inventory': {'quantity': 15, 'unit': 'liều', 'min_quantity': 5}
        },
        {
            'name': 'Vắc-xin cúm mùa',
            'description': 'Vắc-xin phòng ngừa cúm theo mùa',
            'price': Decimal('280000'),
            'inventory': {'quantity': 30, 'unit': 'liều', 'min_quantity': 10}
        },
        {
            'name': 'Erythropoietin 4000 IU',
            'description': 'Thuốc điều trị thiếu máu do suy thận mạn',
            'price': Decimal('380000'),
            'inventory': {'quantity': 20, 'unit': 'bơm tiêm', 'min_quantity': 5}
        },
        {
            'name': 'Rituximab 500mg',
            'description': 'Thuốc sinh học điều trị u lympho không Hodgkin và các bệnh tự miễn',
            'price': Decimal('12000000'),
            'inventory': {'quantity': 3, 'unit': 'lọ', 'min_quantity': 1}
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
    print("Đang thêm danh mục thuốc đặc biệt...")
    add_special_categories()
    
    print("\nĐang thêm thuốc đặc biệt vào các danh mục...")
    add_special_drugs()
    
    print("\nĐang thêm thuốc và tồn kho đặc biệt...")
    add_final_medicines_and_inventory()
    
    print("\nHoàn thành việc thêm dữ liệu thuốc và tồn kho đặc biệt!") 