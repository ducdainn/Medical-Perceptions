from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Symptom, Disease, Diagnosis
from .forms import DiagnosisForm, SymptomForm, DiseaseForm
from accounts.decorators import patient_view_only, doctor_required, admin_required, admin_or_web_manager_required
import pickle
import os
import numpy as np
import pandas as pd
from django.conf import settings

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
    # Check if user has permission to view this diagnosis
    if not request.user.is_staff and diagnosis.patient != request.user:
        messages.error(request, 'Bạn không có quyền xem chẩn đoán này.')
        return redirect('diagnosis:list')
        
    context = {
        'diagnosis': diagnosis
    }
    return render(request, 'diagnosis/diagnosis_detail.html', context)

@doctor_required
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

@patient_view_only
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

@patient_view_only
def disease_list(request):
    form = DiseaseForm()
    
    if request.method == 'POST':
        if not (request.user.is_staff or request.user.is_web_manager):
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

@admin_or_web_manager_required
def symptom_create(request):
    if not (request.user.is_staff or request.user.is_web_manager):
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

@admin_or_web_manager_required
def symptom_edit(request, pk):
    if not (request.user.is_staff or request.user.is_web_manager):
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

@admin_or_web_manager_required
def disease_create(request):
    if not (request.user.is_staff or request.user.is_web_manager):
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

@admin_or_web_manager_required
def disease_edit(request, pk):
    if not (request.user.is_staff or request.user.is_web_manager):
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

@login_required
def recommend_drug(request):
    symptoms = Symptom.objects.all()
    
    if request.method == 'POST':
        # Get selected symptoms
        selected_symptom_ids = request.POST.getlist('symptoms')
        
        if not selected_symptom_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một triệu chứng.')
            return render(request, 'diagnosis/recommend_drug.html', {'symptoms': symptoms})
        
        selected_symptoms = Symptom.objects.filter(id__in=selected_symptom_ids)
        
        # Get patient age, gender and severity
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        severity = request.POST.get('severity', '')
        
        # Validation
        if not age or not gender or not severity:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin tuổi, giới tính và mức độ.')
            return render(request, 'diagnosis/recommend_drug.html', {
                'symptoms': symptoms,
                'selected_symptoms': selected_symptoms,
                'age': age,
                'gender': gender,
                'severity': severity
            })
        
        try:
            age = int(age)
            if age <= 0 or age > 120:
                raise ValueError("Tuổi không hợp lệ")
        except ValueError:
            messages.error(request, 'Tuổi phải là số nguyên dương.')
            return render(request, 'diagnosis/recommend_drug.html', {
                'symptoms': symptoms,
                'selected_symptoms': selected_symptoms,
                'age': age,
                'gender': gender,
                'severity': severity
            })
        
        # Define symptom relationships with diseases using a multilabel approach
        # Each symptom has a primary disease association with a weight 
        # and may have secondary disease associations with lower weights
        symptom_disease_matrix = {
            # Symptom pattern matchers : {disease: weight}
            # Tiêu chảy symptoms
            'tiêu chảy': {'diarrhea': 0.9},
            'đau bụng': {'diarrhea': 0.7, 'gastritis': 0.5},
            'buồn nôn': {'diarrhea': 0.6, 'gastritis': 0.6, 'migraine': 0.3},
            'nôn': {'diarrhea': 0.8, 'gastritis': 0.4},
            'mất nước': {'diarrhea': 0.8},
            'khó chịu': {'diarrhea': 0.3, 'flu': 0.3, 'migraine': 0.3},
            'đi ngoài': {'diarrhea': 0.9},
            'phân lỏng': {'diarrhea': 0.9},
            
            # Viêm dạ dày symptoms
            'dạ dày': {'gastritis': 0.9},
            'ợ chua': {'gastritis': 0.8},
            'ợ nóng': {'gastritis': 0.8},
            'khó tiêu': {'gastritis': 0.7},
            'đầy hơi': {'gastritis': 0.7},
            'đau bụng trên': {'gastritis': 0.8},
            'chán ăn': {'gastritis': 0.6, 'flu': 0.4},
            
            # Viêm khớp symptoms
            'khớp': {'arthritis': 0.9},
            'đau khớp': {'arthritis': 0.9},
            'sưng khớp': {'arthritis': 0.9},
            'cứng khớp': {'arthritis': 0.9},
            'khó vận động': {'arthritis': 0.7},
            'đỏ khớp': {'arthritis': 0.8},
            'nóng khớp': {'arthritis': 0.8},
            'viêm khớp': {'arthritis': 0.9},
            
            # Đau nửa đầu symptoms
            'đau đầu': {'migraine': 0.8, 'flu': 0.5, 'hypertension': 0.4},
            'nhức đầu': {'migraine': 0.8, 'flu': 0.5, 'hypertension': 0.4},
            'chóng mặt': {'migraine': 0.7, 'hypertension': 0.6},
            'nhạy cảm ánh sáng': {'migraine': 0.9},
            'nhạy cảm âm thanh': {'migraine': 0.9},
            'mờ mắt': {'migraine': 0.7, 'hypertension': 0.3},
            'đau vùng mặt': {'migraine': 0.8},
            'đau nửa mặt': {'migraine': 0.9},
            'đau phía trước đầu': {'migraine': 0.8},
            'đau trán': {'migraine': 0.7, 'flu': 0.4},
            
            # Tăng huyết áp symptoms
            'huyết áp cao': {'hypertension': 0.9},
            'huyết áp': {'hypertension': 0.9},
            'mệt mỏi': {'hypertension': 0.4, 'flu': 0.6, 'anxiety': 0.5},
            'khó thở': {'hypertension': 0.7, 'anxiety': 0.5},
            'đau ngực': {'hypertension': 0.7},
            'tim đập mạnh': {'hypertension': 0.7, 'anxiety': 0.6},
            
            # Lo âu/anxiety symptoms
            'lo âu': {'anxiety': 0.9},
            'lo lắng': {'anxiety': 0.9},
            'căng thẳng': {'anxiety': 0.8},
            'khó ngủ': {'anxiety': 0.7},
            'mất ngủ': {'anxiety': 0.7},
            'hồi hộp': {'anxiety': 0.8},
            'tim đập nhanh': {'anxiety': 0.8},
            'khó tập trung': {'anxiety': 0.7},
            'stress': {'anxiety': 0.8},
            'suy nghĩ nhiều': {'anxiety': 0.7},
            'buồn': {'anxiety': 0.6},
            'sợ hãi': {'anxiety': 0.8},
            
            # Cảm cúm symptoms
            'sốt': {'flu': 0.9},
            'ho': {'flu': 0.8},
            'đau họng': {'flu': 0.8},
            'đau nhức cơ thể': {'flu': 0.7, 'arthritis': 0.3},
            'nghẹt mũi': {'flu': 0.8},
            'sổ mũi': {'flu': 0.8},
            'ớn lạnh': {'flu': 0.8},
            'dị ứng': {'flu': 0.7},
            'ngứa': {'flu': 0.6},
            'nổi mề đay': {'flu': 0.7},
            'mẩn đỏ': {'flu': 0.7},
            'nổi ban': {'flu': 0.7},
            'phát ban': {'flu': 0.7},
            'viêm mũi': {'flu': 0.8},
            'hắt hơi': {'flu': 0.7}
        }
        
        # Calculate disease scores based on selected symptoms
        disease_scores = {
            'diarrhea': 0,
            'gastritis': 0,
            'arthritis': 0,
            'migraine': 0,
            'hypertension': 0,
            'anxiety': 0,
            'flu': 0
        }
        
        # Extract the symptom names in lowercase for easier matching
        selected_symptom_names = [symptom.name.lower() for symptom in selected_symptoms]
        
        # Calculate scores based on partial matches of symptom names against patterns
        matches_found = False
        print("DEBUG - Selected symptoms:", selected_symptom_names)
        
        for symptom_name in selected_symptom_names:
            found_match = False
            print(f"DEBUG - Checking symptom: '{symptom_name}'")
            
            # First, try exact symptom name matches
            for pattern, disease_weights in symptom_disease_matrix.items():
                if pattern == symptom_name or pattern in symptom_name:
                    found_match = True
                    matches_found = True
                    # Add weights for matching diseases
                    for disease, weight in disease_weights.items():
                        disease_scores[disease] += weight
                        print(f"Matched '{pattern}' in '{symptom_name}', adding {weight} to {disease}")
            
            # If no match was found, try partial matching for each word in the symptom
            if not found_match:
                symptom_words = symptom_name.split()
                for word in symptom_words:
                    if len(word) < 3:  # Skip very short words
                        continue
                        
                    print(f"DEBUG - Checking word: '{word}'")
                    for pattern, disease_weights in symptom_disease_matrix.items():
                        if word == pattern or (len(word) >= 4 and word in pattern) or (len(pattern) >= 4 and pattern in word):
                            matches_found = True
                            # Add weights for matching diseases with reduced confidence
                            for disease, weight in disease_weights.items():
                                adjusted_weight = weight * 0.7  # Reduce weight for partial word matches
                                disease_scores[disease] += adjusted_weight
                                print(f"Word-matched '{word}' with '{pattern}', adding {adjusted_weight} to {disease}")
        
        # Handle cases where no matches are found - add default weights based on keywords
        if not matches_found:
            print("DEBUG - No matches found, applying default weights based on keywords")
            
            # First make sure diarrhea is never the default
            disease_scores['diarrhea'] = -0.1  # Negative score to ensure it's not selected by default
            
            # Check for general keywords and assign base scores
            for symptom_name in selected_symptom_names:
                # Handle common words that might appear in many symptoms
                common_words = ['đau', 'nhức', 'mệt', 'mỏi', 'ngứa', 'sưng', 'nóng', 'đỏ']
                
                # Map unknown symptoms to potential diseases based on general categories
                if any(term in symptom_name for term in ['đau', 'nhức']):
                    # Head pain
                    if any(term in symptom_name for term in ['đầu', 'trán', 'não', 'sọ', 'mặt']):
                        disease_scores['migraine'] += 0.6
                        print(f"Applied head pain mapping for '{symptom_name}'")
                    # Joint pain
                    elif any(term in symptom_name for term in ['khớp', 'xương', 'cơ', 'chân', 'tay']):
                        disease_scores['arthritis'] += 0.6
                        print(f"Applied joint pain mapping for '{symptom_name}'")
                    # Generic pain
                    else:
                        disease_scores['migraine'] += 0.3
                        disease_scores['arthritis'] += 0.3
                        disease_scores['flu'] += 0.2
                        print(f"Applied generic pain mapping for '{symptom_name}'")
                
                # Skin and allergy symptoms
                if any(term in symptom_name for term in ['da', 'dị ứng', 'nổi', 'ngứa', 'mẩn', 'ban']):
                    disease_scores['flu'] += 0.5
                    print(f"Applied skin/allergy mapping for '{symptom_name}'")
                
                # Fatigue and weakness
                if any(term in symptom_name for term in ['mệt', 'mỏi', 'yếu', 'kiệt sức']):
                    disease_scores['flu'] += 0.5
                    disease_scores['anxiety'] += 0.3
                    print(f"Applied fatigue mapping for '{symptom_name}'")
                
                # Psychological symptoms
                if any(term in symptom_name for term in ['lo', 'buồn', 'stress', 'căng thẳng', 'sợ']):
                    disease_scores['anxiety'] += 0.7
                    print(f"Applied psychological mapping for '{symptom_name}'")
            
            # If we still have no positive scores, default to flu as the safest option
            if all(score <= 0 for score in disease_scores.values()):
                disease_scores['flu'] = 0.3
                print("Applied flu as the default condition")
        
        # Specific disease pattern boosts
        # Flu boost: If both fever AND (cough OR sore throat) are present
        has_fever = any('sốt' in name for name in selected_symptom_names)
        has_cough = any('ho' in name for name in selected_symptom_names)
        has_sore_throat = any('đau họng' in name for name in selected_symptom_names)
        
        if has_fever and (has_cough or has_sore_throat):
            disease_scores['flu'] *= 1.5
            print("Applied flu pattern boost")
        
        # Anxiety boost: If anxiety symptoms are present with minimal physical symptoms
        has_anxiety = any(('lo âu' in name or 'lo lắng' in name or 'căng thẳng' in name) for name in selected_symptom_names)
        physical_symptoms = sum(1 for name in selected_symptom_names if any(ps in name for ps in ['đau đầu', 'đau bụng', 'sốt', 'ho', 'tiêu chảy']))
        
        if has_anxiety and physical_symptoms <= 1:
            disease_scores['anxiety'] *= 1.5
            print("Applied anxiety pattern boost")
        
        # Find disease with highest score
        if all(score == 0 for score in disease_scores.values()):
            print("WARNING: All disease scores are zero, defaulting to most likely based on symptoms")
            # Default to flu or migraine instead of diarrhea when no match is found
            # This is a fallback for symptoms that didn't match any pattern
            symptom_names_str = " ".join(selected_symptom_names).lower()
            
            if any(term in symptom_names_str for term in ['đau đầu', 'nhức đầu', 'đau']):
                matched_disease = 'migraine'
            elif any(term in symptom_names_str for term in ['dị ứng', 'mẩn', 'ngứa']):
                matched_disease = 'flu'
            elif any(term in symptom_names_str for term in ['lo', 'buồn', 'lo âu', 'stress']):
                matched_disease = 'anxiety'
            else:
                matched_disease = 'flu'  # Default to flu as a safer default than diarrhea
            
            print(f"Defaulted to {matched_disease} based on symptom text")
        else:
            matched_disease = max(disease_scores.items(), key=lambda x: x[1])[0]
        
        print("Disease scores:", disease_scores)
        print("Matched disease:", matched_disease)
        
        # Comprehensive fallback recommendations based on disease and severity
        fallback_recommendations = {
            'diarrhea': {
                'LOW': "Oral rehydration salts, Probiotics",
                'NORMAL': "Loperamide, Azithromycin",
                'HIGH': "Loperamide, Fluoroquinolone"
            },
            'gastritis': {
                'LOW': "Antacids, Sucralfate",
                'NORMAL': "PPIs, H. pylori treatment",
                'HIGH': "PPIs, H. pylori treatment"
            },
            'arthritis': {
                'LOW': "NSAIDs, Topical treatments",
                'NORMAL': "Biologicals, Corticosteroids",
                'HIGH': "Biologicals, Corticosteroids"
            },
            'migraine': {
                'LOW': "NSAIDs, Caffeine combinations",
                'NORMAL': "Triptans, Beta-blockers/Anticonvulsants",
                'HIGH': "Triptans, Beta-blockers/Anticonvulsants"
            },
            'hypertension': {
                'LOW': "Lifestyle modifications, Diuretics",
                'NORMAL': "ACE inhibitors, Calcium channel blockers",
                'HIGH': "Combined therapy, Beta-blockers"
            },
            'anxiety': {
                'LOW': "Cognitive behavioral therapy, Lifestyle modifications",
                'NORMAL': "SSRIs, Benzodiazepines",
                'HIGH': "SSRIs, Benzodiazepines, Psychotherapy"
            },
            'flu': {
                'LOW': "Rest, Fluids, Paracetamol",
                'NORMAL': "Oseltamivir, Zanamivir",
                'HIGH': "Oseltamivir, Zanamivir, Respiratory support"
            }
        }
        
        try:
            # Load the model for drug recommendation based on the identified disease
            model_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'drugTree.pkl')
            
            # Map gender (1 for male, 0 for female)
            gender_code = 1 if gender.lower() == 'male' else 0
            
            # Map disease to numerical values
            disease_mapping_nums = {'diarrhea': 0, 'gastritis': 1, 'arthritis': 2, 'migraine': 3, 'hypertension': 4, 'anxiety': 5, 'flu': 6}
            disease_code = disease_mapping_nums.get(matched_disease, 0)
            
            # Map severity to numerical values
            severity_mapping = {'LOW': 0, 'NORMAL': 1, 'HIGH': 2}
            severity_code = severity_mapping.get(severity, 1)
            
            try:
                with open(model_path, 'rb') as f:
                    drug_model = pickle.load(f)
                
                # Prepare numerical features for prediction
                numerical_features = np.array([[disease_code, age, gender_code, severity_code]])
                
                # Try to make a prediction
                recommended_drug = drug_model.predict(numerical_features)[0]
                print(f"Model prediction successful: {recommended_drug}")
                
                # Check if recommended_drug is empty or None
                if not recommended_drug:
                    recommended_drug = fallback_recommendations[matched_disease][severity]
                    print(f"Empty prediction, using fallback: {recommended_drug}")
                
            except Exception as model_error:
                print(f"Error using model: {str(model_error)}")
                # Use fallback recommendations
                recommended_drug = fallback_recommendations[matched_disease][severity]
                print(f"Using fallback recommendation: {recommended_drug}")
        
        except Exception as e:
            import traceback
            print(f"General error during drug recommendation: {str(e)}")
            print(traceback.format_exc())
            # Use fallback recommendations
            recommended_drug = fallback_recommendations[matched_disease][severity]
        
        # Map disease names to Vietnamese for display
        disease_names_vi = {
            'diarrhea': 'Tiêu chảy',
            'gastritis': 'Viêm dạ dày',
            'arthritis': 'Viêm khớp',
            'migraine': 'Đau nửa đầu',
            'hypertension': 'Tăng huyết áp',
            'anxiety': 'Rối loạn lo âu',
            'flu': 'Cảm cúm'
        }
        
        # Pass the results to the template
        return render(request, 'diagnosis/drug_recommendation_result.html', {
            'symptoms': selected_symptoms,
            'age': age,
            'gender': 'Nam' if gender.lower() == 'male' else 'Nữ',
            'severity': 'Nhẹ' if severity == 'LOW' else 'Trung bình' if severity == 'NORMAL' else 'Nặng',
            'disease': matched_disease,
            'disease_name_vi': disease_names_vi.get(matched_disease, matched_disease),
            'recommended_drug': recommended_drug
        })
    
    return render(request, 'diagnosis/recommend_drug.html', {'symptoms': symptoms})

@login_required
def save_recommendation(request):
    if request.method != 'POST':
        messages.error(request, 'Phương thức không được hỗ trợ.')
        return redirect('diagnosis:recommend_drug')
    
    # Get data from form
    symptom_ids = request.POST.get('symptoms', '').split(',')
    disease_name = request.POST.get('disease', '')
    recommended_drug = request.POST.get('recommended_drug', '')
    
    if not disease_name or not recommended_drug:
        messages.error(request, 'Dữ liệu không hợp lệ.')
        return redirect('diagnosis:recommend_drug')
    
    try:
        # Map the disease name to Vietnamese
        disease_name_vi = {
            'diarrhea': 'Tiêu chảy',
            'gastritis': 'Viêm dạ dày',
            'arthritis': 'Viêm khớp',
            'migraine': 'Đau nửa đầu',
            'hypertension': 'Tăng huyết áp',
            'anxiety': 'Rối loạn lo âu',
            'flu': 'Cảm cúm'
        }.get(disease_name, disease_name)
        
        print(f"Looking for disease with name: '{disease_name_vi}'")
        
        # First try with exact match
        disease = Disease.objects.filter(name=disease_name_vi).first()
        if disease:
            print(f"Found exact match for disease: {disease.name} (ID: {disease.id})")
        
        # If no exact match, try case-insensitive exact match
        if not disease:
            disease = Disease.objects.filter(name__iexact=disease_name_vi).first()
            if disease:
                print(f"Found case-insensitive match for disease: {disease.name} (ID: {disease.id})")
        
        # If still no match, check for partial matches
        if not disease:
            matching_diseases = Disease.objects.filter(name__icontains=disease_name_vi)
            if matching_diseases.exists():
                disease = matching_diseases.first()
                print(f"Found partial match for disease: {disease.name} (ID: {disease.id})")
                print(f"Total matching diseases: {matching_diseases.count()}")
                for i, d in enumerate(matching_diseases[:5]):  # Show up to 5 matches for debugging
                    print(f"  Match {i+1}: {d.name} (ID: {d.id})")
        
        # If no disease found at all, create a new one
        if not disease:
            print(f"No match found. Creating new disease: {disease_name_vi}")
            disease = Disease.objects.create(
                name=disease_name_vi,
                description=f"Bệnh được xác định tự động bởi hệ thống khuyến nghị thuốc.",
                severity="medium",
                treatment_guidelines=f"Thuốc được khuyến nghị: {recommended_drug}"
            )
            print(f"Created new disease with ID: {disease.id}")
        
        # Create the diagnosis
        diagnosis = Diagnosis.objects.create(
            patient=request.user,
            disease=disease,
            notes=f"Chẩn đoán tự động từ hệ thống khuyến nghị thuốc.\nThuốc được khuyến nghị: {recommended_drug}",
            confidence_score=0.85  # Placeholder confidence score
        )
        
        # Add symptoms to diagnosis
        symptoms = Symptom.objects.filter(id__in=symptom_ids)
        diagnosis.symptoms.set(symptoms)
        
        messages.success(request, 'Đã lưu khuyến nghị thuốc vào hồ sơ bệnh án.')
        return redirect('diagnosis:detail', pk=diagnosis.pk)
        
    except Exception as e:
        import traceback
        print(f"Error saving recommendation: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f'Lỗi khi lưu khuyến nghị: {str(e)}')
        return redirect('diagnosis:recommend_drug')

@login_required
def test_prescription_button(request):
    """View for testing the prescription request button"""
    return render(request, 'diagnosis/test_prescription_button.html')
