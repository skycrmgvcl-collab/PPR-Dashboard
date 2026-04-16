import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="MGVCL SR Monitoring", layout="wide")

st.title("⚡ MGVCL: SR Release Dashboard")
st.markdown("---")

file = st.file_uploader("Upload PPR File", type=["xls","xlsx","csv"])

if file:
    try:
        # 1. Load and Clean
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)

        # Clean headers and data
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.copy().astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'None', 'NULL', ''], "")

        # 2. Define Required Columns
        col_sr = "SR Number"
        col_type = "SR Type"
        col_tr_recv = "Date Of TR Recv"
        col_rel_date = "Date Of Release Conn"

        # Check if columns exist
        missing = [c for c in [col_sr, col_type, col_tr_recv, col_rel_date] if c not in df.columns]
        if missing:
            st.error(f"Missing columns in Excel: {missing}")
            st.stop()

        # 3. Sidebar Filters
        st.sidebar.header("🔍 Filters")
        sr_search = st.sidebar.text_input("Search SR Number")
        
        scheme_col = "Name Of Scheme"
        if scheme_col in df.columns:
            u_schemes = sorted([x for x in df[scheme_col].unique() if x != ""])
            sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
            df_filtered = df[df[scheme_col].isin(sel_schemes)]
        else:
            df_filtered = df

        if sr_search:
            df_filtered = df_filtered[df_filtered[col_sr].str.contains(sr_search, case=False)]

        # -----------------------------------------------------------
        # 4. JAVASCRIPT: PRINT PERFORM (Updated Fields)
        # -----------------------------------------------------------
        js_release_form = JsCode(f"""
        class PrintRenderer {{
            init(params) {{
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = '<button style="background-color: #1565c0; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Print Form</button>';
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {{
                    const r = params.data;
                    const v = (key) => (r[key] && r[key] !== 'NULL' ? r[key] : '');

                    const html = `<html><head><meta charset="UTF-8"><style>
                        body {{ font-family: Arial; padding: 30px; border: 3px solid black; line-height: 1.6; }}
                        .header {{ text-align: center; font-size: 22px; font-weight: bold; }}
                        .subtitle {{ text-align: center; font-size: 16px; margin-bottom: 20px; text-decoration: underline; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                        td {{ border: 1px solid black; padding: 12px; font-size: 15px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; width: 35%; }}
                        .val {{ font-weight: bold; }}
                        .highlight {{ color: #d32f2f; }}
                    </style></head><body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subtitle">કનેક્શન રીલીઝ અને મીટર ઇન્સ્ટોલેશન રિપોર્ટ</div>
                        <table>
                            <tr><td class="label">SR Number</td><td class="val highlight">${{v('{col_sr}')}}</td></tr>
                            <tr><td class="label">SR Type</td><td class="val">${{v('{col_type}')}}</td></tr>
                            <tr><td class="label">Date Of TR Recv</td><td class="val">${{v('{col_tr_recv}')}}</td></tr>
                            <tr><td class="label">અરજદારનું નામ</td><td class="val">${{v('Name Of Applicant')}}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td class="val">${{v('Village Or City')}}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td class="val">${{v('Name Of Scheme')}}</td></tr>
                            <tr><td colspan="2" style="background:#eee; text-align:center; font-weight:bold;">ફિલ્ડ વિગત</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td>__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td>__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td>____ / ____ / 2026</td></tr>
                        </table>
                        <div style="margin-top: 60px; display: flex; justify-content: space-between; font-weight: bold;">
                            <span>ગ્રાહકની સહી: _______________</span>
                            <span>કર્મચારીની સહી: _______________</span>
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
        # 5. DASHBOARD FILTERING
        # -----------------------------------------------------------
        # LOGIC: TR is Received (not empty) AND Connection is NOT released (empty)
        df_pending = df_filtered[
            (df_filtered[col_tr_recv] != "") & (df_filtered[col_rel_date] == "")
        ].copy()

        st.subheader(f"📊 Release Pending (TR Received): {len(df_pending)}")
        
        if not df_pending.empty:
            gb = GridOptionsBuilder.from_dataframe(df_pending)
            gb.configure_default_column(resizable=True, filter=True, sortable=True)
            
            # Action button
            gb.configure_column("Print", headerName="Action", cellRenderer=js_release_form, width=130, pinned='left')
            
            # Pin primary info
            gb.configure_column(col_sr, pinned='left', width=140)
            gb.configure_column(col_type, width=120)
            gb.configure_column(col_tr_recv, width=150)

            gb.configure_pagination(paginationPageSize=15)
            
            AgGrid(
                df_pending, 
                gridOptions=gb.build(), 
                height=550, 
                theme="streamlit", 
                allow_unsafe_jscode=True, 
                key="sr_fixed_grid"
            )
        else:
            st.success("No pending releases for the selected filters.")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Upload your subdivision report to generate performas.")
