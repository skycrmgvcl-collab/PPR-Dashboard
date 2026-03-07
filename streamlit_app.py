import streamlit as st
import pandas as pd
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

    # convert NULL → blank
    df = df.replace("NULL","")

    df = df.fillna("")

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

body {{
font-family: Shruti;
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
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
padding:6px;
}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>

<br>

<table>

<tr><td width="30%">SR Number</td><td>{row.get("SR Number","")}</td></tr>
<tr><td>Name</td><td>{row.get("Name Of Applicant","")}</td></tr>
<tr><td>Village</td><td>{row.get("Village Or City","")}</td></tr>
<tr><td>Scheme</td><td>{row.get("Name Of Scheme","")}</td></tr>
<tr><td>Load</td><td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
<tr><td>TR MR No</td><td>{row.get("TR MR No","")}</td></tr>

</table>

<br><br>

Customer Sign &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Employee Sign

</body>
</html>
"""

    return base64.b64encode(html.encode()).decode()


# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx","xls","csv"])

if file:

    df = load_file(file)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

    st.sidebar.header("Filters")

    schemes = sorted(df["Name Of Scheme"].unique())

    selected_scheme = st.sidebar.multiselect(
        "Name Of Scheme",
        schemes,
        default=schemes
    )

    df = df[df["Name Of Scheme"].isin(selected_scheme)]

    sr_types = sorted(df["SR Type"].unique())

    selected_sr = st.sidebar.multiselect(
        "SR Type",
        sr_types,
        default=sr_types
    )

    df = df[df["SR Type"].isin(selected_sr)]

    survey = sorted(df["Survey Category"].unique())

    selected_survey = st.sidebar.multiselect(
        "Survey Category",
        survey,
        default=survey
    )

    df = df[df["Survey Category"].isin(selected_survey)]

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------

    search = st.text_input("🔎 Search SR Number")

    if search:
        df = df[df["SR Number"].astype(str).str.contains(search)]

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

    tab1,tab2,tab3,tab4 = st.tabs([
        "Paid Pending",
        "Pending to Issue TMN",
        "Release Pending",
        "All Records"
    ])

# ---------------------------------------------------
# TAB 1 : PAID PENDING
# ---------------------------------------------------

    with tab1:

        ppr_df = df[
            (df["SR Status"].str.upper()=="OPEN") &
            (df["Date Of WCC"].astype(str).str.strip()=="")
        ]

        st.metric("Paid Pending",len(ppr_df))

        st.dataframe(ppr_df,use_container_width=True)

# ---------------------------------------------------
# TAB 2 : TMN PENDING
# ---------------------------------------------------

    with tab2:

        tmn_df = df[
            (df["SR Status"].str.upper()=="OPEN") &
            (df["Date Of WCC"].astype(str).str.strip()!="") &
            (df["Date Of TMN Issued"].astype(str).str.strip()=="")
        ]

        st.metric("Pending to Issue TMN",len(tmn_df))

        st.dataframe(tmn_df,use_container_width=True)

# ---------------------------------------------------
# TAB 3 : RELEASE PENDING
# ---------------------------------------------------

    with tab3:

        release_df = df[
            (df["SR Status"].str.upper()=="OPEN") &
            (df["TR MR No"].astype(str).str.strip()!="") &
            (df["Date Of Release Conn"].astype(str).str.strip()=="")
        ].copy()

        st.metric("Release Pending",len(release_df))

        for i,row in release_df.iterrows():

            col1,col2,col3 = st.columns([3,3,1])

            col1.write(row["SR Number"])
            col2.write(row["Name Of Applicant"])

            html = create_release_html(row)

            link = f'<a href="data:text/html;base64,{html}" target="_blank">🖨 Print</a>'

            col3.markdown(link,unsafe_allow_html=True)

        st.dataframe(release_df,use_container_width=True)

# ---------------------------------------------------
# TAB 4 : ALL RECORDS
# ---------------------------------------------------

    with tab4:

        st.metric("Total Records",len(df))

        st.dataframe(df,use_container_width=True)

# ---------------------------------------------------
# EXPORT
# ---------------------------------------------------

    st.download_button(
        "📥 Export Filtered Data",
        df.to_csv(index=False),
        file_name="ppr_filtered_data.csv"
    )

else:

    st.info("Upload PPR file to begin")
