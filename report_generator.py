import pandas as pd
import re
from fpdf import FPDF  # This will use fpdf2

def format_currency(amount):
    """Formats a number as USD currency."""
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"

def generate_report(df):
    """Analyzes the filtered DataFrame and generates a readable report."""
    if df.empty:
        return "### ⚠️ No Data Available\n\nNo data matches the current filters."

    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

    category_sales = df.groupby('Category')['Sales'].sum()
    best_category = category_sales.idxmax() if not category_sales.empty else "N/A"
    best_category_sales = category_sales.max() if not category_sales.empty else 0

    subcategory_profit = df.groupby('Sub-Category')['Profit'].sum()
    most_profitable_subcategory = subcategory_profit.idxmax() if not subcategory_profit.empty else "N/A"
    least_profitable_subcategory = subcategory_profit.idxmin() if not subcategory_profit.empty else "N/A"

    region_sales = df.groupby('Region')['Sales'].sum()
    best_region = region_sales.idxmax() if not region_sales.empty else "N/A"

    try:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        monthly_sales = df.set_index('Order Date').resample('M')['Sales'].sum()
        peak_month = monthly_sales.idxmax().strftime('%B %Y') if not monthly_sales.empty else "N/A"
    except Exception:
        peak_month = "N/A"

    report = f"""
    ### 📈 **Automated Sales & Profit Analysis**

    #### **Executive Summary:**
    * **Total Sales:** {format_currency(total_sales)}
    * **Total Profit:** {format_currency(total_profit)}
    * **Overall Profit Margin:** {profit_margin:.2f}%

    The best region was **{best_region}**, led by **{best_category}** category
    with sales of {format_currency(best_category_sales)}.

    #### **Detailed Insights:**
    * **Top Performers:**
        * **Best Sales Category:** {best_category} ({format_currency(best_category_sales)}).
        * **Most Profitable Sub-Category:** {most_profitable_subcategory}.
    * **Areas for Improvement:**
        * **Least Profitable Sub-Category:** {least_profitable_subcategory}.
    * **Temporal Trends:**
        * Sales performance peaked in **{peak_month}**.
    """
    return report


# --- PDF Class ---
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Superstore Sales Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


# --- Export to PDF ---
def export_to_pdf(report_text):
    """
    Generates a valid PDF in memory and returns it as bytes.
    Compatible with Streamlit download_button().
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12)

    # Remove emojis and non-latin characters (fpdf can't render them)
    pdf_text = re.sub(r'[^\x00-\x7F]+', '', report_text)
    pdf_safe_text = pdf_text.encode('latin-1', errors='replace').decode('latin-1')

    pdf.multi_cell(0, 10, pdf_safe_text)

    # ✅ Correct: output as bytes (bytearray) — no extra encode()
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')  # fallback (older fpdf2)
    return bytes(pdf_bytes)
