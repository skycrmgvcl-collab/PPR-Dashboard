import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="MGVCL PPR Dashboard", layout="wide")

# -----------------------------------------------------------
# 1. CSS FOR PRINTING (The Performa Design)
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
# 2. FILE LOADING & CLEANING
# -----------------------------------------------------------
st.title("⚡ MGVCL: Meter Installation Dashboard")
file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')

        # Clean Columns
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        col_scheme = "Name Of Scheme"

        # -----------------------------------------------------------
        # 3. SIDEBAR FILTERS
        # -----------------------------------------------------------
        st.sidebar.header("🔍 Filter Options")
        if col_scheme in df.columns:
            schemes = sorted(df[col_scheme].unique())
            selected_schemes = st.sidebar.multiselect("Select Scheme", schemes, default=schemes)
            df = df[df[col_scheme].isin(selected_schemes)]

        # -----------------------------------------------------------
        # 4. FILTERING LOGIC
        # -----------------------------------------------------------
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        t1, t2 = st.tabs(["🚀 Release Pending List", "📁 All Data"])

        with t1:
            st.subheader(f"Total Pending for Installation: {len(df_pending)}")
            
            if not df_pending.empty:
                # We create a "Print" link for each row
                # This doesn't use JavaScript - it uses simple URL encoding
                def make_print_link(row_idx):
                    return f"Print_Form_{row_idx}"

                df_pending["Action"] = df_pending.index.map(make_print_link)

                # DISPLAY THE TABLE
                # Using Streamlit's native data_editor which is bug-free
                event = st.dataframe(
                    df_pending,
                    column_config={
                        "Action": st.column_config.ButtonColumn(
                            "Print Performa",
                            help="Click to generate print preview",
                            key="print_btn"
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="single_row"
                )

                # -----------------------------------------------------------
                # 5. THE PRINT TRIGGER
                # -----------------------------------------------------------
                # When a user clicks a row, we show the print button for that specific record
                selection = event.selection.rows
                if selection:
                    idx = selection[0]
                    selected_row = df_pending.iloc[idx]
                    
                    st.success(f"Selected: {selected_row[col_tr]} - {selected_row.get('Name Of Applicant', '')}")
                    
                    # Generate the HTML
                    html_content = get_print_html(selected_row, col_tr, col_scheme)
                    b64 = base64.b64encode(html_content.encode()).decode()
                    
                    # Create a real browser-trigger for the print
                    href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;"><button style="background-color: #d32f2f; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold; width: 100%;">🖨️ CLICK HERE TO OPEN PRINT PREVIEW</button></a>'
                    st.markdown(href, unsafe_allow_unsafe_html=True)
                    st.info("The button above will open the Performa in a new tab and start the printer automatically.")

            else:
                st.warning("No records found matching criteria (TR No present, Date NULL).")

        with t2:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload your PPR file to begin.")
