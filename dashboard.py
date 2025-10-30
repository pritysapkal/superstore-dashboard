import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
from report_generator import generate_report, export_to_pdf
from prophet import Prophet
from prophet.plot import plot_plotly
import re # Import for the PDF fix

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

# Title and style adjustments
st.title(" :bar_chart: SuperStore Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# --- THIS IS THE NEW "LIVE UPDATE" SECTION ---

# This is the "Publish to web" CSV link from your Google Sheet
# IMPORTANT: PASTE YOUR GOOGLE SHEET "PUBLISH TO WEB" CSV LINK HERE
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRypHGWTsc0NnCBxIawXZ1PYO-mdU7Gmri_hfmtEl2A57AXEzqRywu474a4Q_3JGIp27yPPIXyqej9w/pub?gid=0&single=true&output=csv" 

@st.cache_data(ttl=600) # Cache for 10 minutes (600 seconds)
def load_data(url):
    """Loads data from the Google Sheet and caches it."""
    try:
        df = pd.read_csv(url)
        # Process dates right after loading
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        df.dropna(subset=["Order Date"], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame() # Return empty dataframe on error

# Load the data
with st.spinner("Loading live data from Google Sheets..."):
    df = load_data(DATA_URL)

if df.empty:
    st.error("Could not load data. Please check the Google Sheet link.")
    st.stop()

# --- END OF LIVE UPDATE SECTION ---


# Date processing and filtering
col1, col2 = st.columns((2))

startDate = df["Order Date"].min()
default_end_date = df["Order Date"].max() # This will now show 2024 if your data is updated

# --- THIS IS THE CHANGE YOU REQUESTED ---
# This sets the *calendar's* absolute maximum date to the end of 2024.
max_allowed_date = pd.to_datetime("2024-12-31") 
# --- END OF CHANGE ---

with col1:
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input(
        "End Date",
        value=default_end_date,      # The default is the latest date from your data
        max_value=max_allowed_date   # The calendar won't go past this date
    )
    
# Convert date inputs to datetime objects for comparison
date1 = pd.to_datetime(date1)
date2 = pd.to_datetime(date2)

# Ensure date1 is before date2
if date1 > date2:
    st.error("Error: Start date must be before end date.")
    st.stop()

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Sidebar filters
st.sidebar.header("Choose your filter: ")

# Region filter
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# State filter (dependent on region selection)
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# City filter (dependent on state selection)
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filtering logic
if city:
    filtered_df = df3[df3["City"].isin(city)]
elif state:
    filtered_df = df2[df2["State"].isin(state)]
elif region:
    filtered_df = df[df["Region"].isin(region)]
else:
    filtered_df = df.copy()

# --- KPI DASHBOARD ---
st.subheader("Key Performance Indicators")
total_sales = float(filtered_df["Sales"].sum())
total_profit = float(filtered_df["Profit"].sum())
# Calculate Profit Margin, ensuring not to divide by zero
if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0
total_orders = filtered_df["Order ID"].nunique()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")

with kpi2:
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}")

with kpi3:
    st.metric(label="Profit Margin", value=f"{profit_margin:.2f}%")
    
with kpi4:
    st.metric(label="Total Orders", value=f"{total_orders:,}")

st.markdown("---") # Adds a horizontal line for separation


# --- Data Visualizations ---

# Category and Region sales charts
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
sales_chart_col1, sales_chart_col2 = st.columns(2) # Renamed to avoid overwriting col1/col2

with sales_chart_col1:
    st.subheader("Category wise Sales")
    fig_cat_sales = px.bar(category_df, x="Category", y="Sales",
                           text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                           template="seaborn")
    st.plotly_chart(fig_cat_sales, use_container_width=True, height=400) # Increased height

with sales_chart_col2:
    st.subheader("Region wise Sales")
    fig_reg_sales = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig_reg_sales.update_traces(textposition="outside", textinfo='percent+label')
    st.plotly_chart(fig_reg_sales, use_container_width=True, height=400) # Increased height

# Data view expanders
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_sales.style.background_gradient(cmap="Oranges"))
        csv = region_sales.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

# Time Series Analysis
st.subheader('Time Series Analysis')
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index()
fig_time_series = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"},
                          height=500, template="gridon")
st.plotly_chart(fig_time_series, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# Segment and Category pie charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig_seg_sales = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig_seg_sales.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig_seg_sales, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig_cat_pie = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig_cat_pie.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig_cat_pie, use_container_width=True)



# Summary table and pivot table
import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    st.markdown("Sample Data")
    df_sample = df.sample(5)[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig_table = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig_table, use_container_width=True)

    st.markdown("Month wise Sub-Category Sales")
    # Check if 'month' column already exists
    if 'month' not in filtered_df.columns:
        filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_pivot = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_pivot.style.background_gradient(cmap="Blues"))

# Create a treemap based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

# Create a scatter plot
st.subheader("Relationship between Sales and Profits")
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title_text="Sales vs. Profit using Scatter Plot.",
    title_font=dict(size=20),
    xaxis=dict(title="Sales", title_font=dict(size=19)),
    yaxis=dict(title="Profit", title_font=dict(size=19))
)
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Scatter Plot Data"):
    st.write(filtered_df.sample(50)[["Sales", "Profit", "Quantity", "Category", "Discount"]].style.background_gradient(cmap="Blues"))


# --- CUSTOMER SEGMENTATION (RFM ANALYSIS) ---
st.subheader("👥 Customer Segmentation")

if not filtered_df.empty:
    try:
        # Set a snapshot date for recency calculation (e.g., the day after the last order date in the dataset)
        snapshot_date = filtered_df['Order Date'].max() + pd.Timedelta(days=1)
        
        # Calculate RFM metrics
        rfm_df = filtered_df.groupby('Customer ID').agg({
            'Order Date': lambda date: (snapshot_date - date.max()).days, # Recency
            'Order ID': 'nunique', # Frequency
            'Sales': 'sum' # Monetary
        }).rename(columns={'Order Date': 'Recency', 'Order ID': 'Frequency', 'Sales': 'MonetaryValue'})

        # Create RFM quantiles/scores
        rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], 4, labels=[4, 3, 2, 1]) # Higher score for lower recency
        rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
        rfm_df['M_Score'] = pd.qcut(rfm_df['MonetaryValue'], 4, labels=[1, 2, 3, 4])
        
        # --- More intuitive segmentation ---
        # Define segment mapping
        segment_map = {
            r'[1-2][1-2]': 'Hibernating',
            r'[1-2][3-4]': 'At-Risk',
            r'3[1-2]': 'Needs Attention',
            r'33': 'About to Sleep',
            r'[3-4]4': 'Loyal Customers',
            r'4[1-2]': 'Promising',
            r'43': 'Potential Loyalists',
            r'44': 'Champions'
        }

        rfm_df['Segment'] = rfm_df['R_Score'].astype(str) + rfm_df['F_Score'].astype(str)
        rfm_df['Segment'] = rfm_df['Segment'].replace(segment_map, regex=True)

        # --- Visualize the Segments ---
        segment_counts = rfm_df['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Customer Count']

        fig_segment = px.bar(
            segment_counts,
            x='Segment',
            y='Customer Count',
            title="Number of Customers by Segment",
            text='Customer Count',
            template="seaborn"
        )
        st.plotly_chart(fig_segment, use_container_width=True)

        with st.expander("View RFM Data and Segment Definitions"):
            st.markdown("""
            - **Champions (44):** Bought recently, buy often, and spend the most.
            - **Loyal Customers ([3-4]4):** Buy on a regular basis. Responsive to promotions.
            - **Potential Loyalists (43):** Recent customers, but spent a good amount and bought more than once.
            - **Promising (4[1-2]):** Recent shoppers, but haven't spent much.
            - **Needs Attention (3[1-2]):** Above average recency, frequency, and monetary values. May not have bought very recently though.
            - **About to Sleep (33):** Below average recency, frequency, and monetary values. Will be lost if not reactivated.
            - **At-Risk ([1-2][3-4]):** Purchased often and spent big, but it’s been a while. Need to bring them back!
            - **Hibernating ([1-2][1-2]):** Last purchase was long back, low spenders, and low number of orders.
            """)
            st.dataframe(rfm_df)
    except Exception as e:
        st.error(f"An error occurred during RFM Analysis. This can happen with very small or unique datasets. Error: {e}")
else:
    st.info("Not enough data to perform customer segmentation.")


# Automated Analysis Report section
st.subheader("📝 Automated Analysis Report")

if 'report' not in st.session_state:
    st.session_state.report = ""

if st.button("Generate Analysis Report"):
    if not filtered_df.empty:
        with st.spinner("Analyzing data and generating report..."):
            st.session_state.report = generate_report(filtered_df)
    else:
        st.warning("No data available to generate a report based on current filters.")
        st.session_state.report = ""

if st.session_state.report:
    st.markdown(st.session_state.report)
    try:
        pdf_data = export_to_pdf(st.session_state.report)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_data,
            file_name="Superstore_Analysis_Report.pdf",
            mime="application/pdf"
        )
    except ImportError as e:
        st.error(f"PDF generation failed. Please ensure 'fpdf2' is installed (`pip install fpdf2`). Error: {e}")
    except Exception as e:
        st.error(f"An error occurred during PDF generation: {e}")
else:
    st.info("Click the button above to generate an automated summary of the currently filtered data.")


# --- PREDICTIVE SALES FORECASTING ---
st.subheader("🔮 Predictive Sales Forecasting")

# User input for forecast period
forecast_period = st.slider("Select Forecast Period (Months)", 1, 12, 6, key="forecast_slider")
run_forecast_button = st.button("Run Forecast", key="run_forecast")

if run_forecast_button:
    if not linechart.empty:
        with st.spinner("Training model and generating forecast..."):
            try:
                # Prepare data for Prophet (it requires columns 'ds' and 'y')
                # Convert 'month_year' from "YYYY : Mon" string back to a proper date
                forecast_df = linechart.rename(columns={"month_year": "ds", "Sales": "y"})
                forecast_df['ds'] = pd.to_datetime(forecast_df['ds'], format="%Y : %b")

                # Initialize and train the Prophet model
                model = Prophet()
                model.fit(forecast_df)

                # Create future dataframe and make predictions
                future = model.make_future_dataframe(periods=forecast_period, freq='MS') # MS for Month Start
                forecast = model.predict(future)

                # Display the forecast plot
                st.markdown("#### Forecast Results")
                fig_forecast = plot_plotly(model, forecast)
                fig_forecast.update_layout(
                    title="Sales Forecast with Uncertainty Interval",
                    xaxis_title="Date",
                    yaxis_title="Sales Amount"
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

                # Display the raw forecast data
                with st.expander("View Forecast Data"):
                    st.write("The table below shows the predicted sales values (`yhat`) along with the lower and upper confidence bounds.")
                    st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_period))
            except Exception as e:
                st.error(f"An error occurred during forecasting: {e}")
    else:
        st.warning("Not enough data to run a forecast. Please select a broader date range or different filters.")

