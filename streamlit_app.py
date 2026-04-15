import streamlit as st
import pandas as pd
import base64

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ PPR Monitoring Dashboard")

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------

@st.cache_data
def load_file(file):
    """Loads CSV or Excel files and cleans up column names/NULL values."""
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()
    # Convert 'NULL' string to empty string
    df = df.replace(r'^\s*NULL\s*$', '', regex=True)
    # Fill actual NaN values with empty string
    df = df.fillna("")
    return df

def is_blank(value):
    """Checks if a cell is empty or contains the word NULL."""
    text = str(value).strip()
    return text == "" or text.upper() == "NULL"

def normalized_text(series):
    """Standardizes text for comparison (removes spaces and converts to UPPER)."""
    return series.astype(str).str.strip().str.upper()

def is_open_status(series):
    """Checks if the SR Status starts with 'OPEN'."""
    status = normalized_text(series)
    return status.eq("OPEN") | status.str.startswith("OPEN ")

# ---------------------------------------------------
# RELEASE FORM HTML GENERATOR
# ---------------------------------------------------

def create_release_html(row):
    """Generates a Gujarati print-ready HTML form."""
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Shruti', sans-serif; font-size:14px; padding: 20px; }}
        .header {{ text-align:center; font-weight:bold; font-size:22px; }}
        .title {{ text-align:center; font-weight:bold; font-size:18px; }}
        table {{ width:100%; border-collapse:collapse; margin-top: 20px; }}
        td {{ padding:8px; border-bottom: 1px solid #eee; }}
        .sign-area {{ margin-top: 50px; display: flex; justify-content: space-between; }}
    </style>
    </head>
    <body onload="window.print()">
        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
        <div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
        <table>
            <tr><td width="30%"><b>SR Number</b></td><td>{row.get("SR Number","")}</td></tr>
            <tr><td><b>Name</b></td><td>{row.get("Name Of Applicant","")}</td></tr>
            <tr><td><b>Village</b></td><td>{row.get("Village Or City","")}</td></tr>
            <tr><td><b>Scheme</b></td><td>{row.get("Name Of Scheme","")}</td></tr>
            <tr><td><b>Load</b></td><td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
            <tr><td><b>TR MR No</b></td><td>{row.get("TR MR No","")}</td></tr>
        </table>
        <div class="sign-area">
            <p>Customer Sign: ________________</p>
            <p>Employee Sign: ________________</p>
        </div>
    </body>
    </html>
    """
    return base64.b64encode(html.encode('utf-8')).decode()

# ---------------------------------------------------
# MAIN APPLICATION LOGIC
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    
    # Scheme Filter
    schemes = sorted(df["Name Of Scheme"].unique()) if "Name Of Scheme" in df.columns else []
    scheme_sel = st.sidebar.multiselect("Name Of Scheme", schemes, default=schemes)
    if scheme_sel:
        df = df[df["Name Of Scheme"].isin(scheme_sel)]

    # SR Type Filter
    sr_types = sorted(df["SR Type"].unique()) if "SR Type" in df.columns else []
    sr_sel = st.sidebar.multiselect("SR Type", sr_types, default=sr_types)
    if sr_sel:
        df = df[df["SR Type"].isin(sr_sel)]

    # Survey Category Filter
    survey = sorted(df["Survey Category"].unique()) if "Survey Category" in df.columns else []
    survey_sel = st.sidebar.multiselect("Survey Category", survey, default=survey)
    if survey_sel:
        df = df[df["Survey Category"].isin(survey_sel)]

    # --- SEARCH ---
    search = st.text_input("🔎 Search SR Number")
    if search:
        df = df[df["SR Number"].astype(str).str.contains(search)]

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Paid Pending", 
        "Pending to Issue TMN", 
        "Release Pending", 
        "All Records"
    ])

    # TAB 1: PAID PENDING (Paid but WCC not done)
    with tab1:
        ppr_df = df[
            is_open_status(df["SR Status"]) & 
            (~df["Date Of FQ Paid"].apply(is_blank)) & 
            (df["Date Of WCC"].apply(is_blank))
        ]
        st.metric("Paid Pending", len(ppr_df))
        st.dataframe(ppr_df, use_container_width=True)

    # TAB 2: TMN PENDING (WCC done but TMN not issued)
    with tab2:
        tmn_df = df[
            is_open_status(df["SR Status"]) & 
            (~df["Date Of WCC"].apply(is_blank)) & 
            (df["Date Of TMN Issued"].apply(is_blank))
        ]
        st.metric("Pending to Issue TMN", len(tmn_df))
        st.dataframe(tmn_df, use_container_width=True)

    # TAB 3: RELEASE PENDING (TR MR entered but Connection not released)
    with tab3:
        release_df = df[
            is_open_status(df["SR Status"]) & 
            (~df["TR MR No"].apply(is_blank)) & 
            (df["Date Of Release Conn"].apply(is_blank))
        ].copy()
        
        st.metric("Release Pending", len(release_df))
        
        # Display individual rows with Print buttons
        for i, row in release_df.iterrows():
            col1, col2, col3 = st.columns([3, 3, 1])
            col1.write(f"**SR:** {row['SR Number']}")
            col2.write(row['Name Of Applicant'])
            
            # Print Link
            html_code = create_release_html(row)
            link = f'<a href="data:text/html;base64,{html_code}" target="_blank" style="text-decoration:none;">🖨 Print</a>'
            col3.markdown(link, unsafe_allow_html=True)
        
        st.divider()
        st.dataframe(release_df, use_container_width=True)

    # TAB 4: ALL RECORDS
    with tab4:
        st.metric("Total Records", len(df))
        st.dataframe(df, use_container_width=True)

    # --- EXPORT ---
    st.download_button(
        label="📥 Export Filtered Data to CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="ppr_filtered_data.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload a PPR file (Excel or CSV) to begin monitoring.")
