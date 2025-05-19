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
                'symptoms': ['Chảy máu nướu', 'Sưng nướu', 'Hôi miệng', 'Đau khi nhai', 'Nướu đỏ'],
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
                'symptoms': ['Lo âu', 'Hồi hộp', 'Đổ mồ hôi', 'Khó thở', 'Mất ngủ', 'Căng thẳng', 'Đau đầu'],
                'severity': 'medium',
                'treatment_guidelines': 'Tâm lý trị liệu, liệu pháp nhận thức hành vi, thuốc chống lo âu nếu cần.'
            },
            {
                'name': 'Rối loạn lưỡng cực',
                'description': 'Rối loạn tâm trạng với các giai đoạn hưng cảm và trầm cảm luân phiên.',
                'symptoms': ['Thay đổi tâm trạng', 'Mất ngủ', 'Tăng năng lượng quá mức', 'Trầm cảm', 'Hành vi bốc đồng', 'Suy nghĩ tự sát'],
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
                'name': 'Thiếu máu cục bộ cơ tim',
                'description': 'Giảm cung cấp máu cho cơ tim do tắc nghẽn động mạch vành.',
                'symptoms': ['Đau ngực', 'Đau lan ra cánh tay trái', 'Khó thở', 'Đổ mồ hôi lạnh', 'Hồi hộp', 'Mệt mỏi'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc chẹn beta, thuốc chống đông máu, nong và đặt stent mạch vành, phẫu thuật bắc cầu nối.'
            },
            {
                'name': 'Suy tim',
                'description': 'Tim không đủ khả năng bơm máu đáp ứng nhu cầu cơ thể.',
                'symptoms': ['Khó thở', 'Mệt mỏi', 'Phù chân', 'Phù mặt', 'Đánh trống ngực khi nằm', 'Ho khan'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc ức chế men chuyển, chẹn beta, lợi tiểu, hạn chế natri, đôi khi cần thiết bị hỗ trợ tim hoặc ghép tim.'
            },
            {
                'name': 'Trào ngược dạ dày thực quản',
                'description': 'Acid dạ dày trào ngược lên thực quản gây viêm, khó chịu.',
                'symptoms': ['Ợ nóng', 'Ợ chua', 'Khó nuốt', 'Đau ngực', 'Buồn nôn', 'Nói khàn', 'Ho mạn tính'],
                'severity': 'medium',
                'treatment_guidelines': 'Thuốc ức chế bơm proton, thuốc kháng H2, thay đổi lối sống, ăn ít và không ăn trước khi đi ngủ.'
            },
            {
                'name': 'Hội chứng ruột kích thích',
                'description': 'Rối loạn chức năng ruột với các triệu chứng đau bụng, thay đổi thói quen đại tiện.',
                'symptoms': ['Đau bụng', 'Đầy hơi', 'Tiêu chảy', 'Táo bón', 'Chướng bụng', 'Cảm giác đi đại tiện không hết'],
                'severity': 'medium',
                'treatment_guidelines': 'Thay đổi chế độ ăn uống, thuốc chống co thắt, thuốc chống tiêu chảy hoặc nhuận tràng, quản lý stress.'
            },
            {
                'name': 'Hen suyễn',
                'description': 'Bệnh phổi mãn tính với viêm và co thắt đường thở, gây khó thở.',
                'symptoms': ['Khó thở', 'Thở khò khè', 'Ho', 'Tức ngực', 'Thở nhanh nông', 'Khó nói thành câu'],
                'severity': 'high',
                'treatment_guidelines': 'Thuốc giãn phế quản, corticosteroid dạng hít, kiểm soát yếu tố kích phát, kế hoạch hành động hen suyễn.'
            },
            {
                'name': 'Bệnh phổi tắc nghẽn mạn tính (COPD)',
                'description': 'Nhóm bệnh phổi mạn tính gây khó thở và giảm luồng khí.',
                'symptoms': ['Khó thở khi gắng sức', 'Ho mạn tính', 'Đờm có màu vàng hoặc xanh', 'Thở khò khè', 'Tức ngực'],
                'severity': 'high',
                'treatment_guidelines': 'Ngừng hút thuốc, thuốc giãn phế quản, corticosteroid dạng hít, oxy liệu pháp nếu cần.'
            },
            {
                'name': 'Viêm amidan',
                'description': 'Viêm amidan do vi khuẩn hoặc virus.',
                'symptoms': ['Đau họng', 'Khó nuốt', 'Sốt', 'Hạch cổ sưng', 'Đau tai', 'Hơi thở hôi'],
                'severity': 'medium',
                'treatment_guidelines': 'Kháng sinh nếu do vi khuẩn, giảm đau, uống nhiều nước, súc họng bằng nước muối, cắt amidan nếu tái phát nhiều lần.'
            },
        ]
        
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