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

        # 2. Clean Data - CRITICAL: Convert everything to pure strings
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.astype(str)
        
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        
        # 3. Filter Data
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        # 4. JavaScript for Printing
        # NOTE: We use \\${} to escape the template literals for Python
        render_print_button = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: 'Arial'; padding: 30px; line-height: 1.6; }}
                        .box {{ border: 3px solid black; padding: 20px; }}
                        .header {{ text-align: center; font-weight: bold; font-size: 22px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        td {{ border: 1px solid black; padding: 12px; font-size: 16px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; width: 40%; }}
                        .manual {{ color: blue; font-weight: bold; text-decoration: underline; }}
                    </style></head><body>
                    <div class="box">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div style="text-align:center; font-weight:bold; text-decoration:underline;">મીટર ઇન્સ્ટોલેશન સર્વે રિપોર્ટ</div>
                        <table>
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                            <tr><td class="label">મીટર નંબર (Site)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                        </table>
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

        # 5. Build Grid
        # We manually build the grid dictionary to avoid the Builder's JSON error
        gb = GridOptionsBuilder.from_dataframe(df_pending)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=150, pinned='left')
        gb.configure_pagination(paginationPageSize=15)
        grid_options = gb.build()

        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Pending: {len(df_pending)}")
            if len(df_pending) > 0:
                # The 'key' must be unique for each AgGrid call
                AgGrid(
                    df_pending, 
                    gridOptions=grid_options, 
                    height=500, 
                    allow_unsafe_jscode=True, 
                    theme="streamlit",
                    key="release_grid_final"
                )
            else:
                st.warning("No records found matching the criteria.")

        with t2:
            st.dataframe(df)

    except Exception as e:
        # This catches any remaining serialization issues
        st.error(f"Fatal Error: {str(e)}")
else:
    st.info("Upload your PPR file to generate forms.")
