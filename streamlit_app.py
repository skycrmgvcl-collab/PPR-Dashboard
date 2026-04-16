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

        # Force clean headers to prevent JS mapping errors
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.copy().astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'None', 'NULL', ''], "")

        # 2. Key Columns
        col_sr = "SR Number"
        col_type = "SR Type"
        col_tr_recv = "Date Of TR Recv"
        col_rel_date = "Date Of Release Conn"
        
        # Checking for necessary columns
        if col_sr not in df.columns or col_tr_recv not in df.columns:
            st.error(f"Critical columns '{col_sr}' or '{col_tr_recv}' not found!")
            st.stop()

        # 3. Sidebar Filters
        st.sidebar.header("🔍 Search & Filter")
        sr_search = st.sidebar.text_input("Quick SR Search")
        
        scheme_col = "Name Of Scheme"
        if scheme_col in df.columns:
            u_schemes = sorted([x for x in df[scheme_col].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Scheme Filter", u_schemes, default=u_schemes)
            df_filtered = df[df[scheme_col].isin(sel_schemes)]
        else:
            df_filtered = df

        if sr_search:
            df_filtered = df_filtered[df_filtered[col_sr].str.contains(sr_search, case=False)]

        # -----------------------------------------------------------
        # 4. MASTER JAVASCRIPT: MAXIMUM DATA PERFORMA
        # -----------------------------------------------------------
        js_release_form = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = '<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Master Form</button>';
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const v = (key) => (r[key] && r[key] !== 'NULL' ? r[key] : 'N/A');

                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: Arial; padding: 25px; border: 3px solid black; line-height: 1.4; }}
                        .header {{ text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 2px; }}
                        .subtitle {{ text-align: center; font-size: 15px; text-decoration: underline; margin-bottom: 15px; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        td {{ border: 1px solid black; padding: 8px; font-size: 13px; }}
                        .label {{ background-color: #f2f2f2; font-weight: bold; width: 30%; }}
                        .data {{ font-weight: bold; }}
                        .manual {{ color: blue; font-weight: bold; text-decoration: underline; }}
                        .section-head {{ background-color: #444; color: white; text-align: center; font-weight: bold; }}
                    </style></head><body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subtitle">કનેક્શન રીલીઝ અને મીટર ઇન્સ્ટોલેશન સર્વે રિપોર્ટ</div>
                        
                        <table>
                            <tr class="section-head"><td colspan="2">અરજી અને રજીસ્ટ્રેશન વિગત (Application Details)</td></tr>
                            <tr><td class="label">SR Number</td><td class="data" style="color:red; font-size:16px;">${{v('{col_sr}')}}</td></tr>
                            <tr><td class="label">SR Type</td><td class="data">${{v('{col_type}')}}</td></tr>
                            <tr><td class="label">અરજી તારીખ (App Date)</td><td class="data">${{v('Date Of Application')}}</td></tr>
                            <tr><td class="label">TR મળ્યા તારીખ</td><td class="data" style="background:#fff9c4;">${{v('{col_tr_recv}')}}</td></tr>
                            
                            <tr class="section-head"><td colspan="2">ગ્રાહકની વિગત (Consumer Info)</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td class="data">${{v('Name Of Applicant')}}</td></tr>
                            <tr><td class="label">મોબાઈલ નંબર</td><td class="data">${{v('Mobile Number')}}</td></tr>
                            <tr><td class="label">સરનામું</td><td class="data">${{v('Address1')}} ${{v('Address2')}}, ${{v('Village Or City')}}</td></tr>
                            <tr><td class="label">યોજના / કેટેગરી</td><td class="data">${{v('Name Of Scheme')}} / ${{v('Consumer Category')}}</td></tr>
                            <tr><td class="label">લોડ (Demand)</td><td class="data">${{v('Demand Load')}} ${{v('Load Uom')}} (${{v('Phase')}} Phase)</td></tr>
                            
                            <tr class="section-head"><td colspan="2">ફિલ્ડ ઇન્સ્ટોલેશન વિગત (To be filled by Line Staff)</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                            <tr><td class="label">મીટર રીડીંગ (KWh)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">સીલ નંબર (MCO/Box)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">ફીડર / લોકેશન</td><td class="manual">__________________________</td></tr>
                        </table>
                        
                        <div style="margin-top: 40px; display: flex; justify-content: space-between;">
                            <div style="text-align:center;">___________________<br>ગ્રાહકની સહી</div>
                            <div style="text-align:center;">___________________<br>કર્મચારીની સહી (Sign/Stamp)</div>
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
        # 5. DASHBOARD DISPLAY
        # -----------------------------------------------------------
        # Logic: TR Received AND Not Released
        df_pending = df_filtered[
            (df_filtered[col_tr_recv] != "") & (df_filtered[col_rel_date] == "")
        ].copy()

        st.subheader(f"📊 Pending Connection Release: {len(df_pending)}")
        
        if not df_pending.empty:
            gb = GridOptionsBuilder.from_dataframe(df_pending)
            gb.configure_default_column(resizable=True, filter=True, sortable=True)
            
            # Action button
            gb.configure_column("Print", headerName="Action", cellRenderer=js_release_form, width=150, pinned='left')
            
            # Pinned Info
            gb.configure_column(col_sr, pinned='left', width=140)
            gb.configure_column("Name Of Applicant", width=250)
            gb.configure_column(col_tr_recv, width=150)
            
            gb.configure_pagination(paginationPageSize=20)
            
            AgGrid(
                df_pending, 
                gridOptions=gb.build(), 
                height=600, 
                theme="streamlit", 
                allow_unsafe_jscode=True, 
                key="master_release_grid"
            )
        else:
            st.success("No pending TRs found for connection release.")

    except Exception as e:
        st.error(f"Critical Error: {e}")
else:
    st.info("Please upload your Excel file to generate the Master Release Performas.")
