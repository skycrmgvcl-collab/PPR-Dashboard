import streamlit as st
import pandas as pd
import base64
import re

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ MGVCL PPR Monitoring Dashboard")

# ---------------------------------------------------
# CORE LOGIC FUNCTIONS
# ---------------------------------------------------

@st.cache_data
def load_file(file):
    """Loads file and cleans 'NULL' strings and whitespaces."""
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()
    
    # Powerful Regex to clean 'NULL' case-insensitively
    df = df.replace(to_replace=r'(?i)^\s*NULL\s*$', value='', regex=True)
    df = df.fillna("")
    
    # Global trim for all strings
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def is_blank(value):
    """Checks if cell is empty or 'NULL'."""
    val_str = str(value).strip().upper()
    return val_str == "" or val_str == "NULL" or pd.isna(value)

def is_filled(value):
    """Checks if cell has actual data."""
    return not is_blank(value)

def is_open_status(series):
    """Checks for 'OPEN' status effectively."""
    status = series.astype(str).str.strip().str.upper()
    return status.eq("OPEN") | status.str.startswith("OPEN ")

# ---------------------------------------------------
# PDF/PRINT GENERATOR
# ---------------------------------------------------

def create_release_html(row):
    """Generates a high-quality Gujarati Form for PDF Printing."""
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Arial', sans-serif; font-size:16px; color: #000; padding: 20px; }}
        .border-box {{ border: 3px solid #000; padding: 40px; min-height: 800px; position: relative; }}
        .header {{ text-align:center; font-weight:bold; font-size:26px; margin-bottom:10px; }}
        .title {{ text-align:center; font-weight:bold; font-size:22px; margin-bottom:40px; border-bottom: 2px solid #000; display: inline-block; width: 100%; padding-bottom: 10px; }}
        table {{ width:100%; border-collapse:collapse; margin-top: 20px; }}
        td {{ padding:15px; border: 1px solid #000; font-size: 18px; }}
        .label {{ font-weight: bold; background-color: #f0f0f0; width: 40%; }}
        .footer {{ margin-top: 100px; display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; }}
        .note {{ margin-top: 50px; font-size: 12px; color: #555; font-style: italic; }}
    </style>
    </head>
    <body onload="window.print()">
        <div class="border-box">
            <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
            <div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
            
            <table>
                <tr><td class="label">SR Number</td><td>{row.get("SR Number","")}</td></tr>
                <tr><td class="label">ગ્રાહકનું નામ (Name)</td><td>{row.get("Name Of Applicant","")}</td></tr>
                <tr><td class="label">ગામ / શહેર (Village)</td><td>{row.get("Village Or City","")}</td></tr>
                <tr><td class="label">યોજના (Scheme)</td><td>{row.get("Name Of Scheme","")}</td></tr>
                <tr><td class="label">લોડ (Load)</td><td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
                <tr><td class="label">મીટર નંબર (Meter No)</td><td>{row.get("TR MR No","")}</td></tr>
            </table>
            
            <div class="footer">
                <span>ગ્રાહકની સહી: ________________</span>
                <span>કર્મચારીની સહી: ________________</span>
            </div>
            
            <div class="note">
                તારીખ: ________________ &nbsp;&nbsp;&nbsp;&nbsp; સ્થળ: ________________
            </div>
        </div>
    </body>
    </html>
    """
    return base64.b64encode(html.encode('utf-8')).decode()

# ---------------------------------------------------
# INTERFACE
# ---------------------------------------------------

file = st.file_uploader("📂 Step 1: Upload your Excel/CSV file here", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)
    cols = df.columns.tolist()

    # Filters
    st.sidebar.header("Dashboard Filters")
    scheme_sel = st.sidebar.multiselect("Scheme Name", sorted(df["Name Of Scheme"].unique()) if "Name Of Scheme" in cols else [])
    sr_sel = st.sidebar.multiselect("SR Type", sorted(df["SR Type"].unique()) if "SR Type" in cols else [])

    # Filter Logic
    if scheme_sel: df = df[df["Name Of Scheme"].isin(scheme_sel)]
    if sr_sel: df = df[df["SR Type"].isin(sr_sel)]

    # Search
    search = st.text_input("🔎 Step 2: Search by SR Number (Optional)", placeholder="Search...")
    if search: df = df[df["SR Number"].astype(str).str.contains(search)]

    # Tabs
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending (PRINT PDF)", "All Records"])

    # Column Validation
    req = ["SR Status", "Date Of FQ Paid", "Date Of WCC", "Date Of TMN Issued", "TR MR No", "Date Of Release Conn"]
    missing = [c for c in req if c not in cols]

    if missing:
        st.error(f"Error: Your file is missing these columns: {', '.join(missing)}")
    else:
        with t1:
            res1 = df[is_open_status(df["SR Status"]) & df["Date Of FQ Paid"].apply(is_filled) & df["Date Of WCC"].apply(is_blank)]
            st.metric("Total", len(res1))
            st.dataframe(res1, use_container_width=True)

        with t2:
            res2 = df[is_open_status(df["SR Status"]) & df["Date Of WCC"].apply(is_filled) & df["Date Of TMN Issued"].apply(is_blank)]
            st.metric("Total", len(res2))
            st.dataframe(res2, use_container_width=True)

        with t3:
            res3 = df[is_open_status(df["SR Status"]) & df["TR MR No"].apply(is_filled) & df["Date Of Release Conn"].apply(is_blank)].copy()
            
            st.success(f"✅ Found {len(res3)} records ready for printing.")
            
            if not res3.empty:
                st.info("💡 **How to get PDF:** Click 'Print Form' -> Select 'Save as PDF' in the destination dropdown of the print window.")
                
                for idx, row in res3.iterrows():
                    with st.expander(f"📄 SR: {row['SR Number']} - {row['Name Of Applicant']}", expanded=True):
                        col_info, col_btn = st.columns([3, 1])
                        col_info.write(f"**Scheme:** {row['Name Of Scheme']} | **Meter:** {row['TR MR No']}")
                        
                        # PRINT BUTTON LOGIC
                        html_code = create_release_html(row)
                        button_style = f"""
                            <a href="data:text/html;base64,{html_code}" target="_blank" 
                            style="text-decoration: none; background-color: #28a745; color: white; 
                            padding: 15px 25px; border-radius: 8px; font-weight: bold; 
                            font-size: 18px; display: inline-block; text-align: center; border: 2px solid #1e7e34;">
                            🖨 PRINT FORM (CLICK HERE)
                            </a>"""
                        col_btn.markdown(button_style, unsafe_allow_html=True)
            else:
                st.warning("No records found in 'Release Pending'. Ensure SR Status is 'OPEN', TR MR No is not 'NULL', and Release Date is 'NULL'.")

        with t4:
            st.dataframe(df, use_container_width=True)

    # Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered CSV", data=csv, file_name="ppr_data.csv")

else:
    st.info("Please upload your Excel file to start.")
