import os
import csv
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from diagnosis.models import Disease, Symptom

class Command(BaseCommand):
    help = 'Updates the drug recommendation dataset with new disease data for training the model'

    def handle(self, *args, **options):
        # Define drug recommendations for new diseases
        drug_recommendations = {
            'Bệnh Glaucoma': {
                'LOW': ['Timolol eye drops', 'Latanoprost'],
                'NORMAL': ['Brimonidine eye drops', 'Timolol, Dorzolamide combination'],
                'HIGH': ['Acetazolamide', 'Mannitol, Laser trabeculoplasty']
            },
            'Viêm kết mạc': {
                'LOW': ['Artificial tears', 'Cold compress'],
                'NORMAL': ['Antihistamine eye drops', 'Mast cell stabilizer eye drops'],
                'HIGH': ['Antibiotic eye drops', 'Corticosteroid eye drops']
            },
            'Hội chứng khô mắt': {
                'LOW': ['Artificial tears', 'Eyelid cleaning'],
                'NORMAL': ['Cyclosporine eye drops', 'Lifitegrast'],
                'HIGH': ['Autologous serum tears', 'Therapeutic contact lenses']
            },
            'Viêm tai giữa': {
                'LOW': ['Acetaminophen', 'Warm compress'],
                'NORMAL': ['Amoxicillin', 'Decongestants'],
                'HIGH': ['Amoxicillin-clavulanate', 'Ceftriaxone, Tympanocentesis']
            },
            'Bệnh Meniere': {
                'LOW': ['Meclizine', 'Diazepam'],
                'NORMAL': ['Prochlorperazine', 'Diuretics'],
                'HIGH': ['Gentamicin injection', 'Endolymphatic sac procedures']
            },
            'Viêm da dị ứng': {
                'LOW': ['Hydrocortisone cream', 'Calamine lotion'],
                'NORMAL': ['Triamcinolone cream', 'Oral antihistamines'],
                'HIGH': ['Prednisone', 'Cyclosporine']
            },
            'Bệnh vẩy nến': {
                'LOW': ['Moisturizers', 'Coal tar products'],
                'NORMAL': ['Calcipotriene', 'Tazarotene'],
                'HIGH': ['Methotrexate', 'Biologics (TNF inhibitors)']
            },
            'Viêm nướu': {
                'LOW': ['Chlorhexidine rinse', 'Hydrogen peroxide rinse'],
                'NORMAL': ['Doxycycline', 'Scaling and root planing'],
                'HIGH': ['Metronidazole', 'Flap surgery']
            },
            'Sâu răng': {
                'LOW': ['Fluoride treatments', 'Remineralizing agents'],
                'NORMAL': ['Dental fillings', 'Sealants'],
                'HIGH': ['Root canal therapy', 'Crowns']
            },
            'Nhiệt miệng': {
                'LOW': ['Benzocaine gel', 'Salt water rinses'],
                'NORMAL': ['Fluocinonide gel', 'Lidocaine viscous'],
                'HIGH': ['Dexamethasone elixir', 'Systemic corticosteroids']
            },
            'Viêm đường tiết niệu': {
                'LOW': ['Increased water intake', 'Cranberry supplements'],
                'NORMAL': ['Trimethoprim-sulfamethoxazole', 'Nitrofurantoin'],
                'HIGH': ['Ciprofloxacin', 'Hospitalization for IV antibiotics']
            },
            'Sỏi thận': {
                'LOW': ['Increased water intake', 'Pain relievers'],
                'NORMAL': ['Alpha blockers', 'Potassium citrate'],
                'HIGH': ['Extracorporeal shock wave lithotripsy', 'Percutaneous nephrolithotomy']
            },
            'Đái tháo đường': {
                'LOW': ['Metformin', 'Lifestyle modifications'],
                'NORMAL': ['Sulfonylureas', 'DPP-4 inhibitors'],
                'HIGH': ['Insulin therapy', 'GLP-1 receptor agonists']
            },
            'Cường giáp': {
                'LOW': ['Beta blockers', 'Lifestyle modifications'],
                'NORMAL': ['Methimazole', 'Propylthiouracil'],
                'HIGH': ['Radioactive iodine', 'Thyroidectomy']
            },
            'Suy giáp': {
                'LOW': ['Levothyroxine (low dose)', 'Monitoring'],
                'NORMAL': ['Levothyroxine (moderate dose)', 'Liothyronine'],
                'HIGH': ['Levothyroxine (high dose)', 'Close monitoring']
            },
            'Viêm gan B': {
                'LOW': ['Rest', 'Hydration'],
                'NORMAL': ['Entecavir', 'Tenofovir'],
                'HIGH': ['Interferon therapy', 'Liver transplantation']
            },
            'Xơ gan': {
                'LOW': ['Low-sodium diet', 'Vitamin supplements'],
                'NORMAL': ['Diuretics', 'Beta blockers'],
                'HIGH': ['Transjugular intrahepatic portosystemic shunt', 'Liver transplantation']
            },
            'Rối loạn lo âu': {
                'LOW': ['Lifestyle modifications', 'Relaxation techniques'],
                'NORMAL': ['SSRIs', 'Cognitive behavioral therapy'],
                'HIGH': ['Benzodiazepines', 'Intensive psychotherapy']
            },
            'Rối loạn lưỡng cực': {
                'LOW': ['Mood tracking', 'Therapy'],
                'NORMAL': ['Lithium', 'Valproate'],
                'HIGH': ['Antipsychotics', 'Electroconvulsive therapy']
            },
            'Bệnh Parkinson': {
                'LOW': ['Physical therapy', 'Occupational therapy'],
                'NORMAL': ['Levodopa-carbidopa', 'Dopamine agonists'],
                'HIGH': ['Deep brain stimulation', 'Enteral levodopa']
            },
            'Viêm phế quản': {
                'LOW': ['Increased fluids', 'Humidifier'],
                'NORMAL': ['Bronchodilators', 'Mucolytics'],
                'HIGH': ['Antibiotics', 'Inhaled corticosteroids']
            },
            'Viêm xoang': {
                'LOW': ['Saline nasal irrigation', 'Steam inhalation'],
                'NORMAL': ['Antibiotics', 'Decongestants'],
                'HIGH': ['Oral corticosteroids', 'Sinus surgery']
            },
            'Viêm phổi': {
                'LOW': ['Rest', 'Hydration'],
                'NORMAL': ['Antibiotics (outpatient)', 'Antiviral medications'],
                'HIGH': ['Intravenous antibiotics', 'Oxygen therapy, Hospitalization']
            },
            'Hen phế quản': {
                'LOW': ['Short-acting beta agonists', 'Avoiding triggers'],
                'NORMAL': ['Inhaled corticosteroids', 'Leukotriene modifiers'],
                'HIGH': ['Biologics', 'Bronchial thermoplasty']
            },
            'Viêm khớp dạng thấp': {
                'LOW': ['NSAIDs', 'Physical therapy'],
                'NORMAL': ['Methotrexate', 'Hydroxychloroquine'],
                'HIGH': ['Biologics (TNF inhibitors)', 'JAK inhibitors']
            },
            'Đau thần kinh tọa': {
                'LOW': ['NSAIDs', 'Heat/cold therapy'],
                'NORMAL': ['Muscle relaxants', 'Gabapentin'],
                'HIGH': ['Epidural steroid injections', 'Surgery']
            },
            'Viêm loét dạ dày': {
                'LOW': ['Antacids', 'Lifestyle modifications'],
                'NORMAL': ['Proton pump inhibitors', 'H2 blockers'],
                'HIGH': ['H. pylori eradication therapy', 'Surgery for complicated ulcers']
            }
        }

        # Get the path to the drug recommendation dataset
        dataset_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'Datasets', 'Drug_prescription_Dataset.csv')
        train_data_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'Datasets', 'train_data.csv')
        test_data_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'Datasets', 'test_data.csv')
        
        # Read existing data
        existing_data = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Get header
            for row in reader:
                existing_data.append(row)
        
        # Generate new data for each disease
        new_data = []
        ages = list(range(4, 90))  # Age range 4-89
        genders = ['male', 'female']
        severities = ['LOW', 'NORMAL', 'HIGH']
        
        diseases = Disease.objects.filter(name__in=drug_recommendations.keys())
        self.stdout.write(f'Found {diseases.count()} diseases to add to the dataset')
        
        for disease in diseases:
            english_name = self.translate_to_english(disease.name)
            if english_name in drug_recommendations:
                for age in random.sample(ages, min(len(ages), 10)):  # Take 10 random ages
                    for gender in genders:
                        for severity in severities:
                            drug = ', '.join(drug_recommendations[english_name][severity])
                            new_data.append([english_name.lower(), age, gender, severity, drug])
        
        self.stdout.write(f'Generated {len(new_data)} new data points')
        
        # Write combined data back to the files
        combined_data = existing_data + new_data
        
        # Shuffle the combined data
        random.shuffle(combined_data)
        
        # Save to dataset file
        with open(dataset_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(combined_data)
        
        # Split for training and testing (80/20)
        split_point = int(len(combined_data) * 0.8)
        train_data = combined_data[:split_point]
        test_data = combined_data[split_point:]
        
        # Save training data
        with open(train_data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(train_data)
        
        # Save testing data
        with open(test_data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(test_data)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated drug dataset with {len(new_data)} new entries'))
        self.stdout.write(f'Total dataset size: {len(combined_data)} entries')
        self.stdout.write(f'Training set: {len(train_data)} entries')
        self.stdout.write(f'Testing set: {len(test_data)} entries')
    
    def translate_to_english(self, vietnamese_name):
        """
        Translate Vietnamese disease names to English for matching with the drug recommendations dictionary
        """
        translations = {
            'Bệnh Glaucoma': 'Bệnh Glaucoma',
            'Viêm kết mạc': 'Viêm kết mạc',
            'Hội chứng khô mắt': 'Hội chứng khô mắt',
            'Viêm tai giữa': 'Viêm tai giữa',
            'Bệnh Meniere': 'Bệnh Meniere',
            'Viêm da dị ứng': 'Viêm da dị ứng',
            'Bệnh vẩy nến': 'Bệnh vẩy nến',
            'Viêm nướu': 'Viêm nướu',
            'Sâu răng': 'Sâu răng',
            'Nhiệt miệng': 'Nhiệt miệng',
            'Viêm đường tiết niệu': 'Viêm đường tiết niệu',
            'Sỏi thận': 'Sỏi thận',
            'Đái tháo đường': 'Đái tháo đường',
            'Cường giáp': 'Cường giáp',
            'Suy giáp': 'Suy giáp',
            'Viêm gan B': 'Viêm gan B',
            'Xơ gan': 'Xơ gan',
            'Rối loạn lo âu': 'Rối loạn lo âu',
            'Rối loạn lưỡng cực': 'Rối loạn lưỡng cực',
            'Bệnh Parkinson': 'Bệnh Parkinson',
            'Viêm phế quản': 'Viêm phế quản',
            'Viêm xoang': 'Viêm xoang',
            'Viêm phổi': 'Viêm phổi',
            'Hen phế quản': 'Hen phế quản',
            'Viêm khớp dạng thấp': 'Viêm khớp dạng thấp',
            'Đau thần kinh tọa': 'Đau thần kinh tọa',
            'Viêm loét dạ dày': 'Viêm loét dạ dày',
        }
        return translations.get(vietnamese_name, vietnamese_name) 