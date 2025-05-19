import datetime
from django.core.management.base import BaseCommand
from diagnosis.models import Symptom, Disease

class Command(BaseCommand):
    help = 'Adds missing symptoms that were referenced but not created'

    def handle(self, *args, **options):
        # Thêm các triệu chứng còn thiếu
        missing_symptoms_data = [
            {'name': 'Cảm giác có dị vật trong mắt', 'description': 'Cảm giác như có vật lạ trong mắt, gây khó chịu'},
            {'name': 'Cảm giác bỏng rát', 'description': 'Cảm giác nóng rát, như bị bỏng'},
            {'name': 'Mất thăng bằng', 'description': 'Khó khăn khi giữ thăng bằng, dễ ngã'},
            {'name': 'Sưng', 'description': 'Phần cơ thể bị phù nề, to hơn bình thường'},
            {'name': 'Vảy da', 'description': 'Những mảng da bong ra thành vảy'},
            {'name': 'Móng dày', 'description': 'Móng tay chân dày hơn bình thường'},
            {'name': 'Sưng nướu', 'description': 'Nướu răng sưng đỏ, to hơn bình thường'},
            {'name': 'Đau khi nhai', 'description': 'Cảm giác đau khi nhai thức ăn'},
            {'name': 'Nướu đỏ', 'description': 'Nướu có màu đỏ hơn bình thường, dấu hiệu viêm'},
            {'name': 'Lỗ trên răng', 'description': 'Lỗ hoặc hố trên bề mặt răng do sâu'},
            {'name': 'Đau khi ăn đồ ngọt, nóng, lạnh', 'description': 'Răng đau nhức khi ăn thức ăn ngọt, nóng hoặc lạnh'},
            {'name': 'Đau miệng', 'description': 'Cảm giác đau trong khoang miệng'},
            {'name': 'Khó ăn uống', 'description': 'Khó khăn khi ăn hoặc uống do đau hoặc khó nuốt'},
            {'name': 'Đau vùng bàng quang', 'description': 'Đau ở vùng bụng dưới, nơi bàng quang'},
            {'name': 'Đau dữ dội vùng thắt lưng', 'description': 'Đau dữ dội ở vùng lưng dưới, thường do sỏi thận'},
            {'name': 'Đau lan xuống bụng dưới', 'description': 'Đau từ vùng lưng lan xuống bụng dưới'},
            {'name': 'Tiểu nhiều', 'description': 'Đi tiểu nhiều lần với lượng lớn'},
            {'name': 'Vết thương lâu lành', 'description': 'Vết thương mất thời gian lâu để lành hơn bình thường'},
            {'name': 'Tăng nhịp tim', 'description': 'Tim đập nhanh hơn bình thường'},
            {'name': 'Mắt lồi', 'description': 'Nhãn cầu nhô ra phía trước, thường gặp trong bệnh Graves'},
            {'name': 'Nước tiểu sẫm màu', 'description': 'Nước tiểu có màu sẫm, nâu đến đen'},
            {'name': 'Phù bụng', 'description': 'Bụng căng phồng do tích tụ dịch trong khoang bụng'},
            {'name': 'Dễ bầm tím', 'description': 'Da dễ bị bầm tím khi va chạm nhẹ'},
            {'name': 'Đổ mồ hôi', 'description': 'Ra mồ hôi, thường do lo lắng hoặc căng thẳng'},
            {'name': 'Căng thẳng', 'description': 'Cảm giác áp lực, lo lắng'},
            {'name': 'Tăng năng lượng quá mức', 'description': 'Cảm giác tràn đầy năng lượng, hoạt động nhiều'},
            {'name': 'Hành vi bốc đồng', 'description': 'Hành động không suy nghĩ, thiếu kiểm soát'},
            {'name': 'Suy nghĩ tự sát', 'description': 'Ý nghĩ muốn kết thúc cuộc sống'},
            {'name': 'Cứng cơ', 'description': 'Cơ bị cứng, khó cử động'},
            {'name': 'Chậm vận động', 'description': 'Di chuyển chậm hơn bình thường'},
            {'name': 'Thay đổi giọng nói', 'description': 'Giọng nói thay đổi về âm sắc, âm lượng'},
            {'name': 'Đổ mồ hôi lạnh', 'description': 'Đổ mồ hôi lạnh, thường khi đau hoặc sốc'},
            {'name': 'Ho khan', 'description': 'Ho không có đờm'},
            {'name': 'Ho mạn tính', 'description': 'Ho kéo dài nhiều tuần hoặc tháng'},
            {'name': 'Cảm giác đi đại tiện không hết', 'description': 'Cảm giác chưa đi hết phân sau khi đại tiện'},
            {'name': 'Tức ngực', 'description': 'Cảm giác nặng, đè ép ở ngực'},
            {'name': 'Khó nói thành câu', 'description': 'Khó nói được câu hoàn chỉnh do thiếu hơi'},
            {'name': 'Hạch cổ sưng', 'description': 'Các hạch bạch huyết ở cổ bị sưng to'},
            {'name': 'Hơi thở hôi', 'description': 'Hơi thở có mùi khó chịu'},
            {'name': 'Sốt', 'description': 'Nhiệt độ cơ thể tăng cao hơn bình thường'}
        ]
        
        self.stdout.write('Adding missing symptoms...')
        for symptom_data in missing_symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={'description': symptom_data['description']}
            )
            if created:
                self.stdout.write(f'  Added symptom: {symptom.name}')
            else:
                self.stdout.write(f'  Symptom already exists: {symptom.name}')
                
        # Lấy lại tất cả các bệnh và thêm triệu chứng còn thiếu
        self.stdout.write('Updating diseases with missing symptoms...')
        diseases = Disease.objects.all()
        
        # Bệnh Glaucoma
        try:
            disease = Disease.objects.get(name='Bệnh Glaucoma')
            symptom = Symptom.objects.get(name='Cảm giác có dị vật trong mắt')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Hội chứng khô mắt
        try:
            disease = Disease.objects.get(name='Hội chứng khô mắt')
            symptom = Symptom.objects.get(name='Cảm giác bỏng rát')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Bệnh Meniere
        try:
            disease = Disease.objects.get(name='Bệnh Meniere')
            symptom = Symptom.objects.get(name='Mất thăng bằng')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Viêm da dị ứng
        try:
            disease = Disease.objects.get(name='Viêm da dị ứng')
            symptom = Symptom.objects.get(name='Sưng')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Bệnh vẩy nến
        try:
            disease = Disease.objects.get(name='Bệnh vẩy nến')
            for symptom_name in ['Vảy da', 'Móng dày']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Viêm nướu
        try:
            disease = Disease.objects.get(name='Viêm nướu')
            for symptom_name in ['Sưng nướu', 'Đau khi nhai', 'Nướu đỏ']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Sâu răng
        try:
            disease = Disease.objects.get(name='Sâu răng')
            for symptom_name in ['Lỗ trên răng', 'Đau khi ăn đồ ngọt, nóng, lạnh']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Nhiệt miệng
        try:
            disease = Disease.objects.get(name='Nhiệt miệng')
            for symptom_name in ['Đau miệng', 'Khó ăn uống']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Viêm đường tiết niệu
        try:
            disease = Disease.objects.get(name='Viêm đường tiết niệu')
            symptom = Symptom.objects.get(name='Đau vùng bàng quang')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Sỏi thận
        try:
            disease = Disease.objects.get(name='Sỏi thận')
            for symptom_name in ['Đau dữ dội vùng thắt lưng', 'Đau lan xuống bụng dưới']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Đái tháo đường
        try:
            disease = Disease.objects.get(name='Đái tháo đường')
            for symptom_name in ['Tiểu nhiều', 'Vết thương lâu lành']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Cường giáp
        try:
            disease = Disease.objects.get(name='Cường giáp')
            for symptom_name in ['Tăng nhịp tim', 'Mắt lồi']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Viêm gan B
        try:
            disease = Disease.objects.get(name='Viêm gan B')
            symptom = Symptom.objects.get(name='Nước tiểu sẫm màu')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Xơ gan
        try:
            disease = Disease.objects.get(name='Xơ gan')
            for symptom_name in ['Phù bụng', 'Dễ bầm tím']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Rối loạn lo âu
        try:
            disease = Disease.objects.get(name='Rối loạn lo âu')
            for symptom_name in ['Đổ mồ hôi', 'Căng thẳng']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Rối loạn lưỡng cực
        try:
            disease = Disease.objects.get(name='Rối loạn lưỡng cực')
            for symptom_name in ['Tăng năng lượng quá mức', 'Hành vi bốc đồng', 'Suy nghĩ tự sát']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Bệnh Parkinson
        try:
            disease = Disease.objects.get(name='Bệnh Parkinson')
            for symptom_name in ['Cứng cơ', 'Chậm vận động', 'Mất thăng bằng', 'Thay đổi giọng nói']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Thiếu máu cục bộ cơ tim
        try:
            disease = Disease.objects.get(name='Thiếu máu cục bộ cơ tim')
            for symptom_name in ['Đau ngực lan ra cánh tay trái', 'Đổ mồ hôi lạnh']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Suy tim
        try:
            disease = Disease.objects.get(name='Suy tim')
            symptom = Symptom.objects.get(name='Ho khan')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Trào ngược dạ dày thực quản
        try:
            disease = Disease.objects.get(name='Trào ngược dạ dày thực quản')
            symptom = Symptom.objects.get(name='Ho mạn tính')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Hội chứng ruột kích thích
        try:
            disease = Disease.objects.get(name='Hội chứng ruột kích thích')
            symptom = Symptom.objects.get(name='Cảm giác đi đại tiện không hết')
            disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptom to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Hen suyễn
        try:
            disease = Disease.objects.get(name='Hen suyễn')
            for symptom_name in ['Tức ngực', 'Khó nói thành câu']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Bệnh phổi tắc nghẽn mạn tính (COPD)
        try:
            disease = Disease.objects.get(name='Bệnh phổi tắc nghẽn mạn tính (COPD)')
            for symptom_name in ['Ho mạn tính', 'Tức ngực']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')
            
        # Viêm amidan
        try:
            disease = Disease.objects.get(name='Viêm amidan')
            for symptom_name in ['Hạch cổ sưng', 'Hơi thở hôi', 'Sốt']:
                symptom = Symptom.objects.get(name=symptom_name)
                disease.symptoms.add(symptom)
            self.stdout.write(f'  Added missing symptoms to {disease.name}')
        except (Disease.DoesNotExist, Symptom.DoesNotExist) as e:
            self.stdout.write(f'  Error: {str(e)}')

        self.stdout.write('Completed successfully!') 