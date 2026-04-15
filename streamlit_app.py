import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ MGVCL PPR Monitoring Dashboard")

# -----------------------------------------------------------
# DATA LOADING & ROBUST CLEANING
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR Excel/CSV", type=["xls","xlsx","csv"])

if file:
    try:
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)
    except Exception as e:
        st.error(f"File loading error: {e}")
        st.stop()

    # 1. Clean Column Names
    df_raw.columns = df_raw.columns.str.strip()

    # 2. THE TRIPLE CLEAN (Prevents MarshallComponentException)
    # First, convert to string and replace common null strings
    df_clean = df_raw.astype(str).replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT', '<NA>', 'nan'], "")
    
    # Second, force empty strings where actual Python NaN objects might still hide
    df_clean = df_clean.fillna("")
    
    # Third, reset index (Crucial for AgGrid serialization)
    df_clean = df_clean.reset_index(drop=True)

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    sel_schemes = []
    if "Name Of Scheme" in df_clean.columns:
        u_schemes = sorted([x for x in df_clean["Name Of Scheme"].unique() if x != ""])
        sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)

    sel_types = []
    if "SR Type" in df_clean.columns:
        u_types = sorted([x for x in df_clean["SR Type"].unique() if x != ""])
        sel_types = st.sidebar.multiselect("SR Type", u_types, default=u_types)

    # Filter Logic
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
                <button style="background-color: #2e7d32; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 2px 10px; font-weight: bold; width: 100%;">
                🖨️ PDF
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const html = `
                    <html>
                    <head><meta charset="UTF-8"><style>
                        body { font-family: Arial; padding: 30px; border: 2px solid black; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        td { border: 1px solid black; padding: 10px; font-size: 16px; }
                        .label { background-color: #eee; font-weight: bold; width: 35%; }
                    </style></head>
                    <body>
                        <h2 style="text-align:center;">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
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
                w.document.write(html);
                w.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    # -----------------------------------------------------------
    # GRID DISPLAY FUNCTION
    # -----------------------------------------------------------
    def show_grid(data, key, has_print=False):
        if data.empty:
            st.warning("No data found for this selection.")
            return

        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        if has_print:
            # Added unique field name to avoid conflict
            gb.configure_column("Print_Action", headerName="Action", 
                                cellRenderer=render_print_button, 
                                width=100, pinned='left')
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        
        # We use try-except around AgGrid to catch serialization errors specifically
        try:
            AgGrid(
                data, 
                gridOptions=gb.build(), 
                height=450, 
                theme="streamlit", 
                allow_unsafe_jscode=True, 
                key=key,
                update_mode="NO_UPDATE" # Speed up rendering
            )
        except Exception as e:
            st.error("Grid Rendering Error. Displaying standard table instead.")
            st.dataframe(data)

    # -----------------------------------------------------------
    # TABS & LOGIC
    # -----------------------------------------------------------
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "View All"])

    with t1:
        # LOGIC: OPEN + Paid Date is filled + WCC is blank
        df1 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of FQ Paid"] != "") &
            (df_filtered["Date Of WCC"] == "")
        ].copy().reset_index(drop=True)
        st.write(f"Count: **{len(df1)}**")
        show_grid(df1, "grid1")

    with t2:
        # LOGIC: OPEN + WCC is filled + TMN is blank
        df2 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of WCC"] != "") &
            (df_filtered["Date Of TMN Issued"] == "")
        ].copy().reset_index(drop=True)
        st.write(f"Count: **{len(df2)}**")
        show_grid(df2, "grid2")

    with t3:
        # LOGIC: OPEN + Meter (TR MR) is filled + Release is blank
        df3 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["TR MR No"] != "") &
            (df_filtered["Date Of Release Conn"] == "")
        ].copy().reset_index(drop=True)
        st.write(f"Count: **{len(df3)}**")
        show_grid(df3, "grid3", has_print=True)

    with t4:
        st.write(f"Total Filtered: **{len(df_filtered)}**")
        show_grid(df_filtered, "grid4")

else:
    st.info("Please upload your file (Excel or CSV) to begin.")
