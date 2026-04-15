import streamlit as st
import pandas as pd
import base64

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ PPR Monitoring Dashboard")

# ---------------------------------------------------
# CORE LOGIC FUNCTIONS
# ---------------------------------------------------

@st.cache_data
def load_file(file):
    """Loads file and performs initial cleaning of 'NULL' strings."""
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()
    
    # Convert any variation of 'NULL' string to actual empty string for consistency
    df = df.replace(r'^\s*NULL\s*$', '', regex=True, flags=2) # flag 2 = IgnoreCase
    df = df.fillna("")
    return df

def is_blank(value):
    """Returns True if the value is empty, NaN, or the string 'NULL'."""
    val_str = str(value).strip().upper()
    return val_str == "" or val_str == "NULL" or pd.isna(value)

def is_filled(value):
    """Returns True if the cell actually contains data (not blank/NULL)."""
    return not is_blank(value)

def normalized_text(series):
    """Standardizes text for comparison."""
    return series.astype(str).str.strip().str.upper()

def is_open_status(series):
    """Logic to identify 'OPEN' records regardless of extra spaces."""
    status = normalized_text(series)
    return status.eq("OPEN") | status.str.startswith("OPEN ")

# ---------------------------------------------------
# PRINT FORM GENERATOR
# ---------------------------------------------------

def create_release_html(row):
    """Generates the Gujarati Report HTML."""
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Shruti', 'Arial'; font-size:14px; line-height: 1.6; }}
        .header {{ text-align:center; font-weight:bold; font-size:22px; margin-bottom:5px; }}
        .title {{ text-align:center; font-weight:bold; font-size:18px; margin-bottom:20px; }}
        table {{ width:100%; border-collapse:collapse; }}
        td {{ padding:8px; border-bottom: 1px solid #ddd; }}
        .footer {{ margin-top: 60px; display: flex; justify-content: space-between; font-weight: bold; }}
    </style>
    </head>
    <body onload="window.print()">
        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
        <div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
        <table>
            <tr><td width="35%">SR Number</td><td>{row.get("SR Number","")}</td></tr>
            <tr><td>Name Of Applicant</td><td>{row.get("Name Of Applicant","")}</td></tr>
            <tr><td>Village Or City</td><td>{row.get("Village Or City","")}</td></tr>
            <tr><td>Name Of Scheme</td><td>{row.get("Name Of Scheme","")}</td></tr>
            <tr><td>Demand Load</td><td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
            <tr><td>TR MR No</td><td>{row.get("TR MR No","")}</td></tr>
        </table>
        <div class="footer">
            <span>Customer Sign: ________________</span>
            <span>Employee Sign: ________________</span>
        </div>
    </body>
    </html>
    """
    return base64.b64encode(html.encode('utf-8')).decode()

# ---------------------------------------------------
# APP INTERFACE
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Navigation & Filters")
    
    # Dynamic list generation for filters
    cols = df.columns
    
    scheme_list = sorted(df["Name Of Scheme"].unique()) if "Name Of Scheme" in cols else []
    scheme_sel = st.sidebar.multiselect("Filter Scheme", scheme_list, default=scheme_list)
    
    sr_type_list = sorted(df["SR Type"].unique()) if "SR Type" in cols else []
    sr_sel = st.sidebar.multiselect("Filter SR Type", sr_type_list, default=sr_type_list)

    # Apply Filters
    filtered_df = df[
        (df["Name Of Scheme"].isin(scheme_sel)) & 
        (df["SR Type"].isin(sr_sel))
    ]

    # --- SEARCH ---
    search = st.text_input("🔎 Quick Search (SR Number)")
    if search:
        filtered_df = filtered_df[filtered_df["SR Number"].astype(str).str.contains(search)]

    # --- TABS LOGIC ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Paid Pending", "TMN Pending", "Release Pending", "View All"
    ])

    # TAB 1: PAID PENDING
    # Logic: Status is OPEN + Paid Date exists + WCC Date is NULL/Blank
    with tab1:
        res1 = filtered_df[
            is_open_status(filtered_df["SR Status"]) & 
            filtered_df["Date Of FQ Paid"].apply(is_filled) & 
            filtered_df["Date Of WCC"].apply(is_blank)
        ]
        st.metric("Records Found", len(res1))
        st.dataframe(res1, use_container_width=True)

    # TAB 2: TMN PENDING
    # Logic: Status is OPEN + WCC Date exists + TMN Date is NULL/Blank
    with tab2:
        res2 = filtered_df[
            is_open_status(filtered_df["SR Status"]) & 
            filtered_df["Date Of WCC"].apply(is_filled) & 
            filtered_df["Date Of TMN Issued"].apply(is_blank)
        ]
        st.metric("Records Found", len(res2))
        st.dataframe(res2, use_container_width=True)

    # TAB 3: RELEASE PENDING
    # Logic: Status is OPEN + TR MR No exists + Release Date is NULL/Blank
    with tab3:
        res3 = filtered_df[
            is_open_status(filtered_df["SR Status"]) & 
            filtered_df["TR MR No"].apply(is_filled) & 
            filtered_df["Date Of Release Conn"].apply(is_blank)
        ].copy()
        
        st.metric("Records Found", len(res3))
        
        # Display Print buttons for each row
        if not res3.empty:
            for idx, row in res3.head(20).iterrows(): # Showing first 20 for performance
                c1, c2, c3 = st.columns([2, 4, 1])
                c1.info(f"SR: {row['SR Number']}")
                c2.write(row['Name Of Applicant'])
                html_b64 = create_release_html(row)
                btn_html = f'<a href="data:text/html;base64,{html_b64}" target="_blank" style="background-color:#4CAF50; color:white; padding:8px 12px; text-decoration:none; border-radius:4px;">🖨 Print</a>'
                c3.markdown(btn_html, unsafe_allow_html=True)
            
            st.divider()
        st.dataframe(res3, use_container_width=True)

    # TAB 4: ALL RECORDS
    with tab4:
        st.metric("Total Filtered Records", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)

    # --- DOWNLOAD ---
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data", data=csv_data, file_name="ppr_data.csv", mime="text/csv")

else:
    st.warning("👈 Please upload a file (Excel or CSV) to begin.")
