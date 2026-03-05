import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import base64

st.set_page_config(page_title="PPR Release Dashboard", layout="wide")

st.title("⚡ PPR Release Monitoring Dashboard")

# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx","xls","csv"])


# ---------------------------------------------------------
# RELEASE FORM HTML
# ---------------------------------------------------------

def create_release_html(row):

    html=f"""
<html>
<head>
<meta charset="UTF-8">

<style>

@page {{
size:A4;
margin:10mm;
}}

body {{
font-family:'Shruti','Nirmala UI';
font-size:14px;
}}

.header {{
text-align:center;
font-weight:bold;
font-size:22px;
}}

.title {{
text-align:center;
font-weight:bold;
font-size:18px;
margin-bottom:12px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
padding:6px;
}}

.line {{
border-bottom:1px solid black;
}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>

<div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>

<table>

<tr>
<td width="35%">SR Number</td>
<td class="line">{row.get("SR Number","")}</td>
</tr>

<tr>
<td>Applicant Name</td>
<td class="line">{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td>Scheme</td>
<td class="line">{row.get("Name Of Scheme","")}</td>
</tr>

<tr>
<td>SR Type</td>
<td class="line">{row.get("SR Type","")}</td>
</tr>

<tr>
<td>Load</td>
<td class="line">{row.get("Demand Load","")} {row.get("Load Uom","")}</td>
</tr>

<tr>
<td>Survey Category</td>
<td class="line">{row.get("Survey Category","")}</td>
</tr>

<tr>
<td>Test Report Date</td>
<td class="line">{row.get("Date Of TR Recv","")}</td>
</tr>

<tr>
<td>TR Receipt No</td>
<td class="line">{row.get("TR MR No","")}</td>
</tr>

</table>

<br>

મીટર / મીટર પેટી / સીલિંગ તથા સર્વિસ લાઇન ગ્રાહક તરીકે સાચવવાની સંપૂર્ણ જવાબદારી મારી છે.

<br><br>

<table>

<tr>
<td>ગ્રાહકની સહી</td>
<td>કર્મચારી ની સહી</td>
<td>જુ.ઇ. સહી</td>
<td>ના.ઇ. સહી</td>
</tr>

</table>

</body>
</html>
"""

    return html


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

if file:

    # Read file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    # Replace NULL text
    df.replace("NULL", "", inplace=True)

    # Fill NaN
    df = df.fillna("")

    # Serial number
    df.insert(0,"Sr No",range(1,len(df)+1))


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

    search = st.text_input("🔎 Search SR Number")

    if search:
        df = df[df["SR Number"].astype(str).str.contains(search,case=False)]


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

    schemes = sorted(df["Name Of Scheme"].unique())

    scheme = st.sidebar.selectbox("Name Of Scheme",["All"]+schemes)

    if scheme!="All":
        df = df[df["Name Of Scheme"]==scheme]


    sr_types = sorted(df["SR Type"].unique())

    sr = st.sidebar.selectbox("SR Type",["All"]+sr_types)

    if sr!="All":
        df = df[df["SR Type"]==sr]


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

    tab1,tab2 = st.tabs(["All Records","Release Pending"])


# ---------------------------------------------------------
# ALL RECORDS GRID
# ---------------------------------------------------------

    with tab1:

        gb_all = GridOptionsBuilder.from_dataframe(df)

        gb_all.configure_default_column(
            filter=True,
            sortable=True,
            resizable=True,
            flex=1,
            minWidth=130
        )

        AgGrid(
            df,
            gridOptions=gb_all.build(),
            height=650,
            fit_columns_on_grid_load=True
        )


# ---------------------------------------------------------
# RELEASE PENDING
# ---------------------------------------------------------

    with tab2:

        release_df = df[
            (df["Date Of TR Recv"]!="") &
            (df["Date Of Release Conn"]=="")
        ].copy()


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

        col1,col2 = st.columns(2)

        col1.metric("Release Pending",len(release_df))
        col2.metric("TR Received",(df["Date Of TR Recv"]!="").sum())


# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

        st.download_button(
            "📥 Export Release Pending List",
            release_df.to_csv(index=False),
            file_name="release_pending.csv"
        )


# ---------------------------------------------------------
# BULK PRINT
# ---------------------------------------------------------

        if st.button("🖨 Generate Release Forms"):

            html=""

            for _,row in release_df.iterrows():
                html += create_release_html(row)

            b64 = base64.b64encode(html.encode()).decode()

            st.markdown(
                f'<a href="data:text/html;base64,{b64}" target="_blank">Open Release Forms</a>',
                unsafe_allow_html=True
            )


# ---------------------------------------------------------
# RELEASE PENDING GRID
# ---------------------------------------------------------

        gb = GridOptionsBuilder.from_dataframe(release_df)

        gb.configure_default_column(
            filter=True,
            sortable=True,
            resizable=True,
            flex=1,
            minWidth=130
        )

        AgGrid(
            release_df,
            gridOptions=gb.build(),
            height=650,
            fit_columns_on_grid_load=True
        )

else:

    st.info("Upload PPR file to begin")
