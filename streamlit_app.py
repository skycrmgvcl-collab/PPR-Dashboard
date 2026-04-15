import streamlit as st
import pandas as pd
import base64
import re

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

    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Case-insensitive replacement of 'NULL' string with empty string
    df = df.replace(to_replace=r'(?i)^\s*NULL\s*$', value='', regex=True)
    
    # Fill actual NaN values with empty string
    df = df.fillna("")
    
    # Trim whitespace from all string columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    return df

def is_blank(value):
    """Returns True if the value is empty, NaN, or 'NULL'."""
    if pd.isna(value):
        return True
    val_str = str(value).strip().upper()
    return val_str == "" or val_str == "NULL"

def is_filled(value):
    """Returns True if the cell contains actual data."""
    return not is_blank(value)

def normalized_text(series):
    """Standardizes text for comparison."""
    return series.astype(str).str.strip().str.upper()

def is_open_status(series):
    """Identifies 'OPEN' records accurately."""
    status = normalized_text(series)
    return status.eq("OPEN") | status.str.startswith("OPEN ")

# ---------------------------------------------------
# PRINT FORM GENERATOR (HTML to PDF Workflow)
# ---------------------------------------------------

def create_release_html(row):
    """Generates the Gujarati Report HTML."""
    # We use Shruti or Arial for Gujarati character support
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; font-size:15px; line-height: 1.6; padding: 40px; }}
        .header {{ text-align:center; font-weight:bold; font-size:24px; margin-bottom:5px; }}
        .title {{ text-align:center; font-weight:bold; font-size:20px; margin-bottom:30px; text-decoration: underline; }}
        table {{ width:100%; border-collapse:collapse; margin-bottom: 50px; }}
        td {{ padding:12px; border: 1px solid #000; }}
        .label {{ font-weight: bold; background-color: #f2f2f2; width: 40%; }}
        .footer {{ margin-top: 100px; display: flex; justify-content: space-between; font-weight: bold; }}
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
    </head>
    <body onload="window.print()">
        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
        <div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
        
        <table>
            <tr><td class="label">SR Number</td><td>{row.get("SR Number","")}</td></tr>
            <tr><td class="label">Name Of Applicant</td><td>{row.get("Name Of Applicant","")}</td></tr>
            <tr><td class="label">Village Or City</td><td>{row.get("Village Or City","")}</td></tr>
            <tr><td class="label">Name Of Scheme</td><td>{row.get("Name Of Scheme","")}</td></tr>
            <tr><td class="label">Demand Load</td><td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
            <tr><td class="label">TR MR No (Meter No)</td><td>{row.get("TR MR No","")}</td></tr>
        </table>
        
        <div class="footer">
            <span>ગ્રાહકની સહી: ________________</span>
            <span>કર્મચારીની સહી: ________________</span>
        </div>
        
        <p style="text-align:center; font-size:10px; color:gray;" class="no-print">
            (Press Ctrl+P or Cmd+P if print dialog doesn't appear)
        </p>
    </body>
    </html>
    """
    return base64.b64encode(html.encode('utf-8')).decode()

# ---------------------------------------------------
# APP INTERFACE
# ---------------------------------------------------

file = st.file_uploader("📂 Upload PPR Excel / CSV", type=["xlsx", "xls", "csv"])

if file:
    df = load_file(file)
    cols = df.columns.tolist()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Dashboard Filters")
    
    # Scheme Filter
    scheme_list = sorted(df["Name Of Scheme"].unique()) if "Name Of Scheme" in cols else []
    scheme_sel = st.sidebar.multiselect("Select Scheme", scheme_list, default=scheme_list)
    
    # SR Type Filter
    sr_type_list = sorted(df["SR Type"].unique()) if "SR Type" in cols else []
    sr_sel = st.sidebar.multiselect("Select SR Type", sr_type_list, default=sr_type_list)

    # Apply Filters to the dataframe
    filtered_df = df.copy()
    if "Name Of Scheme" in cols:
        filtered_df = filtered_df[filtered_df["Name Of Scheme"].isin(scheme_sel)]
    if "SR Type" in cols:
        filtered_df = filtered_df[filtered_df["SR Type"].isin(sr_sel)]

    # --- SEARCH BAR ---
    search = st.text_input("🔎 Search by SR Number", placeholder="Type SR Number here...")
    if search and "SR Number" in cols:
        filtered_df = filtered_df[filtered_df["SR Number"].astype(str).str.contains(search, case=False)]

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "🕒 Paid Pending", "📋 TMN Pending", "✅ Release Pending", "📊 View All"
    ])

    # Required column check
    required = ["SR Status", "Date Of FQ Paid", "Date Of WCC", "Date Of TMN Issued", "TR MR No", "Date Of Release Conn"]
    missing = [c for c in required if c not in cols]

    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
    else:
        # TAB 1: PAID PENDING
        with tab1:
            res1 = filtered_df[
                is_open_status(filtered_df["SR Status"]) & 
                filtered_df["Date Of FQ Paid"].apply(is_filled) & 
                filtered_df["Date Of WCC"].apply(is_blank)
            ]
            st.metric("Total Paid Pending", len(res1))
            st.dataframe(res1, use_container_width=True)

        # TAB 2: TMN PENDING
        with tab2:
            res2 = filtered_df[
                is_open_status(filtered_df["SR Status"]) & 
                filtered_df["Date Of WCC"].apply(is_filled) & 
                filtered_df["Date Of TMN Issued"].apply(is_blank)
            ]
            st.metric("Total TMN Pending", len(res2))
            st.dataframe(res2, use_container_width=True)

        # TAB 3: RELEASE PENDING (The Print Section)
        with tab3:
            res3 = filtered_df[
                is_open_status(filtered_df["SR Status"]) & 
                filtered_df["TR MR No"].apply(is_filled) & 
                filtered_df["Date Of Release Conn"].apply(is_blank)
            ].copy()
            
            st.metric("Total Ready to Release", len(res3))
            
            if not res3.empty:
                st.write("### Generate Release Forms (PDF/Print)")
                for idx, row in res3.iterrows():
                    # Display a card-like row for each connection
                    with st.container():
                        c1, c2, c3 = st.columns([2, 4, 1.5])
                        c1.markdown(f"**SR:** `{row['SR Number']}`")
                        c2.write(f"👤 {row['Name Of Applicant']}")
                        
                        # Generate HTML for printing
                        html_b64 = create_release_html(row)
                        # Styled Print Button
                        btn_html = f'''
                            <a href="data:text/html;base64,{html_b64}" target="_blank" 
                            style="background-color:#28a745; color:white; padding:8px 16px; 
                            text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;
                            text-align:center; width:100%;">🖨 Print Form</a>
                        '''
                        c3.markdown(btn_html, unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No records match the 'Release Pending' criteria.")

        # TAB 4: VIEW ALL
        with tab4:
            st.metric("Total Records Loaded", len(filtered_df))
            st.dataframe(filtered_df, use_container_width=True)

    # --- FOOTER EXPORT ---
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Current View to CSV", data=csv_data, file_name="ppr_dashboard_export.csv", mime="text/csv")

else:
    st.info("💡 Please upload your PPR file to see the monitoring data.")
