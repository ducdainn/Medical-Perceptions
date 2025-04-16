from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Revenue, Expense, FinancialReport
from .forms import RevenueForm, ExpenseForm, FinancialReportForm

@login_required
def finance_dashboard(request):
    # Lấy dữ liệu cho biểu đồ (30 ngày gần nhất)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Tổng doanh thu và chi phí
    total_revenue = Revenue.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or 0
    net_income = total_revenue - total_expense

    # Doanh thu theo loại
    revenue_by_type = Revenue.objects.filter(date__range=[start_date, end_date]).values('revenue_type').annotate(total=Sum('amount'))

    # Chi phí theo loại
    expense_by_type = Expense.objects.filter(date__range=[start_date, end_date]).values('expense_type').annotate(total=Sum('amount'))

    # Doanh thu và chi phí gần đây
    recent_revenues = Revenue.objects.all().order_by('-date')[:5]
    recent_expenses = Expense.objects.all().order_by('-date')[:5]

    # Báo cáo tài chính gần đây
    recent_reports = FinancialReport.objects.all().order_by('-generated_at')[:5]

    context = {
        'title': 'Bảng điều khiển tài chính',
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net_income': net_income,
        'revenue_by_type': revenue_by_type,
        'expense_by_type': expense_by_type,
        'recent_revenues': recent_revenues,
        'recent_expenses': recent_expenses,
        'recent_reports': recent_reports,
    }

    return render(request, 'finance/dashboard.html', context)

# === DOANH THU ===
@login_required
def revenue_list(request):
    revenues = Revenue.objects.all().order_by('-date')

    context = {
        'title': 'Danh sách doanh thu',
        'revenues': revenues,
    }

    return render(request, 'finance/revenue_list.html', context)

@login_required
def revenue_create(request):
    if request.method == 'POST':
        form = RevenueForm(request.POST)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.recorded_by = request.user
            revenue.save()
            messages.success(request, 'Thêm doanh thu thành công')
            return redirect('finance:revenue_list')
    else:
        form = RevenueForm()

    context = {
        'title': 'Thêm doanh thu',
        'form': form,
    }

    return render(request, 'finance/revenue_form.html', context)

@login_required
def revenue_edit(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk)

    if request.method == 'POST':
        form = RevenueForm(request.POST, instance=revenue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật doanh thu thành công')
            return redirect('finance:revenue_list')
    else:
        form = RevenueForm(instance=revenue)

    context = {
        'title': 'Chỉnh sửa doanh thu',
        'form': form,
        'revenue': revenue,
    }

    return render(request, 'finance/revenue_form.html', context)

@login_required
def revenue_delete(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk)

    if request.method == 'POST':
        revenue.delete()
        messages.success(request, 'Xóa doanh thu thành công')
        return redirect('finance:revenue_list')

    context = {
        'title': 'Xóa doanh thu',
        'revenue': revenue,
    }

    return render(request, 'finance/revenue_confirm_delete.html', context)

# === CHI PHÍ ===
@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')

    context = {
        'title': 'Danh sách chi phí',
        'expenses': expenses,
    }

    return render(request, 'finance/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            messages.success(request, 'Thêm chi phí thành công')
            return redirect('finance:expense_list')
    else:
        form = ExpenseForm()

    context = {
        'title': 'Thêm chi phí',
        'form': form,
    }
    
    return render(request, 'finance/expense_form.html', context)

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật chi phí thành công')
            return redirect('finance:expense_list')
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'title': 'Chỉnh sửa chi phí',
        'form': form,
        'expense': expense,
    }

    return render(request, 'finance/expense_form.html', context)

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Xóa chi phí thành công')
        return redirect('finance:expense_list')

    context = {
        'title': 'Xóa chi phí',
        'expense': expense,
    }

    return render(request, 'finance/expense_confirm_delete.html', context)

# === BÁO CÁO TÀI CHÍNH ===
@login_required
def report_list(request):
    reports = FinancialReport.objects.all().order_by('-generated_at')

    context = {
        'title': 'Danh sách báo cáo tài chính',
        'reports': reports,
    }

    return render(request, 'finance/report_list.html', context)

@login_required
def report_create(request):
    if request.method == 'POST':
        form = FinancialReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)

            # Tính tổng doanh thu và chi phí trong khoảng thời gian
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            total_revenue = Revenue.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_expense = Expense.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            report.total_revenue = total_revenue
            report.total_expense = total_expense
            report.net_income = total_revenue - total_expense
            report.generated_by = request.user

            report.save()
            messages.success(request, 'Tạo báo cáo tài chính thành công')
            return redirect('finance:report_detail', pk=report.pk)
    else:
        form = FinancialReportForm()

    context = {
        'title': 'Tạo báo cáo tài chính',
        'form': form,
    }

    return render(request, 'finance/report_form.html', context)

@login_required
def report_detail(request, pk):
    report = get_object_or_404(FinancialReport, pk=pk)

    # Lấy doanh thu và chi phí trong khoảng thời gian của báo cáo
    revenues = Revenue.objects.filter(date__range=[report.start_date, report.end_date]).order_by('-date')
    expenses = Expense.objects.filter(date__range=[report.start_date, report.end_date]).order_by('-date')

    # Doanh thu theo loại
    revenue_by_type = Revenue.objects.filter(date__range=[report.start_date, report.end_date]).values('revenue_type').annotate(total=Sum('amount'))

    # Chi phí theo loại
    expense_by_type = Expense.objects.filter(date__range=[report.start_date, report.end_date]).values('expense_type').annotate(total=Sum('amount'))

    context = {
        'title': f'Báo cáo tài chính {report.get_report_type_display()}',
        'report': report,
        'revenues': revenues,
        'expenses': expenses,
        'revenue_by_type': revenue_by_type,
        'expense_by_type': expense_by_type,
    }

    return render(request, 'finance/report_detail.html', context)

@login_required
def report_edit(request, pk):
    report = get_object_or_404(FinancialReport, pk=pk)

    if request.method == 'POST':
        form = FinancialReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)

            # Tính lại tổng doanh thu và chi phí trong khoảng thời gian
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            total_revenue = Revenue.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_expense = Expense.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            report.total_revenue = total_revenue
            report.total_expense = total_expense
            report.net_income = total_revenue - total_expense
            report.save()
            
            messages.success(request, 'Cập nhật báo cáo tài chính thành công')
            return redirect('finance:report_detail', pk=report.pk)
    else:
        form = FinancialReportForm(instance=report)

    context = {
        'title': 'Chỉnh sửa báo cáo tài chính',
        'form': form,
        'report': report,
    }

    return render(request, 'finance/report_form.html', context)

@login_required
def report_delete(request, pk):
    report = get_object_or_404(FinancialReport, pk=pk)

    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Xóa báo cáo tài chính thành công')
        return redirect('finance:report_list')

    context = {
        'title': 'Xóa báo cáo tài chính',
        'report': report,
    }

    return render(request, 'finance/report_confirm_delete.html', context)
