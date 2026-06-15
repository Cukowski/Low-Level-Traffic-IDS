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
    parser.add_argument(
        "--holdout-source-pattern",
        type=str,
        default=None,
        help="Optional source_file substring to use as a held-out test file.",
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


def save_random_forest_feature_importance(
    model: RandomForestClassifier,
    feature_names: pd.Index,
    table_path: Path,
    figure_path: Path,
    top_n: int = 15,
) -> pd.DataFrame:
    feature_importance = (
        pd.DataFrame(
            {
                "feature": feature_names,
                "importance": model.feature_importances_,
            }
        )
        .sort_values("importance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    feature_importance.to_csv(table_path, index=False)

    plot_data = feature_importance.sort_values("importance", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(plot_data["feature"], plot_data["importance"], color="#4c78a8")
    ax.set_title("Random Forest Top Feature Importances")
    ax.set_xlabel("Importance")
    ax.set_ylabel("Feature")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=150)
    plt.close(fig)

    return feature_importance


def build_models() -> dict[str, Pipeline | RandomForestClassifier]:
    return {
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


def train_and_evaluate_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    figures_dir: Path,
    tables_dir: Path,
    metrics_filename: str,
    comparison_figure_filename: str,
    confusion_prefix: str = "",
    save_feature_importance: bool = False,
) -> pd.DataFrame:
    if y_train.nunique() < 2:
        raise ValueError("Both BENIGN and MALICIOUS classes are required for training.")

    metrics = []
    for model_name, model in build_models().items():
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        metrics.append(compute_binary_metrics(model_name, y_test, predictions))

        slug = model_name.lower().replace(" ", "_")
        plot_confusion_matrix(
            y_test,
            predictions,
            f"Confusion Matrix: {model_name}",
            figures_dir / f"{confusion_prefix}confusion_matrix_{slug}.png",
        )

        if save_feature_importance and model_name == "Random Forest":
            save_random_forest_feature_importance(
                model,
                X_train.columns,
                tables_dir / "random_forest_top_features.csv",
                figures_dir / "random_forest_top_features.png",
            )

    metrics_df = save_metrics_csv(metrics, tables_dir / metrics_filename)
    plot_model_metrics(metrics_df, figures_dir / comparison_figure_filename)
    return metrics_df


def run_holdout_source_validation(
    raw_df: pd.DataFrame,
    holdout_pattern: str,
    sample_size: int | None,
    figures_dir: Path,
    tables_dir: Path,
) -> None:
    if "source_file" not in raw_df.columns:
        raise ValueError("Holdout validation requires a source_file column.")

    holdout_mask = raw_df["source_file"].astype(str).str.contains(
        holdout_pattern,
        case=False,
        regex=False,
        na=False,
    )
    if not holdout_mask.any():
        raise ValueError(f"No source_file values contain holdout pattern: {holdout_pattern}")
    if holdout_mask.all():
        raise ValueError("Holdout pattern matches every row, leaving no training data.")

    train_raw = raw_df.loc[~holdout_mask].copy()
    test_raw = raw_df.loc[holdout_mask].copy()
    holdout_sources = sorted(test_raw["source_file"].astype(str).unique())

    X_train, y_train, train_summary = clean_cicids_dataframe(train_raw)
    X_test, y_test, test_summary = clean_cicids_dataframe(test_raw)

    common_features = X_train.columns.intersection(X_test.columns)
    if common_features.empty:
        raise ValueError("No common numeric feature columns remain after holdout cleaning.")

    X_train = X_train.loc[:, common_features]
    X_test = X_test.loc[:, common_features]
    X_train, y_train = stratified_sample(X_train, y_train, sample_size)

    summary_rows = [
        {"metric": "holdout_source_pattern", "value": holdout_pattern},
        {"metric": "holdout_source_files", "value": "; ".join(holdout_sources)},
        {"metric": "raw_training_pool_rows", "value": len(train_raw)},
        {"metric": "raw_holdout_test_rows", "value": len(test_raw)},
        {"metric": "training_rows_used", "value": len(X_train)},
        {"metric": "holdout_test_rows_used", "value": len(X_test)},
        {"metric": "common_numeric_features_used", "value": len(common_features)},
        {"metric": "training_benign_rows", "value": int((y_train == 0).sum())},
        {"metric": "training_malicious_rows", "value": int((y_train == 1).sum())},
        {"metric": "holdout_benign_rows", "value": int((y_test == 0).sum())},
        {"metric": "holdout_malicious_rows", "value": int((y_test == 1).sum())},
    ]
    train_summary = train_summary.assign(metric="train_" + train_summary["metric"])
    test_summary = test_summary.assign(metric="test_" + test_summary["metric"])
    holdout_summary = pd.concat(
        [pd.DataFrame(summary_rows), train_summary, test_summary],
        ignore_index=True,
    )
    holdout_summary.to_csv(tables_dir / "holdout_dataset_summary.csv", index=False)

    train_and_evaluate_models(
        X_train,
        X_test,
        y_train,
        y_test,
        figures_dir,
        tables_dir,
        metrics_filename="holdout_metrics_summary.csv",
        comparison_figure_filename="holdout_model_metrics_comparison.png",
        confusion_prefix="holdout_",
        save_feature_importance=False,
    )


def main() -> int:
    args = parse_args()

    figures_dir = Path("results/figures")
    tables_dir = Path("results/tables")
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from {args.data}...")
    raw_df = load_cicids_csvs(args.data)

    if args.holdout_source_pattern:
        run_holdout_source_validation(
            raw_df,
            args.holdout_source_pattern,
            args.sample,
            figures_dir,
            tables_dir,
        )
        print(f"Saved holdout metrics to {tables_dir / 'holdout_metrics_summary.csv'}")
        print(f"Saved holdout figures to {figures_dir}")
        return 0

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

    train_and_evaluate_models(
        X_train,
        X_test,
        y_train,
        y_test,
        figures_dir,
        tables_dir,
        metrics_filename="metrics_summary.csv",
        comparison_figure_filename="model_metrics_comparison.png",
        save_feature_importance=True,
    )

    print(f"Saved metrics to {tables_dir / 'metrics_summary.csv'}")
    print(f"Saved figures to {figures_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
