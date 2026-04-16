import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, JsCode

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

        # 2. Clean Data - CRITICAL: Pure strings only
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        
        # 3. Filter Data
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        # 4. JavaScript for Printing (Standard JS String)
        js_button = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: 'Arial'; padding: 30px; }}
                        .box {{ border: 3px solid black; padding: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        td {{ border: 1px solid black; padding: 12px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; }}
                    </style></head><body>
                    <div class="box">
                        <h2 style="text-align:center;">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
                        <table style="width:100%">
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                            <tr><td class="label">મીટર નંબર</td><td>__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td>____ / ____ / 2026</td></tr>
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

        # 5. MANUAL GRID OPTIONS (Bypasses GridOptionsBuilder to avoid JSON error)
        # We define only what is strictly necessary
        grid_options = {
            "columnDefs": [
                {
                    "headerName": "Action",
                    "field": "Print",
                    "cellRenderer": js_button,
                    "width": 120,
                    "pinned": "left",
                    "sortable": False,
                    "filter": False
                }
            ] + [{"field": col, "filter": True, "sortable": True} for col in df_pending.columns],
            "pagination": True,
            "paginationPageSize": 15,
            "domLayout": "autoHeight"
        }

        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Pending: {len(df_pending)}")
            if len(df_pending) > 0:
                AgGrid(
                    df_pending,
                    gridOptions=grid_options,
                    allow_unsafe_jscode=True,
                    theme="streamlit",
                    key="manual_grid_fixed"
                )
            else:
                st.warning("No records match (TR MR No != NULL and Date == NULL)")

        with t2:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Please upload your PPR file.")
