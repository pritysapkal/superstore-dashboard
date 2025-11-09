import pandas as pd
import re
from fpdf import FPDF  # This will import fpdf2, as specified in requirements.txt

def format_currency(amount):
    """Formats a number as USD currency."""
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"

def generate_report(df):
    """
    Analyzes the filtered DataFrame and generates a dynamic, human-readable report.
    Handles empty or insufficient data gracefully.
    """
    
    # Check for empty data
    if df.empty:
        return "### ⚠️ No Data Available\n\nNo data matches the current filters. Please select a broader date range or different filter options."

    # --- Overall Performance ---
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    
    # --- Best and Worst Performers ---
    category_sales = df.groupby('Category')['Sales'].sum()
    if not category_sales.empty:
        best_category = category_sales.idxmax()
        best_category_sales = category_sales.max()
    else:
        best_category = "N/A"
        best_category_sales = 0

    subcategory_profit = df.groupby('Sub-Category')['Profit'].sum()
    if not subcategory_profit.empty:
        most_profitable_subcategory = subcategory_profit.idxmax()
        least_profitable_subcategory = subcategory_profit.idxmin()
    else:
        most_profitable_subcategory = "N/A"
        least_profitable_subcategory = "N/A"

    region_sales = df.groupby('Region')['Sales'].sum()
    if not region_sales.empty:
        best_region = region_sales.idxmax()
    else:
        best_region = "N/A"

    # --- Time Series Insights ---
    try:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        monthly_sales = df.set_index('Order Date').resample('M')['Sales'].sum()
        peak_month = monthly_sales.idxmax().strftime('%B %Y') if not monthly_sales.empty else "N/A"
    except Exception:
        peak_month = "N/A"

    # --- Building the Report String ---
    report = f"""
    ### 📈 **Automated Sales & Profit Analysis**

    Here is a summary of the data based on your current filters.

    ---

    #### **Executive Summary:**

    * **Total Sales:** **{format_currency(total_sales)}**
    * **Total Profit:** **{format_currency(total_profit)}**
    * **Overall Profit Margin:** **{profit_margin:.2f}%**

    The analysis reveals that **{best_region}** was the top-performing region. 
    The primary driver of sales was the **{best_category}** category, contributing **{format_currency(best_category_sales)}**.

    ---

    #### **Detailed Insights:**

    * **Top Performers:**
        * **Best Sales Category:** **{best_category}** ({format_currency(best_category_sales)}).
        * **Most Profitable Sub-Category:** **{most_profitable_subcategory}**.

    * **Areas for Improvement:**
        * **Least Profitable Sub-Category:** **{least_profitable_subcategory}**. This sub-category should be reviewed.

    * **Temporal Trends:**
        * The sales performance peaked in **{peak_month}**, indicating a potential seasonal high.
    """
    
    return report

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Superstore Sales Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_to_pdf(report_text):
    """
    Exports the generated report text to a PDF file in memory.
    This version includes the FINAL fix for the 0kb/corrupted PDF error.
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12) 

    # --- THIS IS THE FINAL FIX ---
    
    # 1. Remove the emoji, as it's not in the 'latin-1' or 'cp1252' charsets.
    pdf_text = re.sub(r'📈', '', report_text)
    
    # 2. The core PDF fonts (like Helvetica) use 'latin-1' / 'cp1252' encoding.
    #    They cannot render other characters.
    #    We MUST encode the text to this format.
    #    'errors="replace"' will change any unknown character (like a weird
    #    quote or symbol) into a '?' instead of crashing.
    #    This GUARANTEES the text is 100% safe to give to the PDF.
    pdf_safe_text = pdf_text.encode('latin-1', errors='replace').decode('latin-1')
    
    # 3. Pass the 100% safe text to multi_cell. 
    pdf.multi_cell(0, 10, pdf_safe_text)

    # 4. The .output() method from fpdf2 already returns bytes.
    return pdf.output()
