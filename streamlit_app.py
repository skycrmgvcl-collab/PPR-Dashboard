import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="MGVCL PPR Dashboard", layout="wide")

# -----------------------------------------------------------
# 1. PERFORMA GENERATOR
# -----------------------------------------------------------
def get_print_html(row, col_tr, col_scheme):
    """Generates the HTML Performa for a specific row"""
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Arial'; padding: 30px; line-height: 1.6; }}
            .border-box {{ border: 4px solid black; padding: 25px; }}
            .header {{ text-align: center; font-weight: bold; font-size: 24px; margin-bottom: 5px; }}
            .sub-header {{ text-align: center; font-size: 18px; text-decoration: underline; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ border: 1px solid black; padding: 15px; font-size: 18px; }}
            .label {{ background-color: #f2f2f2; font-weight: bold; width: 40%; }}
            .manual-entry {{ color: blue; font-weight: bold; }}
            .footer {{ margin-top: 60px; display: flex; justify-content: space-between; font-weight: bold; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="border-box">
            <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
            <div class="sub-header">મીટર ઇન્સ્ટોલેશન અને સર્વે રિપોર્ટ (Release Pending)</div>
            <table>
                <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">{row[col_tr]}</td></tr>
                <tr><td class="label">ગ્રાહકનું નામ (Applicant)</td><td>{row.get('Name Of Applicant', '')}</td></tr>
                <tr><td class="label">ગામ / શહેર (Village/City)</td><td>{row.get('Village Or City', '')}</td></tr>
                <tr><td class="label">યોજના (Scheme)</td><td>{row.get(col_scheme, '')}</td></tr>
                <tr><td class="label">ઇન્સ્ટોલ કરેલ મીટર નં.</td><td class="manual-entry">__________________________</td></tr>
                <tr><td class="label">મીટર મેક (Make)</td><td class="manual-entry">__________________________</td></tr>
                <tr><td class="label">રીલીઝ તારીખ</td><td class="manual-entry">____ / ____ / 2026</td></tr>
            </table>
            <div class="footer">
                <span>ગ્રાહકની સહી: ______________</span>
                <span>કર્મચારીની સહી: ______________</span>
            </div>
        </div>
    </body>
    </html>
    """

# -----------------------------------------------------------
# 2. FILE LOADING & SIDEBAR
# -----------------------------------------------------------
st.title("⚡ MGVCL: Meter Installation Dashboard")
file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        # Load File
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')

        # Clean Columns and Data
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"

        # Sidebar Filters
        st.sidebar.header("🔍 Filters")
        if col_scheme in df.columns:
            schemes = sorted(df[col_scheme].unique())
            selected_schemes = st.sidebar.multiselect("Select Scheme", schemes, default=schemes)
            df = df[df[col_scheme].isin(selected_schemes)]

        # -----------------------------------------------------------
        # 3. FILTERING LOGIC
        # -----------------------------------------------------------
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        t1, t2 = st.tabs(["🚀 Release Pending List", "📁 All Data"])

        with t1:
            st.subheader(f"Total Pending: {len(df_pending)}")
            
            if not df_pending.empty:
                st.info("💡 **How to Print:** Click the radio button next to a row to select it, then click the red button that appears below.")
                
                # Using st.dataframe for the table
                # We add a temporary column for selection identification
                df_display = df_pending.copy()
                df_display.insert(0, "Select", "⭕")

                # Show the table
                st.dataframe(df_display, use_container_width=True)

                # Selection Box
                # Since we can't put a button in a row in old Streamlit versions easily,
                # we use a Selectbox tied to the TR MR No
                selection_list = df_pending[col_tr].tolist()
                selected_tr = st.selectbox("👉 Choose a TR MR Number to Print", selection_list)

                if selected_tr:
                    selected_row = df_pending[df_pending[col_tr] == selected_tr].iloc[0]
                    
                    st.success(f"Selected: {selected_row[col_tr]} for {selected_row.get('Name Of Applicant', 'N/A')}")
                    
                    # Generate the HTML and encode for browser safety
                    html_content = get_print_html(selected_row, col_tr, col_scheme)
                    b64 = base64.b64encode(html_content.encode()).decode()
                    
                    # Large Print Trigger Button
                    href = f'''
                    <a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;">
                        <div style="
                            background-color: #d32f2f; 
                            color: white; 
                            padding: 15px; 
                            text-align: center; 
                            border-radius: 10px; 
                            font-size: 20px; 
                            font-weight: bold; 
                            cursor: pointer;
                            border: 2px solid #b71c1c;
                            margin-top: 10px;">
                            🖨️ CLICK HERE TO PRINT PERFORMAS
                        </div>
                    </a>
                    '''
                    st.markdown(href, unsafe_allow_unsafe_html=True)
                    st.caption("Note: Clicking the button opens a new tab. Please allow pop-ups if blocked.")

            else:
                st.warning("No records found where TR No is assigned but Date is NULL.")

        with t2:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload your PPR file.")
