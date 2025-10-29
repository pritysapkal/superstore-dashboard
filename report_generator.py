import pandas as pd
from fpdf import FPDF

def format_currency(amount):
    """Formats a number as USD currency."""
    if pd.isna(amount):
        return "$0.00"
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"

def generate_report(df):
    """
    Analyzes the filtered DataFrame and generates a dynamic, human-readable report.
    """
    if df.empty:
        return "No data to analyze."

    # --- Overall Performance ---
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    
    # --- Best and Worst Performers ---
    category_sales = df.groupby('Category')['Sales'].sum()
    best_category = category_sales.idxmax() if not category_sales.empty else "N/A"
    best_category_sales = category_sales.max() if not category_sales.empty else 0
    
    subcategory_profit = df.groupby('Sub-Category')['Profit'].sum()
    most_profitable_subcategory = subcategory_profit.idxmax() if not subcategory_profit.empty else "N/A"
    least_profitable_subcategory = subcategory_profit.idxmin() if not subcategory_profit.empty else "N/A"

    region_sales = df.groupby('Region')['Sales'].sum()
    best_region = region_sales.idxmax() if not region_sales.empty else "N/A"

    # --- Time Series Insights ---
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    monthly_sales = df.set_index('Order Date').resample('M')['Sales'].sum()
    peak_month = monthly_sales.idxmax().strftime('%B %Y') if not monthly_sales.empty else "N/A"

    # --- Building the Report String ---
    # The final "This is an automated report..." line has been removed from this template.
    report = f"""
    ### 📈 **Automated Sales & Profit Analysis Report**
    Here is a summary of the data based on your current filters.
    ---
    #### **Executive Summary:**
    * **Total Sales:** **{format_currency(total_sales)}**
    * **Total Profit:** **{format_currency(total_profit)}**
    * **Overall Profit Margin:** **{profit_margin:.2f}%**

    The analysis reveals that **{best_region}** was the top-performing region. The primary driver of sales was the **{best_category}** category, contributing **{format_currency(best_category_sales)}**.
    ---
    #### **Detailed Insights:**
    * **Top Performers:**
        * **Best Sales Category:** **{best_category}** ({format_currency(best_category_sales)}).
        * **Most Profitable Sub-Category:** **{most_profitable_subcategory}**.
    * **Areas for Improvement:**
        * **Least Profitable Sub-Category:** **{least_profitable_subcategory}**. This sub-category should be reviewed for potential cost-saving measures or pricing adjustments.
    * **Temporal Trends:**
        * The sales performance peaked in **{peak_month}**, indicating a potential seasonal high or a successful sales campaign during that period.
    """
    
    return report

class PDF(FPDF):
    """Custom PDF class to define header and footer."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Superstore Sales Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_to_pdf(report_text):
    """
    Exports the generated report text to a PDF file in memory.
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Clean up markdown characters for a cleaner PDF output
    pdf_text = report_text.replace("###", "").replace("####", "").replace("**", "").replace("*", "").replace("---", "")

    # --- CHANGE 1: REMOVE EMOJI TO PREVENT '?' ---
    # This specifically removes the emoji character so it doesn't get converted to '?'
    pdf_text = pdf_text.replace("📈", "").strip()
    
    # Process text for PDF compatibility
    pdf_text = pdf_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, pdf_text)

    # Convert the bytearray from FPDF into bytes, which st.download_button expects.
    return bytes(pdf.output(dest='S'))

