import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

# -----------------------------------------------------------
# DATA CLEANING HELPERS
# -----------------------------------------------------------
def clean_dataframe(df):
    """
    Standardizes the dataframe: strips whitespace, converts to uppercase,
    and handles various 'null' string representations.
    """
    # Convert all data to string and clean
    df = df.astype(str).apply(lambda x: x.str.strip().str.upper())
    # Replace null-like strings with empty strings
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
        # Handle different file types with robust error settings
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            # on_bad_lines='skip' prevents the ParserError if rows have extra commas
            # encoding='latin1' handles special characters better than default utf-8
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # Clean column names
        df_raw.columns = df_raw.columns.str.strip()
        
        # Apply global cleaning
        df_clean = clean_dataframe(df_raw)
        df_clean = df_clean.reset_index(drop=True)

        # Sidebar Filters
        st.sidebar.header("🔍 Filters")
        if "Name Of Scheme" in df_clean.columns:
            u_schemes = sorted([x for x in df_clean["Name Of Scheme"].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
            df_filtered = df_clean[df_clean["Name Of Scheme"].isin(sel_schemes)].copy().reset_index(drop=True)
        else:
            st.error("Column 'Name Of Scheme' not found in file.")
            df_filtered = df_clean

        # -----------------------------------------------------------
        # JAVASCRIPT: THE "MANUAL ENTRY" FORM
        # -----------------------------------------------------------
        render_print_button = JsCode("""
        class PrintRenderer {
            init(params) {
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `<button style="background-color: #e65100; color: white; border: none; 
                    border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Staff Form</button>`;
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {
                    const r = params.data;
                    const html = `<html><head><meta charset="UTF-8"><style>
                        body { font-family: 'Arial'; padding: 30px; line-height: 1.6; }
                        .border-box { border: 3px solid black; padding: 20px; }
                        .header { text-align: center; font-weight: bold; font-size: 22px; }
                        .title { text-align: center; font-size: 18px; text-decoration: underline; margin-bottom: 30px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                        td { border: 1px solid black; padding: 12px; font-size: 16px; }
                        .label { background-color: #f5f5f5; font-weight: bold; width: 40%; }
                        .manual-field { font-weight: bold; color: blue; text-decoration: underline; }
                        .footer { margin-top: 50px; display: flex; justify-content: space-between; font-weight: bold; }
                    </style></head><body>
                    <div class="border-box">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="title">મીટર ઇન્સ્ટોલેશન અને સર્વે રિપોર્ટ (Staff Copy)</div>
                        <table>
                            <tr><td class="label">SR Number</td><td>\${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>\${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>\${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td>\${r['Name Of Scheme'] || ''}</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નંબર</td><td class="manual-field">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual-field">__________________________</td></tr>
                            <tr><td class="label">પ્રારંભિક રીડિંગ (Initial Reading)</td><td class="manual-field">__________________________</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલેશન તારીખ</td><td class="manual-field">____ / ____ / 2026</td></tr>
                            <tr><td class="label">સીલ નંબર (Seal No)</td><td class="manual-field">__________________________</td></tr>
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
                });
            }
            getGui() { return this.eGui; }
        }
        """)

        def show_grid(data, key, has_print=False):
            if data.empty:
                st.warning("No records found for the current selection.")
                return
            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_default_column(resizable=True, filter=True, sortable=True)
            if has_print:
                gb.configure_column("Print", headerName="Staff Form", cellRenderer=render_print_button, width=120, pinned='left')
            gb.configure_pagination(paginationPageSize=15)
            AgGrid(data, gridOptions=gb.build(), height=450, theme="streamlit", allow_unsafe_jscode=True, key=key)

        # -----------------------------------------------------------
        # TABS
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["📋 Pending for Meter Installation", "📁 All Data"])

        with t1:
            # Logic to filter pending records
            # Ensure columns exist before filtering to prevent KeyErrors
            req_cols = ["SR Status", "Date Of Release Conn"]
            if all(col in df_filtered.columns for col in req_cols):
                df_pending = df_filtered[
                    (df_filtered["SR Status"].str.contains("OPEN")) &
                    (df_filtered["Date Of Release Conn"] == "")
                ].copy().reset_index(drop=True)
                
                st.subheader(f"Records Pending Meter Installation: {len(df_pending)}")
                st.info("Click 'Staff Form' to print the report for field use.")
                show_grid(df_pending, "grid_meter", has_print=True)
            else:
                st.error(f"Missing required columns for filtering: {req_cols}")

        with t2:
            show_grid(df_filtered, "grid_all")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload your PPR Excel or CSV file to generate Staff Survey Forms.")
