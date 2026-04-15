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
# STABLE PRINT GENERATOR (JAVASCRIPT BLOB METHOD)
# ---------------------------------------------------

def get_print_script(row):
    """Creates a robust JavaScript trigger to prevent blank popups."""
    
    # The actual HTML content of your form
    report_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; border: 2px solid #000; }}
            .header {{ text-align:center; font-weight:bold; font-size:24px; }}
            .title {{ text-align:center; font-size:20px; text-decoration:underline; margin-bottom:30px; }}
            table {{ width:100%; border-collapse:collapse; }}
            td {{ padding:12px; border: 1px solid #000; font-size:16px; }}
            .label {{ background-color: #f2f2f2; font-weight:bold; width: 40%; }}
            .footer {{ margin-top: 60px; display: flex; justify-content: space-between; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class='header'>મધ્ય ગુજરાત વીજ કંપની લી.</div>
        <div class='title'>નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
        <table>
            <tr><td class='label'>SR Number</td><td>{row.get("SR Number","")}</td></tr>
            <tr><td class='label'>Name</td><td>{row.get("Name Of Applicant","")}</td></tr>
            <tr><td class='label'>Village</td><td>{row.get("Village Or City","")}</td></tr>
            <tr><td class='label'>Scheme</td><td>{row.get("Name Of Scheme","")}</td></tr>
            <tr><td class='label'>Meter No (TR MR)</td><td>{row.get("TR MR No","")}</td></tr>
        </table>
        <div class='footer'>
            <span>Customer Sign</span>
            <span>Employee Sign</span>
        </div>
        <script>window.print();</script>
    </body>
    </html>
    """.replace("\n", "").replace("'", "\\'")

    # This JS creates a 'Blob' which browsers handle much better than raw data strings
    js_code = f"""
    <script>
    function printReport_{row['SR Number']}() {{
        var htmlContent = '{report_html}';
        var blob = new Blob([htmlContent], {{type: 'text/html'}});
        var url = URL.createObjectURL(blob);
        var win = window.open(url, '_blank');
        if(!win) {{
            alert('Please allow pop-ups for this website to print the form.');
        }}
    }}
    </script>
    <button onclick="printReport_{row['SR Number']}()" 
    style="background-color: #28a745; color: white; padding: 10px 20px; 
    border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
    🖨 GENERATE PDF / PRINT
    </button>
    """
    return js_code

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

file = st.file_uploader("Upload File", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "All"])

    with tab3:
        # Filter for records ready to print
        res3 = df[
            is_open_status(df["SR Status"]) & 
            df["TR MR No"].apply(is_filled) & 
            df["Date Of Release Conn"].apply(is_blank)
        ].copy()

        if not res3.empty:
            st.success(f"Found {len(res3)} records. Click the button to generate the PDF form.")
            for idx, row in res3.iterrows():
                with st.container():
                    col_txt, col_btn = st.columns([3, 1])
                    col_txt.write(f"**SR:** {row['SR Number']} | **Name:** {row['Name Of Applicant']}")
                    
                    # Injecting the JS Button
                    col_btn.components.v1.html(get_print_script(row), height=60)
                    st.divider()
        else:
            st.warning("No records found that are ready for release.")

    with tab4:
        st.dataframe(df)

else:
    st.info("Upload an Excel file to see the 'Release Pending' print buttons.")
