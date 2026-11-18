
import pandas as pd

# 1. Load the dataset
file_path = "dataset/Phishing_Email.csv"
df = pd.read_csv(file_path)

# 2. Basic information
print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATASET INFORMATION ---")
df.info()

# 3. Missing values
print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

# 4. Duplicate records
print("\n--- DUPLICATE EMAILS ---")
print(df["Email Text"].duplicated().sum())

# 5. Email class distribution
print("\n--- EMAIL TYPE DISTRIBUTION ---")
print(df["Email Type"].value_counts())

print("\n--- CLASS PERCENTAGE ---")
print(df["Email Type"].value_counts(normalize=True) * 100)

# 6. Email length analysis
df["email_length"] = df["Email Text"].fillna("").astype(str).str.len()

print("\n--- EMAIL LENGTH STATISTICS ---")
print(df["email_length"].describe())

# 7. Sample emails
print("\n--- SAMPLE EMAILS ---")
print(df[["Email Text", "Email Type"]].head(5))


# 8. Investigate empty email records

print("\n--- EMPTY EMAIL RECORDS ---")

empty_mask = df["Email Text"].fillna("").astype(str).str.strip() == ""

print("Empty records:", empty_mask.sum())

print(df.loc[empty_mask, ["Unnamed: 0", "Email Type"]].head(10))


# 9. Investigate duplicate emails

print("\n--- DUPLICATE EMAIL ANALYSIS ---")

email_text = df["Email Text"].fillna("").astype(str)

duplicate_mask = email_text.duplicated(keep=False)

print("Rows involved in duplicates:", duplicate_mask.sum())

duplicate_records = df.loc[
    duplicate_mask,
    ["Email Text", "Email Type"]
]

print(duplicate_records.head(10))


# 10. Check duplicate emails with conflicting labels

print("\n--- DUPLICATE LABEL CONFLICTS ---")

duplicate_label_counts = (
    df.assign(email_clean=email_text)
      .groupby("email_clean")["Email Type"]
      .nunique()
)

conflicting_emails = duplicate_label_counts[
    duplicate_label_counts > 1
]

print("Emails with different labels:", len(conflicting_emails))


# 11. Investigate unusually long emails

print("\n--- LONGEST EMAIL RECORDS ---")

df["email_length"] = email_text.str.len()

longest_emails = df.nlargest(5, "email_length")

for index, row in longest_emails.iterrows():
    print("\nRow:", index)
    print("Label:", row["Email Type"])
    print("Length:", row["email_length"])
    print("Content preview:", str(row["Email Text"])[:300])


# 12. Check unique labels

print("\n--- UNIQUE EMAIL LABELS ---")
print(df["Email Type"].unique())


# 13. Investigate conflicting duplicate emails

print("\n--- CONFLICTING EMAIL DETAILS ---")

valid_df = df.dropna(subset=["Email Text"]).copy()

conflict_groups = (
    valid_df.groupby("Email Text")["Email Type"]
    .nunique()
)

conflict_texts = conflict_groups[
    conflict_groups > 1
].index

for text in conflict_texts:
    records = valid_df[
        valid_df["Email Text"] == text
    ]

    print("\nEmail content preview:")
    print(text[:500])

    print("\nAssociated labels:")
    print(records[["Unnamed: 0", "Email Type"]])


# 14. Investigate literal empty values

print("\n--- PLACEHOLDER TEXT VALUES ---")

placeholder_mask = (
    valid_df["Email Text"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["empty", "null", "none", "nan"])
)

print("Placeholder records:", placeholder_mask.sum())

print(
    valid_df.loc[
        placeholder_mask,
        ["Unnamed: 0", "Email Text", "Email Type"]
    ].head(20)
)


# 15. Investigate the extremely long email

print("\n--- EXTREME EMAIL INSPECTION ---")

longest_row = df.loc[
    df["Email Text"].fillna("").astype(str).str.len().idxmax()
]

long_text = str(longest_row["Email Text"])

print("Row ID:", longest_row["Unnamed: 0"])
print("Label:", longest_row["Email Type"])
print("Length:", len(long_text))
print("First 500 characters:")
print(repr(long_text[:500]))

print("\nLast 300 characters:")
print(repr(long_text[-300:]))

print("\nNumber of newline characters:", long_text.count("\n"))


# 16. Accurate data quality investigation

print("\n--- ACCURATE DATA QUALITY CHECK ---")

# Convert email text to string safely
text = df["Email Text"].fillna("").astype(str).str.strip()

# Identify unusable email records
missing_mask = df["Email Text"].isna()
blank_mask = text.eq("") & ~missing_mask
placeholder_mask = text.str.lower().isin(
    ["empty", "null", "none", "nan"]
)

print("Missing values:", missing_mask.sum())
print("Blank email records:", blank_mask.sum())
print("Placeholder records:", placeholder_mask.sum())

# Valid email content only
valid_mask = ~(missing_mask | blank_mask | placeholder_mask)
valid_df = df.loc[valid_mask].copy()

print("\nRecords with usable email content:", len(valid_df))

# Check exact duplicate email content
valid_df["clean_text"] = (
    valid_df["Email Text"].astype(str).str.strip()
)

print("\n--- VALID EMAIL DUPLICATES ---")

print(
    "Repeated occurrences:",
    valid_df["clean_text"].duplicated().sum()
)

print(
    "Rows involved in duplicate groups:",
    valid_df["clean_text"].duplicated(keep=False).sum()
)

# Check genuine conflicting labels
label_counts = (
    valid_df.groupby("clean_text")["Email Type"].nunique()
)

real_conflicts = label_counts[label_counts > 1]

print("\n--- REAL LABEL CONFLICTS ---")
print("Conflicting email groups:", len(real_conflicts))

if len(real_conflicts) > 0:
    for email in real_conflicts.index[:5]:
        print("\nEmail preview:", email[:300])
        print(
            valid_df.loc[
                valid_df["clean_text"] == email,
                "Email Type"
            ].value_counts()
        )

# Identify unusually large emails
print("\n--- EMAIL LENGTH OUTLIERS ---")

valid_df["email_length"] = valid_df["clean_text"].str.len()

print(valid_df["email_length"].describe())

print("\nEmails above 50,000 characters:")
print(
    valid_df.loc[
        valid_df["email_length"] > 50000,
        ["Unnamed: 0", "email_length", "Email Type"]
    ].head(20)
)

# Inspect notebook metadata indicator
print("\n--- NOTEBOOK METADATA CHECK ---")

print(
    "Contains nbformat:",
    valid_df["clean_text"].str.contains(
        "nbformat", case=False, regex=False
    ).sum()
)
