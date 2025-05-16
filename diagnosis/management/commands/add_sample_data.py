import datetime
from django.core.management.base import BaseCommand
from diagnosis.models import Symptom, Disease
from pharmacy.models import Medicine, Drug, DrugCategory

class Command(BaseCommand):
    help = 'Adds sample symptoms, diseases, and drugs to the database'

    def handle(self, *args, **options):
        # Add symptoms
        symptoms_data = [
            # Digestive system
            {'name': 'Tiêu chảy', 'description': 'Đi ngoài phân lỏng nhiều lần trong ngày'},
            {'name': 'Đau bụng', 'description': 'Cảm giác đau ở vùng bụng'},
            {'name': 'Buồn nôn', 'description': 'Cảm giác muốn nôn'},
            {'name': 'Nôn', 'description': 'Tống xuất thức ăn từ dạ dày qua đường miệng'},
            {'name': 'Đau dạ dày', 'description': 'Cảm giác đau ở vùng dạ dày'},
            {'name': 'Ợ chua', 'description': 'Cảm giác chua ở cổ họng'},
            {'name': 'Ợ nóng', 'description': 'Cảm giác nóng ở vùng ngực và họng'},
            {'name': 'Khó tiêu', 'description': 'Cảm giác khó chịu sau khi ăn'},
            {'name': 'Đầy hơi', 'description': 'Cảm giác đầy bụng, căng tức'},
            {'name': 'Mất nước', 'description': 'Thiếu nước trong cơ thể, khô miệng, khát nước'},
            {'name': 'Đi ngoài nhiều lần', 'description': 'Phải đi vệ sinh nhiều lần trong ngày'},
            {'name': 'Đau bụng trên', 'description': 'Đau ở vùng bụng phía trên, gần dạ dày'},
            {'name': 'Táo bón', 'description': 'Khó khăn khi đi đại tiện, phân khô cứng'},
            {'name': 'Chướng bụng', 'description': 'Bụng căng phồng, đầy hơi'},
            {'name': 'Phân có máu', 'description': 'Phân có lẫn máu tươi hoặc máu đen'},
            {'name': 'Khó nuốt', 'description': 'Khó khăn khi nuốt thức ăn hoặc nước uống'},
            {'name': 'Đau vùng mặt', 'description': 'Cảm giác đau ở vùng mặt, thường gặp trong viêm xoang'},
            {'name': 'Giảm khứu giác', 'description': 'Giảm hoặc mất khả năng ngửi, thường gặp trong viêm xoang'},
            {'name': 'Cơ lưng căng cứng', 'description': 'Cảm giác căng cứng ở các cơ vùng lưng'},
            {'name': 'Đau tăng khi cử động', 'description': 'Cảm giác đau tăng lên khi cử động vùng bị đau'},
            {'name': 'Sốt nhẹ', 'description': 'Nhiệt độ cơ thể tăng nhẹ, thường dưới 38.5°C'},
            {'name': 'Đờm có màu vàng hoặc xanh', 'description': 'Chất nhầy đặc được tạo ra trong phổi có màu vàng hoặc xanh'},
            
            # Musculoskeletal system
            {'name': 'Đau khớp', 'description': 'Cảm giác đau ở các khớp'},
            {'name': 'Sưng khớp', 'description': 'Khớp bị sưng, to hơn bình thường'},
            {'name': 'Cứng khớp', 'description': 'Khó khăn khi cử động khớp'},
            {'name': 'Khó vận động', 'description': 'Khó khăn khi di chuyển'},
            {'name': 'Đau lưng', 'description': 'Đau ở vùng lưng, có thể lan xuống chân'},
            {'name': 'Đau cơ', 'description': 'Đau nhức các cơ trong cơ thể'},
            {'name': 'Yếu cơ', 'description': 'Cảm giác yếu ở các nhóm cơ'},
            {'name': 'Đau cổ', 'description': 'Đau ở vùng cổ, khó cử động đầu'},
            {'name': 'Chuột rút', 'description': 'Co thắt cơ đột ngột và đau'},
            {'name': 'Tê chân tay', 'description': 'Cảm giác tê ở tay hoặc chân'},
            
            # Neurological system
            {'name': 'Đau đầu', 'description': 'Cảm giác đau ở vùng đầu'},
            {'name': 'Nhức đầu', 'description': 'Cảm giác nhức ở vùng đầu'},
            {'name': 'Chóng mặt', 'description': 'Cảm giác xoay vòng, mất thăng bằng'},
            {'name': 'Nhạy cảm ánh sáng', 'description': 'Khó chịu khi tiếp xúc với ánh sáng mạnh'},
            {'name': 'Mất ngủ', 'description': 'Khó đi vào giấc ngủ hoặc duy trì giấc ngủ'},
            {'name': 'Run tay', 'description': 'Tay run không kiểm soát được'},
            {'name': 'Lú lẫn', 'description': 'Khó tập trung, không định hướng được'},
            {'name': 'Hay quên', 'description': 'Khó nhớ thông tin mới hoặc thông tin cũ'},
            {'name': 'Co giật', 'description': 'Cơ thể co giật không kiểm soát'},
            {'name': 'Nhạy cảm âm thanh', 'description': 'Khó chịu với âm thanh lớn'},
            
            # Respiratory system
            {'name': 'Ho', 'description': 'Ho khan hoặc có đờm'},
            {'name': 'Khó thở', 'description': 'Cảm giác khó hít thở, thiếu không khí'},
            {'name': 'Đau họng', 'description': 'Cảm giác đau rát ở vùng họng'},
            {'name': 'Nghẹt mũi', 'description': 'Mũi bị tắc, khó thở qua mũi'},
            {'name': 'Chảy mũi', 'description': 'Dịch chảy ra từ mũi'},
            {'name': 'Thở khò khè', 'description': 'Tiếng khò khè khi thở'},
            {'name': 'Đau ngực khi thở', 'description': 'Đau ngực mỗi khi hít thở sâu'},
            {'name': 'Thở nhanh', 'description': 'Nhịp thở nhanh hơn bình thường'},
            {'name': 'Ho ra máu', 'description': 'Ho có kèm theo máu'},
            {'name': 'Hắt hơi', 'description': 'Hắt hơi nhiều lần'},
            
            # Cardiovascular system
            {'name': 'Đau ngực', 'description': 'Cảm giác đau ở vùng ngực'},
            {'name': 'Hồi hộp', 'description': 'Tim đập nhanh, mạnh hơn bình thường'},
            {'name': 'Khó thở khi gắng sức', 'description': 'Khó thở khi hoạt động, vận động'},
            {'name': 'Phù chân', 'description': 'Chân sưng, phù nề'},
            {'name': 'Tăng huyết áp', 'description': 'Huyết áp cao hơn mức bình thường'},
            {'name': 'Hạ huyết áp', 'description': 'Huyết áp thấp hơn mức bình thường'},
            {'name': 'Đánh trống ngực', 'description': 'Cảm giác tim đập mạnh, không đều'},
            {'name': 'Đau lan xuống tay', 'description': 'Đau từ ngực lan xuống cánh tay, thường là bên trái'},
            
            # General symptoms
            {'name': 'Mệt mỏi', 'description': 'Cảm giác yếu, kiệt sức'},
            {'name': 'Chán ăn', 'description': 'Không muốn ăn, giảm cảm giác thèm ăn'},
            {'name': 'Sụt cân', 'description': 'Giảm cân không rõ nguyên nhân'},
            {'name': 'Phát ban', 'description': 'Xuất hiện ban đỏ trên da'},
            {'name': 'Đổ mồ hôi đêm', 'description': 'Đổ nhiều mồ hôi vào ban đêm'},
            {'name': 'Tăng cân', 'description': 'Tăng cân không rõ nguyên nhân'},
            {'name': 'Ngứa', 'description': 'Cảm giác ngứa ở da'},
            {'name': 'Thay đổi màu da', 'description': 'Da thay đổi màu sắc bất thường'},
            {'name': 'Dị ứng', 'description': 'Phản ứng quá mức của hệ miễn dịch'},
            {'name': 'Sưng hạch bạch huyết', 'description': 'Hạch bạch huyết sưng to, có thể sờ thấy'},
            
            # Mental health symptoms
            {'name': 'Lo âu', 'description': 'Cảm giác lo lắng thường xuyên'},
            {'name': 'Trầm cảm', 'description': 'Cảm giác buồn, không thấy vui vẻ với mọi thứ'},
            {'name': 'Stress', 'description': 'Cảm giác căng thẳng do áp lực'},
            {'name': 'Thay đổi tâm trạng', 'description': 'Tâm trạng thay đổi bất thường'},
            {'name': 'Khó tập trung', 'description': 'Không thể tập trung vào công việc'},
        ]
        
        self.stdout.write('Adding symptoms...')
        for symptom_data in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={'description': symptom_data['description']}
            )
            if created:
                self.stdout.write(f'  Added symptom: {symptom.name}')
            else:
                self.stdout.write(f'  Symptom already exists: {symptom.name}')
        
        # Add diseases
        diseases_data = [
            {
                'name': 'Tiêu chảy',
                'description': 'Đi ngoài phân lỏng nhiều lần trong ngày, có thể kèm theo đau bụng, buồn nôn.',
                'symptoms': ['Tiêu chảy', 'Đau bụng', 'Buồn nôn', 'Nôn', 'Mất nước', 'Đi ngoài nhiều lần'],
                'severity': 'medium',
                'treatment_guidelines': 'Uống nhiều nước, bù nước và điện giải, sử dụng thuốc kháng sinh nếu cần thiết.'
            },
            {
                'name': 'Viêm dạ dày',
                'description': 'Viêm lớp niêm mạc dạ dày, gây đau và khó chịu ở vùng bụng trên.',
                'symptoms': ['Đau dạ dày', 'Ợ chua', 'Ợ nóng', 'Khó tiêu', 'Đầy hơi', 'Đau bụng trên', 'Buồn nôn'],
                'severity': 'medium',
                'treatment_guidelines': 'Sử dụng thuốc ức chế bơm proton, thuốc kháng H2, thuốc diệt H. pylori nếu cần.'
            },
            {
                'name': 'Viêm khớp',
                'description': 'Viêm các khớp gây đau, sưng và cứng khớp, ảnh hưởng đến khả năng vận động.',
                'symptoms': ['Đau khớp', 'Sưng khớp', 'Cứng khớp', 'Khó vận động'],
                'severity': 'high',
                'treatment_guidelines': 'Sử dụng thuốc chống viêm không steroid, corticosteroid, thuốc điều trị sinh học.'
            },
            {
                'name': 'Đau nửa đầu',
                'description': 'Đau đầu từng cơn, thường đau một bên đầu, kèm theo nhạy cảm với ánh sáng, âm thanh.',
                'symptoms': ['Đau đầu', 'Nhức đầu', 'Chóng mặt', 'Buồn nôn', 'Nhạy cảm ánh sáng', 'Nhạy cảm âm thanh'],
                'severity': 'medium',
                'treatment_guidelines': 'Sử dụng thuốc giảm đau, thuốc chống đau nửa đầu, thuốc chẹn beta hoặc thuốc chống co giật.'
            },
            {
                'name': 'Cảm cúm',
                'description': 'Nhiễm virus gây sốt, ho, đau họng, đau nhức cơ thể.',
                'symptoms': ['Sốt', 'Ho', 'Đau họng', 'Nghẹt mũi', 'Chảy mũi', 'Mệt mỏi', 'Đau cơ', 'Hắt hơi'],
                'severity': 'low',
                'treatment_guidelines': 'Nghỉ ngơi, uống nhiều nước, sử dụng thuốc giảm đau hạ sốt, thuốc chống virus nếu cần.'
            },
            {
                'name': 'Tăng huyết áp',
                'description': 'Tình trạng áp lực máu lên thành động mạch cao hơn bình thường, có thể gây tổn thương tim và mạch máu.',
                'symptoms': ['Đau đầu', 'Chóng mặt', 'Tăng huyết áp', 'Mệt mỏi', 'Khó thở khi gắng sức', 'Đau ngực'],
                'severity': 'high',
                'treatment_guidelines': 'Thay đổi lối sống, sử dụng thuốc hạ huyết áp, kiểm soát chế độ ăn uống và tập luyện.'
            },
            {
                'name': 'Viêm phổi',
                'description': 'Nhiễm trùng các túi khí trong phổi, thường do vi khuẩn hoặc virus.',
                'symptoms': ['Ho', 'Sốt', 'Khó thở', 'Đau ngực khi thở', 'Mệt mỏi', 'Đờm có màu vàng hoặc xanh', 'Thở nhanh'],
                'severity': 'high',
                'treatment_guidelines': 'Sử dụng kháng sinh, nghỉ ngơi, uống nhiều nước, sử dụng thuốc giảm đau và hạ sốt.'
            },
            {
                'name': 'Viêm loét dạ dày',
                'description': 'Vết loét ở niêm mạc dạ dày hoặc tá tràng, thường do vi khuẩn H. pylori hoặc sử dụng thuốc NSAIDs.',
                'symptoms': ['Đau dạ dày', 'Đau bụng trên', 'Buồn nôn', 'Chán ăn', 'Đầy hơi', 'Ợ nóng', 'Phân có máu'],
                'severity': 'high',
                'treatment_guidelines': 'Sử dụng thuốc ức chế bơm proton, thuốc kháng H2, điều trị diệt H. pylori, tránh sử dụng NSAIDs.'
            },
            {
                'name': 'Trầm cảm',
                'description': 'Rối loạn tâm trạng gây buồn bã, mất hứng thú với các hoạt động thường ngày.',
                'symptoms': ['Trầm cảm', 'Mệt mỏi', 'Mất ngủ', 'Chán ăn', 'Sụt cân', 'Lo âu', 'Khó tập trung'],
                'severity': 'medium',
                'treatment_guidelines': 'Tâm lý trị liệu, thuốc chống trầm cảm, thay đổi lối sống, liệu pháp hành vi nhận thức.'
            },
            {
                'name': 'Viêm xoang',
                'description': 'Viêm các xoang cạnh mũi, thường do nhiễm trùng hoặc dị ứng.',
                'symptoms': ['Nghẹt mũi', 'Chảy mũi', 'Đau vùng mặt', 'Đau đầu', 'Nhức đầu', 'Ho', 'Giảm khứu giác'],
                'severity': 'low',
                'treatment_guidelines': 'Sử dụng thuốc kháng sinh, thuốc giảm viêm, thuốc xịt mũi, rửa mũi bằng nước muối.'
            },
            {
                'name': 'Đau thắt lưng',
                'description': 'Đau ở vùng lưng dưới, có thể do chấn thương, căng cơ, thoát vị đĩa đệm.',
                'symptoms': ['Đau lưng', 'Khó vận động', 'Tê chân tay', 'Cơ lưng căng cứng', 'Đau tăng khi cử động'],
                'severity': 'medium',
                'treatment_guidelines': 'Nghỉ ngơi, sử dụng thuốc giảm đau, vật lý trị liệu, tập thể dục nhẹ nhàng.'
            },
            {
                'name': 'Viêm khớp dạng thấp',
                'description': 'Bệnh tự miễn gây viêm màng hoạt dịch ở nhiều khớp, dẫn đến đau và biến dạng khớp.',
                'symptoms': ['Đau khớp', 'Sưng khớp', 'Cứng khớp', 'Mệt mỏi', 'Sốt nhẹ', 'Sưng hạch bạch huyết'],
                'severity': 'high',
                'treatment_guidelines': 'Sử dụng thuốc chống viêm, thuốc điều chỉnh bệnh, liệu pháp sinh học, vật lý trị liệu.'
            },
        ]
        
        self.stdout.write('Adding diseases...')
        for disease_data in diseases_data:
            disease, created = Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults={
                    'description': disease_data['description'],
                    'severity': disease_data['severity'],
                    'treatment_guidelines': disease_data['treatment_guidelines']
                }
            )
            
            if created:
                # Add symptoms to the disease
                for symptom_name in disease_data['symptoms']:
                    try:
                        symptom = Symptom.objects.get(name=symptom_name)
                        disease.symptoms.add(symptom)
                    except Symptom.DoesNotExist:
                        self.stdout.write(f'  Warning: Symptom {symptom_name} does not exist')
                
                self.stdout.write(f'  Added disease: {disease.name}')
            else:
                self.stdout.write(f'  Disease already exists: {disease.name}')
        
        # Add medicines
        medicines_data = [
            {
                'name': 'Loperamide',
                'description': 'Thuốc chống tiêu chảy, làm chậm nhu động ruột.',
                'price': 25000
            },
            {
                'name': 'Azithromycin',
                'description': 'Kháng sinh dùng điều trị tiêu chảy do vi khuẩn.',
                'price': 50000
            },
            {
                'name': 'Omeprazole',
                'description': 'Thuốc ức chế bơm proton dùng trong điều trị viêm dạ dày.',
                'price': 35000
            },
            {
                'name': 'Bismuth subsalicylate',
                'description': 'Thuốc điều trị tiêu chảy và khó tiêu.',
                'price': 40000
            },
            {
                'name': 'Ibuprofen',
                'description': 'Thuốc chống viêm không steroid dùng điều trị viêm khớp, đau đầu.',
                'price': 20000
            },
            {
                'name': 'Sumatriptan',
                'description': 'Thuốc điều trị đau nửa đầu.',
                'price': 75000
            },
            {
                'name': 'Paracetamol',
                'description': 'Thuốc giảm đau, hạ sốt.',
                'price': 15000
            },
            {
                'name': 'Amoxicillin',
                'description': 'Kháng sinh dùng điều trị nhiễm khuẩn đường hô hấp, tai mũi họng.',
                'price': 45000
            },
            {
                'name': 'Methotrexate',
                'description': 'Thuốc điều trị viêm khớp dạng thấp.',
                'price': 90000
            },
            {
                'name': 'Prednisolone',
                'description': 'Corticosteroid dùng điều trị viêm khớp, bệnh tự miễn.',
                'price': 65000
            },
            {
                'name': 'Enalapril',
                'description': 'Thuốc ức chế men chuyển dùng trong điều trị tăng huyết áp.',
                'price': 55000
            },
            {
                'name': 'Amlodipine',
                'description': 'Thuốc chẹn kênh canxi dùng trong điều trị tăng huyết áp.',
                'price': 60000
            },
            {
                'name': 'Hydrochlorothiazide',
                'description': 'Thuốc lợi tiểu dùng trong điều trị tăng huyết áp.',
                'price': 30000
            },
            {
                'name': 'Cefuroxime',
                'description': 'Kháng sinh điều trị nhiễm trùng đường hô hấp, viêm phổi.',
                'price': 70000
            },
            {
                'name': 'Ciprofloxacin',
                'description': 'Kháng sinh nhóm quinolone dùng trong các nhiễm khuẩn nặng.',
                'price': 55000
            },
            {
                'name': 'Clarithromycin',
                'description': 'Kháng sinh macrolide dùng trong điều trị H. pylori.',
                'price': 65000
            },
            {
                'name': 'Famotidine',
                'description': 'Thuốc kháng H2 dùng trong điều trị viêm dạ dày.',
                'price': 40000
            },
            {
                'name': 'Ranitidine',
                'description': 'Thuốc kháng H2 dùng trong điều trị loét dạ dày.',
                'price': 35000
            },
            {
                'name': 'Propranolol',
                'description': 'Thuốc chẹn beta dùng trong điều trị đau nửa đầu, tăng huyết áp.',
                'price': 50000
            },
            {
                'name': 'Fluoxetine',
                'description': 'Thuốc chống trầm cảm nhóm ức chế tái hấp thu serotonin chọn lọc (SSRI).',
                'price': 80000
            },
            {
                'name': 'Sertraline',
                'description': 'Thuốc chống trầm cảm nhóm SSRI.',
                'price': 85000
            },
            {
                'name': 'Diclofenac',
                'description': 'Thuốc chống viêm không steroid dùng điều trị đau nhức, viêm khớp.',
                'price': 25000
            },
            {
                'name': 'Naproxen',
                'description': 'Thuốc chống viêm không steroid dùng điều trị đau nhức, viêm khớp.',
                'price': 30000
            },
            {
                'name': 'Sucralfate',
                'description': 'Thuốc bảo vệ niêm mạc dạ dày, điều trị loét dạ dày.',
                'price': 45000
            },
            {
                'name': 'Loratadine',
                'description': 'Thuốc kháng histamine điều trị dị ứng, viêm mũi dị ứng.',
                'price': 35000
            },
        ]
        
        self.stdout.write('Adding medicines...')
        for medicine_data in medicines_data:
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_data['name'],
                defaults={
                    'description': medicine_data['description'],
                    'price': medicine_data['price']
                }
            )
            
            if created:
                self.stdout.write(f'  Added medicine: {medicine.name}')
            else:
                self.stdout.write(f'  Medicine already exists: {medicine.name}')
        
        # Add a drug category first
        category, created = DrugCategory.objects.get_or_create(
            name='Thuốc điều trị tổng hợp',
            defaults={
                'description': 'Danh mục các thuốc điều trị nhiều bệnh lý khác nhau'
            }
        )
        
        if created:
            self.stdout.write('Added drug category: Thuốc điều trị tổng hợp')
        else:
            self.stdout.write('Drug category already exists: Thuốc điều trị tổng hợp')
        
        # Add drug combinations
        drugs_data = [
            {
                'name': 'Oral rehydration salts, Probiotics',
                'description': 'Điều trị tiêu chảy nhẹ, phục hồi nước và điện giải, cân bằng vi khuẩn đường ruột.',
                'composition': 'ORS: Natri chloride, Kali chloride, Glucose. Probiotics: Lactobacillus acidophilus.',
                'dosage': 'ORS: 1 gói pha với 1 lít nước, uống trong ngày. Probiotics: 1-2 viên/ngày.',
                'usage': 'Dùng đường uống sau mỗi lần đi ngoài.',
                'side_effects': 'Hiếm gặp: buồn nôn, đầy hơi.',
                'contraindications': 'Không có chống chỉ định đặc biệt.',
                'price': 55000,
                'stock': 100,
                'manufacturer': 'ORS Pharma',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=365)
            },
            {
                'name': 'Loperamide, Azithromycin',
                'description': 'Điều trị tiêu chảy mức độ trung bình do vi khuẩn.',
                'composition': 'Loperamide hydrochloride 2mg, Azithromycin 500mg.',
                'dosage': 'Loperamide: 2mg sau mỗi lần đi ngoài (tối đa 16mg/ngày). Azithromycin: 500mg/ngày x 3 ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Buồn nôn, đau bụng, nhức đầu, chóng mặt.',
                'contraindications': 'Không dùng cho người mẫn cảm với thuốc. Thận trọng với phụ nữ mang thai.',
                'price': 75000,
                'stock': 80,
                'manufacturer': 'Antibiotics Co.',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'Loperamide, Fluoroquinolone',
                'description': 'Điều trị tiêu chảy nặng do vi khuẩn.',
                'composition': 'Loperamide hydrochloride 2mg, Ciprofloxacin 500mg.',
                'dosage': 'Loperamide: 2mg sau mỗi lần đi ngoài (tối đa 16mg/ngày). Ciprofloxacin: 500mg x 2 lần/ngày x 3-5 ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Buồn nôn, đau đầu, chóng mặt, mệt mỏi.',
                'contraindications': 'Không dùng cho người mẫn cảm với thuốc, phụ nữ mang thai, trẻ em dưới 18 tuổi.',
                'price': 85000,
                'stock': 60,
                'manufacturer': 'BioPharm',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'Antacids, Sucralfate',
                'description': 'Điều trị viêm dạ dày nhẹ, bảo vệ niêm mạc dạ dày.',
                'composition': 'Aluminium hydroxide, Magnesium hydroxide, Sucralfate 1g.',
                'dosage': 'Antacids: 10-20ml sau mỗi bữa ăn và trước khi đi ngủ. Sucralfate: 1g x 4 lần/ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Táo bón, tiêu chảy, đầy hơi.',
                'contraindications': 'Thận trọng khi sử dụng cho người bệnh thận.',
                'price': 65000,
                'stock': 90,
                'manufacturer': 'GastroHealth',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=365)
            },
            {
                'name': 'PPIs, H. pylori treatment',
                'description': 'Điều trị viêm dạ dày, loét dạ dày do H. pylori.',
                'composition': 'Omeprazole 20mg, Amoxicillin 1g, Clarithromycin 500mg.',
                'dosage': 'Omeprazole: 20mg x 2 lần/ngày. Amoxicillin: 1g x 2 lần/ngày. Clarithromycin: 500mg x 2 lần/ngày. Trong 7-14 ngày.',
                'usage': 'Dùng đường uống trước khi ăn.',
                'side_effects': 'Buồn nôn, đau đầu, tiêu chảy, đau bụng.',
                'contraindications': 'Không dùng cho người mẫn cảm với thành phần của thuốc.',
                'price': 120000,
                'stock': 50,
                'manufacturer': 'HelicoCure',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'NSAIDs, Topical treatments',
                'description': 'Điều trị viêm khớp nhẹ, giảm đau và viêm tại chỗ.',
                'composition': 'Ibuprofen 400mg, Gel chống viêm (Diclofenac 1%).',
                'dosage': 'Ibuprofen: 400mg x 3 lần/ngày. Gel chống viêm: bôi 3-4 lần/ngày.',
                'usage': 'Uống thuốc sau khi ăn, bôi gel lên vùng đau.',
                'side_effects': 'Đau dạ dày, buồn nôn, khó tiêu.',
                'contraindications': 'Không dùng cho người có tiền sử loét dạ dày, hen suyễn, suy thận nặng.',
                'price': 55000,
                'stock': 75,
                'manufacturer': 'JointCare',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=545)
            },
            {
                'name': 'Biologicals, Corticosteroids',
                'description': 'Điều trị viêm khớp nặng, ức chế phản ứng viêm.',
                'composition': 'Methotrexate 10mg, Prednisolone 5mg.',
                'dosage': 'Methotrexate: 7.5-20mg/tuần. Prednisolone: 5-10mg/ngày.',
                'usage': 'Dùng đường uống theo chỉ định của bác sĩ.',
                'side_effects': 'Buồn nôn, suy giảm tế bào máu, tăng nguy cơ nhiễm trùng.',
                'contraindications': 'Không dùng cho phụ nữ mang thai, cho con bú, người suy gan, thận.',
                'price': 150000,
                'stock': 40,
                'manufacturer': 'ImmunoPharm',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'NSAIDs, Caffeine combinations',
                'description': 'Điều trị đau đầu nhẹ, giảm đau nhanh.',
                'composition': 'Ibuprofen 400mg, Caffeine 65mg.',
                'dosage': 'Ibuprofen 400mg + Caffeine 65mg: 1-2 viên mỗi 6 giờ khi cần.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Mất ngủ, hồi hộp, đánh trống ngực, khó tiêu.',
                'contraindications': 'Không dùng cho người bị bệnh tim mạch, cao huyết áp không kiểm soát.',
                'price': 45000,
                'stock': 120,
                'manufacturer': 'HeadRelief',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=365)
            },
            {
                'name': 'Triptans, Beta-blockers/Anticonvulsants',
                'description': 'Điều trị đau nửa đầu từ trung bình đến nặng.',
                'composition': 'Sumatriptan 50mg, Propranolol 40mg.',
                'dosage': 'Sumatriptan: 50-100mg khi có cơn đau. Propranolol: 40-120mg/ngày chia 2-3 lần.',
                'usage': 'Dùng đường uống khi có cơn đau nửa đầu.',
                'side_effects': 'Chóng mặt, buồn nôn, mệt mỏi, nhịp tim chậm.',
                'contraindications': 'Không dùng cho người bị bệnh mạch vành, đột quỵ, huyết áp không kiểm soát.',
                'price': 120000,
                'stock': 60,
                'manufacturer': 'MigraineControl',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=545)
            },
            {
                'name': 'Acetaminophen, Lifestyle changes',
                'description': 'Điều trị đau đầu nhẹ đến trung bình và cải thiện lối sống.',
                'composition': 'Paracetamol 500mg.',
                'dosage': 'Paracetamol: 500-1000mg mỗi 4-6 giờ khi cần (tối đa 4g/ngày).',
                'usage': 'Dùng đường uống khi có cơn đau, kết hợp nghỉ ngơi, giảm căng thẳng.',
                'side_effects': 'Hiếm gặp: phát ban, tổn thương gan khi dùng liều cao và kéo dài.',
                'contraindications': 'Thận trọng ở người bệnh gan, thận, nghiện rượu.',
                'price': 35000,
                'stock': 150,
                'manufacturer': 'SafePain',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=455)
            },
            {
                'name': 'Lifestyle modifications, Diuretics',
                'description': 'Điều trị tăng huyết áp nhẹ, giảm muối trong chế độ ăn.',
                'composition': 'Hydrochlorothiazide 12.5mg.',
                'dosage': 'Hydrochlorothiazide: 12.5-25mg mỗi ngày.',
                'usage': 'Dùng đường uống vào buổi sáng.',
                'side_effects': 'Hạ kali máu, tăng axit uric máu, rối loạn điện giải.',
                'contraindications': 'Không dùng cho người bị bệnh gout cấp, suy thận nặng.',
                'price': 40000,
                'stock': 90,
                'manufacturer': 'CardioHealth',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'ACE inhibitors, Calcium channel blockers',
                'description': 'Điều trị tăng huyết áp trung bình đến nặng.',
                'composition': 'Enalapril 5mg, Amlodipine 5mg.',
                'dosage': 'Enalapril: 5-20mg/ngày. Amlodipine: 5-10mg/ngày.',
                'usage': 'Dùng đường uống theo chỉ định của bác sĩ.',
                'side_effects': 'Ho khan, phù mạch, phù chân, đau đầu, chóng mặt.',
                'contraindications': 'Không dùng cho phụ nữ mang thai, người có tiền sử phù mạch.',
                'price': 100000,
                'stock': 70,
                'manufacturer': 'Pressuredown',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=545)
            },
            {
                'name': 'Combined therapy, Beta-blockers',
                'description': 'Điều trị tăng huyết áp khó kiểm soát.',
                'composition': 'Hydrochlorothiazide 12.5mg, Enalapril 10mg, Propranolol 40mg.',
                'dosage': 'Hydrochlorothiazide: 12.5-25mg/ngày. Enalapril: 5-20mg/ngày. Propranolol: 40-120mg/ngày.',
                'usage': 'Dùng đường uống theo chỉ định của bác sĩ.',
                'side_effects': 'Mệt mỏi, chóng mặt, hạ huyết áp tư thế, nhịp tim chậm.',
                'contraindications': 'Không dùng cho người bị hen, block tim, suy tim nặng.',
                'price': 130000,
                'stock': 45,
                'manufacturer': 'ComplexCare',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'Cephalosporins, Mucolytics',
                'description': 'Điều trị viêm phổi do vi khuẩn.',
                'composition': 'Cefuroxime 500mg, Acetylcysteine 600mg.',
                'dosage': 'Cefuroxime: 500mg x 2 lần/ngày x 7-10 ngày. Acetylcysteine: 600mg/ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Buồn nôn, tiêu chảy, đau đầu, phát ban.',
                'contraindications': 'Không dùng cho người dị ứng với kháng sinh nhóm beta-lactam.',
                'price': 110000,
                'stock': 55,
                'manufacturer': 'RespiCure',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=455)
            },
            {
                'name': 'Quinolones, Anti-inflammatory',
                'description': 'Điều trị viêm phổi nặng.',
                'composition': 'Ciprofloxacin 500mg, Ibuprofen 400mg.',
                'dosage': 'Ciprofloxacin: 500mg x 2 lần/ngày x 7-14 ngày. Ibuprofen: 400mg x 3 lần/ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Buồn nôn, đau đầu, mệt mỏi, đau khớp, gân.',
                'contraindications': 'Không dùng cho trẻ em đang phát triển, phụ nữ mang thai.',
                'price': 130000,
                'stock': 40,
                'manufacturer': 'LungHealth',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=545)
            },
            {
                'name': 'H2 blockers, Antacids',
                'description': 'Điều trị viêm loét dạ dày nhẹ.',
                'composition': 'Famotidine 20mg, Antacids (Aluminium hydroxide, Magnesium hydroxide).',
                'dosage': 'Famotidine: 20mg x 2 lần/ngày. Antacids: 10-20ml sau mỗi bữa ăn và trước khi đi ngủ.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Táo bón, tiêu chảy, đau đầu.',
                'contraindications': 'Thận trọng khi dùng cho người suy thận nặng.',
                'price': 70000,
                'stock': 80,
                'manufacturer': 'StomachCare',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=455)
            },
            {
                'name': 'SSRIs, Counseling',
                'description': 'Điều trị trầm cảm.',
                'composition': 'Fluoxetine 20mg, Sertraline 50mg.',
                'dosage': 'Fluoxetine: 20mg mỗi sáng. Sertraline: 50-100mg mỗi ngày.',
                'usage': 'Dùng đường uống vào buổi sáng.',
                'side_effects': 'Buồn nôn, nhức đầu, mất ngủ, lo âu, rối loạn tình dục.',
                'contraindications': 'Không dùng cùng với thuốc ức chế MAO, người có xu hướng tự tử.',
                'price': 90000,
                'stock': 60,
                'manufacturer': 'MindCare',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
            {
                'name': 'Antihistamines, Decongestants',
                'description': 'Điều trị viêm xoang do dị ứng.',
                'composition': 'Loratadine 10mg, Pseudoephedrine 60mg.',
                'dosage': 'Loratadine: 10mg mỗi ngày. Pseudoephedrine: 60mg x 2-3 lần/ngày.',
                'usage': 'Dùng đường uống.',
                'side_effects': 'Khô miệng, buồn ngủ, nhức đầu, hồi hộp.',
                'contraindications': 'Không dùng cho người bị tăng nhãn áp, bệnh tim mạch nặng.',
                'price': 60000,
                'stock': 85,
                'manufacturer': 'AllergyRelief',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=455)
            },
            {
                'name': 'Muscle relaxants, Pain relievers',
                'description': 'Điều trị đau thắt lưng.',
                'composition': 'Cyclobenzaprine 5mg, Naproxen 250mg.',
                'dosage': 'Cyclobenzaprine: 5-10mg x 3 lần/ngày. Naproxen: 250-500mg x 2 lần/ngày.',
                'usage': 'Dùng đường uống sau khi ăn.',
                'side_effects': 'Buồn ngủ, chóng mặt, khô miệng, đau dạ dày.',
                'contraindications': 'Không dùng cho người bị glaucoma, bí tiểu, suy gan, thận nặng.',
                'price': 75000,
                'stock': 65,
                'manufacturer': 'BackPainRelief',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=455)
            },
            {
                'name': 'Disease-modifying agents, Biologics',
                'description': 'Điều trị viêm khớp dạng thấp.',
                'composition': 'Methotrexate 7.5mg, Etanercept 50mg.',
                'dosage': 'Methotrexate: 7.5-20mg/tuần. Etanercept: 50mg/tuần tiêm dưới da.',
                'usage': 'Dùng theo chỉ định của bác sĩ.',
                'side_effects': 'Buồn nôn, suy giảm tế bào máu, tăng nguy cơ nhiễm trùng.',
                'contraindications': 'Không dùng cho phụ nữ mang thai, người có bệnh nhiễm trùng đang hoạt động.',
                'price': 200000,
                'stock': 30,
                'manufacturer': 'RheumaSpecialty',
                'expiry_date': datetime.date.today() + datetime.timedelta(days=730)
            },
        ]
        
        self.stdout.write('Adding drug combinations...')
        for drug_data in drugs_data:
            drug, created = Drug.objects.get_or_create(
                name=drug_data['name'],
                defaults={
                    'category': category,
                    'description': drug_data['description'],
                    'composition': drug_data['composition'],
                    'dosage': drug_data['dosage'],
                    'usage': drug_data['usage'],
                    'side_effects': drug_data['side_effects'],
                    'contraindications': drug_data['contraindications'],
                    'price': drug_data['price'],
                    'stock': drug_data['stock'],
                    'manufacturer': drug_data['manufacturer'],
                    'expiry_date': drug_data['expiry_date']
                }
            )
            
            if created:
                self.stdout.write(f'  Added drug combination: {drug.name}')
            else:
                self.stdout.write(f'  Drug combination already exists: {drug.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample data')) 