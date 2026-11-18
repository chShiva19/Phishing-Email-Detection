# PhishGuard – Experimental Results

## 1. Dataset Summary

The phishing email detection system was developed using an email text classification dataset.

| Description | Count |
|---|---:|
| Original dataset records | 18,650 |
| Cleaned dataset records | 17,520 |
| Safe Emails | 10,977 |
| Phishing Emails | 6,543 |
| Training records (80%) | 14,016 |
| Testing records (20%) | 3,504 |

## 2. Model Performance Comparison

Three machine learning algorithms were evaluated using the held-out test dataset.

| Model | Accuracy | Phishing Precision | Phishing Recall | Phishing F1-score |
|---|---:|---:|---:|---:|
| Logistic Regression | 97.95% | 98% | 97% | 97.24% |
| Multinomial Naive Bayes | 97.35% | 99% | 94% | 96.36% |
| Linear SVM | **98.80%** | **98%** | **99%** | **98.40%** |

## 3. Selected Model

Linear Support Vector Machine (Linear SVM) was selected because it achieved the highest recorded test accuracy and phishing F1-score among the three evaluated models.

## 4. Confusion Matrix

The following results were obtained using the Linear SVM model.

| Actual Class | Predicted Safe | Predicted Phishing |
|---|---:|---:|
| Safe Email | 2,172 | 23 |
| Phishing Email | 19 | 1,290 |

### Interpretation

- True Safe: 2,172 safe emails correctly classified.
- False Phishing: 23 safe emails incorrectly classified as phishing.
- False Safe: 19 phishing emails incorrectly classified as safe.
- True Phishing: 1,290 phishing emails correctly classified.

## 5. Live Application Testing

The deployed Streamlit application was tested with sample emails.

- Safe email predictions were displayed.
- Phishing email predictions were displayed.
- Detection Analytics reflected the saved test detections.
- Detection History displayed the recorded email predictions and timestamps.
- CSV export option was available.
- Model Evaluation displayed the recorded model metrics and confusion matrix.

## 6. Project Limitations

- The current system classifies email text using TF-IDF and Linear SVM.
- It does not independently inspect sender identity, email headers, attachments, or URLs.
- Evaluation results are based on the available held-out test dataset.
- Real-world performance may differ on previously unseen emails.
- Cloud detection history may require external persistent storage for long-term retention.

## 7. Conclusion

The PhishGuard system demonstrates a machine learning-based approach to phishing email text classification. Among the three evaluated algorithms, Linear SVM achieved the highest recorded accuracy of 98.80% and phishing F1-score of 98.40%. The Streamlit dashboard provides email analysis, detection analytics, history management, and model evaluation features.