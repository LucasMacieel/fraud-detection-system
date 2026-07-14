# EDA Insights

1. The dataset has a high class imbalance (~3.5% fraud rate), thus, accuracy isn't a suitable metric for this context. Precision-recall AUC should be the primary metric.
2. Many features have a high missing rate.
3. The data reveal a strong temporal signal via the time-of-day component.
4. Fraudulent transactions have slightly different distributions compared to non-fraudulent ones.
5. ProductCD 'W' has the highest transaction count but the lowest fraud rate amongst the other categories.
6. The 'Discover' brand has the highest fraud rate amongst 'MasterCard', 'Visa' and 'American Express', and the credit modality has a higher fraud rate compared to debit.
7. The 'outlook.com' email domain has the highest fraud rate.
8. Mobile devices have a higher fraud rate compared to desktop devices.
9. The numerical features related to transaction counter (C) and timedelta (D) show high collinearity in some cases. For example, C1 and C11 had a perfect linear correlation (1.0).
10. The Vesta engineered numerical features (Vxx) have strong predictive signal to detect fraud, showing significant positive and negative Pearson's correlation coefficients.
11. The 'DeviceInfo' feature is the categorical feature with the highest association with fraud, along with other features such as the ID variables, 'R_emaildomain' and 'ProductCD', as indicated by their significant Chi-Square and Cramer's V values.