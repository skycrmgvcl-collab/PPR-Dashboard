import streamlit as st
import pandas as pd

st.set_page_config(page_title="PPR Staff Survey Dashboard", layout="wide")
st.title("⚡ MGVCL: Meter Installation & Survey Dashboard")

file = st.file_uploader("Upload PPR File", type=["xls", "xlsx", "csv"])

if file:
    try:
        # 1. Load File
        if file.name.endswith(('xlsx', 'xls')):
            df_raw = pd.read_excel(file)
        else:
            df_raw = pd.read_csv(file, encoding='latin1', on_bad_lines='skip', engine='python')

        # 2. Clean Data (Force everything to strings to avoid NaT/NaN issues)
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        df = df_raw.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip().replace(['nan', 'NaN', 'NaT', 'NAT', '<NA>', 'None', ''], 'NULL')

        col_tr = "TR MR No"
        col_date = "Date Of Release Conn"
        
        # 3. Filter Data
        mask = (df[col_tr].str.upper() != "NULL") & (df[col_date].str.upper() == "NULL")
        df_pending = df[mask].copy().reset_index(drop=True)

        t1, t2 = st.tabs(["🚀 Release Pending", "📁 Full Database"])

        with t1:
            st.subheader(f"Total Pending: {len(df_pending)}")
            
            if len(df_pending) > 0:
                # STEP 4: SELECTION SYSTEM (Bypasses the AgGrid JSON Bug)
                st.info("Step 1: Select a Consumer from the list below. Step 2: Click the Print button.")
                
                # Create a label for the dropdown
                df_pending["Selection_Label"] = df_pending[col_tr] + " - " + df_pending["Name Of Applicant"]
                
                selected_label = st.selectbox("Select Record to Print", df_pending["Selection_Label"].tolist())
                selected_row = df_pending[df_pending["Selection_Label"] == selected_label].iloc[0]

                # STEP 5: THE PRINT ENGINE (Using standard HTML component)
                # This opens the print dialog as soon as the button is clicked
                print_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Arial'; padding: 20px; }}
                        .box {{ border: 3px solid black; padding: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        td {{ border: 1px solid black; padding: 12px; font-size: 16px; }}
                        .label {{ background-color: #f5f5f5; font-weight: bold; width: 40%; }}
                    </style>
                </head>
                <body>
                    <div class="box">
                        <h2 style="text-align:center;">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
                        <h3 style="text-align:center; text-decoration:underline;">મીટર ઇન્સ્ટોલેશન સર્વે રિપોર્ટ</h3>
                        <table>
                            <tr><td class="label">TR / MR Number</td><td style="color:red; font-weight:bold;">{selected_row[col_tr]}</td></tr>
                            <tr><td class="label">SR Number</td><td>{selected_row.get('SR Number', '')}</td></tr>
                            <tr><td class="label">ગ્રાહકનું નામ</td><td>{selected_row.get('Name Of Applicant', '')}</td></tr>
                            <tr><td class="label">ગામ / શહેર</td><td>{selected_row.get('Village Or City', '')}</td></tr>
                            <tr><td class="label">મીટર નંબર (Site)</td><td>__________________________</td></tr>
                            <tr><td class="label">રીલીઝ તારીખ</td><td>____ / ____ / 2026</td></tr>
                        </table>
                    </div>
                    <script>window.print();</script>
                </body>
                </html>
                """

                if st.button("🖨️ Generate & Print Performa"):
                    # This opens a new window with the HTML content
                    import streamlit.components.v1 as components
                    components.html(f"<script>var w = window.open(); w.document.write(`{print_html}`); w.document.close();</script>", height=0)
                    st.success(f"Printing Form for {selected_row['Name Of Applicant']}...")

                st.divider()
                st.write("### Preview of Pending List")
                st.dataframe(df_pending.drop(columns=["Selection_Label"]), use_container_width=True)
            else:
                st.warning("No records found (TR MR No != NULL and Date == NULL)")

        with t2:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Critical Error: {str(e)}")
else:
    st.info("Please upload your PPR file.")
