import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        # 1. Load File
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # 2. Aggressive String Cleaning (Removes Functions/Objects that cause JSON errors)
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        # Convert everything to a simple string immediately
        df = df_raw.copy().astype(str)
        
        # Standardize all null-like values to the string "NULL"
        # This handles the 'NaT' and 'nan' issue you saw in your debugger
        for col in df.columns:
            df[col] = df[col].str.strip()
            df[col] = df[col].replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        # 3. Define Column Names (Exact match based on your debugger)
        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        
        if col_tr not in df.columns or col_date not in df.columns:
            st.error(f"Columns not found. Available: {list(df.columns)}")
            st.stop()

        # 4. Filter: TR is NOT NULL and Date IS NULL
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        # -----------------------------------------------------------
        # JAVASCRIPT: THE PRINT BUTTON
        # -----------------------------------------------------------
        # We use a f-string to pass the column names into the JS code
        render_print_button = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #d32f2f; color: white; border: none; 
                    border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: 'Arial'; padding: 30px; line-height: 1.6; }}
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
                        <div style="text-align:center; font-weight:bold; text-decoration:underline;">મીટર ઇન્સ્ટોલેશન સર્વે રિપોર્ટ</div>
                        <table>
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                        </table>
                        <div class="footer">
                            <span>ગ્રાહકની સહી: ______________</span>
                            <span>સ્ટાફની સહી: ______________</span>
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
        # UI DISPLAY
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Pending: {len(df_pending)}")
            
            if len(df_pending) > 0:
                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_default_column(resizable=True, filter=True, sortable=True)
                
                # Add the print column
                gb.configure_column(
                    "Print", 
                    headerName="Action", 
                    cellRenderer=render_print_button, 
                    width=150, 
                    pinned='left'
                )
                
                gb.configure_pagination(paginationPageSize=15)
                
                # Render Grid
                AgGrid(
                    df_pending, 
                    gridOptions=gb.build(), 
                    height=500, 
                    theme="streamlit", 
                    allow_unsafe_jscode=True,  # Mandatory for JsCode
                    key="release_grid"
                )
            else:
                st.warning("No records found where TR MR No is assigned and Release Date is 'NULL'.")

        with t2:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Fatal Error: {e}")
else:
    st.info("Upload your PPR file to generate forms.")
