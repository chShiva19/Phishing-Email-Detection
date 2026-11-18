
import pandas as pd

df = pd.read_csv("dataset/processed/cleaned_emails.csv")

print("--- FINAL DATASET VALIDATION ---")

print("Dataset shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate emails:")
print(df["email_text"].duplicated().sum())

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nClass percentages:")
print(df["label"].value_counts(normalize=True) * 100)

print("\nSample safe email:")
print(
    df.loc[df["label"] == "Safe Email", "email_text"].iloc[0][:500]
)

print("\nSample phishing email:")
print(
    df.loc[df["label"] == "Phishing Email", "email_text"].iloc[0][:500]
)
