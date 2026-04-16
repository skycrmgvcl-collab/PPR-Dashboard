import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # 1. Clean Column Names
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        # 2. Targeted Cleaning for MGVCL PPR Format
        # Convert to string and handle the 'NaT' and 'nan' issue
        df = df_raw.copy()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace common "empty" indicators with a unified "NULL"
            df[col] = df[col].replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"

        # 3. The Filter: TR is NOT NULL and Date IS NULL
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        t1, t2, t3 = st.tabs(["🚀 Release Pending", "🔍 Data Debugger", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Records for Installation: {len(df_pending)}")
            
            if not df_pending.empty:
                render_print_button = JsCode(f"""
                class PrintRenderer {{
                    init(params) {{
                        this.eGui = document.createElement('div');
                        this.eGui.innerHTML = `<button style="background-color: #e65100; color: white; border: none; 
                            border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>`;
                        this.btn = this.eGui.querySelector('button');
                        this.btn.addEventListener('click', () => {{
                            const r = params.data;
                            const html = `<html><head><meta charset="UTF-8"><style>
                                body {{ font-family: 'Arial'; padding: 25px; line-height: 1.5; }}
                                .border-box {{ border: 3px solid black; padding: 20px; }}
                                .header {{ text-align: center; font-weight: bold; font-size: 20px; }}
                                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                                td {{ border: 1px solid black; padding: 10px; }}
                                .label {{ background-color: #f2f2f2; font-weight: bold; width: 40%; }}
                                .fill {{ color: blue; font-weight: bold; }}
                            </style></head><body>
                            <div class="border-box">
                                <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                                <div style="text-align:center; font-weight:bold;">મીટર ઇન્સ્ટોલેશન અને સર્વે રિપોર્ટ</div>
                                <table>
                                    <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                                    <tr><td class="label">SR Number</td><td>${{r['SR Number'] || ''}}</td></tr>
                                    <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['Name Of Applicant'] || ''}}</td></tr>
                                    <tr><td class="label">ગામ / શહેર</td><td>${{r['Village Or City'] || ''}}</td></tr>
                                    <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td class="fill">________________________</td></tr>
                                    <tr><td class="label">ઇન્સ્ટોલેશન તારીખ</td><td class="fill">____ / ____ / 2026</td></tr>
                                </table>
                                <div style="margin-top:40px; display:flex; justify-content:space-between;">
                                    <span>ગ્રાહકની સહી: ____________</span>
                                    <span>સ્ટાફની સહી: ____________</span>
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

                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=150, pinned='left')
                gb.configure_pagination(paginationPageSize=20)
                AgGrid(df_pending, gridOptions=gb.build(), height=500, theme="streamlit", allow_unsafe_jscode=True, key="pending_grid")
            else:
                st.warning("No records found where TR MR No is assigned but Date is NULL.")
                st.info("Based on your Debugger, almost all rows currently have 'NULL' in the TR MR No column.")

        with t2:
            st.write("### Current Column State")
            st.write("The system has converted 'NaT' or empty cells to 'NULL' for filtering.")
            st.table(df[[col_tr, col_date]].head(20))

        with t3:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload the PPR_REPORT.xls file.")
