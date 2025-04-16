from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Sale, SaleItem, Payment, Shift
from .forms import SaleForm, SaleItemFormSet, PaymentForm
from pharmacy.models import Medicine, Transaction

@login_required
def pos_dashboard(request):
    # Lấy dữ liệu thông kê
    today = timezone.now().date()
    
    # Hóa đơn bán hàng mới nhất
    latest_sales = Sale.objects.all().order_by('-created_at')[:5]
    
    # Tổng doanh số bán hàng
    total_sales_amount = Sale.objects.filter(status='completed').aggregate(total=Sum('items__unit_price'))['total'] or Decimal('0')
    
    # Số lượng đơn hàng theo trạng thái
    pending_sales_count = Sale.objects.filter(status='pending').count()
    completed_sales_count = Sale.objects.filter(status='completed').count()
    
    # Số lượng giao dịch chưa xác nhận
    unconfirmed_transactions_count = Transaction.objects.filter(
        transaction_type='sale',
        sales__isnull=True
    ).count()
    
    context = {
        'title': 'Bảng điều khiển POS',
        'latest_sales': latest_sales,
        'total_sales_amount': total_sales_amount,
        'pending_sales_count': pending_sales_count,
        'completed_sales_count': completed_sales_count,
        'unconfirmed_transactions_count': unconfirmed_transactions_count,
    }
    
    return render(request, 'pos/dashboard.html', context)

@login_required
def sale_list(request):
    # Lấy tất cả hóa đơn bán hàng
    sales = Sale.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Danh sách hóa đơn bán hàng',
        'sales': sales,
    }
    
    return render(request, 'pos/sale_list.html', context)

@login_required
def transaction_list(request):
    # Lấy các giao dịch bán hàng chưa xác nhận thành hóa đơn
    transactions = Transaction.objects.filter(
        transaction_type='sale',
        sales__isnull=True
    ).order_by('-created_at')
    
    context = {
        'title': 'Danh sách giao dịch chờ xác nhận',
        'transactions': transactions,
    }
    
    return render(request, 'pos/transaction_list.html', context)

@login_required
def confirm_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    
    # Kiểm tra xem giao dịch này đã được xác nhận thành hóa đơn chưa
    if Sale.objects.filter(transaction=transaction).exists():
        messages.warning(request, 'Giao dịch này đã được xác nhận thành hóa đơn')
        return redirect('pos:transaction_list')
    
    if request.method == 'POST':
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Lưu hóa đơn với liên kết đến giao dịch
            sale = form.save(commit=False)
            sale.cashier = request.user
            sale.transaction = transaction
            sale.save()
            
            # Lưu các mặt hàng trong hóa đơn
            formset.instance = sale
            formset.save()
            
            messages.success(request, 'Xác nhận giao dịch thành hóa đơn thành công')
            return redirect('pos:sale_detail', pk=sale.pk)
    else:
        # Thiết lập giá trị mặc định cho form dựa trên thông tin từ giao dịch
        initial_data = {
            'customer_name': transaction.prescription.patient_name if transaction.prescription else 'Khách vãng lai',
            'notes': f'Xác nhận từ giao dịch #{transaction.id} - {transaction.notes}',
        }
        form = SaleForm(initial=initial_data)
        formset = SaleItemFormSet()
    
    context = {
        'title': f'Xác nhận giao dịch #{transaction.id} thành hóa đơn',
        'form': form,
        'formset': formset,
        'transaction': transaction,
    }
    
    return render(request, 'pos/confirm_transaction.html', context)

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale_items = sale.items.all()
    payments = sale.payments.all()
    
    # Tính tổng tiền đã thanh toán
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Tính số tiền còn lại cần thanh toán
    remaining_balance = sale.total_amount - total_paid
    
    # Form thanh toán
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            payment.sale = sale
            payment.save()
            
            # Cập nhật trạng thái hóa đơn nếu đã thanh toán đủ
            new_total_paid = total_paid + payment.amount
            if new_total_paid >= sale.total_amount:
                sale.status = 'completed'
                sale.save()
            
            messages.success(request, 'Thanh toán thành công')
            return redirect('pos:sale_detail', pk=sale.pk)
    else:
        # Điền sẵn số tiền còn lại
        payment_form = PaymentForm(initial={
            'amount': remaining_balance,
            'payment_method': 'cash',
        })
    
    context = {
        'title': f'Chi tiết hóa đơn #{sale.id}',
        'sale': sale,
        'sale_items': sale_items,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
        'payment_form': payment_form,
    }
    
    return render(request, 'pos/sale_detail.html', context)

@login_required
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if sale.status == 'completed':
        messages.warning(request, 'Không thể chỉnh sửa hóa đơn đã hoàn thành')
        return redirect('pos:sale_detail', pk=sale.pk)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        formset = SaleItemFormSet(request.POST, instance=sale)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            messages.success(request, 'Cập nhật hóa đơn thành công')
            return redirect('pos:sale_detail', pk=sale.pk)
    else:
        form = SaleForm(instance=sale)
        formset = SaleItemFormSet(instance=sale)
    
    context = {
        'title': f'Chỉnh sửa hóa đơn #{sale.id}',
        'form': form,
        'formset': formset,
        'sale': sale,
    }
    
    return render(request, 'pos/sale_form.html', context)

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Xóa hóa đơn thành công')
        return redirect('pos:sale_list')
    
    context = {
        'title': f'Xóa hóa đơn #{sale.id}',
        'sale': sale,
    }
    
    return render(request, 'pos/sale_confirm_delete.html', context)

@login_required
def medicine_price_api(request):
    """API để lấy giá của thuốc"""
    medicine_id = request.GET.get('medicine_id')
    try:
        medicine = Medicine.objects.get(pk=medicine_id)
        return JsonResponse({'price': str(medicine.price)})
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy thuốc'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
