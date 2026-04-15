import streamlit as st
import streamlit.components.v1 as components  # Added this vital import
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

    df.columns = df.columns.str.strip()
    # Replace any variation of NULL with empty string
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
# STABLE PRINT GENERATOR
# ---------------------------------------------------

def get_print_button_html(row):
    """Creates a JavaScript-powered button to generate the report."""
    
    # Clean up the data to avoid JS errors
    sr = str(row.get("SR Number", ""))
    name = str(row.get("Name Of Applicant", "")).replace("'", "\\'")
    village = str(row.get("Village Or City", "")).replace("'", "\\'")
    scheme = str(row.get("Name Of Scheme", "")).replace("'", "\\'")
    meter = str(row.get("TR MR No", "")).replace("'", "\\'")
    load = f"{row.get('Demand Load','')} {row.get('Load Uom','')}"

    report_content = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; border: 5px solid #000; }}
            .header {{ text-align:center; font-weight:bold; font-size:26px; }}
            .title {{ text-align:center; font-size:22px; text-decoration:underline; margin-bottom:40px; }}
            table {{ width:100%; border-collapse:collapse; margin-bottom: 50px; }}
            td {{ padding:15px; border: 1px solid #000; font-size:18px; }}
            .label {{ background-color: #f2f2f2; font-weight:bold; width: 40%; }}
            .footer {{ margin-top: 100px; display: flex; justify-content: space-between; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class='header'>મધ્ય ગુજરાત વીજ કંપની લી.</div>
        <div class='title'>નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
        <table>
            <tr><td class='label'>SR Number</td><td>{sr}</td></tr>
            <tr><td class='label'>ગ્રાહકનું નામ</td><td>{name}</td></tr>
            <tr><td class='label'>ગામ / શહેર</td><td>{village}</td></tr>
            <tr><td class='label'>યોજના</td><td>{scheme}</td></tr>
            <tr><td class='label'>લોડ</td><td>{load}</td></tr>
            <tr><td class='label'>મીટર નંબર (TR MR)</td><td>{meter}</td></tr>
        </table>
        <div class='footer'>
            <span>ગ્રાહકની સહી</span>
            <span>કર્મચારીની સહી</span>
        </div>
        <script>window.onload = function() {{ window.print(); }};</script>
    </body>
    </html>
    """.replace("\n", " ")

    # The actual button with embedded JS logic
    raw_html = f"""
    <button id="printBtn" style="
        background-color: #28a745; 
        color: white; 
        padding: 10px 20px; 
        border: none; 
        border-radius: 5px; 
        font-weight: bold; 
        cursor: pointer;
        width: 100%;
    ">🖨 GENERATE PDF</button>

    <script>
    document.getElementById('printBtn').onclick = function() {{
        var win = window.open('', '_blank');
        win.document.write('{report_content}');
        win.document.close();
    }};
    </script>
    """
    return raw_html

# ---------------------------------------------------
# MAIN APP INTERFACE
# ---------------------------------------------------

file = st.file_uploader("Upload PPR File", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "All Records"])

    with tab3:
        # Filter logic for Release Pending
        res3 = df[
            is_open_status(df["SR Status"]) & 
            df["TR MR No"].apply(is_filled) & 
            df["Date Of Release Conn"].apply(is_blank)
        ].copy()

        if not res3.empty:
            st.info("💡 **Tip:** Click the green button. When the new tab opens, select **'Save as PDF'** in your printer settings.")
            
            for idx, row in res3.iterrows():
                col_info, col_btn = st.columns([3, 1])
                col_info.write(f"**SR:** {row['SR Number']} | **Name:** {row['Name Of Applicant']}")
                
                # Using the imported components to render the button
                with col_btn:
                    components.html(get_print_button_html(row), height=60)
                st.divider()
        else:
            st.warning("No records found ready for Release. Check your data for 'OPEN' status and 'NULL' dates.")

    with tab4:
        st.dataframe(df, use_container_width=True)

else:
    st.info("Please upload a file to enable the dashboard.")
