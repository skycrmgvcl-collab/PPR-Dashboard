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

        # 2. Aggressive Cleaning
        # Strip spaces from headers
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        # Convert entire dataframe to string, strip spaces, and handle actual NaN values
        df = df_raw.astype(str).replace(['nan', 'NaN', 'None', '<NA>'], 'NULL')
        df = df.apply(lambda x: x.str.strip())

        # 3. Column Mapping
        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"

        if col_tr not in df.columns or col_date not in df.columns:
            st.error(f"Missing columns! Looked for '{col_tr}' and '{col_date}'. Available: {list(df.columns)}")
            st.stop()

        # -----------------------------------------------------------
        # LOGIC: TR MR No != "NULL" AND Date == "NULL"
        # -----------------------------------------------------------
        # We use .str.upper() to be safe against "Null", "null", or "NULL"
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        # -----------------------------------------------------------
        # TABS
        # -----------------------------------------------------------
        t1, t2, t3 = st.tabs(["🚀 Release Pending", "🔍 Data Debugger", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Records for Installation/Release: {len(df_pending)}")
            
            if len(df_pending) > 0:
                # JavaScript Print Code
                render_print_button = JsCode(f"""
                class PrintRenderer {{
                    init(params) {{
                        this.eGui = document.createElement('div');
                        this.eGui.innerHTML = `<button style="background-color: #d32f2f; color: white; border: none; 
                            border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Performa</button>`;
                        this.btn = this.eGui.querySelector('button');
                        this.btn.addEventListener('click', () => {{
                            const r = params.data;
                            const html = `<html><head><meta charset="UTF-8"><style>
                                body {{ font-family: 'Arial'; padding: 30px; }}
                                .box {{ border: 3px solid black; padding: 20px; }}
                                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                                td {{ border: 1px solid black; padding: 12px; font-size: 16px; }}
                                .label {{ background-color: #f5f5f5; font-weight: bold; }}
                            </style></head><body>
                            <div class="box">
                                <h2 style="text-align:center;">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
                                <h3 style="text-align:center; text-decoration:underline;">કનેક્શન રીલીઝ રિપોર્ટ</h3>
                                <table>
                                    <tr><td class="label">TR / MR No</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                                    <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                                    <tr><td class="label">SR Number</td><td>${{r['SR Number'] || ''}}</td></tr>
                                    <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                                    <tr><td class="label">મીટર નંબર (Site)</td><td>__________________________</td></tr>
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

                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=150, pinned='left')
                gb.configure_pagination(paginationPageSize=15)
                AgGrid(df_pending, gridOptions=gb.build(), height=500, theme="streamlit", allow_unsafe_jscode=True, key="grid")
            else:
                st.warning("No records found matching the criteria.")

        with t2:
            st.info("This tab shows exactly what is in your columns to help identify why the filter isn't working.")
            debug_df = df[[col_tr, col_date]].head(20)
            st.write("First 20 rows of relevant columns:")
            st.table(debug_df)
            
            # Additional check
            tr_vals = df[col_tr].unique()[:10]
            st.write(f"Sample values found in '{col_tr}':", tr_vals)
            dt_vals = df[col_date].unique()[:10]
            st.write(f"Sample values found in '{col_date}':", dt_vals)

        with t3:
            st.dataframe(df)

    except Exception as e:
        st.error(f"System Error: {e}")
else:
    st.info("Awaiting PPR file upload...")
