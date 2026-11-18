

## Data Quality Investigation

- 533 literal placeholder records containing "empty".
- 16 missing email text values.
- 19 blank/whitespace email values (initial check).
- One conflicting group was caused by placeholder text.
- One extremely large malformed record contained notebook metadata.
- Exact duplicate email content requires further validation.

## Cleaning Strategy
- Preserve the original dataset.
- Exclude records without usable email content.
- Investigate genuine label conflicts.
- Deduplicate before train/test splitting.
- Document all excluded records and reasons.

## Final Cleaning Results

Original records: 18,650
Clean records: 17,520

Removed:
- Missing values: 16
- Blank/placeholders: 536
- Malformed record: 1
- Duplicate occurrences: 577

Final classes:
- Safe Email: 10,977
- Phishing Email: 6,543

Remaining duplicates: 0
Remaining missing values: 0

Original dataset preserved.
Cleaned dataset saved separately.