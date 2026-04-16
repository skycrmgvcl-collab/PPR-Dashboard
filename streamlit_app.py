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
        # Load file with robust settings
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # Clean column names (strip whitespace)
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        # Convert all data to string and strip spaces for accurate comparison
        df = df_raw.astype(str).apply(lambda x: x.str.strip())

        # -----------------------------------------------------------
        # COLUMN DEFINITIONS
        # -----------------------------------------------------------
        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"
        col_applicant = "Name Of Applicant"
        col_village = "Village Or City"
        col_sr = "SR Number"

        # -----------------------------------------------------------
        # FILTER LOGIC: RELEASE PENDING
        # -----------------------------------------------------------
        # Logic: TR MR No is NOT "NULL" AND Date Of Release Conn IS "NULL"
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
                        body {{ font-family: 'Arial'; padding: 30px; line-height: 1.6; }}
                        .border-box {{ border: 3px solid black; padding: 20px; }}
                        .header {{ text-align: center; font-weight: bold; font-size: 22px; }}
                        .title {{ text-align: center; font-size: 18px; text-decoration: underline; margin-bottom: 30px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                        td {{ border: 1px solid black; padding: 12px; font-size: 16px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; width: 40%; }}
                        .manual {{ color: blue; font-weight: bold; text-decoration: underline; }}
                        .footer {{ margin-top: 50px; display: flex; justify-content: space-between; font-weight: bold; }}
                    </style></head><body>
                    <div class="border-box">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="title">કનેક્શન રીલીઝ રિપોર્ટ (Staff Performa)</div>
                        
                        <table>
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">${{r['{col_tr}']}}</td></tr>
                            <tr><td class="label">SR Number</td><td>${{r['{col_sr}']}}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>${{r['{col_applicant}']}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${{r['{col_village}']}}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td>${{r['{col_scheme}']}}</td></tr>
                            
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નંબર</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">પ્રારંભિક રીડિંગ</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                            <tr><td class="label">સીલ નંબર</td><td class="manual">__________________________</td></tr>
                        </table>

                        <div style="margin-top:20px;"><b>નોંધ:</b> ઉપર મુજબની વિગતો સ્થળ પર ચકાસીને મેન્યુઅલી ભરવી.</div>

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
        # TABS
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Records for Installation/Release: {len(df_pending)}")
            
            if not df_pending.empty:
                st.info("The records below have a TR MR Number but are awaiting a Connection Release Date.")
                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_default_column(resizable=True, filter=True, sortable=True)
                # Adding the manual print button
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
                st.warning("No records found where TR MR No is present and Release Date is 'NULL'.")

        with t2:
            st.subheader("All Data from File")
            st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload the PPR file to generate the Staff Survey Performa.")
