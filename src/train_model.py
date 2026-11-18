import joblib
import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

# 1. Load cleaned dataset
df = pd.read_csv("dataset/processed/cleaned_emails.csv")

X = df["email_text"]
y = df["label"]

# 2. Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# 3. Define ML models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Naive Bayes": MultinomialNB(),
    "Linear SVM": LinearSVC()
}

results = {}

# 4. Train and evaluate each model
for name, classifier in models.items():

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=50000,
            ngram_range=(1, 2),
            min_df=2
        )),
        ("model", classifier)
    ])

    print(f"\nTraining {name}...")

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    phishing_f1 = f1_score(
        y_test,
        predictions,
        pos_label="Phishing Email"
    )

    results[name] = {
        "pipeline": pipeline,
        "accuracy": accuracy,
        "phishing_f1": phishing_f1
    }

    print("\nAccuracy:", round(accuracy * 100, 2), "%")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    print("Confusion Matrix:")
    print(confusion_matrix(
        y_test,
        predictions,
        labels=["Safe Email", "Phishing Email"]
    ))

# 5. Compare models
print("\n--- MODEL COMPARISON ---")

for name, result in results.items():
    print(
        name,
        "| Accuracy:", round(result["accuracy"] * 100, 2), "%",
        "| Phishing F1:", round(result["phishing_f1"], 4)
    )

# 6. Select best model based on phishing F1-score
best_name = max(
    results,
    key=lambda name: results[name]["phishing_f1"]
)

best_model = results[best_name]["pipeline"]

print("\nBest model:", best_name)
# Save the best trained model
os.makedirs("models", exist_ok=True)

joblib.dump(best_model, "models/best_model.pkl")

print("Best model saved successfully!")