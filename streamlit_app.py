import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

# -----------------------------------------------------------
# DATA CLEANING HELPERS
# -----------------------------------------------------------
def clean_dataframe(df):
    # Convert all data to string and clean whitespace/case
    df = df.astype(str).apply(lambda x: x.str.strip().str.upper())
    # Standardize null-like strings to empty strings
    null_values = ['NULL', 'NAN', 'NONE', '<NA>', 'N/A', '']
    for val in null_values:
        df = df.replace(val, "")
    return df

# -----------------------------------------------------------
# FILE UPLOADER
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        # Load file with robust settings for messy CSVs
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # Clean columns and data
        df_raw.columns = df_raw.columns.str.strip()
        df_clean = clean_dataframe(df_raw)
        df_clean = df_clean.reset_index(drop=True)

        # Sidebar Filters
        st.sidebar.header("🔍 Filters")
        scheme_col = "Name Of Scheme"
        if scheme_col in df_clean.columns:
            u_schemes = sorted([x for x in df_clean[scheme_col].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
            df_filtered = df_clean[df_clean[scheme_col].isin(sel_schemes)].copy().reset_index(drop=True)
        else:
            st.error(f"Column '{scheme_col}' not found.")
            df_filtered = df_clean

        # -----------------------------------------------------------
        # JAVASCRIPT: PRINT PERFORMAS
        # -----------------------------------------------------------
        render_print_button = JsCode("""
        class PrintRenderer {
            init(params) {
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #004d40; color: white; border: none; 
                    border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Release Form</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body { font-family: 'Arial'; padding: 30px; line-height: 1.4; }
                        .border-box { border: 2px solid black; padding: 20px; }
                        .header { text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 5px; }
                        .title { text-align: center; font-size: 16px; text-decoration: underline; margin-bottom: 20px; }
                        table { width: 100%; border-collapse: collapse; }
                        td { border: 1px solid black; padding: 10px; font-size: 14px; }
                        .label { background-color: #f0f0f0; font-weight: bold; width: 35%; }
                        .manual { color: blue; font-weight: bold; }
                        .footer { margin-top: 40px; display: flex; justify-content: space-between; }
                    </style></head><body>
                    <div class="border-box">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="title">કનેક્શન રીલીઝ રિપોર્ટ (Release Pending Performa)</div>
                        <table>
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">\${r['TR MR No'] || 'N/A'}</td></tr>
                            <tr><td class="label">SR Number</td><td>\${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>\${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>\${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td>\${r['Name Of Scheme'] || ''}</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નંબર</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">સીલ નંબર</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
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
                });
            }
            getGui() { return this.eGui; }
        }
        """)

        def show_grid(data, key, has_print=False):
            if data.empty:
                st.warning("No records match these criteria.")
                return
            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_default_column(resizable=True, filter=True, sortable=True)
            if has_print:
                gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=140, pinned='left')
            gb.configure_pagination(paginationPageSize=15)
            AgGrid(data, gridOptions=gb.build(), height=500, theme="streamlit", allow_unsafe_jscode=True, key=key)

        # -----------------------------------------------------------
        # MAIN TABS
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            # logic: TR MR No is NOT empty AND Date Of Release Conn IS empty
            col_tr = "TR MR No"
            col_date = "Date Of Release Conn"

            if col_tr in df_filtered.columns and col_date in df_filtered.columns:
                df_release_pending = df_filtered[
                    (df_filtered[col_tr] != "") & 
                    (df_filtered[col_date] == "")
                ].copy().reset_index(drop=True)

                st.subheader(f"Total Release Pending: {len(df_release_pending)}")
                st.info("These records have a TR MR Number but no Release Date. Print the Performa for field verification.")
                show_grid(df_release_pending, "release_grid", has_print=True)
            else:
                st.error(f"Required columns missing: Ensure file has '{col_tr}' and '{col_date}'")

        with t2:
            st.subheader("All Records")
            show_grid(df_filtered, "all_data_grid")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload the PPR file to start.")
