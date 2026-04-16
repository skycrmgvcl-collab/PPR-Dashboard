import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="MGVCL Monitoring Dashboard", layout="wide")

st.title("⚡ Subdivision SR & Installation Dashboard")
st.markdown("---")

# -----------------------------------------------------------
# DATA LOADING & ROBUST CLEANING
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Read Data
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file, encoding="utf-8-sig", on_bad_lines='skip')
    else:
        df_raw = pd.read_excel(file)

    # Clean data: Replace NULL/nan and fix whitespace
    df_raw.columns = df_raw.columns.str.strip()
    df = df_raw.copy().astype(str)
    for col in df.columns:
        df[col] = df[col].str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT', 'NaT', ''], "")

    # Sidebar Filters
    st.sidebar.header("🔍 Global Filters")
    
    # Scheme Filter
    scheme_col = "Name Of Scheme"
    if scheme_col in df.columns:
        u_schemes = sorted([x for x in df[scheme_col].unique() if x != ""])
        sel_schemes = st.sidebar.multiselect("Select Scheme", u_schemes, default=u_schemes)
    else:
        sel_schemes = []

    # Apply Base Filter
    df_filtered = df[df[scheme_col].isin(sel_schemes)] if sel_schemes else df

    # -----------------------------------------------------------
    # JAVASCRIPT: RELEASE FORM (For Installation)
    # -----------------------------------------------------------
    js_release_form = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #d32f2f; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold; width: 100%;">
                🖨️ Release Form
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const htmlContent = `
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            @page { size: A4; margin: 10mm; }
                            body { font-family: 'Arial', sans-serif; padding: 20px; border: 3px solid black; }
                            .header { text-align: center; font-size: 22px; font-weight: bold; }
                            .title { text-align: center; font-size: 18px; text-decoration: underline; margin: 20px 0; }
                            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                            td { border: 1px solid black; padding: 12px; font-size: 16px; }
                            .label { background-color: #f5f5f5; font-weight: bold; width: 35%; }
                            .fill { color: blue; font-weight: bold; }
                        </style>
                    </head>
                    <body onload="window.print()">
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="title">કનેક્શન રીલીઝ રિપોર્ટ (Release Performa)</div>
                        <table>
                            <tr><td class="label">TR / MR No</td><td style="color:red; font-weight:bold;">${r['TR MR No'] || 'NOT ASSIGNED'}</td></tr>
                            <tr><td class="label">અરજદારનું નામ</td><td>${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">SR Number</td><td>${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">મીટર નંબર</td><td class="fill">__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td class="fill">____ / ____ / 2026</td></tr>
                        </table>
                    </body>
                    </html>
                `;
                var w = window.open('', '_blank');
                w.document.write(htmlContent);
                w.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    # -----------------------------------------------------------
    # GRID HELPER
    # -----------------------------------------------------------
    def show_dashboard_grid(data, key, button_type=None):
        if data.empty:
            st.warning("No records found for this stage.")
            return
        
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        if button_type == "release":
            gb.configure_column("Print", headerName="Action", cellRenderer=js_release_form, width=140, pinned='left')
        
        gb.configure_pagination(paginationPageSize=15)
        AgGrid(data, gridOptions=gb.build(), height=500, theme="streamlit", 
               allow_unsafe_jscode=True, key=key)

    # -----------------------------------------------------------
    # TABS SYSTEM
    # -----------------------------------------------------------
    t1, t2, t3 = st.tabs(["🚀 Release Pending", "📋 Survey Pending", "📁 Full Database"])

    with t1:
        # LOGIC: TR MR No is NOT NULL and Date of Release IS NULL
        col_tr = "TR MR No"
        col_rel_date = "Date Of Release Conn"
        
        if col_tr in df.columns and col_rel_date in df.columns:
            df_release = df_filtered[
                (df_filtered[col_tr] != "") & 
                (df_filtered[col_rel_date] == "")
            ].copy()
            
            st.subheader(f"Total Release Pending: {len(df_release)}")
            st.info("These consumers have TR MR Numbers but the connection is not yet released.")
            show_dashboard_grid(df_release, "rel_grid", button_type="release")
        else:
            st.error(f"Required columns '{col_tr}' or '{col_rel_date}' missing from file.")

    with t2:
        # LOGIC: Survey Category is empty
        col_survey = "Survey Category"
        if col_survey in df.columns:
            df_survey = df_filtered[df_filtered[col_survey] == ""].copy()
            st.subheader(f"Total Survey Pending: {len(df_survey)}")
            show_dashboard_grid(df_survey, "survey_grid")
        else:
            st.write("Column 'Survey Category' not found for survey tracking.")

    with t3:
        st.subheader("Complete Records")
        show_dashboard_grid(df_filtered, "full_grid")

else:
    st.info("Please upload the subdivision PPR/SR report file.")
