import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="MGVCL Final Dashboard", layout="wide")

st.title("⚡ MGVCL: Connection Release Dashboard (Full Data)")
st.markdown("---")

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    try:
        # 1. Load Data
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)

        # 2. PRO CLEANING: Standardize column names for JavaScript
        # This removes spaces and special characters that break JS variables
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        df = df_raw.copy().astype(str)
        for col in df.columns:
            # Replace all variations of 'empty' with a standard empty string
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'None', 'NULL', ''], "")

        # 3. Sidebar Filter
        st.sidebar.header("🔍 Filters")
        scheme_col = "Name Of Scheme"
        if scheme_col in df.columns:
            u_schemes = sorted([x for x in df[scheme_col].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Select Scheme", u_schemes, default=u_schemes)
            df_filtered = df[df[scheme_col].isin(sel_schemes)]
        else:
            df_filtered = df

        # -----------------------------------------------------------
        # 4. MASTER JAVASCRIPT: Mapping Every Possible Field
        # -----------------------------------------------------------
        js_release_form = JsCode("""
        class PrintRenderer {
            init(params) {
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = '<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Release Form</button>';
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {
                    const r = params.data;
                    
                    // Fail-safe helper: returns value or empty string
                    const v = (key) => (r[key] && r[key] !== 'NULL' ? r[key] : '');

                    const html = `<html><head><meta charset="UTF-8"><style>
                        body { font-family: Arial, sans-serif; padding: 30px; border: 3px solid black; line-height: 1.4; }
                        .header { text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 2px; }
                        .subtitle { text-align: center; font-size: 15px; margin-bottom: 15px; text-decoration: underline; }
                        table { width: 100%; border-collapse: collapse; margin-top: 5px; }
                        td { border: 1px solid black; padding: 10px; font-size: 14px; }
                        .label { background-color: #f2f2f2; font-weight: bold; width: 30%; }
                        .data { font-weight: bold; color: #000; }
                        .manual { color: blue; font-weight: bold; text-decoration: underline; }
                        .footer { margin-top: 40px; display: flex; justify-content: space-between; }
                    </style></head><body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subtitle">કનેક્શન રીલીઝ રિપોર્ટ (Release Performa)</div>
                        
                        <table>
                            <tr><td class="label">TR / MR No</td><td class="data" style="color:red; font-size:16px;">${v('TR MR No')}</td></tr>
                            <tr><td class="label">SR Number</td><td class="data">${v('SR Number')}</td></tr>
                            <tr><td class="label">અરજદારનું નામ</td><td class="data">${v('Name Of Applicant')}</td></tr>
                            <tr><td class="label">મોબાઈલ નંબર</td><td class="data">${v('Mobile Number')}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td class="data">${v('Village Or City')}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td class="data">${v('Name Of Scheme')}</td></tr>
                            <tr><td class="label">કેટેગરી</td><td class="data">${v('Consumer Category')}</td></tr>
                            <tr><td class="label">લોડ (Load)</td><td class="data">${v('Demand Load')} ${v('Load Uom')}</td></tr>
                            <tr><td class="label">સરનામું</td><td class="data">${v('Address1')} ${v('Address2')}</td></tr>
                            
                            <tr><td colspan="2" style="background: #ddd; font-weight: bold; text-align: center;">ફિલ્ડ ઇન્સ્ટોલેશન વિગત (Office Use Only)</td></tr>
                            
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                            <tr><td class="label">મીટર રીડિંગ (Initial)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">સીલ નંબર</td><td class="manual">__________________________</td></tr>
                        </table>
                        
                        <div class="footer">
                            <div>ગ્રાહકની સહી: ________________</div>
                            <div>લાઇનમેન/સ્ટાફ સહી: ________________</div>
                        </div>
                    </body></html>`;
                    
                    const w = window.open('', '_blank');
                    w.document.write(html);
                    w.document.close();
                });
            }
            getGui() { return this.eGui; }
        }
        """)

        # -----------------------------------------------------------
        # 5. DATA LOGIC & DISPLAY
        # -----------------------------------------------------------
        col_tr = "TR MR No"
        col_rel_date = "Date Of Release Conn"

        if col_tr in df.columns and col_rel_date in df.columns:
            # Show records where TR exists but Release Date is blank
            df_release = df_filtered[
                (df_filtered[col_tr] != "") & (df_filtered[col_rel_date] == "")
            ].copy()
            
            st.subheader(f"📊 Release Pending Records: {len(df_release)}")
            
            if not df_release.empty:
                gb = GridOptionsBuilder.from_dataframe(df_release)
                gb.configure_default_column(resizable=True, filter=True, sortable=True)
                
                # Add the Action/Print column
                gb.configure_column(
                    "Print", 
                    headerName="Action", 
                    cellRenderer=js_release_form, 
                    width=140, 
                    pinned='left'
                )
                
                gb.configure_pagination(paginationPageSize=15)
                
                AgGrid(
                    df_release, 
                    gridOptions=gb.build(), 
                    height=550, 
                    theme="streamlit", 
                    allow_unsafe_jscode=True, 
                    key="release_grid_v2"
                )
            else:
                st.success("✅ No pending releases found!")
        else:
            st.error(f"Required columns missing! Make sure your file has: '{col_tr}' and '{col_rel_date}'")

    except Exception as e:
        st.error(f"Fatal Error: {e}")
else:
    st.info("👋 Welcome! Please upload your subdivision PPR Excel file to start generating Release Performas.")
