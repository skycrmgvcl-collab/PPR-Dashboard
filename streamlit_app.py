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
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df_raw = pd.read_excel(file)

    # Clean data: Standardize Column Names and NULL values
    df_raw.columns = df_raw.columns.str.strip()
    
    # Cleaning Logic: Handle 'NULL', 'nan', etc.
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip().replace(
            ['NULL', 'null', 'nan', 'NaN', 'None', 'NAT', 'nan'], ""
        )

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    unique_schemes = sorted([x for x in df_raw["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Scheme", unique_schemes, default=unique_schemes)
    
    unique_types = sorted([x for x in df_raw["SR Type"].unique() if x != ""])
    sel_types = st.sidebar.multiselect("SR Type", unique_types, default=unique_types)

    # Apply Filtering
    df_filtered = df_raw[
        (df_raw["Name Of Scheme"].isin(sel_schemes)) & 
        (df_raw["SR Type"].isin(sel_types))
    ].copy()

    # -----------------------------------------------------------
    # JAVASCRIPT PRINT RENDERER (Gujarati Support)
    # -----------------------------------------------------------
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #1976d2; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 4px 12px; font-weight: bold;">
                🖨️ Print Form
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const htmlContent = `
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            @page { size: A4; margin: 10mm; }
                            body { font-family: 'Arial', sans-serif; padding: 20px; }
                            .header { text-align: center; font-size: 22px; font-weight: bold; }
                            .title { text-align: center; font-size: 18px; font-weight: bold; text-decoration: underline; margin: 20px 0; }
                            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                            td { border: 1px solid black; padding: 12px; font-size: 16px; }
                            .label { background-color: #f2f2f2; font-weight: bold; width: 35%; }
                            .footer { margin-top: 60px; display: flex; justify-content: space-between; font-weight: bold; }
                        </style>
                    </head>
                    <body>
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>
                        <table>
                            <tr><td class="label">SR Number</td><td>${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">યોજના</td><td>${r['Name Of Scheme'] || ''}</td></tr>
                            <tr><td class="label">લોડ</td><td>${r['Demand Load'] || ''} ${r['Load Uom'] || ''}</td></tr>
                            <tr><td class="label">મીટર નંબર (TR MR No)</td><td>${r['TR MR No'] || ''}</td></tr>
                        </table>
                        <div class="footer">
                            <span>ગ્રાહકની સહી: ______________</span>
                            <span>કર્મચારીની સહી: ______________</span>
                        </div>
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
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        if show_print:
            # Adding the Print button column to the left
            gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, 
                                width=120, pinned='left')
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        AgGrid(data, gridOptions=gb.build(), height=500, theme="streamlit", 
               allow_unsafe_jscode=True, key=key)

    # -----------------------------------------------------------
    # TABS LOGIC
    # -----------------------------------------------------------
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "All Records"])

    with t1:
        # LOGIC: Paid Date exists but WCC is blank
        df_paid = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of FQ Paid"] != "") &
            (df_filtered["Date Of WCC"] == "")
        ]
        st.write(f"Paid Pending: **{len(df_paid)}**")
        show_grid(df_paid, "grid1")

    with t2:
        # LOGIC: WCC Date exists but TMN Issued is blank
        df_tmn = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["Date Of WCC"] != "") &
            (df_filtered["Date Of TMN Issued"] == "")
        ]
        st.write(f"Pending TMN: **{len(df_tmn)}**")
        show_grid(df_tmn, "grid2")

    with t3:
        # LOGIC: TR MR No entered but Release Date is blank
        df_release = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (df_filtered["TR MR No"] != "") &
            (df_filtered["Date Of Release Conn"] == "")
        ]
        st.write(f"Ready for Release: **{len(df_release)}**")
        # Print button enabled here
        show_grid(df_release, "grid3", show_print=True)

    with t4:
        st.write(f"Total Filtered Records: **{len(df_filtered)}**")
        show_grid(df_filtered, "grid4")

else:
    st.info("Please upload your file (Excel or CSV) to begin tracking.")
