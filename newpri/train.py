import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle

# Load your sensitivity data from CSV or Excel
sensitivity_data = pd.read_excel('sensitivity.xlsx')

# Assuming 'Crime Name', 'FIR Summary', and 'Severity' are columns in your CSV
X = sensitivity_data[['Crime Name', 'FIR Summary']]
y = sensitivity_data['Severity']

# Split data into training and validation sets
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

# TF-IDF vectorization
tfidf_vectorizer = TfidfVectorizer(max_features=1000)  # You can adjust max_features as needed
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train['Crime Name'] + ' ' + X_train['FIR Summary'])
X_valid_tfidf = tfidf_vectorizer.transform(X_valid['Crime Name'] + ' ' + X_valid['FIR Summary'])

# Initialize Gradient Boosting Classifier
gb_model = GradientBoostingClassifier()

# Fit the model
gb_model.fit(X_train_tfidf, y_train)

# Make predictions on validation set
y_pred = gb_model.predict(X_valid_tfidf)

# Evaluate model performance
print("Accuracy:", accuracy_score(y_valid, y_pred))
print(classification_report(y_valid, y_pred))

# Save the model to a file using pickle
with open('sensitivity_gb_model.pkl', 'wb') as f:
    pickle.dump(gb_model, f)

# Save the TF-IDF vectorizer as well (optional)
with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf_vectorizer, f)
    