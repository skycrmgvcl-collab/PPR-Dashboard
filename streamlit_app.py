import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import base64

st.set_page_config(page_title="PPR Release Dashboard", layout="wide")

st.title("⚡ PPR Release Monitoring Dashboard")

# ----------------------------------------------------
# FILE UPLOAD
# ----------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx","xls","csv"])

# ----------------------------------------------------
# RELEASE FORM
# ----------------------------------------------------

def create_release_html(row):

    html = f"""
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
margin-bottom:10px;
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
<td>Village</td>
<td class="line">{row.get("Village Or City","")}</td>
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
<td>TR Date</td>
<td class="line">{row.get("Date Of TR Recv","")}</td>
</tr>

<tr>
<td>TR MR No</td>
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


# ----------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------

if file:

    # READ FILE

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # CLEAN HEADERS

    df.columns = df.columns.str.strip()

    df.replace("NULL","", inplace=True)

    df = df.fillna("")

# ----------------------------------------------------
# SEARCH
# ----------------------------------------------------

    search = st.text_input("🔎 Search SR Number")

    if search:
        df = df[df["SR Number"].astype(str).str.contains(search,case=False)]

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

    schemes = sorted(df["Name Of Scheme"].unique())

    scheme = st.sidebar.selectbox("Name Of Scheme",["All"]+schemes)

    if scheme!="All":
        df = df[df["Name Of Scheme"]==scheme]


    sr_types = sorted(df["SR Type"].unique())

    sr = st.sidebar.selectbox("SR Type",["All"]+sr_types)

    if sr!="All":
        df = df[df["SR Type"]==sr]

# ----------------------------------------------------
# RELEASE PENDING LOGIC
# ----------------------------------------------------

    release_df = df[
        (df["Date Of TR Recv"].astype(str).str.strip()!="") &
        ((df["Date Of Release Conn"].astype(str).str.strip()=="") |
         (df["Date Of Release Conn"].isna())) &
        (df["SR Status"].astype(str).str.upper()=="OPEN")
    ].copy()

# ----------------------------------------------------
# SUMMARY METRICS
# ----------------------------------------------------

    col1,col2 = st.columns(2)

    col1.metric("Release Pending",len(release_df))
    col2.metric("TR Received",(df["Date Of TR Recv"].astype(str).str.strip()!="").sum())

# ----------------------------------------------------
# DISPLAY COLUMNS
# ----------------------------------------------------

    display_cols = [
        "SR Number",
        "Name Of Applicant",
        "Village Or City",
        "SR Type",
        "Name Of Scheme",
        "Demand Load",
        "Survey Category",
        "Date Of TR Recv",
        "TR MR No",
        "Date Of Release Conn",
        "Consumer No",
        "SR Status"
    ]

    display_cols = [c for c in display_cols if c in release_df.columns]

    release_display = release_df[display_cols]

# ----------------------------------------------------
# GRID DISPLAY
# ----------------------------------------------------

    gb = GridOptionsBuilder.from_dataframe(release_display)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=120
    )

    AgGrid(
        release_display,
        gridOptions=gb.build(),
        height=650,
        fit_columns_on_grid_load=True
    )

# ----------------------------------------------------
# EXPORT BUTTON
# ----------------------------------------------------

    st.download_button(
        "📥 Export Release Pending List",
        release_display.to_csv(index=False),
        file_name="release_pending.csv"
    )

# ----------------------------------------------------
# BULK RELEASE FORM PRINT
# ----------------------------------------------------

    if st.button("🖨 Generate Release Forms"):

        html = ""

        for _,row in release_df.iterrows():
            html += create_release_html(row)

        b64 = base64.b64encode(html.encode()).decode()

        st.markdown(
            f'<a href="data:text/html;base64,{b64}" target="_blank">Open Release Forms</a>',
            unsafe_allow_html=True
        )

else:

    st.info("Upload PPR file to begin")
