from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Medicine, Inventory, Prescription, Transaction, PrescriptionItem, TransactionItem
from .forms import (
    MedicineForm, PrescriptionForm, TransactionForm,
    PrescriptionItemFormSet, get_transaction_item_formset
)

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

@login_required
def medicine_list(request):
    medicines = Medicine.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/medicine_list.html', {
        'medicines': medicines,
        'title': 'Danh sách thuốc'
    })

@login_required
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

@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    inventory = Inventory.objects.filter(medicine=medicine).first()
    return render(request, 'pharmacy/medicine_detail.html', {
        'medicine': medicine,
        'inventory': inventory,
        'title': f'Chi tiết thuốc: {medicine.name}'
    })

@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thuốc thành công.')
            return redirect('pharmacy:medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'title': f'Sửa thuốc: {medicine.name}'
    })

@login_required
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
    prescriptions = Prescription.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/prescription_list.html', {
        'prescriptions': prescriptions,
        'title': 'Danh sách đơn thuốc'
    })

@login_required
def prescription_create(request):
    medicines = Medicine.objects.all()
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.pharmacist = request.user
            prescription.save()
            
            formset.instance = prescription
            formset.save()
            
            messages.success(request, 'Tạo đơn thuốc thành công.')
            return redirect('pharmacy:prescription_detail', pk=prescription.pk)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()
    
    return render(request, 'pharmacy/prescription_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'title': 'Tạo đơn thuốc mới'
    })

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
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
