from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Sum, F, Q
from .models import Medicine, Inventory, Prescription, Transaction, PrescriptionItem, TransactionItem, PrescriptionRequest
from .forms import (
    MedicineForm, PrescriptionForm, TransactionForm,
    PrescriptionItemFormSet, get_transaction_item_formset
)
from accounts.decorators import medicine_view_only, pharmacist_required, admin_required, admin_or_web_manager_required
from diagnosis.models import Symptom, Disease
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.functions import TruncDay, TruncMonth

User = get_user_model()

@login_required
def pharmacy_dashboard(request):
    medicines = Medicine.objects.all()
    inventory = Inventory.objects.all()
    prescriptions = Prescription.objects.all().order_by('-created_at')
    transactions = Transaction.objects.all().order_by('-created_at')
    
    context = {
        'medicines': medicines,
        'inventory': inventory,
        'prescriptions': prescriptions,
        'transactions': transactions,
    }
    return render(request, 'pharmacy/dashboard.html', context)

@medicine_view_only
def medicine_list(request):
    medicines = Medicine.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/medicine_list.html', {
        'medicines': medicines,
        'title': 'Danh sách thuốc'
    })

@pharmacist_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, 'Thêm thuốc mới thành công.')
            return redirect('pharmacy:medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'title': 'Thêm thuốc mới'
    })

@medicine_view_only
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    inventory = Inventory.objects.filter(medicine=medicine).first()
    return render(request, 'pharmacy/medicine_detail.html', {
        'medicine': medicine,
        'inventory': inventory,
        'title': f'Chi tiết thuốc: {medicine.name}'
    })

@admin_or_web_manager_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thuốc thành công.')
            return redirect('pharmacy:medicine_detail', pk=medicine.pk)
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'title': f'Chỉnh sửa thuốc: {medicine.name}'
    })

@admin_or_web_manager_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Xóa thuốc thành công.')
        return redirect('pharmacy:medicine_list')
    return redirect('pharmacy:medicine_detail', pk=pk)

@login_required
def inventory_management(request):
    inventory = Inventory.objects.all()
    medicines = Medicine.objects.all()
    return render(request, 'pharmacy/inventory.html', {
        'inventory': inventory,
        'medicines': medicines
    })

@login_required
def inventory_create(request):
    if request.method == 'POST':
        medicine_id = request.POST.get('medicine')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        min_quantity = request.POST.get('min_quantity')
        
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            inventory = Inventory.objects.create(
                medicine=medicine,
                quantity=quantity,
                unit=unit,
                min_quantity=min_quantity
            )
            messages.success(request, 'Thêm tồn kho thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('pharmacy:inventory')

@login_required
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        try:
            inventory.quantity = request.POST.get('quantity')
            inventory.unit = request.POST.get('unit')
            inventory.min_quantity = request.POST.get('min_quantity')
            inventory.save()
            messages.success(request, 'Cập nhật tồn kho thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('pharmacy:inventory')

@login_required
def inventory_delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        try:
            inventory.delete()
            messages.success(request, 'Xóa tồn kho thành công.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('pharmacy:inventory')

@login_required
def prescription_list(request):
    if request.user.is_staff:
        prescriptions = Prescription.objects.all().order_by('-created_at')
    else:
        prescriptions = Prescription.objects.filter(patient=request.user).order_by('-created_at')
    
    return render(request, 'pharmacy/prescription_list.html', {
        'prescriptions': prescriptions,
        'title': 'Danh sách đơn thuốc'
    })

@login_required
def request_prescription(request):
    """Xử lý yêu cầu kê đơn thuốc từ kết quả khuyến nghị"""
    if request.method == 'POST':
        try:
            # Get data from the form
            symptoms_str = request.POST.get('symptoms', '')
            symptoms_ids = [s.strip() for s in symptoms_str.split(',') if s.strip()]
            disease = request.POST.get('disease', '')
            disease_name_vi = request.POST.get('disease_name_vi', '')
            recommended_drug = request.POST.get('recommended_drug', '')
            
            # Enhanced debug logging
            print(f"REQUEST PRESCRIPTION DEBUG: Creating prescription request for user {request.user.username}")
            print(f"REQUEST PRESCRIPTION DEBUG: Disease: {disease}, Disease VI: {disease_name_vi}")
            print(f"REQUEST PRESCRIPTION DEBUG: Symptom IDs: {symptoms_ids}")
            print(f"REQUEST PRESCRIPTION DEBUG: Recommended drug: {recommended_drug}")
            print(f"REQUEST PRESCRIPTION DEBUG: Request method: {request.method}")
            print(f"REQUEST PRESCRIPTION DEBUG: Is AJAX: {'XMLHttpRequest' in request.headers.get('X-Requested-With', '')}")
            
            # Input validation
            if not disease and not disease_name_vi:
                raise ValueError("Không tìm thấy thông tin về bệnh.")
            
            if not recommended_drug:
                raise ValueError("Không tìm thấy thông tin về thuốc khuyến nghị.")
            
            # Get symptom names for better readability
            symptoms_text = []
            for symptom_id in symptoms_ids:
                if symptom_id:
                    try:
                        symptom = Symptom.objects.get(pk=int(symptom_id))
                        symptoms_text.append(symptom.name)
                    except (Symptom.DoesNotExist, ValueError) as e:
                        print(f"REQUEST PRESCRIPTION DEBUG: Could not find symptom {symptom_id}: {e}")
            
            symptoms_str = ", ".join(symptoms_text) if symptoms_text else "Không có triệu chứng cụ thể"
            
            # Create the prescription request
            prescription_request = PrescriptionRequest.objects.create(
                patient=request.user,
                recommended_drug=recommended_drug,
                disease=disease_name_vi or disease,
                symptoms=symptoms_str,
                status='pending'
            )
            
            # Log success
            print(f"REQUEST PRESCRIPTION DEBUG: Successfully created request #{prescription_request.id}")
            print(f"REQUEST PRESCRIPTION DEBUG: Request details - Patient: {prescription_request.patient.username}, Disease: {prescription_request.disease}, Status: {prescription_request.status}")
            
            # Check if the request was actually created
            try:
                verification = PrescriptionRequest.objects.get(pk=prescription_request.id)
                print(f"REQUEST PRESCRIPTION DEBUG: Verified request exists in database with ID #{verification.id}")
            except PrescriptionRequest.DoesNotExist:
                print(f"REQUEST PRESCRIPTION DEBUG: ERROR - Could not verify request in database after creation!")
            
            # Notify user and redirect
            messages.success(request, 'Yêu cầu kê đơn thuốc đã được gửi thành công. Dược sĩ sẽ xem xét và xử lý yêu cầu của bạn.')
            
            # Check if this is an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            print(f"REQUEST PRESCRIPTION DEBUG: Is AJAX request: {is_ajax}")
            
            if is_ajax:
                redirect_url = reverse('pharmacy:prescription_request_detail', kwargs={'pk': prescription_request.pk})
                print(f"REQUEST PRESCRIPTION DEBUG: AJAX response with redirect to {redirect_url}")
                return JsonResponse({
                    'success': True,
                    'message': 'Yêu cầu kê đơn thuốc đã được gửi thành công.',
                    'redirect_url': redirect_url
                })
            else:
                print(f"REQUEST PRESCRIPTION DEBUG: Standard redirect to detail page")
                return redirect('pharmacy:prescription_request_detail', pk=prescription_request.pk)
        except Exception as e:
            # Log and handle errors
            import traceback
            print(f"REQUEST PRESCRIPTION DEBUG: Error creating request: {e}")
            print(f"REQUEST PRESCRIPTION DEBUG: Traceback: {traceback.format_exc()}")
            
            error_message = f'Có lỗi xảy ra khi gửi yêu cầu: {str(e)}'
            messages.error(request, error_message)
            
            # Handle AJAX request errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                print(f"REQUEST PRESCRIPTION DEBUG: Returning JSON error response")
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=400)
            else:
                print(f"REQUEST PRESCRIPTION DEBUG: Redirecting to recommend_drug after error")
                return redirect('diagnosis:recommend_drug')
    
    # Default fallback for GET requests
    print(f"REQUEST PRESCRIPTION DEBUG: GET request - redirecting to recommend_drug")
    messages.info(request, 'Vui lòng sử dụng khuyến nghị thuốc để tạo yêu cầu kê đơn.')
    return redirect('diagnosis:recommend_drug')

@login_required
def prescription_request_list(request):
    """Hiển thị danh sách yêu cầu kê đơn thuốc của người dùng hiện tại"""
    prescription_requests = PrescriptionRequest.objects.filter(patient=request.user).order_by('-created_at')
    
    paginator = Paginator(prescription_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pharmacy/prescription_request_list.html', {
        'page_obj': page_obj,
        'total_requests': prescription_requests.count(),
        'pending_requests': prescription_requests.filter(status='pending').count(),
        'completed_requests': prescription_requests.filter(status='completed').count(),
    })

@login_required
def prescription_request_detail(request, pk):
    """Hiển thị chi tiết yêu cầu kê đơn thuốc"""
    prescription_request = get_object_or_404(PrescriptionRequest, pk=pk)
    
    # Kiểm tra quyền truy cập - chỉ cho phép dược sĩ hoặc chủ sở hữu yêu cầu
    if prescription_request.patient != request.user and not (request.user.is_pharmacist or request.user.is_staff):
        messages.error(request, 'Bạn không có quyền truy cập vào yêu cầu này.')
        return redirect('pharmacy:prescription_request_list')
    
    return render(request, 'pharmacy/prescription_request_detail.html', {
        'request': prescription_request,
    })

@login_required
def pharmacist_prescription_requests(request):
    """Hiển thị danh sách yêu cầu kê đơn thuốc cho dược sĩ"""
    # Print debug info for user
    print(f"PHARMACIST REQUESTS DEBUG: User: {request.user.username}, is_pharmacist: {request.user.is_pharmacist}, is_staff: {request.user.is_staff}, is_admin: {request.user.is_admin}")
    
    # Check if user has pharmacist permissions
    if not (request.user.is_pharmacist or request.user.is_staff or request.user.is_admin):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    # Default to 'all' status filter if none specified
    status_filter = request.GET.get('status', 'all')
    
    # Find all prescription requests regardless of status initially
    try:
        prescription_requests = PrescriptionRequest.objects.all().order_by('-created_at')
        
        # Apply status filter if needed
        if status_filter != 'all':
            prescription_requests = prescription_requests.filter(status=status_filter)
        
        # Count requests by status for statistics
        total_count = PrescriptionRequest.objects.count()
        pending_count = PrescriptionRequest.objects.filter(status='pending').count()
        approved_count = PrescriptionRequest.objects.filter(status='approved').count()
        completed_count = PrescriptionRequest.objects.filter(status='completed').count()
        rejected_count = PrescriptionRequest.objects.filter(status='rejected').count()
        
        # Enhanced debug logging
        print(f"PHARMACIST REQUESTS DEBUG: Database connection successful")
        print(f"PHARMACIST REQUESTS DEBUG: Total requests in DB: {total_count}")
        print(f"PHARMACIST REQUESTS DEBUG: Status filter: {status_filter}")
        print(f"PHARMACIST REQUESTS DEBUG: Filtered request count: {prescription_requests.count()}")
        print(f"PHARMACIST REQUESTS DEBUG: Breakdown - Pending: {pending_count}, Approved: {approved_count}, Completed: {completed_count}, Rejected: {rejected_count}")
        
        # Print all request IDs for debugging
        for req in prescription_requests:
            print(f"PHARMACIST REQUESTS DEBUG: Request #{req.id} - {req.patient.username} - {req.status}")
        
        # Create context - we'll just directly pass the queryset without pagination for simplicity
        context = {
            'prescription_requests': prescription_requests,
            'status_filter': status_filter,
            'total_requests': total_count,
            'pending_requests': pending_count,
            'approved_requests': approved_count,
            'completed_requests': completed_count,
            'rejected_requests': rejected_count,
        }
        
        print(f"PHARMACIST REQUESTS DEBUG: Rendering template with context: {context}")
        return render(request, 'pharmacy/pharmacist_prescription_requests.html', context)
        
    except Exception as e:
        # Log and handle errors
        print(f"PHARMACIST REQUESTS DEBUG: Error: {str(e)}")
        messages.error(request, f"Có lỗi xảy ra: {str(e)}")
        return redirect('pharmacy:dashboard')

@login_required
def approve_prescription_request(request, pk):
    """Dược sĩ xử lý và duyệt yêu cầu kê đơn thuốc"""
    if not (request.user.is_pharmacist or request.user.is_staff):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('home')
    
    prescription_request = get_object_or_404(PrescriptionRequest, pk=pk)
    
    if prescription_request.status != 'pending':
        messages.error(request, 'Yêu cầu này đã được xử lý trước đó.')
        return redirect('pharmacy:pharmacist_requests')
    
    if request.method == 'POST':
        try:
            # Log approval action
            print(f"APPROVE REQUEST DEBUG: User {request.user.username} approving request #{prescription_request.id}")
            
            # Cập nhật trạng thái yêu cầu thành "approved"
            prescription_request.status = 'approved'
            prescription_request.pharmacist = request.user
            prescription_request.save()
            
            print(f"APPROVE REQUEST DEBUG: Request #{prescription_request.id} marked as approved")
            
            # Redirect đến trang tạo đơn thuốc mới với thông tin từ yêu cầu
            return redirect(f"{reverse('pharmacy:prescription_create')}?request_id={prescription_request.pk}")
        except Exception as e:
            print(f"APPROVE REQUEST DEBUG: Error approving request: {e}")
            messages.error(request, f'Có lỗi xảy ra khi duyệt yêu cầu: {str(e)}')
            return redirect('pharmacy:pharmacist_requests')
    
    return redirect('pharmacy:prescription_request_detail', pk=pk)

@login_required
def reject_prescription_request(request, pk):
    """Dược sĩ từ chối yêu cầu kê đơn thuốc"""
    if not (request.user.is_pharmacist or request.user.is_staff):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('home')
    
    prescription_request = get_object_or_404(PrescriptionRequest, pk=pk)
    
    if prescription_request.status != 'pending':
        messages.error(request, 'Yêu cầu này đã được xử lý trước đó.')
        return redirect('pharmacy:pharmacist_requests')
    
    if request.method == 'POST':
        try:
            rejection_reason = request.POST.get('rejection_reason', '')
            
            # Log rejection action
            print(f"REJECT REQUEST DEBUG: User {request.user.username} rejecting request #{prescription_request.id}")
            print(f"REJECT REQUEST DEBUG: Reason: {rejection_reason}")
            
            prescription_request.status = 'rejected'
            prescription_request.pharmacist = request.user
            prescription_request.rejection_reason = rejection_reason
            prescription_request.save()
            
            print(f"REJECT REQUEST DEBUG: Request #{prescription_request.id} marked as rejected")
            
            messages.success(request, 'Đã từ chối yêu cầu kê đơn thuốc.')
            return redirect('pharmacy:pharmacist_requests')
        except Exception as e:
            print(f"REJECT REQUEST DEBUG: Error rejecting request: {e}")
            messages.error(request, f'Có lỗi xảy ra khi từ chối yêu cầu: {str(e)}')
            return redirect('pharmacy:pharmacist_requests')
    
    return render(request, 'pharmacy/reject_prescription_request.html', {
        'request': prescription_request,
    })

@login_required
def delete_prescription_request(request, pk):
    """Xóa yêu cầu kê đơn thuốc"""
    prescription_request = get_object_or_404(PrescriptionRequest, pk=pk)
    
    # Kiểm tra quyền - chỉ cho phép chủ sở hữu hoặc quản trị viên xóa
    if prescription_request.patient != request.user and not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền xóa yêu cầu này.')
        return redirect('pharmacy:prescription_request_list')
    
    if request.method == 'POST':
        prescription_request.delete()
        messages.success(request, 'Đã xóa yêu cầu kê đơn thuốc.')
        return redirect('pharmacy:prescription_request_list')
    
    return render(request, 'pharmacy/delete_prescription_request.html', {
        'request': prescription_request,
    })

@login_required
def prescription_create(request):
    """Tạo đơn thuốc mới, có thể từ yêu cầu đã được duyệt"""
    if not (request.user.is_pharmacist or request.user.is_staff or request.user.is_doctor):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('pharmacy:prescription_list')
    
    # Kiểm tra nếu có request_id trong query parameter
    request_id = request.GET.get('request_id')
    prescription_request = None
    
    if request_id:
        try:
            prescription_request = PrescriptionRequest.objects.get(pk=request_id, status='approved')
        except PrescriptionRequest.DoesNotExist:
            messages.error(request, 'Không tìm thấy yêu cầu kê đơn thuốc đã được duyệt.')
            return redirect('pharmacy:prescription_create')
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            
            # Gán dược sĩ cho đơn thuốc
            prescription.pharmacist = request.user
            prescription.save()
            
            # Lưu các item trong đơn thuốc
            items = formset.save(commit=False)
            for item in items:
                item.prescription = prescription
                item.save()
            
            # Nếu đơn thuốc được tạo từ yêu cầu, cập nhật liên kết và trạng thái
            if prescription_request:
                prescription_request.prescription = prescription
                prescription_request.status = 'completed'
                prescription_request.save()
            
            messages.success(request, 'Đơn thuốc đã được tạo thành công.')
            return redirect('pharmacy:prescription_detail', pk=prescription.pk)
    else:
        initial_data = {}
        
        # Nếu có yêu cầu kê đơn thuốc, điền sẵn thông tin
        if prescription_request:
            initial_data = {
                'patient': prescription_request.patient,
                'patient_name': prescription_request.patient.get_full_name() or prescription_request.patient.username,
                'notes': f"Dựa trên yêu cầu #{prescription_request.id}. Bệnh: {prescription_request.disease}. Triệu chứng: {prescription_request.symptoms}."
            }
        
        form = PrescriptionForm(initial=initial_data)
        formset = PrescriptionItemFormSet()
    
    medicines = Medicine.objects.all()
    
    return render(request, 'pharmacy/prescription_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'prescription_request': prescription_request
    })

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # Check if user has permission to view this prescription
    if not request.user.is_staff and prescription.patient != request.user:
        messages.error(request, 'Bạn không có quyền xem đơn thuốc này.')
        return redirect('pharmacy:prescription_list')
    
    items = prescription.items.all()
    return render(request, 'pharmacy/prescription_detail.html', {
        'prescription': prescription,
        'items': items,
        'title': f'Chi tiết đơn thuốc #{prescription.id}'
    })

@login_required
def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    medicines = Medicine.objects.all()
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionItemFormSet(request.POST, instance=prescription)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Cập nhật đơn thuốc thành công.')
            return redirect('pharmacy:prescription_detail', pk=prescription.pk)
    else:
        form = PrescriptionForm(instance=prescription)
        formset = PrescriptionItemFormSet(instance=prescription)
    
    return render(request, 'pharmacy/prescription_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'title': f'Sửa đơn thuốc #{prescription.id}'
    })

@login_required
def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, 'Xóa đơn thuốc thành công.')
        return redirect('pharmacy:prescription_list')
    return redirect('pharmacy:prescription_detail', pk=pk)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/transaction_list.html', {
        'transactions': transactions,
        'title': 'Danh sách giao dịch'
    })

@login_required
def transaction_create(request):
    medicines = Medicine.objects.all()
    TransactionItemFormSet = get_transaction_item_formset()
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        formset = TransactionItemFormSet(request.POST, prefix='items')
        
        try:
            if form.is_valid() and formset.is_valid():
                transaction = form.save(commit=False)
                transaction.created_by = request.user
                transaction.save()
                
                formset.instance = transaction
                formset.save()
                
                # Cập nhật trạng thái đơn thuốc thành 'completed' nếu là giao dịch bán hàng
                if transaction.transaction_type == 'sale' and transaction.prescription:
                    transaction.prescription.status = 'completed'
                    transaction.prescription.save()
                
                messages.success(request, 'Tạo giao dịch thành công.')
                return redirect('pharmacy:transaction_detail', pk=transaction.pk)
            else:
                print("Form errors:", form.errors)
                print("Formset errors:", formset.errors)
                for form in formset:
                    print("Item form errors:", form.errors)
                messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
        except Exception as e:
            print("Exception:", str(e))
            messages.error(request, f'Lỗi: {str(e)}')
    else:
        form = TransactionForm()
        formset = TransactionItemFormSet(prefix='items')
    
    return render(request, 'pharmacy/transaction_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'title': 'Tạo giao dịch mới'
    })

@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    items = transaction.items.all()
    return render(request, 'pharmacy/transaction_detail.html', {
        'transaction': transaction,
        'items': items,
        'title': f'Chi tiết giao dịch #{transaction.id}'
    })

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    medicines = Medicine.objects.all()
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        formset = TransactionItemFormSet(request.POST, instance=transaction)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Cập nhật giao dịch thành công.')
            return redirect('pharmacy:transaction_detail', pk=transaction.pk)
    else:
        form = TransactionForm(instance=transaction)
        formset = TransactionItemFormSet(instance=transaction)
    
    return render(request, 'pharmacy/transaction_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'title': f'Sửa giao dịch #{transaction.id}'
    })

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Xóa giao dịch thành công.')
        return redirect('pharmacy:transaction_list')
    return redirect('pharmacy:transaction_detail', pk=pk)

@login_required
def prescription_items_api(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    items = []
    for item in prescription.items.all():
        items.append({
            'medicine': item.medicine.id,
            'quantity': item.quantity,
            'unit': item.unit,
            'medicine_price': float(item.medicine.price)
        })
    return JsonResponse(items, safe=False)

@login_required
def prescription_request_help(request):
    """Hiển thị trang hướng dẫn sử dụng tính năng yêu cầu kê đơn thuốc"""
    return render(request, 'pharmacy/prescription_request_help.html')
