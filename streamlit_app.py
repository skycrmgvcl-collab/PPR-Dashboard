import streamlit as st
import pandas as pd
import base64

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ MGVCL PPR Monitoring Dashboard")

# ---------------------------------------------------
# CORE LOGIC FUNCTIONS
# ---------------------------------------------------

@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    # Clean column names (remove spaces)
    df.columns = df.columns.str.strip()
    # Replace 'NULL' strings case-insensitively
    df = df.replace(to_replace=r'(?i)^\s*NULL\s*$', value='', regex=True)
    df = df.fillna("")
    return df

def is_blank(value):
    val_str = str(value).strip().upper()
    return val_str == "" or val_str == "NULL" or pd.isna(value)

def is_filled(value):
    return not is_blank(value)

def is_open_status(series):
    status = series.astype(str).str.strip().str.upper()
    return status.eq("OPEN") | status.str.startswith("OPEN ")

# ---------------------------------------------------
# PRINT FORM GENERATOR (HTML DOWNLOAD METHOD)
# ---------------------------------------------------

def get_html_download_link(row):
    """Generates an HTML file that the user can download and print."""
    
    sr = str(row.get("SR Number", ""))
    name = str(row.get("Name Of Applicant", ""))
    village = str(row.get("Village Or City", ""))
    scheme = str(row.get("Name Of Scheme", ""))
    meter = str(row.get("TR MR No", ""))
    load = f"{row.get('Demand Load','')} {row.get('Load Uom','')}"

    report_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body {{ font-family: 'Arial', sans-serif; padding: 40px; }}
            .border-box {{ border: 4px solid #000; padding: 30px; }}
            .header {{ text-align:center; font-weight:bold; font-size:24px; margin-bottom: 5px; }}
            .title {{ text-align:center; font-size:20px; text-decoration:underline; margin-bottom:40px; }}
            table {{ width:100%; border-collapse:collapse; }}
            td {{ padding:15px; border: 1px solid #000; font-size:18px; }}
            .label {{ background-color: #f2f2f2; font-weight:bold; width: 40%; }}
            .footer {{ margin-top: 80px; display: flex; justify-content: space-between; font-weight:bold; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="border-box">
            <div class='header'>મધ્ય ગુજરાત વીજ કંપની લી.</div>
            <div class='title'>નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
            <table>
                <tr><td class='label'>SR Number</td><td>{sr}</td></tr>
                <tr><td class='label'>ગ્રાહકનું નામ</td><td>{name}</td></tr>
                <tr><td class='label'>ગામ / શહેર</td><td>{village}</td></tr>
                <tr><td class='label'>યોજના</td><td>{scheme}</td></tr>
                <tr><td class='label'>લોડ</td><td>{load}</td></tr>
                <tr><td class='label'>મીટર નંબર (TR MR No)</td><td>{meter}</td></tr>
            </table>
            <div class='footer'>
                <span>ગ્રાહકની સહી: ______________</span>
                <span>કર્મચારીની સહી: ______________</span>
            </div>
        </div>
    </body>
    </html>
    """
    return report_html

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

uploaded_file = st.file_uploader("📂 Step 1: Upload PPR File", type=["xlsx", "xls", "csv"])

if uploaded_file:
    df_raw = load_file(uploaded_file)
    cols = df_raw.columns.tolist()

    # --- SIDEBAR FILTERS (RESTORED) ---
    st.sidebar.header("📊 Filter Options")
    
    selected_schemes = []
    if "Name Of Scheme" in cols:
        unique_schemes = sorted(df_raw["Name Of Scheme"].unique())
        selected_schemes = st.sidebar.multiselect("Select Scheme", unique_schemes, default=unique_schemes)
    
    selected_types = []
    if "SR Type" in cols:
        unique_types = sorted(df_raw["SR Type"].unique())
        selected_types = st.sidebar.multiselect("Select SR Type", unique_types, default=unique_types)

    # Apply Filters
    df = df_raw.copy()
    if selected_schemes:
        df = df[df["Name Of Scheme"].isin(selected_schemes)]
    if selected_types:
        df = df[df["SR Type"].isin(selected_types)]

    # --- TABS ---
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending (PRINT)", "All Data"])

    with t3:
        # Check required columns for Release Pending
        req = ["SR Status", "TR MR No", "Date Of Release Conn"]
        missing = [c for c in req if c not in cols]

        if missing:
            st.error(f"Required columns missing: {missing}")
        else:
            res3 = df[
                is_open_status(df["SR Status"]) & 
                df["TR MR No"].apply(is_filled) & 
                df["Date Of Release Conn"].apply(is_blank)
            ].copy()

            st.success(f"Found {len(res3)} records ready for printing.")
            
            for idx, row in res3.iterrows():
                col_txt, col_btn = st.columns([3, 1])
                col_txt.write(f"**SR:** {row['SR Number']} | **Name:** {row['Name Of Applicant']}")
                
                # HTML Generation
                html_content = get_html_download_link(row)
                
                # Download Button (No Pop-ups needed!)
                col_btn.download_button(
                    label="📥 Download Print Form",
                    data=html_content,
                    file_name=f"Report_{row['SR Number']}.html",
                    mime="text/html",
                    key=f"btn_{idx}"
                )
                st.divider()

    with t4:
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Welcome! Please upload an Excel/CSV file to enable the dashboard and filters.")
