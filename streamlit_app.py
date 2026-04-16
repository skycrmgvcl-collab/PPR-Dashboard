import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="MGVCL Release Dashboard", layout="wide")

st.title("⚡ MGVCL: Connection Release Dashboard")
st.markdown("---")

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    try:
        # 1. Load Data
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)

        # 2. Clean Data - CRITICAL: We strip spaces from headers
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.copy().astype(str)
        
        # Replace all types of "null" with empty strings
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'None', 'NULL', 'nan', ''], "")

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
        # 4. ROBUST JAVASCRIPT (Mapping columns correctly)
        # -----------------------------------------------------------
        js_release_form = JsCode("""
        class PrintRenderer {
            init(params) {
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = '<button style="background-color: #d32f2f; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">🖨️ Release Form</button>';
                this.btn = this.eGui.querySelector('button');
                this.btn.addEventListener('click', () => {
                    const r = params.data;
                    
                    // Helper function to get data even if column names vary slightly
                    const getVal = (names) => {
                        for (let n of names) { if (r[n] && r[n] !== 'NULL') return r[n]; }
                        return '';
                    };

                    const html = `<html><head><meta charset="UTF-8"><style>
                        body { font-family: Arial, sans-serif; padding: 30px; border: 3px solid black; line-height: 1.6; }
                        .header { text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 5px; }
                        .subtitle { text-align: center; font-size: 16px; margin-bottom: 20px; text-decoration: underline; }
                        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                        td { border: 1px solid black; padding: 12px; font-size: 15px; }
                        .label { background-color: #f5f5f5; font-weight: bold; width: 35%; }
                        .val { font-weight: bold; }
                        .manual { color: blue; font-weight: bold; text-decoration: underline; }
                    </style></head><body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subtitle">કનેક્શન રીલીઝ રિપોર્ટ (Release Performa)</div>
                        <table>
                            <tr><td class="label">TR / MR No</td><td class="val" style="color:red;">${getVal(['TR MR No', 'TR_MR_NO', 'TR NO'])}</td></tr>
                            <tr><td class="label">અરજદારનું નામ</td><td class="val">${getVal(['Name Of Applicant', 'NAME', 'APPLICANT_NAME'])}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td class="val">${getVal(['Village Or City', 'VILLAGE', 'CITY'])}</td></tr>
                            <tr><td class="label">SR Number</td><td class="val">${getVal(['SR Number', 'SR_NO', 'SR'])}</td></tr>
                            <tr><td class="label">યોજના (Scheme)</td><td class="val">${getVal(['Name Of Scheme', 'SCHEME'])}</td></tr>
                            <tr><td class="label">ગ્રાહક કેટેગરી</td><td class="val">${getVal(['Consumer Category', 'CATEGORY'])}</td></tr>
                            <tr><td class="label">લોડ (Load)</td><td class="val">${getVal(['Demand Load', 'LOAD'])} ${getVal(['Load Uom', 'UOM'])}</td></tr>
                            <tr><td colspan="2" style="background: #eee; font-weight: bold; text-align: center;">ફિલ્ડ વિગત (To be filled by staff)</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નંબર</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">મીટર મેક (Make)</td><td class="manual">__________________________</td></tr>
                            <tr><td class="label">ઇન્સ્ટોલેશન તારીખ</td><td class="manual">____ / ____ / 2026</td></tr>
                        </table>
                        <div style="margin-top: 50px; display: flex; justify-content: space-between;">
                            <span>ગ્રાહકની સહી: _______________</span>
                            <span>સ્ટાફની સહી: _______________</span>
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
        # 5. TABS
        # -----------------------------------------------------------
        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            col_tr = "TR MR No"
            col_rel_date = "Date Of Release Conn"
            
            if col_tr in df.columns and col_rel_date in df.columns:
                # Logic: TR Number is present, but Release Date is empty
                df_release = df_filtered[
                    (df_filtered[col_tr] != "") & (df_filtered[col_rel_date] == "")
                ].copy()
                
                st.subheader(f"Total Pending: {len(df_release)}")
                
                if not df_release.empty:
                    gb = GridOptionsBuilder.from_dataframe(df_release)
                    gb.configure_default_column(resizable=True, filter=True, sortable=True)
                    gb.configure_column("Print", headerName="Action", cellRenderer=js_release_form, width=140, pinned='left')
                    gb.configure_pagination(paginationPageSize=15)
                    
                    AgGrid(
                        df_release, 
                        gridOptions=gb.build(), 
                        height=500, 
                        theme="streamlit", 
                        allow_unsafe_jscode=True, 
                        key="release_grid"
                    )
                else:
                    st.success("No records found for release.")
            else:
                st.error(f"Excel is missing required columns. Found: {list(df.columns)}")

        with t2:
            st.dataframe(df_filtered)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload your PPR file.")
