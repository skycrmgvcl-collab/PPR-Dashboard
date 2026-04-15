import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ PPR Monitoring Dashboard")

# -----------------------------------------------------------
# DATA LOADING & CLEANING
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Read Data
    try:
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Clean data: Standardize Column Names
    df_raw.columns = df_raw.columns.str.strip()
    
    # Robust Cleaning: Convert everything to string and handle NULLs
    # This prevents MarshallComponentException by ensuring serializable data
    df_clean = df_raw.astype(str).replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT', '<NA>'], "")
    df_clean = df_clean.apply(lambda x: x.str.strip())

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    
    # Filter by Scheme
    if "Name Of Scheme" in df_clean.columns:
        u_schemes = sorted([x for x in df_clean["Name Of Scheme"].unique() if x != ""])
        sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
    else:
        sel_schemes = []

    # Filter by Type
    if "SR Type" in df_clean.columns:
        u_types = sorted([x for x in df_clean["SR Type"].unique() if x != ""])
        sel_types = st.sidebar.multiselect("SR Type", u_types, default=u_types)
    else:
        sel_types = []

    # Apply Filter Logic
    mask = pd.Series([True] * len(df_clean))
    if sel_schemes:
        mask &= df_clean["Name Of Scheme"].isin(sel_schemes)
    if sel_types:
        mask &= df_clean["SR Type"].isin(sel_types)
    
    df_filtered = df_clean[mask].copy().reset_index(drop=True)

    # -----------------------------------------------------------
    # JAVASCRIPT PRINT RENDERER
    # -----------------------------------------------------------
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #1976d2; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 2px 8px; font-size: 12px; font-weight: bold;">
                🖨️ Print
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const htmlContent = `
                    <html>
                    <head><meta charset="UTF-8"><style>
                        body { font-family: sans-serif; padding: 40px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        td { border: 1px solid black; padding: 10px; }
                        .label { background-color: #f2f2f2; font-weight: bold; width: 35%; }
                        .header { text-align: center; font-size: 20px; font-weight: bold; }
                    </style></head>
                    <body>
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <h3 style="text-align:center;">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</h3>
                        <table>
                            <tr><td class="label">SR Number</td><td>${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">Name</td><td>${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">Village</td><td>${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">Meter No</td><td>${r['TR MR No'] || ''}</td></tr>
                        </table>
                        <script>window.print();</script>
                    </body>
                    </html>
                `;
                var w = window.open('', '_blank');
                w.document.write(htmlContent);
                w.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    # -----------------------------------------------------------
    # GRID DISPLAY FUNCTION
    # -----------------------------------------------------------
    def show_grid(data, key, show_print=False):
        if data.empty:
            st.warning("No records found for this category.")
            return

        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        if show_print:
            gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, 
                                width=100, pinned='left')
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        
        # Fixed: allow_unsafe_jscode=True must be paired with correct data cleaning
        AgGrid(
            data, 
            gridOptions=gb.build(), 
            height=400, 
            theme="streamlit", 
            allow_unsafe_jscode=True, 
            key=key,
            enable_enterprise_modules=False
        )

    # -----------------------------------------------------------
    # TABS & LOGIC
    # -----------------------------------------------------------
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "All Records"])

    with t1:
        # LOGIC: OPEN Status + Paid Date is NOT empty + WCC Date IS empty
        df_paid = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of FQ Paid"] != "") &
            (df_filtered["Date Of WCC"] == "")
        ].copy()
        st.subheader(f"Paid Pending Records: {len(df_paid)}")
        show_grid(df_paid, "grid_paid")

    with t2:
        # LOGIC: OPEN Status + WCC Date is NOT empty + TMN Issued IS empty
        df_tmn = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of WCC"] != "") &
            (df_filtered["Date Of TMN Issued"] == "")
        ].copy()
        st.subheader(f"TMN Pending Records: {len(df_tmn)}")
        show_grid(df_tmn, "grid_tmn")

    with t3:
        # LOGIC: OPEN Status + Meter No (TR MR) is NOT empty + Release Date IS empty
        df_release = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["TR MR No"] != "") &
            (df_filtered["Date Of Release Conn"] == "")
        ].copy()
        st.subheader(f"Release Pending Records: {len(df_release)}")
        show_grid(df_release, "grid_release", show_print=True)

    with t4:
        st.subheader("All Filtered Records")
        show_grid(df_filtered, "grid_all")

else:
    st.info("Please upload your PPR file to begin.")
