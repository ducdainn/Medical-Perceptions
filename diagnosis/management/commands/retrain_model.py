import os
import pandas as pd
import numpy as np
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Retrains the drug recommendation model with updated dataset'

    def handle(self, *args, **options):
        # Paths to dataset files and model
        train_data_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'Datasets', 'train_data.csv')
        test_data_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'Datasets', 'test_data.csv')
        model_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'drugTree.pkl')
        
        self.stdout.write(f'Loading training data from {train_data_path}')
        self.stdout.write(f'Loading testing data from {test_data_path}')
        
        # Load the data
        train_data = pd.read_csv(train_data_path)
        test_data = pd.read_csv(test_data_path)
        
        self.stdout.write(f'Training set size: {train_data.shape[0]} records')
        self.stdout.write(f'Testing set size: {test_data.shape[0]} records')
        
        # Pre-processing
        # Encoding disease, gender, and severity into numerical values
        disease_encoder = LabelEncoder()
        gender_encoder = LabelEncoder()
        severity_encoder = LabelEncoder()
        
        # Fit and transform training data
        train_data['disease_code'] = disease_encoder.fit_transform(train_data['disease'])
        train_data['gender_code'] = gender_encoder.fit_transform(train_data['gender'])
        train_data['severity_code'] = severity_encoder.fit_transform(train_data['severity'])
        
        # Transform testing data using the same encoders
        test_data['disease_code'] = disease_encoder.transform(test_data['disease'])
        test_data['gender_code'] = gender_encoder.transform(test_data['gender'])
        test_data['severity_code'] = severity_encoder.transform(test_data['severity'])
        
        # Save the encoders for use in prediction
        encoders = {
            'disease': disease_encoder,
            'gender': gender_encoder,
            'severity': severity_encoder
        }
        
        encoders_path = os.path.join(settings.BASE_DIR, 'recomend_drugbuild_model', 'encoders.pkl')
        with open(encoders_path, 'wb') as f:
            pickle.dump(encoders, f)
            
        self.stdout.write(f'Saved encoders to {encoders_path}')
        
        # Define features and target
        X_train = train_data[['disease_code', 'age', 'gender_code', 'severity_code']]
        y_train = train_data['drug']
        
        X_test = test_data[['disease_code', 'age', 'gender_code', 'severity_code']]
        y_test = test_data['drug']
        
        # Initialize and train the model
        drug_tree = DecisionTreeClassifier(criterion="entropy", max_depth=10)
        self.stdout.write('Training the model...')
        drug_tree.fit(X_train, y_train)
        
        # Evaluate the model
        accuracy = drug_tree.score(X_test, y_test)
        self.stdout.write(f'Model accuracy: {accuracy:.4f}')
        
        # Save the model
        with open(model_path, 'wb') as f:
            pickle.dump(drug_tree, f)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully trained and saved the model to {model_path}'))
        
        # Generate some test predictions
        self.stdout.write('\nSample predictions:')
        for i in range(min(5, len(test_data))):
            disease = test_data.iloc[i]['disease']
            age = test_data.iloc[i]['age']
            gender = test_data.iloc[i]['gender']
            severity = test_data.iloc[i]['severity']
            actual_drug = test_data.iloc[i]['drug']
            
            # Get features for prediction
            features = np.array([
                test_data.iloc[i]['disease_code'],
                test_data.iloc[i]['age'],
                test_data.iloc[i]['gender_code'],
                test_data.iloc[i]['severity_code']
            ]).reshape(1, -1)
            
            # Make prediction
            predicted_drug = drug_tree.predict(features)[0]
            
            # Output the results
            self.stdout.write(f'Disease: {disease}, Age: {age}, Gender: {gender}, Severity: {severity}')
            self.stdout.write(f'Actual drug: {actual_drug}')
            self.stdout.write(f'Predicted drug: {predicted_drug}')
            self.stdout.write('-' * 80) 