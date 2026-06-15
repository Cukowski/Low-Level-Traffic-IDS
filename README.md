# Low-Level Traffic IDS

This project compares Logistic Regression and Random Forest for binary intrusion detection using CICIDS2017-style CSV data. The target is simplified to:

- `BENIGN` -> `0`
- Any other label -> `1`

The goal is to produce reproducible evidence for a university data science report: dataset summaries, metrics tables, confusion matrices, and comparison plots.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dataset

Place one or more CICIDS2017 CSV files manually in:

```text
data/raw/
```

Do not commit raw datasets. The `.gitignore` file ignores `data/raw/*` while keeping `data/raw/.gitkeep` so the folder structure remains in Git.

Expected examples:

```text
data/raw/Monday-WorkingHours.pcap_ISCX.csv
data/raw/Tuesday-WorkingHours.pcap_ISCX.csv
```

## Run the Experiment

Run the full experiment from the repository root:

```powershell
python -m src.train_models --data data/raw --sample 200000
```

The `--sample` argument is optional. It keeps runtime manageable by taking a stratified sample while preserving benign and malicious class proportions.

## Held-out File Validation

For a stricter supplementary check, use one CICIDS2017 source file as the test set and train on all other source files:

```powershell
python -m src.train_models --data data/raw --sample 200000 --holdout-source-pattern "Friday-WorkingHours-Afternoon-DDos"
```

Rows whose `source_file` contains the pattern become the held-out test set. The remaining files form the training pool. Holdout outputs are saved with `holdout_` filenames so the original random-split results are not overwritten.

## Outputs

All generated outputs are saved under `results/`:

```text
results/
  figures/
    class_distribution.png
    confusion_matrix_logistic_regression.png
    confusion_matrix_random_forest.png
    model_metrics_comparison.png
  tables/
    dataset_summary.csv
    metrics_summary.csv
```

## Method

The preprocessing code:

- strips whitespace from column names,
- detects `Label` or similar label-column names,
- removes rows with missing labels,
- converts labels to binary BENIGN vs MALICIOUS,
- replaces infinity values with missing values,
- keeps numeric features,
- imputes missing numeric values safely.

The modeling code uses a stratified train/test split. Logistic Regression is trained with feature scaling as an interpretable baseline. Random Forest is trained as the main model.

## Notebook

The notebook `notebooks/01_cicids2017_experiment.ipynb` mirrors the script workflow and is intended for exploration and report screenshots.
