import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="MGVCL SR Master Dashboard", layout="wide")

st.title("⚡ MGVCL: Connection Release Master Dashboard")
st.markdown("---")

file = st.file_uploader("Upload PPR File", type=["xls","xlsx","csv"])

if file:
    try:
        # 1. Load and Standardize Headers
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)

        # Clean headers to ensure JavaScript can map them
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.copy().astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'None', 'NULL', ''], "")

        # 2. Define Key Logic Columns
        col_sr = "SR Number"
        col_type = "SR Type"
        col_tr_recv = "Date Of TR Recv"
        col_rel_date = "Date Of Release Conn"
        scheme_col = "Name Of Scheme"
        
        # 3. Sidebar Filters
        st.sidebar.header("🔍 Search & Filter")
        sr_search = st.sidebar.text_input("Quick SR Search")
        
        # Scheme Filter Logic
        if scheme_col in df.columns:
            u_schemes = sorted([x for x in df[scheme_col].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Scheme Filter", u_schemes, default=u_schemes)
            df_filtered = df[df[scheme_col].isin(sel_schemes)]
        else:
            sel_schemes = [] # Fallback for key generation
            df_filtered = df

        # SR Search Logic
        if sr_search:
            df_filtered = df_filtered[df_filtered[col_sr].str.contains(sr_search, case=False)]

        # -----------------------------------------------------------
        # 4. MASTER JAVASCRIPT: PRINT FORM LOGIC
        # -----------------------------------------------------------
        js_release_form = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = '<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>';
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const v = (key) => (r[key] && r[key] !== 'NULL' ? r[key] : '---');

                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; border: 2px solid black; line-height: 1.3; }}
                        .header {{ text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 2px; }}
                        .subtitle {{ text-align: center; font-size: 16px; text-decoration: underline; margin-bottom: 15px; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        td {{ border: 1px solid black; padding: 10px; font-size: 14px; height: 35px; }}
                        .label {{ background-color: #f2f2f2; font-weight: bold; width: 35%; }}
                        .data {{ font-weight: bold; }}
                        .section-head {{ background-color: #444; color: white; text-align: center; font-weight: bold; font-size: 15px; }}
                        .highlight {{ color: red; font-size: 17px; }}
                    </style></head><body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subtitle">કનેક્શન રીલીઝ અને મીટર ઇન્સ્ટોલેશન રિપોર્ટ</div>
                        
                        <table>
                            <tr class="section-head"><td colspan="2">અરજી અને રજીસ્ટ્રેશન વિગત (Office Record)</td></tr>
                            <tr><td class="label">SR Number</td><td class="data highlight">${{v('{col_sr}')}}</td></tr>
                            <tr><td class="label">SR Type / Category</td><td class="data">${{v('{col_type}')}} / ${{v('Consumer Category')}}</td></tr>
                            <tr><td class="label">Date Of TR Recv</td><td class="data">${{v('{col_tr_recv}')}}</td></tr>
                            <tr><td class="label">Application Date</td><td class="data">${{v('RC Date')}}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td class="data">${{v('Name Of Scheme')}}</td></tr>
                            
                            <tr class="section-head"><td colspan="2">ગ્રાહક અને સ્થળ વિગત (Consumer Info)</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td class="data">${{v('Name Of Applicant')}}</td></tr>
                            <tr><td class="label">મોબાઈલ નંબર</td><td class="data">${{v('Mobile Number')}}</td></tr>
                            <tr><td class="label">સરનામું</td><td class="data">${{v('Address1')}} ${{v('Address2')}}, ${{v('Village Or City')}}</td></tr>
                            <tr><td class="label">લોડ (Demand)</td><td class="data">${{v('Demand Load')}} ${{v('Load Uom')}} (${{v('Phase')}} Phase)</td></tr>
                            
                            <tr class="section-head"><td colspan="2">ઇન્સ્ટોલેશન વિગત (Field Entry)</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td></td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td></td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="data">____ / ____ / 2026</td></tr>
                            <tr><td class="label">મીટર રીડિંગ (KWh)</td><td></td></tr>
                            <tr><td class="label">સીલ નંબર (MCO/Box)</td><td></td></tr>
                            <tr><td class="label">ફીડર / લોકેશન / પોલ નં.</td><td></td></tr>
                        </table>
                        
                        <div style="margin-top: 40px; display: flex; justify-content: space-between;">
                            <div style="text-align:center;">___________________<br>ગ્રાહકની સહી</div>
                            <div style="text-align:center;">___________________<br>કર્મચારીની સહી</div>
                        </div>
                    </body></html>`;
                    const w = window.open('', '_blank');
                    w.document.write(html);
                    w.document.close();
                }});
            }}
            getGui() {{ return this.eGui; }}
        }}
        """)

        # -----------------------------------------------------------
        # 5. DASHBOARD FILTERING & DISPLAY
        # -----------------------------------------------------------
        if col_tr_recv in df.columns and col_rel_date in df.columns:
            # Filter for Pending cases
            df_pending = df_filtered[
                (df_filtered[col_tr_recv] != "") & (df_filtered[col_rel_date] == "")
            ].copy()

            st.subheader(f"📊 Total Pending Releases: {len(df_pending)}")
            
            if not df_pending.empty:
                gb = GridOptionsBuilder.from_dataframe(df_pending)
                gb.configure_default_column(resizable=True, filter=True, sortable=True)
                
                # Action Column Configuration
                gb.configure_column("Print", headerName="Action", cellRenderer=js_release_form, width=140, pinned='left')
                gb.configure_column(col_sr, pinned='left', width=140)
                
                gb.configure_pagination(paginationPageSize=20)
                
                # --- KEY FIX: DYNAMIC KEY ---
                # This key changes whenever the filters change, forcing the grid to refresh.
                dynamic_key = f"grid_{len(df_pending)}_{len(sel_schemes)}_{sr_search}"
                
                AgGrid(
                    df_pending, 
                    gridOptions=gb.build(), 
                    height=600, 
                    theme="streamlit", 
                    allow_unsafe_jscode=True, 
                    key=dynamic_key
                )
            else:
                st.success("No pending cases found for the selected filters.")
        else:
            st.error(f"Missing essential headers: Make sure the file has '{col_tr_recv}' and '{col_rel_date}'.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Welcome! Please upload your PPR Excel file in the sidebar to begin.")
