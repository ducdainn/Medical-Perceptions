import datetime
from django.core.management.base import BaseCommand
from diagnosis.models import Symptom, Disease

class Command(BaseCommand):
    help = 'Adds more diverse symptoms and diseases to the database'

    def handle(self, *args, **options):
        # Thêm các triệu chứng mới
        new_symptoms_data = [
            # Triệu chứng về mắt
            {'name': 'Mờ mắt', 'description': 'Nhìn không rõ, hình ảnh bị mờ hoặc nhòe'},
            {'name': 'Đau mắt', 'description': 'Cảm giác đau ở vùng mắt'},
            {'name': 'Mắt đỏ', 'description': 'Mắt bị đỏ, sung huyết kết mạc'},
            {'name': 'Mắt khô', 'description': 'Cảm giác khô rát ở mắt, thiếu nước mắt'},
            {'name': 'Nhìn đôi', 'description': 'Nhìn thấy hai hình ảnh của một vật thể duy nhất'},
            {'name': 'Sưng mí mắt', 'description': 'Mí mắt bị sưng, có thể đỏ và đau'},
            {'name': 'Nhạy cảm với ánh sáng', 'description': 'Cảm thấy khó chịu khi tiếp xúc với ánh sáng'},
            {'name': 'Nổi bọt kết mạc', 'description': 'Xuất hiện bọt, u nhỏ trên kết mạc mắt'},
            {'name': 'Chảy nước mắt', 'description': 'Tiết nước mắt quá nhiều'},
            
            # Triệu chứng về tai
            {'name': 'Ù tai', 'description': 'Cảm giác nghe tiếng ù, rít trong tai'},
            {'name': 'Chóng mặt khi thay đổi tư thế', 'description': 'Cảm giác chóng mặt khi đứng dậy hoặc thay đổi tư thế đột ngột'},
            {'name': 'Đau tai', 'description': 'Cảm giác đau ở vùng tai'},
            {'name': 'Nghe kém', 'description': 'Giảm khả năng nghe, phải cố gắng mới nghe rõ'},
            {'name': 'Chảy dịch từ tai', 'description': 'Có dịch chảy ra từ tai'},
            {'name': 'Ngứa trong tai', 'description': 'Cảm giác ngứa bên trong ống tai'},
            
            # Triệu chứng về da
            {'name': 'Da khô', 'description': 'Da trở nên khô, có thể bong tróc'},
            {'name': 'Mụn nước', 'description': 'Mụn chứa dịch trong xuất hiện trên da'},
            {'name': 'Mụn mủ', 'description': 'Mụn chứa mủ màu trắng hoặc vàng'},
            {'name': 'Bỏng rát da', 'description': 'Cảm giác bỏng rát trên da'},
            {'name': 'Thay đổi màu sắc móng', 'description': 'Móng tay, móng chân thay đổi màu sắc'},
            {'name': 'Rụng tóc', 'description': 'Tóc rụng nhiều hơn bình thường'},
            {'name': 'Nổi mề đay', 'description': 'Nổi sẩn đỏ, ngứa trên da'},
            {'name': 'Vết thâm', 'description': 'Vùng da bị thâm, sẫm màu hơn'},
            {'name': 'Sẹo lồi', 'description': 'Sẹo phát triển quá mức, nhô cao hơn mặt da'},
            
            # Triệu chứng về miệng và răng
            {'name': 'Đau răng', 'description': 'Cảm giác đau ở một hoặc nhiều răng'},
            {'name': 'Chảy máu nướu', 'description': 'Nướu chảy máu khi đánh răng hoặc ăn'},
            {'name': 'Hôi miệng', 'description': 'Hơi thở có mùi hôi'},
            {'name': 'Lưỡi trắng', 'description': 'Lưỡi có lớp màu trắng phủ bên trên'},
            {'name': 'Khô miệng', 'description': 'Cảm giác khô trong miệng, thiếu nước bọt'},
            {'name': 'Loét miệng', 'description': 'Vết loét trong miệng, thường đau'},
            {'name': 'Ê buốt răng', 'description': 'Cảm giác ê buốt khi ăn nóng, lạnh hoặc ngọt'},
            
            # Triệu chứng về tiết niệu
            {'name': 'Tiểu rắt', 'description': 'Đi tiểu thường xuyên, số lượng ít'},
            {'name': 'Tiểu buốt', 'description': 'Cảm giác buốt, đau khi đi tiểu'},
            {'name': 'Tiểu ra máu', 'description': 'Nước tiểu có màu đỏ do có máu'},
            {'name': 'Tiểu đêm', 'description': 'Phải thức dậy đi tiểu vào ban đêm'},
            {'name': 'Khó tiểu', 'description': 'Khó khăn khi bắt đầu tiểu hoặc duy trì dòng tiểu'},
            {'name': 'Tiểu không tự chủ', 'description': 'Không kiểm soát được việc đi tiểu'},
            {'name': 'Nước tiểu đục', 'description': 'Nước tiểu không trong, có màu đục'},
            
            # Triệu chứng về nội tiết
            {'name': 'Khát nước nhiều', 'description': 'Cảm giác khát nước thường xuyên, uống nhiều nước'},
            {'name': 'Đổ mồ hôi nhiều', 'description': 'Ra mồ hôi nhiều hơn bình thường'},
            {'name': 'Không chịu được nóng', 'description': 'Cảm thấy khó chịu khi ở trong môi trường nóng'},
            {'name': 'Không chịu được lạnh', 'description': 'Cảm thấy khó chịu khi ở trong môi trường lạnh'},
            {'name': 'Tăng cân không kiểm soát', 'description': 'Tăng cân mà không thay đổi chế độ ăn'},
            {'name': 'Giảm cân không kiểm soát', 'description': 'Giảm cân mà không thay đổi chế độ ăn hoặc tập luyện'},
            
            # Triệu chứng về tiêu hóa bổ sung
            {'name': 'Khó nuốt', 'description': 'Cảm giác khó khăn khi nuốt thức ăn hoặc nước uống'},
            {'name': 'Vàng da', 'description': 'Da và mắt có màu vàng'},
            {'name': 'Phân màu đen', 'description': 'Phân có màu đen, thường do xuất huyết đường tiêu hóa trên'},
            {'name': 'Phân nhạt màu', 'description': 'Phân có màu nhạt, xám hoặc trắng'},
            {'name': 'Đau vùng gan', 'description': 'Đau ở vùng gan, bên phải của bụng trên'},
            
            # Triệu chứng về tâm thần kinh bổ sung
            {'name': 'Mất ngủ dai dẳng', 'description': 'Khó đi vào giấc ngủ hoặc duy trì giấc ngủ trong thời gian dài'},
            {'name': 'Ảo giác', 'description': 'Nhìn, nghe, cảm nhận những thứ không có thật'},
            {'name': 'Rối loạn lo âu', 'description': 'Lo lắng quá mức về nhiều việc, khó kiểm soát'},
            {'name': 'Suy giảm trí nhớ', 'description': 'Khó nhớ thông tin mới, quên những sự kiện gần đây'},
            {'name': 'Rối loạn giấc ngủ', 'description': 'Thay đổi chu kỳ ngủ-thức, ngủ quá nhiều hoặc quá ít'},
            {'name': 'Ám ảnh', 'description': 'Suy nghĩ, hình ảnh hoặc thôi thúc lặp đi lặp lại không mong muốn'},
            {'name': 'Tự hại', 'description': 'Hành vi cố ý gây tổn thương cho bản thân'},
            
            # Triệu chứng bổ sung về tim mạch
            {'name': 'Đánh trống ngực khi nằm', 'description': 'Cảm giác tim đập mạnh, nhanh khi nằm xuống'},
            {'name': 'Tím tái môi và đầu chi', 'description': 'Môi, đầu ngón tay, ngón chân có màu tím'},
            {'name': 'Ngất', 'description': 'Mất ý thức tạm thời, thường kèm theo ngã'},
            {'name': 'Phù mặt', 'description': 'Sưng ở vùng mặt'},
            {'name': 'Đau ngực lan ra cánh tay trái', 'description': 'Đau ngực lan xuống cánh tay trái'},
            
            # Triệu chứng về hô hấp bổ sung
            {'name': 'Nói khàn', 'description': 'Giọng nói trở nên khàn, thay đổi âm vực'},
            {'name': 'Thở nhanh nông', 'description': 'Hơi thở nhanh và nông'},
            {'name': 'Ngưng thở khi ngủ', 'description': 'Ngưng thở tạm thời trong khi ngủ, thường kèm theo ngáy to'},
            {'name': 'Hen suyễn', 'description': 'Khó thở, thở khò khè do co thắt phế quản'},
            {'name': 'Viêm phổi', 'description': 'Viêm nhiễm trong phổi, gây ho, sốt, khó thở'},
            
            # Thêm nhiều triệu chứng mới nữa
            {'name': 'Khô họng', 'description': 'Cảm giác khô rát trong họng'},
            {'name': 'Đau nhức xương khớp', 'description': 'Cảm giác đau nhức ở các khớp xương'},
            {'name': 'Viêm khớp', 'description': 'Viêm các khớp, thường gây đau và sưng'},
            {'name': 'Viêm lợi', 'description': 'Viêm nướu răng, thường đỏ và chảy máu'},
            {'name': 'Viêm da tiếp xúc', 'description': 'Viêm da do tiếp xúc với chất gây kích ứng'},
            {'name': 'Viêm xoang', 'description': 'Viêm các xoang cạnh mũi'},
            {'name': 'Nghẹt mũi', 'description': 'Khó thở qua mũi do tắc nghẽn'},
            {'name': 'Mụn trứng cá', 'description': 'Mụn nhỏ, đỏ hoặc có mủ trên da'},
            {'name': 'Nhức nửa đầu', 'description': 'Đau dữ dội ở một bên đầu'},
            {'name': 'Nhạy cảm với âm thanh', 'description': 'Khó chịu với tiếng ồn'},
            {'name': 'Thiếu máu', 'description': 'Giảm số lượng hồng cầu hoặc hemoglobin'},
            {'name': 'Rối loạn nhịp tim', 'description': 'Nhịp tim không đều'},
            {'name': 'Viêm khớp dạng thấp', 'description': 'Viêm khớp do hệ miễn dịch tấn công các mô của cơ thể'},
            {'name': 'Viêm đại tràng', 'description': 'Viêm niêm mạc đại tràng'},
            {'name': 'Rối loạn tiêu hóa', 'description': 'Các vấn đề về tiêu hóa, như khó tiêu, đầy hơi'},
        ]
        
        self.stdout.write('Adding new symptoms...')
        for symptom_data in new_symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={'description': symptom_data['description']}
            )
            if created:
                self.stdout.write(f'  Added symptom: {symptom.name}')
            else:
                self.stdout.write(f'  Symptom already exists: {symptom.name}')
        
        # Thêm các bệnh mới
        new_diseases_data = [
            {
                'name': 'Bệnh Glaucoma',
                'description': 'Bệnh tăng nhãn áp, tổn thương thần kinh thị giác dẫn đến mù lòa nếu không được điều trị.',
                'symptoms': ['Mờ mắt', 'Đau mắt', 'Nhìn đôi', 'Đau đầu', 'Nhạy cảm với ánh sáng', 'Buồn nôn'],
                'severity': 'high',
                'treatment_guidelines': 'Dùng thuốc nhỏ mắt giảm nhãn áp, phẫu thuật laser hoặc phẫu thuật lỗ thoát nước.'
            },
            {
                'name': 'Viêm kết mạc',
                'description': 'Viêm màng kết mạc của mắt, thường do vi khuẩn, virus hoặc dị ứng.',
                'symptoms': ['Mắt đỏ', 'Ngứa', 'Chảy nước mắt', 'Sưng mí mắt', 'Cảm giác có dị vật trong mắt'],
                'severity': 'low',
                'treatment_guidelines': 'Dùng thuốc nhỏ mắt kháng sinh hoặc kháng viêm, rửa mắt bằng nước muối sinh lý.'
            },
            {
                'name': 'Hội chứng khô mắt',
                'description': 'Tình trạng mắt không sản xuất đủ nước mắt hoặc nước mắt bốc hơi quá nhanh.',
                'symptoms': ['Mắt khô', 'Cảm giác bỏng rát', 'Mờ mắt', 'Nhạy cảm với ánh sáng', 'Mắt đỏ'],
                'severity': 'medium',
                'treatment_guidelines': 'Dùng nước mắt nhân tạo, thuốc kích thích sản xuất nước mắt, nút lỗ lệ đạo.'
            },
            {
                'name': 'Viêm tai giữa',
                'description': 'Viêm nhiễm ở tai giữa, thường gặp ở trẻ em sau nhiễm trùng đường hô hấp trên.',
                'symptoms': ['Đau tai', 'Sốt', 'Chảy dịch từ tai', 'Nghe kém', 'Ù tai', 'Chóng mặt'],
                'severity': 'medium',
                'treatment_guidelines': 'Dùng kháng sinh, thuốc giảm đau, giảm viêm, đôi khi cần đặt ống thông nhĩ.'
            },
            {
                'name': 'Bệnh Meniere',
                'description': 'Rối loạn tai trong ảnh hưởng đến thính giác và thăng bằng.',
                'symptoms': ['Chóng mặt', 'Ù tai', 'Nghe kém', 'Buồn nôn', 'Mất thăng bằng', 'Chóng mặt khi thay đổi tư thế'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc chống chóng mặt, lợi tiểu, thay đổi chế độ ăn ít muối, đôi khi cần phẫu thuật.'
            },
            {
                'name': 'Viêm da dị ứng',
                'description': 'Phản ứng viêm da do tiếp xúc với chất gây dị ứng.',
                'symptoms': ['Ngứa', 'Phát ban', 'Da khô', 'Mụn nước', 'Bỏng rát da', 'Sưng'],
                'severity': 'medium',
                'treatment_guidelines': 'Tránh tiếp xúc với tác nhân gây dị ứng, dùng thuốc kháng histamine, corticosteroid bôi tại chỗ.'
            },
            {
                'name': 'Bệnh vẩy nến',
                'description': 'Bệnh tự miễn gây tăng sinh tế bào da quá mức, tạo mảng vảy đỏ, ngứa.',
                'symptoms': ['Phát ban', 'Vảy da', 'Ngứa', 'Da khô', 'Vết thâm', 'Móng dày'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc bôi corticosteroid, vitamin D3, retinoid, liệu pháp ánh sáng, thuốc ức chế miễn dịch.'
            },
            {
                'name': 'Viêm nướu',
                'description': 'Viêm nướu răng, thường do vệ sinh răng miệng kém.',
                'symptoms': ['Chảy máu nướu', 'Sưng nướu', 'Hôi miệng', 'Đau khi nhai', 'Nướu đỏ', 'Viêm lợi'],
                'severity': 'medium',
                'treatment_guidelines': 'Vệ sinh răng miệng kỹ, cạo vôi răng, súc miệng bằng nước muối hoặc dung dịch sát khuẩn.'
            },
            {
                'name': 'Sâu răng',
                'description': 'Hư hại men răng và ngà răng do vi khuẩn.',
                'symptoms': ['Đau răng', 'Ê buốt răng', 'Lỗ trên răng', 'Đau khi ăn đồ ngọt, nóng, lạnh'],
                'severity': 'medium',
                'treatment_guidelines': 'Trám răng, điều trị tủy nếu sâu sâu, nhổ răng nếu hư hại nặng.'
            },
            {
                'name': 'Nhiệt miệng',
                'description': 'Vết loét nhỏ trong miệng, thường tự khỏi sau 1-2 tuần.',
                'symptoms': ['Loét miệng', 'Đau miệng', 'Khó ăn uống', 'Sốt nhẹ'],
                'severity': 'low',
                'treatment_guidelines': 'Súc miệng bằng nước muối, thuốc giảm đau tại chỗ, tránh thức ăn cay, nóng.'
            },
            {
                'name': 'Viêm đường tiết niệu',
                'description': 'Nhiễm trùng đường tiết niệu, thường gặp ở phụ nữ.',
                'symptoms': ['Tiểu rắt', 'Tiểu buốt', 'Nước tiểu đục', 'Đau vùng bàng quang', 'Tiểu ra máu'],
                'severity': 'medium',
                'treatment_guidelines': 'Dùng kháng sinh, uống nhiều nước, thuốc giảm đau.'
            },
            {
                'name': 'Sỏi thận',
                'description': 'Sỏi hình thành trong thận, có thể di chuyển xuống đường tiết niệu.',
                'symptoms': ['Đau dữ dội vùng thắt lưng', 'Tiểu ra máu', 'Buồn nôn', 'Tiểu rắt', 'Đau lan xuống bụng dưới'],
                'severity': 'high',
                'treatment_guidelines': 'Uống nhiều nước, thuốc giảm đau, tán sỏi bằng sóng xung kích, phẫu thuật nội soi nếu cần.'
            },
            {
                'name': 'Đái tháo đường',
                'description': 'Rối loạn chuyển hóa glucose, tăng đường huyết do thiếu hoặc kém đáp ứng insulin.',
                'symptoms': ['Khát nước nhiều', 'Tiểu nhiều', 'Giảm cân không kiểm soát', 'Mệt mỏi', 'Mờ mắt', 'Vết thương lâu lành'],
                'severity': 'high',
                'treatment_guidelines': 'Kiểm soát chế độ ăn, tập luyện, thuốc hạ đường huyết, insulin nếu cần.'
            },
            {
                'name': 'Cường giáp',
                'description': 'Tuyến giáp hoạt động quá mức, sản xuất nhiều hormone giáp.',
                'symptoms': ['Đổ mồ hôi nhiều', 'Không chịu được nóng', 'Giảm cân không kiểm soát', 'Tăng nhịp tim', 'Run tay', 'Mắt lồi'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc kháng giáp, iốt phóng xạ, phẫu thuật cắt tuyến giáp.'
            },
            {
                'name': 'Suy giáp',
                'description': 'Tuyến giáp hoạt động kém, sản xuất không đủ hormone giáp.',
                'symptoms': ['Mệt mỏi', 'Không chịu được lạnh', 'Tăng cân không kiểm soát', 'Da khô', 'Táo bón', 'Trầm cảm'],
                'severity': 'medium',
                'treatment_guidelines': 'Bổ sung hormone tuyến giáp (Levothyroxine).'
            },
            {
                'name': 'Viêm gan B',
                'description': 'Viêm gan do virus viêm gan B (HBV), có thể cấp tính hoặc mạn tính.',
                'symptoms': ['Vàng da', 'Mệt mỏi', 'Buồn nôn', 'Đau vùng gan', 'Chán ăn', 'Sốt', 'Nước tiểu sẫm màu'],
                'severity': 'high',
                'treatment_guidelines': 'Nghỉ ngơi, ăn uống lành mạnh, thuốc kháng virus, theo dõi chức năng gan.'
            },
            {
                'name': 'Xơ gan',
                'description': 'Tình trạng sẹo hóa gan do tổn thương mạn tính, ảnh hưởng đến chức năng gan.',
                'symptoms': ['Vàng da', 'Phù chân', 'Phù bụng', 'Dễ bầm tím', 'Mệt mỏi', 'Chán ăn', 'Phân nhạt màu'],
                'severity': 'high',
                'treatment_guidelines': 'Điều trị nguyên nhân, kiêng rượu, chế độ ăn ít muối, thuốc lợi tiểu, ghép gan trong trường hợp nặng.'
            },
            {
                'name': 'Rối loạn lo âu',
                'description': 'Rối loạn tâm lý với lo lắng quá mức, ảnh hưởng đến sinh hoạt hàng ngày.',
                'symptoms': ['Lo âu', 'Hồi hộp', 'Đổ mồ hôi', 'Khó thở', 'Mất ngủ', 'Căng thẳng', 'Đau đầu', 'Rối loạn lo âu'],
                'severity': 'medium',
                'treatment_guidelines': 'Tâm lý trị liệu, liệu pháp nhận thức hành vi, thuốc chống lo âu nếu cần.'
            },
            {
                'name': 'Rối loạn lưỡng cực',
                'description': 'Rối loạn tâm trạng với các giai đoạn hưng cảm và trầm cảm luân phiên.',
                'symptoms': ['Thay đổi tâm trạng', 'Mất ngủ', 'Tăng năng lượng quá mức', 'Trầm cảm', 'Hành vi bốc đồng', 'Suy nghĩ tự sát', 'Tự hại'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc ổn định tâm trạng, liệu pháp tâm lý, thuốc chống trầm cảm và chống loạn thần.'
            },
            {
                'name': 'Bệnh Parkinson',
                'description': 'Rối loạn thoái hóa thần kinh ảnh hưởng đến vận động, gây run, cứng cơ.',
                'symptoms': ['Run tay', 'Cứng cơ', 'Chậm vận động', 'Mất thăng bằng', 'Thay đổi giọng nói', 'Khó nuốt'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc Levodopa, thuốc chống Parkinson khác, vật lý trị liệu, đôi khi cần phẫu thuật kích thích não sâu.'
            },
            {
                'name': 'Viêm phế quản',
                'description': 'Viêm niêm mạc phế quản, thường gây ho nhiều và khó thở.',
                'symptoms': ['Ho kéo dài', 'Ho có đờm', 'Khò khè', 'Khó thở', 'Đau ngực', 'Mệt mỏi'],
                'severity': 'medium',
                'treatment_guidelines': 'Thuốc long đờm, giãn phế quản, kháng sinh nếu do vi khuẩn, hít thuốc corticosteroid nếu cần.'
            },
            {
                'name': 'Viêm xoang',
                'description': 'Viêm niêm mạc các xoang cạnh mũi, thường do vi khuẩn hoặc virus.',
                'symptoms': ['Đau đầu', 'Nghẹt mũi', 'Chảy mũi', 'Giảm khứu giác', 'Đau mặt', 'Sốt nhẹ', 'Ho về đêm'],
                'severity': 'medium',
                'treatment_guidelines': 'Rửa mũi bằng nước muối sinh lý, kháng sinh nếu do vi khuẩn, thuốc giảm viêm, giảm đau.'
            },
            {
                'name': 'Viêm phổi',
                'description': 'Viêm nhiễm tại phổi, có thể do vi khuẩn, virus hoặc nấm.',
                'symptoms': ['Sốt cao', 'Ho có đờm màu vàng hoặc xanh', 'Khó thở', 'Đau ngực khi hít thở', 'Mệt mỏi', 'Đổ mồ hôi đêm'],
                'severity': 'high',
                'treatment_guidelines': 'Kháng sinh phù hợp nếu do vi khuẩn, thuốc kháng virus nếu do virus, bổ sung oxy nếu cần, nghỉ ngơi và uống nhiều nước.'
            },
            {
                'name': 'Hen phế quản',
                'description': 'Bệnh mạn tính gây viêm và co thắt đường thở, làm khó thở.',
                'symptoms': ['Khó thở', 'Khò khè', 'Tức ngực', 'Ho, đặc biệt về đêm', 'Khó thở khi gắng sức', 'Hen suyễn'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc giãn phế quản dạng hít, corticosteroid dạng hít, thuốc kiểm soát dài hạn, tránh các yếu tố kích phát.'
            },
            {
                'name': 'Viêm khớp dạng thấp',
                'description': 'Bệnh tự miễn gây viêm màng hoạt dịch tại các khớp.',
                'symptoms': ['Đau nhức xương khớp', 'Sưng khớp', 'Cứng khớp buổi sáng', 'Mệt mỏi', 'Sốt nhẹ', 'Viêm khớp dạng thấp', 'Viêm khớp'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc chống viêm không steroid (NSAIDs), thuốc chống thấp khớp làm thay đổi bệnh (DMARDs), thuốc sinh học, vật lý trị liệu.'
            },
            {
                'name': 'Đau thần kinh tọa',
                'description': 'Đau dọc theo đường đi của dây thần kinh tọa, thường do đĩa đệm thoát vị chèn ép.',
                'symptoms': ['Đau từ lưng dưới xuống chân', 'Tê bì chân', 'Yếu chân', 'Khó di chuyển', 'Đau tăng khi ngồi'],
                'severity': 'medium',
                'treatment_guidelines': 'Thuốc giảm đau, vật lý trị liệu, nghỉ ngơi, tiêm corticosteroid cạnh cột sống, phẫu thuật nếu nghiêm trọng.'
            },
            {
                'name': 'Viêm loét dạ dày',
                'description': 'Vết loét ở niêm mạc dạ dày, thường do vi khuẩn H. pylori hoặc sử dụng NSAIDs kéo dài.',
                'symptoms': ['Đau thượng vị', 'Buồn nôn', 'Nôn', 'Chán ăn', 'Đầy hơi', 'Ợ chua', 'Phân đen'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc ức chế bơm proton (PPI), kháng sinh nếu do H. pylori, tránh rượu và thức ăn cay nóng, thuốc kháng acid.'
            },
        ]
        
        # Dictionary to store symptom objects
        symptom_objects = {}
        for symptom in Symptom.objects.all():
            symptom_objects[symptom.name] = symptom
        
        self.stdout.write('Adding new diseases...')
        for disease_data in new_diseases_data:
            disease, created = Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults={
                    'description': disease_data['description'],
                    'severity': disease_data['severity'],
                    'treatment_guidelines': disease_data['treatment_guidelines']
                }
            )
            
            if created:
                self.stdout.write(f'  Added disease: {disease.name}')
                # Add symptoms to the disease
                for symptom_name in disease_data['symptoms']:
                    if symptom_name in symptom_objects:
                        disease.symptoms.add(symptom_objects[symptom_name])
                    else:
                        self.stdout.write(f'    Warning: Symptom "{symptom_name}" not found')
            else:
                self.stdout.write(f'  Disease already exists: {disease.name}')
                
        self.stdout.write(self.style.SUCCESS('Successfully added more data to the database!')) 