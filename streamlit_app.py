import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Page Configuration
st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")
st.title("⚡ MGVCL PPR Monitoring Dashboard")

# -----------------------------------------------------------
# DATA LOADING & CLEANING
# -----------------------------------------------------------
file = st.file_uploader("Upload PPR Excel/CSV", type=["xls","xlsx","csv"])

def is_actually_filled(series):
    """Checks for data that is NOT empty, NOT 'NULL', and NOT 'NaN'."""
    s = series.astype(str).str.strip().str.upper()
    return (s != "") & (s != "NAN") & (s != "NULL") & (s != "NONE") & (s != "<NA>")

def is_actually_blank(series):
    return ~is_actually_filled(series)

if file:
    try:
        if file.name.endswith("csv"):
            df_raw = pd.read_csv(file, encoding="utf-8-sig")
        else:
            df_raw = pd.read_excel(file)
    except Exception as e:
        st.error(f"File loading error: {e}")
        st.stop()

    # 1. Clean Column Names
    df_raw.columns = df_raw.columns.str.strip()
    
    # 2. THE BULLETPROOF CLEAN (Prevents MarshallComponentException)
    # We create a clean version where everything is a string and no 'NULL's exist
    df_clean = df_raw.copy()
    for col in df_clean.columns:
        # Convert to string, strip whitespace, and replace 'NULL' variants with ""
        df_clean[col] = df_clean[col].astype(str).str.strip().replace(
            ['NULL', 'null', 'nan', 'NaN', 'None', 'NAT', '<NA>', 'nan'], ""
        )
    
    # Force any remaining actual NaN objects to empty strings
    df_clean = df_clean.fillna("")
    # IMPORTANT: Reset index so AgGrid doesn't see duplicate or messy index numbers
    df_clean = df_clean.reset_index(drop=True)

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    u_schemes = sorted([x for x in df_clean["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Scheme", u_schemes, default=u_schemes)
    
    u_types = sorted([x for x in df_clean["SR Type"].unique() if x != ""])
    sel_types = st.sidebar.multiselect("SR Type", u_types, default=u_types)

    # Apply Filter Logic
    df_filtered = df_clean[
        (df_clean["Name Of Scheme"].isin(sel_schemes)) & 
        (df_clean["SR Type"].isin(sel_types))
    ].copy().reset_index(drop=True)

    # -----------------------------------------------------------
    # JAVASCRIPT PRINT RENDERER
    # -----------------------------------------------------------
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #2e7d32; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 2px 10px; font-weight: bold; width: 100%;">
                🖨️ PDF
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const html = `
                    <html>
                    <head><meta charset="UTF-8"><style>
                        body { font-family: Arial; padding: 30px; border: 2px solid black; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        td { border: 1px solid black; padding: 10px; font-size: 16px; }
                        .label { background-color: #eee; font-weight: bold; width: 35%; }
                    </style></head>
                    <body>
                        <h2 style="text-align:center;">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
                        <h3 style="text-align:center;">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</h3>
                        <table>
                            <tr><td class="label">SR Number</td><td>${r['SR Number'] || ''}</td></tr>
                            <tr><td class="label">Name</td><td>${r['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">Village</td><td>${r['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">Meter No</td><td>${r['TR MR No'] || ''}</td></tr>
                        </table>
                        <script>window.print();</script>
                    </body>
                    </html>
                `;
                var w = window.open('', '_blank');
                w.document.write(html);
                w.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    # -----------------------------------------------------------
    # GRID DISPLAY FUNCTION
    # -----------------------------------------------------------
    def show_grid(data, key, has_print=False):
        if data.empty:
            st.warning("No records found for this category.")
            return

        # Double-check: ensure no objects exist that break JSON
        # We reset index again just to be 100% safe inside the function
        display_df = data.copy().reset_index(drop=True)

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        if has_print:
            gb.configure_column("Print_Action", headerName="Action", 
                                cellRenderer=render_print_button, 
                                width=100, pinned='left')
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        
        try:
            AgGrid(
                display_df, 
                gridOptions=gb.build(), 
                height=450, 
                theme="streamlit", 
                allow_unsafe_jscode=True, 
                key=key,
                reload_data=True
            )
        except Exception as e:
            st.error("Component failed to load. Displaying simple table instead.")
            st.dataframe(display_df)

    # -----------------------------------------------------------
    # TABS & LOGIC
    # -----------------------------------------------------------
    t1, t2, t3, t4 = st.tabs(["Paid Pending", "TMN Pending", "Release Pending", "All Records"])

    with t1:
        df1 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (is_actually_filled(df_filtered["Date Of FQ Paid"])) &
            (is_actually_blank(df_filtered["Date Of WCC"]))
        ]
        st.write(f"Count: **{len(df1)}**")
        show_grid(df1, "grid1")

    with t2:
        df2 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (is_actually_filled(df_filtered["Date Of WCC"])) &
            (is_actually_blank(df_filtered["Date Of TMN Issued"]))
        ]
        st.write(f"Count: **{len(df2)}**")
        show_grid(df2, "grid2")

    with t3:
        df3 = df_filtered[
            (df_filtered["SR Status"].str.upper() == "OPEN") &
            (is_actually_filled(df_filtered["TR MR No"])) &
            (is_actually_blank(df_filtered["Date Of Release Conn"]))
        ]
        st.write(f"Count: **{len(df3)}**")
        show_grid(df3, "grid3", has_print=True)

    with t4:
        st.write(f"Total: **{len(df_filtered)}**")
        show_grid(df_filtered, "grid4")

else:
    st.info("Upload file to begin.")
