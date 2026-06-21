# 🚦 Gridlock 2.0: Unified Parking Intelligence Engine

**[🔴 LIVE DASHBOARD: Click Here to Launch Gridlock 2.0](https://gridlock-btp.streamlit.app)**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gridlock-btp.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Predictive Hardware Auditing & AI-Driven Spatial Hotspot Discovery for Urban Traffic Enforcement.**

Gridlock 2.0 is a prototype developed for **Theme 1: Poor Visibility on Parking-Induced Congestion**. It replaces legacy, reactive traffic dashboards with a proactive Machine Learning pipeline that discovers hidden violation hotspots and autonomously audits municipal hardware reliability.

---

## 📑 Table of Contents
- [The Problem](#-the-problem)
- [Key Features](#-key-features)
- [Architecture & Methodology](#-architecture--methodology)
- [Tech Stack](#-tech-stack)
- [Installation & Local Setup](#-installation--local-setup)
- [Project Structure](#-project-structure)

---

## 📌 The Problem
Traditional urban traffic enforcement is **patrol-based and reactive**. Current Business Intelligence (BI) dashboards only plot violation volumes at predefined, "named" junctions. 
* **The Spatial Blindspot:** In our dataset, nearly **47% of confirmed violations** occur outside these named zones (logged simply as "No Junction"), making the city's worst congestion clusters mathematically invisible to current tracking tools.
* **The Hardware Drain:** Miscalibrated enforcement cameras generate massive volumes of false-positive flags, wasting thousands of hours of human-reviewer time. 

---

## 🚀 Key Features

### 🗺️ 1. Unified Hotspot Command Center
* **Hidden Cluster Discovery:** Autonomously mines orphaned GPS coordinates to discover and map undocumented illegal parking hotspots.
* **The Temporal Vacuum:** High-resolution density heatmaps proving that enforcement drops to near-zero by 2:00 PM IST, leaving the evening commute entirely unmonitored.
* **Actionable Directives Engine:** Translates raw tabular data into localized police deployment commands (e.g., specific vehicle targeting, optimal peak-hour deployment windows).

### 🛠️ 2. Camera Reliability Audit
* **Automated Triage Layer:** A target-encoded Machine Learning classifier that evaluates historical reviewer patterns to identify broken or miscalibrated hardware.
* **Hardware Registry:** Generates a ranked operational directive detailing exactly which cameras require physical recalibration (e.g., `FKDEV02236` at an 86.9% failure rate).

---

## 🧠 Architecture & Methodology

### 1. Spatial Discovery (DBSCAN)
We deployed an unsupervised **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** algorithm over 54,493 orphaned coordinates.
* **Parameters:** `eps = 0.00045` (Euclidean mapping to roughly ~50m radius bounding boxes), `min_samples = 20`.
* **Result:** Successfully extracted 273 stable, dense undocumented hotspots, seamlessly merging them into a unified tracking hierarchy alongside known junctions.

### 2. The Pressure Index
Because external traffic-speed telemetry was outside the dataset scope, we engineered a deterministic, normalized **Parking Pressure Index ($P$)** to act as a proxy for physical congestion friction:

$$P = W_v\left(\frac{V}{V_{max}}\right) + W_d\left(\frac{D}{D_{max}}\right) + W_c\left(\frac{C}{C_{max}}\right)$$

*(Where V = Violation Volume, D = Active Days, C = Unique Devices).*
**Robustness:** A mathematical sensitivity check across three extreme weighting schemes verified that 90% of the Top 10 worst zones remain entirely stable.

### 3. Hardware Audit Model (Random Forest)
* **Model:** `RandomForestClassifier(n_estimators=150, max_depth=18, class_weight='balanced')`
* **Leakage-Safe Target Encoding:** The primary feature (`device_hist_approve_rate`) is computed **strictly on the training split** to prevent data leakage into the test set.
* **The Honest Ceiling (AUC 0.795):** The model operates against a strict **69.87% majority-class baseline**. We explicitly treat ~0.80 AUC as our operational ceiling; full automation requires ground-truth photo evidence (absent from this dataset). This pipeline acts as a triage layer, not a human replacement.

---

## 💻 Tech Stack
* **Core:** Python 3.9+
* **Data Engineering:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn
* **Geospatial & Visualization:** Folium, Plotly Express, Streamlit-Folium
* **Deployment:** Streamlit Community Cloud

---

## ⚙️ Installation & Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/gridlock-2.0.git
cd gridlock-2.0
```

**2. Create a virtual environment**
```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```
**macOS / Linux**
```bash
source venv/bin/activate
```
**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Data Provisioning**

Ensure the pre-processed dataset (`theme1_clean_final.csv`) is located in the `data/` directory.

**5. Launch the application**

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

## 📂 Project Structure

```plaintext
gridlock-2.0/
├── data/
│   └── theme1_clean_final.csv      # Trimmed, cleaned dataset (18.6 MB)
├── app.py                          # Main Streamlit application & ML pipeline
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```