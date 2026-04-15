import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

# -----------------------------------------------------------
# DATA CLEANING HELPERS
# -----------------------------------------------------------
def clean_val(val):
    s = str(val).strip().upper()
    if s in ['NULL', 'NAN', 'NONE', '<NA>', '']:
        return ""
    return str(val).strip()

# -----------------------------------------------------------
# FILE UPLOADER
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR File", type=["xls","xlsx","csv"])

if file:
    df_raw = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
    df_raw.columns = df_raw.columns.str.strip()

    # Apply global string cleaning to prevent Marshall Errors
    df_clean = df_raw.applymap(clean_val)
    df_clean = df_clean.reset_index(drop=True)

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    u_schemes = sorted([x for x in df_clean["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
    
    df_filtered = df_clean[df_clean["Name Of Scheme"].isin(sel_schemes)].copy().reset_index(drop=True)

    # -----------------------------------------------------------
    # JAVASCRIPT: THE "MANUAL ENTRY" FORM
    # -----------------------------------------------------------
    # I have added "__________" so staff can write on the paper
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
                        <tr><td class="label">SR Number</td><td>${r['SR Number'] || ''}</td></tr>
                        <tr><td class="label">ગ્રાહકનું નામ</td><td>${r['Name Of Applicant'] || ''}</td></tr>
                        <tr><td class="label">ગામ / શહેર</td><td>${r['Village Or City'] || ''}</td></tr>
                        <tr><td class="label">યોજના (Scheme)</td><td>${r['Name Of Scheme'] || ''}</td></tr>
                        
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
            st.warning("No pending records found.")
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
        # LOGIC: Show records where Status is OPEN and Release Date is empty
        # We don't care if TR MR No is NULL, because the staff will fill it manually!
        df_pending = df_filtered[
            (df_filtered["SR Status"].str.upper().str.contains("OPEN")) &
            (df_filtered["Date Of Release Conn"] == "")
        ].copy().reset_index(drop=True)
        
        st.subheader(f"Records Pending Meter Installation: {len(df_pending)}")
        st.info("Click 'Staff Form' to print the report. Staff will write the Meter Number on this paper at the site.")
        show_grid(df_pending, "grid_meter", has_print=True)

    with t2:
        show_grid(df_filtered, "grid_all")

else:
    st.info("Please upload your PPR Excel file to generate Staff Survey Forms.")
