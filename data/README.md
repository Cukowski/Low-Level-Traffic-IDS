# Dataset Information: CICIDS2017

## Source
The data used in this project is the **CICIDS2017** dataset, provided by the Canadian Institute for Cybersecurity (CIC).

* **Kaggle Link**: [CICIDS2017 Dataset](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset)  
* **Download Link**: [CICIDS2017 Dataset](https://www.unb.ca/cic/datasets/ids-2017.html)

## Why this Dataset?
Most publicly available IDS datasets (like DARPA98 or KDD99) are outdated, lack traffic diversity, and are often heavily anonymized, which prevents them from reflecting current trends. CICIDS2017 was selected because it meets 11 critical criteria for a valid IDS dataset, including:
* **Attack Diversity**: Includes DoS, DDoS, Brute Force, XSS, SQL Injection, Infiltration, Port scan, and Botnet.
* **Traffic Variety**: Captures common protocols such as HTTP, HTTPS, FTP, and SSH.
* **Reliability**: Includes completely labeled network flows with over 80 extracted features.

## Feature Set
The dataset contains 80 network traffic features extracted via the CICFlowMeter software. Key features identified for detection include:
* **Inter-Arrival Time (IAT)**: Critical for detecting DoS attacks.
* **Initial Window Bytes**: Useful for tracing Brute Force attacks like SSH-Patator.
* **Packet Length Statistics**: Instrumental in identifying Heartbleed and Web attacks.

## Data Handling
* **Format**: The raw data is provided in `.pcap` and `.csv` formats.
* **Structure**: The data is organized by day (Monday to Friday), with specific attack scenarios occurring on different days.
* **Privacy**: Please ensure compliance with the CIC's terms of use when handling this data.
