from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Symptom, Disease, Diagnosis
from .forms import DiagnosisForm, SymptomForm, DiseaseForm

# Create your views here.

@login_required
def diagnosis_list(request):
    diagnoses = Diagnosis.objects.filter(patient=request.user) if not request.user.is_staff else Diagnosis.objects.all()
    context = {
        'diagnoses': diagnoses
    }
    return render(request, 'diagnosis/diagnosis_list.html', context)

@login_required
def diagnosis_detail(request, pk):
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    context = {
        'diagnosis': diagnosis
    }
    return render(request, 'diagnosis/diagnosis_detail.html', context)

@login_required
def diagnosis_create(request):
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.patient = request.user
            diagnosis.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Chẩn đoán đã được tạo thành công.')
            return redirect('diagnosis:detail', pk=diagnosis.pk)
    else:
        form = DiagnosisForm()
    
    context = {
        'form': form,
        'symptoms': Symptom.objects.all(),
        'diseases': Disease.objects.all()
    }
    return render(request, 'diagnosis/diagnosis_form.html', context)

@login_required
def symptom_list(request):
    form = SymptomForm()
    
    if request.method == 'POST':
        if not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
            return redirect('diagnosis:symptoms')
            
        action = request.POST.get('action', None)
        
        if action == 'delete':
            symptom_id = request.POST.get('symptom_id')
            symptom = get_object_or_404(Symptom, pk=symptom_id)
            symptom.delete()
            messages.success(request, 'Đã xóa triệu chứng thành công.')
            
        elif action == 'edit':
            symptom_id = request.POST.get('symptom_id')
            symptom = get_object_or_404(Symptom, pk=symptom_id)
            form = SymptomForm(request.POST, instance=symptom)
            if form.is_valid():
                form.save()
                messages.success(request, 'Đã cập nhật triệu chứng thành công.')
            
        else:  # Add new symptom
            form = SymptomForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Đã thêm triệu chứng mới thành công.')
                form = SymptomForm()  # Reset form after successful submission
            
        return redirect('diagnosis:symptoms')
        
    symptoms = Symptom.objects.all()
    context = {
        'symptoms': symptoms,
        'form': form
    }
    return render(request, 'diagnosis/symptom_list.html', context)

@login_required
def symptom_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('diagnosis:symptoms')
        
    if request.method == 'POST':
        form = SymptomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm triệu chứng mới thành công.')
            return redirect('diagnosis:symptoms')
    else:
        form = SymptomForm()
    
    context = {
        'form': form,
        'title': 'Thêm triệu chứng mới'
    }
    return render(request, 'diagnosis/symptom_form.html', context)

@login_required
def symptom_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('diagnosis:symptoms')
    
    symptom = get_object_or_404(Symptom, pk=pk)
    
    if request.method == 'POST':
        form = SymptomForm(request.POST, instance=symptom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật triệu chứng thành công.')
            return redirect('diagnosis:symptoms')
    else:
        form = SymptomForm(instance=symptom)
    
    context = {
        'form': form,
        'symptom': symptom,
        'title': 'Chỉnh sửa triệu chứng'
    }
    return render(request, 'diagnosis/symptom_form.html', context)

@login_required
def disease_list(request):
    form = DiseaseForm()
    
    if request.method == 'POST':
        if not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
            return redirect('diagnosis:diseases')
            
        action = request.POST.get('action', None)
        
        if action == 'delete':
            disease_id = request.POST.get('disease_id')
            try:
                disease = Disease.objects.get(pk=disease_id)
                disease.delete()
                messages.success(request, 'Đã xóa bệnh thành công.')
            except Disease.DoesNotExist:
                messages.error(request, 'Không tìm thấy bệnh để xóa.')
            
        elif action == 'edit':
            disease_id = request.POST.get('disease_id')
            try:
                disease = Disease.objects.get(pk=disease_id)
                form = DiseaseForm(request.POST, instance=disease)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Đã cập nhật bệnh thành công.')
                else:
                    error_msg = ""
                    for field, errors in form.errors.items():
                        error_msg += f"{field}: {', '.join(errors)} | "
                    messages.error(request, f'Lỗi khi cập nhật bệnh: {error_msg}')
                    context = {
                        'diseases': Disease.objects.all(),
                        'symptoms': Symptom.objects.all(),
                        'form': form
                    }
                    return render(request, 'diagnosis/disease_list.html', context)
            except Disease.DoesNotExist:
                messages.error(request, 'Không tìm thấy bệnh để cập nhật.')
            
        else:  # Add new disease
            print("==== Thêm bệnh trong disease_list ====")
            print(f"POST data: {request.POST}")
            print(f"Severity từ POST: '{request.POST.get('severity')}'")
            
            form = DiseaseForm(request.POST)
            if form.is_valid():
                try:
                    disease = form.save()
                    messages.success(request, 'Đã thêm bệnh mới thành công.')
                    form = DiseaseForm()  # Reset form after successful submission
                except Exception as e:
                    messages.error(request, f'Lỗi khi thêm bệnh: {str(e)}')
            else:
                print(f"Lỗi form: {form.errors}")
                print(f"Severity trong cleaned_data: '{form.cleaned_data.get('severity', 'không có')}'")
                error_msg = ""
                for field, errors in form.errors.items():
                    error_msg += f"{field}: {', '.join(errors)} | "
                messages.error(request, f'Lỗi dữ liệu: {error_msg}')
                context = {
                    'diseases': Disease.objects.all(),
                    'symptoms': Symptom.objects.all(),
                    'form': form
                }
                return render(request, 'diagnosis/disease_list.html', context)
            
        return redirect('diagnosis:diseases')
        
    diseases = Disease.objects.all()
    symptoms = Symptom.objects.all()
    context = {
        'diseases': diseases,
        'symptoms': symptoms,
        'form': form
    }
    return render(request, 'diagnosis/disease_list.html', context)

@login_required
def disease_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('diagnosis:diseases')
        
    if request.method == 'POST':
        print("==== Thêm bệnh trong disease_create ====")
        print(f"POST data: {request.POST}")
        print(f"Severity từ POST: '{request.POST.get('severity')}'")
        
        form = DiseaseForm(request.POST)
        if form.is_valid():
            try:
                disease = form.save()
                messages.success(request, 'Đã thêm bệnh mới thành công.')
                return redirect('diagnosis:diseases')
            except Exception as e:
                messages.error(request, f'Lỗi khi thêm bệnh: {str(e)}')
        else:
            print(f"Lỗi form: {form.errors}")
            if 'severity' in form.cleaned_data:
                print(f"Severity trong cleaned_data: '{form.cleaned_data.get('severity')}'")
            error_msg = ""
            for field, errors in form.errors.items():
                error_msg += f"{field}: {', '.join(errors)} | "
            messages.error(request, f'Lỗi dữ liệu: {error_msg}')
    else:
        form = DiseaseForm()
    
    context = {
        'form': form,
        'title': 'Thêm bệnh mới',
        'symptoms': Symptom.objects.all()
    }
    return render(request, 'diagnosis/disease_form.html', context)

@login_required
def disease_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('diagnosis:diseases')
    
    disease = get_object_or_404(Disease, pk=pk)
    
    if request.method == 'POST':
        form = DiseaseForm(request.POST, instance=disease)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật bệnh thành công.')
            return redirect('diagnosis:diseases')
    else:
        form = DiseaseForm(instance=disease)
    
    context = {
        'form': form,
        'disease': disease,
        'title': 'Chỉnh sửa bệnh'
    }
    return render(request, 'diagnosis/disease_form.html', context)
