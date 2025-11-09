import pandas as pd
import re
from fpdf import FPDF  # fpdf2 is a "drop-in replacement", so the import name is the same

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
    # By Category
    category_sales = df.groupby('Category')['Sales'].sum()
    if not category_sales.empty:
        best_category = category_sales.idxmax()
        best_category_sales = category_sales.max()
    else:
        best_category = "N/A"
        best_category_sales = 0

    # By Sub-Category
    subcategory_profit = df.groupby('Sub-Category')['Profit'].sum()
    if not subcategory_profit.empty:
        most_profitable_subcategory = subcategory_profit.idxmax()
        least_profitable_subcategory = subcategory_profit.idxmin()
    else:
        most_profitable_subcategory = "N/A"
        least_profitable_subcategory = "N/A"

    # By Region
    region_sales = df.groupby('Region')['Sales'].sum()
    if not region_sales.empty:
        best_region = region_sales.idxmax()
    else:
        best_region = "N/A"

    # --- Time Series Insights ---
    try:
        # Ensure 'Order Date' is in datetime format before using .dt accessor
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        monthly_sales = df.set_index('Order Date').resample('M')['Sales'].sum()
        peak_month = monthly_sales.idxmax().strftime('%B %Y') if not monthly_sales.empty else "N/A"
    except Exception:
        peak_month = "N/A" # Handle potential resampling errors with very little data

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
    This version includes a robust encoding fix to prevent
    the "Failed to load PDF" corrupted file error.
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12) # This font uses 'cp1252' encoding

    # --- THIS IS THE fpdf2 CORRUPTION FIX ---
    
    # 1. Remove the emoji, as the core PDF fonts don't include it.
    pdf_text = re.sub(r'📈', '', report_text)
    
    # 2. Force-encode the text to the font's encoding ('cp1252').
    #    This will find any characters the font can't handle.
    # 3. Replace any unknown characters with a simple '?' instead of crashing.
    # 4. Decode it back to a string that multi_cell can use.
    #
    # This is the line that prevents the "Failed to load" error.
    # It ensures the text we pass to the PDF is 100% safe.
    pdf_safe_text = pdf_text.encode('cp1252', 'replace').decode('cp1252')

    # 5. Pass the 100% safe text to multi_cell.
    pdf.multi_cell(0, 10, pdf_safe_text)

    # 6. The .output() method from fpdf2 already returns bytes.
    return pdf.output()
