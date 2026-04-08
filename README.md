# Low-Level-Traffic-IDS
An anomaly-based Intrusion Detection System (IDS) using signal processing and machine learning to detect malicious network behavior in the CICIDS2017 dataset.

## Project Overview
Modern organizations generate immense volumes of low-level network traffic data that traditional signature-based detection systems often struggle to process, especially when faced with novel "zero-day" vulnerabilities. This project treats network traffic not merely as discrete packets, but as a continuous digital signal comprising variables such as packet size, flow duration, and arrival timing. 

By applying Signal Processing for Statistics and Data Science (SPSDS) principles, we aim to distinguish the "noise" of cyber attacks from the baseline of normal operations.

## Research Question
Can low-level network traffic signals be used to detect malicious behaviour effectively, and does Random Forest outperform Logistic Regression in distinguishing malicious traffic from normal network activity?

## Hypothesis
A Random Forest classifier trained on low-level network traffic features will detect malicious behaviour more effectively than Logistic Regression, specifically regarding the F1-score and False Positive Rate. This performance is expected to improve if signal-processing features, such as Fourier-based representations of packet timing, are integrated.

## Methodology & Technologies
This project follows a structured data science lifecycle:
1.  **Data Acquisition**: Utilizing the CICIDS2017 dataset for its modern attack diversity.
2.  **Signal Processing**: Applying Fast Fourier Transforms (FFT) to extract frequency-domain features from packet arrival times.
3.  **Modeling**: Implementing and comparing Logistic Regression (baseline) and Random Forest (main model).
4.  **Evaluation**: Measuring success through a robust suite of metrics to minimize "alert fatigue".

### Technical Stack
* **Language**: Python
* **Libraries**: `scikit-learn` for machine learning, `scipy` for signal processing, and `pandas` for data manipulation.

## Evaluation Metrics
To ensure a practical balance between speed and accuracy, we evaluate the models using:
* **Precision**: $\text{Pr} = \frac{TP}{TP+FP}$
* **Recall**: $\text{Rc} = \frac{TP}{TP+FN}$
* **F1-Score**: $F1 = 2 \cdot \frac{Pr \cdot Rc}{Pr + Rc}$
* **False Positive Rate (FPR)**: Critical for reducing administrative overhead.

## Project Structure
This repository is organized to separate data, code, and documentation cleanly. As the project evolves, we plan to implement the following structure:

```text
├── docs/               # Project proposals and future reports.
├── references/         # Academic papers and cited literature.
├── data/               # Instructions for downloading CICIDS2017 (raw data is not tracked).
│   └── README.md       # Download links and dataset details.
├── notebooks/          # (Planned) Jupyter Notebooks for Exploratory Data Analysis (EDA).
├── src/                # (Planned) Python scripts for the models and FFT logic.
├── results/            # (Planned) Confusion matrices, F1-score plots, and signal graphs.
├── .gitignore          # Rules to ignore large data files and __pycache__.
├── LICENSE             # (Planned) Open source license (e.g., MIT/GPL).
└── README.md           # The main landing page (this file).
```

## References
* Buczak, A.L. and Guven, E. (2016). A Survey of Data Mining and Machine Learning Methods for Cyber Security Intrusion Detection. *IEEE Communications Surveys & Tutorials*.
* Farnaaz, N. and Jabbar, M.A. (2016). Random Forest Modeling for Network Intrusion Detection System. *Procedia Computer Science*.
* Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*.
* Sharafaldin, I. et al. (2018). Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. *ICISSP*.
