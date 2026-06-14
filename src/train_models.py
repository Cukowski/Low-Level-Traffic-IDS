from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.data_utils import clean_cicids_dataframe, load_cicids_csvs
from src.metrics import compute_binary_metrics, plot_confusion_matrix, save_metrics_csv


RANDOM_STATE = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train Logistic Regression and Random Forest on CICIDS2017-style CSV data."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw"),
        help="CSV file or directory containing CICIDS2017-style CSV files.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Optional stratified sample size to keep runtime manageable.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Fraction of rows held out for testing.",
    )
    return parser.parse_args()


def stratified_sample(X: pd.DataFrame, y: pd.Series, sample_size: int | None) -> tuple[pd.DataFrame, pd.Series]:
    if sample_size is None or sample_size >= len(X):
        return X.reset_index(drop=True), y.reset_index(drop=True)

    if y.nunique() < 2:
        return X.reset_index(drop=True), y.reset_index(drop=True)

    if sample_size < y.nunique():
        raise ValueError("Sample size must be at least the number of target classes.")

    X_sampled, _, y_sampled, _ = train_test_split(
        X,
        y,
        train_size=sample_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    return X_sampled.reset_index(drop=True), y_sampled.reset_index(drop=True)


def plot_class_distribution(y: pd.Series, output_path: Path) -> None:
    counts = y.map({0: "BENIGN", 1: "MALICIOUS"}).value_counts().reindex(["BENIGN", "MALICIOUS"], fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 4))
    counts.plot(kind="bar", ax=ax, color=["#4c78a8", "#f58518"])
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Rows")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_model_metrics(metrics_df: pd.DataFrame, output_path: Path) -> None:
    metric_columns = ["accuracy", "precision", "recall", "f1_score", "false_positive_rate"]
    plot_df = metrics_df.set_index("model")[metric_columns]

    fig, ax = plt.subplots(figsize=(9, 5))
    plot_df.T.plot(kind="bar", ax=ax)
    ax.set_title("Model Metrics Comparison")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Model")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> int:
    args = parse_args()

    figures_dir = Path("results/figures")
    tables_dir = Path("results/tables")
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from {args.data}...")
    raw_df = load_cicids_csvs(args.data)
    X, y, dataset_summary = clean_cicids_dataframe(raw_df)
    X, y = stratified_sample(X, y, args.sample)

    sample_rows = pd.DataFrame(
        [
            {"metric": "rows_used_for_experiment", "value": len(X)},
            {"metric": "features_used_for_experiment", "value": X.shape[1]},
        ]
    )
    dataset_summary = pd.concat([dataset_summary, sample_rows], ignore_index=True)
    dataset_summary.to_csv(tables_dir / "dataset_summary.csv", index=False)
    plot_class_distribution(y, figures_dir / "class_distribution.png")

    if y.nunique() < 2:
        raise ValueError("Both BENIGN and MALICIOUS classes are required for stratified training.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "Logistic Regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }

    metrics = []
    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        metrics.append(compute_binary_metrics(model_name, y_test, predictions))

        slug = model_name.lower().replace(" ", "_")
        plot_confusion_matrix(
            y_test,
            predictions,
            f"Confusion Matrix: {model_name}",
            figures_dir / f"confusion_matrix_{slug}.png",
        )

    metrics_df = save_metrics_csv(metrics, tables_dir / "metrics_summary.csv")
    plot_model_metrics(metrics_df, figures_dir / "model_metrics_comparison.png")

    print(f"Saved metrics to {tables_dir / 'metrics_summary.csv'}")
    print(f"Saved figures to {figures_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
