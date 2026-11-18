
import joblib

# 1. Load the saved ML model
model = joblib.load("models/best_model.pkl")

# 2. Sample emails for testing
test_emails = [
    """
    Hi Team,
    Please find the meeting agenda attached.
    Our meeting is scheduled for tomorrow at 10 AM.
    Regards,
    John
    """,

    """
    Congratulations! You have won a cash prize.
    Click the link below immediately to claim your reward.
    Verify your account details to receive the money.
    """
]

# 3. Predict email categories
predictions = model.predict(test_emails)

# 4. Display results
for i, prediction in enumerate(predictions):

    print(f"\nEmail {i + 1}")
    print("Prediction:", prediction)

    if prediction == "Phishing Email":
        print("Status: Potentially suspicious email!")
    else:
        print("Status: Classified as safe by the model.")
