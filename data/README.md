# Dataset Information: CICIDS2017

This project expects CICIDS2017-style CSV files with a label column such as `Label`.

## Where to Put Data

Place one or more CSV files manually in:

```text
data/raw/
```

The experiment script loads every `.csv` file under that directory. Raw dataset files are intentionally ignored by Git because they are large and should not be committed.

## Sources

- Official CIC page: https://www.unb.ca/cic/datasets/ids-2017.html
- Kaggle mirror: https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset

Use the CSV or machine-learning version of the dataset, not the packet capture files, unless you plan to extract features yourself.

## Label Handling

The code converts labels into a binary target:

- `BENIGN` -> `0`
- Any other label -> `1`

This supports the project question of detecting benign versus malicious network flows.
