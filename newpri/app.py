from flask import Flask, request, render_template, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Function to calculate age from date of birth
def calculate_age(birth_date):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Function to evaluate legal conditions and integrate results into input_data
def evaluate_legal_conditions(input_data):
    legal_compliance_array = []
    anonymize_fields = {}  # Dictionary to store anonymization decisions
    laws_referenced = {}  # Dictionary to store laws referenced for each field

    for data_point in input_data:
        legal_compliance = {
            'Victim_Name': False,
            'Victim_Aadhaar_number': False,
            'Victim_DOB': False,
            'Victim_Caste': False,
            'Victim_Profession': False,
            'Victim_Sex': False,
            'Accused_Name': False,
            'Accused_Aadhaar_number': False,
            'Accused_DOB': False,
            'Accused_Caste': False,
            'Accused_Profession': False,
            'Accused_Sex': False,
            'Arrest_Name': False,
            'Arrest_Aadhaar_number': False,
            'Arrest_DOB': False,
            'Arrest_Caste': False,
            'Arrest_Profession': False,
            'Arrest_Sex': False
        }

        # GDPR Article 5: Anonymize personal data
        # Indian Personal Data Protection Bill, 2019: Section 4 - Processing of sensitive personal data

        # Check age-related conditions
        if 'Victim_DOB' in data_point:
            victim_dob = datetime.strptime(data_point['Victim_DOB'], '%Y-%m-%d')
            age = calculate_age(victim_dob)
            if age < 18:
                for field in ['Victim_Name', 'Victim_Aadhaar_number', 'Victim_DOB', 'Victim_Caste', 'Victim_Profession', 'Victim_Sex']:
                    legal_compliance[field] = True
                    laws_referenced[field] = ['GDPR Article 6: Lawfulness of processing (Child data)',
                                              'Indian IT Act, 2000: Section 43A (Child data protection)']

        # Check for sensitive fields that require anonymization
        sensitive_fields = ['Victim_Aadhaar_number', 'Accused_Aadhaar_number', 'Arrest_Aadhaar_number']
        for field in sensitive_fields:
            if field in data_point:
                legal_compliance[field] = True
                laws_referenced[field] = ['GDPR Article 9: Processing of special categories of personal data',
                                          'Indian Personal Data Protection Bill, 2019: Section 3 - Sensitive personal data']

        # Check if FIR summary contains sensitive information
        if 'FIR Summary' in data_point:
            fir_summary = data_point['FIR Summary'].lower()
            sensitive_keywords = ['loud music', 'violent', 'theft', 'murder', 'sexual assault', 'kidnapping', 'domestic violence', 'fraud', 'drug trafficking', 'human trafficking']
            for keyword in sensitive_keywords:
                if keyword in fir_summary:
                    for field in ['Victim_Name', 'Accused_Name', 'Arrest_Name', 'Victim_DOB', 'Accused_DOB', 'Arrest_DOB', 'Victim_Sex', 'Accused_Sex', 'Arrest_Sex']:
                        legal_compliance[field] = True
                        laws_referenced[field] = ['GDPR Article 10: Processing of personal data relating to criminal convictions and offences',
                                                  'Indian Personal Data Protection Bill, 2019: Section 31 - Processing of personal data for legal purposes']

        if 'Victim_Sex' in data_point and data_point['Victim_Sex'] == 'Female':
            for field in ['Victim_Name', 'Victim_Aadhaar_number', 'Victim_Sex']:
                legal_compliance[field] = True
                laws_referenced[field] = ['Indian Personal Data Protection Bill, 2019: Gender protection']

        if 'Victim_Profession' in data_point and data_point['Victim_Profession'] in ['Professional A', 'Professional B']:
            legal_compliance['Victim_Profession'] = True
            laws_referenced['Victim_Profession'] = ['GDPR Article 5: Anonymize personal data']

        # Append legal compliance dictionary for current data point
        legal_compliance_array.append(legal_compliance)

        # Integrate legal compliance results into original input_data
        data_point['Legal_Compliance'] = legal_compliance

        # Update anonymize_fields dictionary based on current data point
        for key, value in legal_compliance.items():
            if key in anonymize_fields:
                anonymize_fields[key] = anonymize_fields[key] or value
            else:
                anonymize_fields[key] = value

    return input_data, anonymize_fields, laws_referenced

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    # Get the form data from the POST request
    form_data = request.form.to_dict()

    # Process the form data
    processed_data, anonymize_fields, laws_referenced = evaluate_legal_conditions([form_data])

    # Render preview template and pass processed data to it
    return render_template('preview.html', processed_data=processed_data[0], anonymize_fields=anonymize_fields, laws_referenced=laws_referenced)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Get the form data from the POST request
    form_data = request.form.to_dict()

    # Process the form data
    processed_data, anonymize_fields, laws_referenced = evaluate_legal_conditions([form_data])

    # Example: Save processed_data to a database or perform further actions
    # For demonstration, we'll just return a JSON response
    return jsonify({'message': 'Form submitted successfully!', 'processed_data': processed_data[0], 'anonymize_fields': anonymize_fields, 'laws_referenced': laws_referenced})

if __name__ == '__main__':
    app.run(debug=True)
