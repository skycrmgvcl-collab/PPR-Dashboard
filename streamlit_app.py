import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

# -----------------------------------------------------------
# FILE UPLOADER
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        # 1. Load File
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # 2. Basic Header Cleaning
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        # 3. Targeted Cleaning
        # We convert everything to string and strip spaces, but keep the word "NULL" for the filter
        df = df_raw.astype(str).apply(lambda x: x.str.strip())

        # -----------------------------------------------------------
        # COLUMN DETECTION
        # -----------------------------------------------------------
        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"

        # Check if columns exist
        available_cols = list(df.columns)
        if col_tr not in available_cols or col_date not in available_cols:
            st.error(f"Required columns not found! Found: {available_cols}")
            st.stop()

        # -----------------------------------------------------------
        # FILTER LOGIC (As per your requirement)
        # -----------------------------------------------------------
        # Condition 1: TR MR No is NOT "NULL" (meaning it has a real value)
        # Condition 2: Date Of Release Conn IS "NULL"
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        # -----------------------------------------------------------
        # JAVASCRIPT: PRINT PERFORMAS
        # -----------------------------------------------------------
        render_print_button = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #1565c0; color: white; border: none; 
                    border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: 'Arial'; padding: 30px; }}
                        .border-box {{ border: 3px solid black; padding: 20px; }}
                        .header {{ text-align: center; font-weight: bold; font-size: 22px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        td {{ border: 1px solid black; padding: 12px; font-size: 16px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; width: 40%; }}
                        .manual {{ color: blue; font-weight: bold; text-decoration: underline; }}
                        .footer {{ margin-top: 50px; display: flex; justify-content: space-between; font-weight: bold; }}
                    </style></head><body>
                    <div class="border-box">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div style="text-align:center; text-decoration:underline;">મીટર ઇન્સ્ટોલેશન રિપોર્ટ (Release Pending)</div>
                        <table>
                            <tr><td class="label">TR / MR No</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                            <tr><td class="label">SR Number</td><td>${{r['SR Number'] || ''}}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td>${{r['{col_scheme}'] || ''}}</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નંબર</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલેશન તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                        </table>
                        <div class="footer">
                            <span>ગ્રાહકની સહી: ______________</span>
                            <span>કર્મચારીની સહી: ______________</span>
                        </div>
                    </div>
                    <script>window.print();</script>
                    </body></html>`;
                    var w = window.open('', '_blank');
                    w.document.write(html);
                    w.document.close();
                }});
            }}
            getGui() {{ return this.eGui; }}
        }}
        """)

        # -----------------------------------------------------------
        # TABS & DISPLAY
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["🚀 Release Pending", "📁 All Data"])

        with t1:
            st.subheader(f"Records found: {len(df_pending)}")
            if len(df_pending) > 0:
                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_default_column(resizable=True, filter=True, sortable=True)
                gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=150, pinned='left')
                gb.configure_pagination(paginationPageSize=15)
                
                AgGrid(
                    df_pending, 
                    gridOptions=gb.build(), 
                    height=500, 
                    theme="streamlit", 
                    allow_unsafe_jscode=True, 
                    key="release_grid"
                )
            else:
                st.warning("No records match the 'Release Pending' criteria.")
                st.info(f"Criteria: '{col_tr}' is NOT 'NULL' AND '{col_date}' IS 'NULL'")

        with t2:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload your PPR file.")
