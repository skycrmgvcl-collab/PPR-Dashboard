import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")

st.title("⚡ PPR Monitoring Dashboard")

# ---------------------------------------------------
# LOAD FILE
# ---------------------------------------------------

@st.cache_data
def load_file(file):

    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    df = df.fillna("")
    df = df.replace("NULL","")

    return df


# ---------------------------------------------------
# RELEASE FORM
# ---------------------------------------------------

def create_release_html(row):

    html=f"""
<html>
<head>
<meta charset="UTF-8">
<style>
body{{font-family:'Shruti';font-size:14px}}
</style>
</head>

<body onload="window.print()">

<h2 style="text-align:center">મધ્ય ગુજરાત વીજ કંપની લી.</h2>
<h3 style="text-align:center">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</h3>

<table width="100%" border="0">

<tr><td>SR Number</td><td>{row["SR Number"]}</td></tr>
<tr><td>Name</td><td>{row["Name Of Applicant"]}</td></tr>
<tr><td>Village</td><td>{row["Village Or City"]}</td></tr>
<tr><td>Scheme</td><td>{row["Name Of Scheme"]}</td></tr>
<tr><td>Load</td><td>{row["Demand Load"]} {row["Load Uom"]}</td></tr>
<tr><td>TR MR No</td><td>{row["TR MR No"]}</td></tr>

</table>

<br><br>

Customer Sign &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Employee Sign

</body>
</html>
"""

    return base64.b64encode(html.encode()).decode()


# ---------------------------------------------------
# GRID FUNCTION
# ---------------------------------------------------

def show_grid(df,key):

    # columns to display (stable)
    display_cols=[
    "SR Number",
    "Name Of Applicant",
    "Village Or City",
    "SR Type",
    "Name Of Scheme",
    "Demand Load",
    "Survey Category",
    "TR MR No",
    "Consumer No"
    ]

    display_cols=[c for c in display_cols if c in df.columns]

    grid_df=df[display_cols]

    gb=GridOptionsBuilder.from_dataframe(grid_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )

    gb.configure_pagination(paginationPageSize=50)

    AgGrid(
        grid_df,
        gridOptions=gb.build(),
        height=600,
        key=key
    )


# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file=st.file_uploader("Upload PPR Excel / CSV",type=["xlsx","xls","csv"])

if file:

    df=load_file(file)

# ---------------------------------------------------
# SIDEBAR FILTER
# ---------------------------------------------------

    st.sidebar.header("Filters")

    scheme=st.sidebar.multiselect(
        "Name Of Scheme",
        sorted(df["Name Of Scheme"].unique()),
        default=df["Name Of Scheme"].unique()
    )

    df=df[df["Name Of Scheme"].isin(scheme)]

    sr=st.sidebar.multiselect(
        "SR Type",
        sorted(df["SR Type"].unique()),
        default=df["SR Type"].unique()
    )

    df=df[df["SR Type"].isin(sr)]

    survey=st.sidebar.multiselect(
        "Survey Category",
        sorted(df["Survey Category"].unique()),
        default=df["Survey Category"].unique()
    )

    df=df[df["Survey Category"].isin(survey)]

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------

    search=st.text_input("🔎 Search SR Number")

    if search:
        df=df[df["SR Number"].astype(str).str.contains(search)]

# ---------------------------------------------------
# OPEN SR ONLY
# ---------------------------------------------------

    df=df[df["SR Status"].str.upper()=="OPEN"]

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

    tab1,tab2,tab3,tab4=st.tabs([
        "Paid Pending Report",
        "Pending to Issue TMN",
        "Release Pending",
        "All Records"
    ])

# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------

    with tab1:

        ppr_df=df[df["Date Of WCC"]==""]

        st.metric("Paid Pending",len(ppr_df))

        show_grid(ppr_df,"ppr_grid")


# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------

    with tab2:

        tmn_df=df[
            (df["Date Of WCC"]!="") &
            (df["Date Of TMN Issued"]=="")
        ]

        st.metric("TMN Pending",len(tmn_df))

        show_grid(tmn_df,"tmn_grid")


# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------

    with tab3:

        release_df=df[
            (df["TR MR No"]!="") &
            (df["Date Of Release Conn"]=="")
        ]

        st.metric("Release Pending",len(release_df))

        show_grid(release_df,"release_grid")


# ---------------------------------------------------
# TAB 4
# ---------------------------------------------------

    with tab4:

        st.metric("Total Records",len(df))

        show_grid(df,"all_grid")


else:

    st.info("Upload PPR file to begin")
