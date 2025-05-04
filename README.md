# AI-Powered-Climate-Risk-Assessment-for-Real-Estate

**ClimateWise Real Estate** is a Streamlit-powered interactive web application designed to empower real estate investors with insights that incorporate climate risk, property trends, and AI-driven forecasting.

---

## Dataset Sources

- [📁 Redfin + NOAA Combined Data (filled_redfin_noaa_data.csv)](https://umbc.box.com/s/y35pq35cm71zaityqkbvtruggbqmkywb)
- [📁 FEMA Disaster Data (fema_cleaned.csv)](https://umbc.box.com/s/mbdp77ulx63gown4rpo7qm4uonza17y8)
- [📁 NOAA Raw Weather Data](https://umbc.box.com/s/99g456vm684hqivbjo8f99c2lpvj9npi)
- [📁 Redfin Market Tracker](https://umbc.box.com/s/kpyu3vg9bbxsh0jx06hp0ch7qv1r4uey)

---

## Project Overview

This project integrates diverse data sources to evaluate and predict real estate value in the context of climate change.

### Key Objectives:
- Use **Redfin** housing data and **NOAA** Synthetic weather statistics for historical trends.
- Include **FEMA** disaster records to measure climate exposure and event frequency.
- Forecast property prices using machine learning techniques.
- Calculate a **custom risk score** for each city based on disaster frequency, weather volatility, and market fluctuations.
- Visualize and communicate results in an intuitive Streamlit dashboard.

---

## Features

- **Price Prediction** using historical Redfin data and growth modeling.
- **Risk Score Calculation** factoring FEMA disasters, weather standard deviations, and real estate price volatility.
- **Interactive Selection** of State and City for personalized insights.
- **Professional UI/UX** with charts, color-coded risk indicators, and forecast visualizations.
---

## How to Run the App

### 1. Clone or Download the Repository

Ensure the following data files are in your project folder:
- `filled_redfin_noaa_data.csv`
- `fema_cleaned.csv`

### 2. Install Required Python Libraries

```bash
pip install streamlit pandas numpy matplotlib plotly
````

### 3. Launch the App

```bash
streamlit run climatewise_app.py
```

Navigate to the URL in your terminal (usually `http://localhost:8501`) to view the dashboard.

---

## 📁 Main Files

| File Name                     | Description                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------- |
| `climatewise_app.py`          | Main Streamlit application with logic for data loading, UI, prediction, and risk scoring |
| `filled_redfin_noaa_data.csv` | Cleaned and combined Redfin and NOAA dataset                                             |
| `fema_cleaned.csv`            | Processed FEMA disaster declarations for risk evaluation                                 |
| `Final_Project_Soumitra_Shivangi.ipynb`         | Prototype logic notebook used for developing risk score calculations                     |

