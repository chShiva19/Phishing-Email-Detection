
import pandas as pd
from pathlib import Path

# 1. Load original dataset
file_path = "dataset/Phishing_Email.csv"
df = pd.read_csv(file_path)

print("Original records:", len(df))

# 2. Remove records with missing email text
missing_mask = df["Email Text"].isna()
df = df.loc[~missing_mask].copy()

print("Missing records removed:", missing_mask.sum())

# 3. Remove blank and placeholder emails
df["Email Text"] = df["Email Text"].astype(str).str.strip()

placeholder_values = ["", "empty", "null", "none", "nan"]

placeholder_mask = (
    df["Email Text"].str.lower().isin(placeholder_values)
)

df = df.loc[~placeholder_mask].copy()

print("Blank/placeholder records removed:", placeholder_mask.sum())

# 4. Remove the confirmed malformed notebook record
metadata_mask = (
    df["Email Text"].str.len().gt(1_000_000)
    & df["Email Text"].str.contains(
        r"nbformat|codemirror_mode|nbconvert_exporter",
        case=False,
        regex=True,
        na=False
    )
)

df = df.loc[~metadata_mask].copy()

print("Malformed records removed:", metadata_mask.sum())

# 5. Check for genuine conflicting labels
label_counts = (
    df.groupby("Email Text")["Email Type"].nunique()
)

conflicts = label_counts[label_counts > 1]

print("Conflicting email groups:", len(conflicts))

if len(conflicts) > 0:
    raise ValueError(
        "Conflicting labels found. Investigate before deduplication."
    )

# 6. Remove exact duplicate email content
before_deduplication = len(df)

df = df.drop_duplicates(
    subset=["Email Text"],
    keep="first"
).copy()

duplicates_removed = before_deduplication - len(df)

print("Duplicate records removed:", duplicates_removed)

# 7. Remove unnecessary index column
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# 8. Rename columns
df = df.rename(columns={
    "Email Text": "email_text",
    "Email Type": "label"
})

# 9. Final validation
print("\n--- CLEAN DATASET SUMMARY ---")

print("Final records:", len(df))
print("\nClass distribution:")
print(df["label"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nRemaining duplicate emails:")
print(df["email_text"].duplicated().sum())

# 10. Save cleaned dataset
output_folder = Path("dataset/processed")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "cleaned_emails.csv"

df.to_csv(output_file, index=False)

print("\nCleaned dataset saved at:", output_file)
