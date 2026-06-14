# First Draft Notes

## Research Question

Can low-level network traffic features distinguish benign and malicious behavior in CICIDS2017-style data, and does Random Forest outperform Logistic Regression for binary intrusion detection?

## Experimental Setup

- Dataset: CICIDS2017-style CSV files placed in `data/raw/`.
- Target: Binary classification where `BENIGN` is encoded as `0` and all other attack labels are encoded as `1`.
- Models:
  - Logistic Regression as an interpretable baseline with feature scaling.
  - Random Forest as the main nonlinear model.
- Split: Stratified train/test split to preserve class proportions.
- Robustness: Column whitespace is stripped, infinity values are replaced, numeric missing values are imputed, and non-numeric feature columns are coerced or excluded.

## Evidence Generated

Running the training script creates:

- `results/tables/dataset_summary.csv`
- `results/tables/metrics_summary.csv`
- `results/figures/class_distribution.png`
- `results/figures/confusion_matrix_logistic_regression.png`
- `results/figures/confusion_matrix_random_forest.png`
- `results/figures/model_metrics_comparison.png`
- `results/tables/random_forest_top_features.csv`
- `results/figures/random_forest_top_features.png`

## Metrics to Discuss

- Accuracy: Overall proportion of correct predictions.
- Precision: How many predicted malicious flows were actually malicious.
- Recall: How many actual malicious flows were detected.
- F1-score: Balance between precision and recall.
- False positive rate: Fraction of benign flows incorrectly flagged as malicious. This is important because high false positives create alert fatigue.

## Interpretation Template

Use `metrics_summary.csv` to compare models. If Random Forest has higher F1-score and lower false positive rate than Logistic Regression, that supports the project hypothesis. If Logistic Regression performs similarly, discuss whether the numeric CICFlowMeter features are already linearly separable or whether class imbalance and feature leakage should be investigated.

Use the confusion matrices to explain concrete error types:

- False positives: Benign traffic flagged as malicious.
- False negatives: Malicious traffic missed by the IDS.

Use the Random Forest feature importance outputs to support interpretation:

- Feature importance highlights which cleaned numeric traffic features were most useful for the Random Forest model.
- High-importance features can be discussed as low-level traffic signals that separate benign and malicious flows.
- Feature importance is model-specific, so describe it as supporting evidence rather than proof of causal network behavior.

## Limitations

- Results depend on which CICIDS2017 CSV files are placed in `data/raw/`.
- Random sampling is used only when `--sample` is provided, so report the sample size.
- CICIDS2017 is a flow-level benchmark dataset and may not represent all modern production networks.
