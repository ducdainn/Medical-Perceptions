import os
import django
import datetime
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revicare.settings')
django.setup()

from pharmacy.models import DrugCategory, Drug, Medicine, Inventory

def add_more_drugs():
    """Add more drugs to existing categories"""
    # Get all categories
    categories = DrugCategory.objects.all()
    
    # Drugs for "Thuốc tiêu hóa" category
    if categories.filter(name='Thuốc tiêu hóa').exists():
        category = categories.get(name='Thuốc tiêu hóa')
        drugs_data = [
            {
                'name': 'Pantoprazole',
                'description': 'Thuốc ức chế bơm proton điều trị loét dạ dày, trào ngược dạ dày thực quản',
                'composition': 'Pantoprazole sodium sesquihydrate tương đương 40mg pantoprazole',
                'usage': 'Uống 1 lần/ngày trước bữa ăn sáng',
                'dosage': 'Người lớn: 20-40mg/ngày, tùy theo tình trạng bệnh',
                'side_effects': 'Đau đầu, buồn nôn, đau bụng, tiêu chảy',
                'contraindications': 'Mẫn cảm với pantoprazole hoặc các thành phần khác của thuốc',
                'price': Decimal('75000'),
                'stock': 120,
                'manufacturer': 'Takeda Pharmaceuticals',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Mebeverine',
                'description': 'Thuốc chống co thắt điều trị hội chứng ruột kích thích',
                'composition': 'Mebeverine hydrochloride 135mg',
                'usage': 'Uống 3 lần/ngày trước bữa ăn 20 phút',
                'dosage': 'Người lớn: 135mg, 3 lần/ngày',
                'side_effects': 'Hiếm gặp: phản ứng dị ứng, chóng mặt',
                'contraindications': 'Mẫn cảm với mebeverine, bệnh nhân bị tắc ruột cơ học',
                'price': Decimal('65000'),
                'stock': 90,
                'manufacturer': 'Abbott',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Domperidone',
                'description': 'Thuốc điều trị các rối loạn nhu động dạ dày, nôn và buồn nôn',
                'composition': 'Domperidone 10mg',
                'usage': 'Uống 3-4 lần/ngày, 15-30 phút trước bữa ăn',
                'dosage': 'Người lớn: 10mg, 3-4 lần/ngày. Tối đa 40mg/ngày',
                'side_effects': 'Đau đầu, buồn nôn, khô miệng, đôi khi gây rối loạn nhịp tim',
                'contraindications': 'Suy gan nặng, tình trạng có thể bị ảnh hưởng bởi kích thích nhu động dạ dày-ruột',
                'price': Decimal('45000'),
                'stock': 150,
                'manufacturer': 'Janssen Pharmaceutica',
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
    
    # Drugs for "Thuốc da liễu" category
    if categories.filter(name='Thuốc da liễu').exists():
        category = categories.get(name='Thuốc da liễu')
        drugs_data = [
            {
                'name': 'Mometasone Furoate',
                'description': 'Kem corticosteroid điều trị viêm da, chàm',
                'composition': 'Mometasone furoate 0.1% (1mg/g)',
                'usage': 'Bôi lên vùng da bị bệnh ngày 1 lần',
                'dosage': 'Bôi một lớp mỏng lên vùng da bị bệnh, ngày 1 lần',
                'side_effects': 'Nóng rát, ngứa, bỏng rát, khô da tại chỗ',
                'contraindications': 'Mẫn cảm với thành phần của thuốc, nhiễm khuẩn da',
                'price': Decimal('120000'),
                'stock': 50,
                'manufacturer': 'Schering-Plough',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Adapalene',
                'description': 'Gel điều trị mụn trứng cá',
                'composition': 'Adapalene 0.1% (1mg/g)',
                'usage': 'Bôi lên vùng da bị mụn ngày 1 lần vào buổi tối',
                'dosage': 'Bôi một lớp mỏng lên vùng da bị mụn, ngày 1 lần vào buổi tối',
                'side_effects': 'Khô da, đỏ da, kích ứng, bong tróc',
                'contraindications': 'Mẫn cảm với adapalene hoặc bất kỳ thành phần nào của thuốc',
                'price': Decimal('160000'),
                'stock': 40,
                'manufacturer': 'Galderma',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Ketoconazole',
                'description': 'Thuốc kháng nấm dạng kem điều trị các bệnh nhiễm nấm ngoài da',
                'composition': 'Ketoconazole 2% (20mg/g)',
                'usage': 'Bôi lên vùng da bị bệnh ngày 1-2 lần',
                'dosage': 'Bôi một lớp mỏng lên vùng da bị bệnh, ngày 1-2 lần trong 2-4 tuần',
                'side_effects': 'Kích ứng da, ngứa, bỏng rát tại chỗ',
                'contraindications': 'Mẫn cảm với ketoconazole hoặc các thành phần khác của thuốc',
                'price': Decimal('85000'),
                'stock': 70,
                'manufacturer': 'Janssen Pharmaceutica',
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
                
    # Drugs for "Thuốc nội tiết" category
    if categories.filter(name='Thuốc nội tiết').exists():
        category = categories.get(name='Thuốc nội tiết')
        drugs_data = [
            {
                'name': 'Levothyroxine',
                'description': 'Hormone tuyến giáp tổng hợp điều trị suy giáp',
                'composition': 'Levothyroxine sodium tương đương 100mcg levothyroxine',
                'usage': 'Uống 1 lần/ngày vào buổi sáng lúc đói',
                'dosage': 'Liều lượng cá nhân hóa, thường bắt đầu 50-100mcg/ngày và điều chỉnh theo kết quả xét nghiệm',
                'side_effects': 'Nhịp tim nhanh, đau đầu, mất ngủ, tiêu chảy (khi dùng liều cao)',
                'contraindications': 'Cường giáp chưa điều trị, nhồi máu cơ tim cấp',
                'price': Decimal('65000'),
                'stock': 120,
                'manufacturer': 'Abbott',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Insulin Glargine',
                'description': 'Insulin tác dụng kéo dài điều trị đái tháo đường',
                'composition': 'Insulin glargine 100 UI/ml',
                'usage': 'Tiêm dưới da 1 lần/ngày vào cùng một thời điểm',
                'dosage': 'Liều lượng cá nhân hóa theo nhu cầu của bệnh nhân',
                'side_effects': 'Hạ đường huyết, phản ứng tại chỗ tiêm',
                'contraindications': 'Mẫn cảm với insulin glargine, hạ đường huyết',
                'price': Decimal('350000'),
                'stock': 40,
                'manufacturer': 'Sanofi-Aventis',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
            },
            {
                'name': 'Gliclazide',
                'description': 'Thuốc hạ đường huyết dạng uống nhóm sulfonylurea',
                'composition': 'Gliclazide 80mg',
                'usage': 'Uống trước bữa ăn',
                'dosage': 'Bắt đầu 40-80mg/ngày, có thể tăng dần đến 320mg/ngày chia 2 lần',
                'side_effects': 'Hạ đường huyết, buồn nôn, đau bụng',
                'contraindications': 'Đái tháo đường týp 1, hôn mê do đái tháo đường, nhiễm toan ceton',
                'price': Decimal('70000'),
                'stock': 90,
                'manufacturer': 'Servier',
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
                
    # Drugs for "Vitamin và khoáng chất" category
    if categories.filter(name='Vitamin và khoáng chất').exists():
        category = categories.get(name='Vitamin và khoáng chất')
        drugs_data = [
            {
                'name': 'Vitamin D3',
                'description': 'Vitamin D bổ sung điều trị và phòng ngừa thiếu vitamin D',
                'composition': 'Cholecalciferol (Vitamin D3) 1000 IU',
                'usage': 'Uống 1 lần/ngày cùng bữa ăn',
                'dosage': 'Phòng ngừa: 1000-2000 IU/ngày. Điều trị thiếu hụt: 5000 IU/ngày trong 8-12 tuần',
                'side_effects': 'Ít gặp: buồn nôn, táo bón, khô miệng. Quá liều: tăng canxi máu',
                'contraindications': 'Tăng canxi máu, sỏi thận, bệnh sarcoidosis',
                'price': Decimal('130000'),
                'stock': 150,
                'manufacturer': 'Nature Made',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=730)
            },
            {
                'name': 'Vitamin B Complex',
                'description': 'Phức hợp vitamin B bổ sung các vitamin nhóm B',
                'composition': 'Vitamin B1, B2, B3, B5, B6, B12, Folic acid',
                'usage': 'Uống 1 viên/ngày sau bữa ăn',
                'dosage': 'Người lớn: 1 viên/ngày',
                'side_effects': 'Hiếm gặp: buồn nôn, tiêu chảy, nước tiểu có màu vàng đậm',
                'contraindications': 'Mẫn cảm với bất kỳ thành phần nào của thuốc',
                'price': Decimal('90000'),
                'stock': 200,
                'manufacturer': 'Healthy Life',
                'expiry_date': timezone.now().date() + datetime.timedelta(days=548)
            },
            {
                'name': 'Sắt Fumarat',
                'description': 'Bổ sung sắt điều trị và phòng ngừa thiếu máu do thiếu sắt',
                'composition': 'Sắt fumarat tương đương 100mg sắt nguyên tố',
                'usage': 'Uống 1-2 lần/ngày sau bữa ăn',
                'dosage': 'Điều trị thiếu máu: 100-200mg sắt nguyên tố/ngày, chia 1-2 lần',
                'side_effects': 'Buồn nôn, táo bón, đau bụng, phân đen',
                'contraindications': 'Thừa sắt, bệnh tan máu, viêm loét đường tiêu hóa',
                'price': Decimal('75000'),
                'stock': 120,
                'manufacturer': 'VitaHealth',
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

def add_more_medicines_and_inventory():
    """Add more medicines and inventory for diversity"""
    medicines_data = [
        {
            'name': 'Ambroxol 30mg',
            'description': 'Thuốc long đờm và tiêu chất nhầy',
            'price': Decimal('35000'),
            'inventory': {'quantity': 180, 'unit': 'viên', 'min_quantity': 30}
        },
        {
            'name': 'Ginkgo Biloba 120mg',
            'description': 'Cải thiện tuần hoàn máu não và ngoại vi',
            'price': Decimal('160000'),
            'inventory': {'quantity': 90, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Diclofenac 75mg',
            'description': 'Thuốc giảm đau, chống viêm không steroid',
            'price': Decimal('50000'),
            'inventory': {'quantity': 100, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Cetirizine 10mg',
            'description': 'Thuốc kháng histamine điều trị dị ứng',
            'price': Decimal('45000'),
            'inventory': {'quantity': 120, 'unit': 'viên', 'min_quantity': 25}
        },
        {
            'name': 'Bromhexine 8mg',
            'description': 'Thuốc long đờm',
            'price': Decimal('30000'),
            'inventory': {'quantity': 150, 'unit': 'viên', 'min_quantity': 30}
        },
        {
            'name': 'Simethicone 40mg',
            'description': 'Thuốc khử bọt gas đường tiêu hóa',
            'price': Decimal('40000'),
            'inventory': {'quantity': 100, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Dexamethasone 0.5mg',
            'description': 'Glucocorticoid điều trị các tình trạng viêm',
            'price': Decimal('60000'),
            'inventory': {'quantity': 60, 'unit': 'viên', 'min_quantity': 15}
        },
        {
            'name': 'Cefadroxil 500mg',
            'description': 'Kháng sinh cephalosporin thế hệ 1',
            'price': Decimal('75000'),
            'inventory': {'quantity': 80, 'unit': 'viên', 'min_quantity': 15}
        },
        {
            'name': 'Enalapril 10mg',
            'description': 'Thuốc ức chế men chuyển điều trị tăng huyết áp',
            'price': Decimal('55000'),
            'inventory': {'quantity': 90, 'unit': 'viên', 'min_quantity': 20}
        },
        {
            'name': 'Metronidazole 250mg',
            'description': 'Thuốc kháng khuẩn và kháng ký sinh trùng',
            'price': Decimal('40000'),
            'inventory': {'quantity': 120, 'unit': 'viên', 'min_quantity': 25}
        },
        {
            'name': 'Paracetamol 250mg/5ml',
            'description': 'Siro giảm đau hạ sốt cho trẻ em',
            'price': Decimal('35000'),
            'inventory': {'quantity': 50, 'unit': 'chai', 'min_quantity': 10}
        },
        {
            'name': 'Amoxicillin 250mg/5ml',
            'description': 'Siro kháng sinh cho trẻ em',
            'price': Decimal('65000'),
            'inventory': {'quantity': 40, 'unit': 'chai', 'min_quantity': 8}
        },
        {
            'name': 'Vitamin C 1000mg',
            'description': 'Viên sủi bổ sung vitamin C',
            'price': Decimal('120000'),
            'inventory': {'quantity': 30, 'unit': 'tuýp', 'min_quantity': 5}
        },
        {
            'name': 'Canxi 500mg',
            'description': 'Viên sủi bổ sung canxi',
            'price': Decimal('130000'),
            'inventory': {'quantity': 25, 'unit': 'tuýp', 'min_quantity': 5}
        },
        {
            'name': 'Boric acid 3%',
            'description': 'Dung dịch nhỏ tai',
            'price': Decimal('25000'),
            'inventory': {'quantity': 60, 'unit': 'lọ', 'min_quantity': 12}
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
    print("Đang thêm thuốc mới vào các danh mục...")
    add_more_drugs()
    
    print("\nĐang thêm thuốc và tồn kho đa dạng...")
    add_more_medicines_and_inventory()
    
    print("\nHoàn thành việc thêm dữ liệu thuốc và tồn kho!") 