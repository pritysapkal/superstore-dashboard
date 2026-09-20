# Superstore Sales Dashboard

A Streamlit-powered business intelligence dashboard for analyzing a Superstore sales dataset. The application provides interactive filtering, KPI summaries, trend and category analysis, customer segmentation, automated reporting, and sales forecasting.

## Live app

Open the deployed dashboard here: https://superstore-dashboard-kyimkdiuzk58oss36mjqsw.streamlit.app/

## Overview

This project helps users explore sales performance across regions, states, cities, categories, and time periods. It is designed for quick operational analysis and executive-style reporting, with a clean dashboard interface and exportable insights.

### Included capabilities
- Interactive date range filtering
- Region, state, and city filters
- KPI cards for sales, profit, margin, and orders
- Category and regional sales visualizations
- Time-series sales trend analysis
- Sub-category and segment performance summaries
- Customer segmentation using RFM analysis
- Automated report generation
- PDF export of the generated analysis
- Predictive forecasting using Prophet

## Project structure

```text
superstore-dashboard/
├── dashboard.py              # Main Streamlit dashboard app
├── report_generator.py       # Report generation and PDF export logic
├── Superstore.csv            # Dataset used by the dashboard
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation
```

## Dataset

The dashboard uses the `Superstore.csv` file as the primary local dataset. It contains transactional sales records with fields such as:
- Order date
- Region, state, city
- Segment
- Category and sub-category
- Sales, quantity, discount, and profit

The app also attempts to load a live Google Sheets CSV first, and if unavailable, it falls back to the local CSV file.

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- Prophet
- FPDF2
- NumPy
- mlxtend

## Requirements

Python 3.9+ is recommended.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## How to run

1. Open a terminal in the project folder.
2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Launch the dashboard:

```bash
streamlit run dashboard.py
```

5. Open the local URL shown in the terminal (typically `http://localhost:8501`).

## Dashboard features

### Sales overview
The dashboard calculates and displays:
- Total sales
- Total profit
- Profit margin
- Total orders

### Visual analytics
- Category-wise sales bar chart
- Regional sales pie chart
- Time-series monthly sales trend
- Segment-wise sales chart
- Hierarchical treemap of region, category, and sub-category sales
- Scatter plot for sales vs profit

### Customer segmentation (RFM)
The app groups customers based on:
- Recency
- Frequency
- Monetary value

This segmentation helps identify high-value, at-risk, loyal, and inactive customer groups.

### Report generation
The app can generate a summary report based on the current filtered data and allow download as a PDF.

### Forecasting
The forecasting section uses Prophet to predict sales for a chosen number of future months based on historical patterns.

## Notes

- If the Google Sheet link is unavailable, the app automatically uses the bundled dataset.
- Forecasting performance depends on the amount and quality of historical data available in the selected date range.
- Some widgets may need a larger date range to produce meaningful forecasting or segmentation results.

## License

This project is intended for educational and personal analytics use. Add a license if you plan to share or distribute it publicly.

## Contributing

Contributions are welcome. You can improve the dashboard by:
- refining the visual design
- adding more business KPIs
- enhancing forecast model configuration
- building automated email or PDF report formatting
- adding deployment support for cloud hosting
