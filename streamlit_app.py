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
    df = df.replace(r'^\s*NULL\s*$', '', regex=True)

    df = df.fillna("")

    return df


# ---------------------------------------------------
# CHECK BLANK FUNCTION
# ---------------------------------------------------

def is_blank(value):
    if pd.isna(value):
        return True

    text = str(value).strip()
    return text == "" or text.upper() == "NULL"


def normalized_text(series):
    return series.astype(str).str.strip().str.upper()


def is_open_status(series):
    status = normalized_text(series)
    return status.eq("OPEN") | status.str.startswith("OPEN ")


# ---------------------------------------------------
# RELEASE FORM HTML
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

    schemes = sorted(df["Name Of Scheme"].dropna().unique())

    scheme_sel = st.sidebar.multiselect(
        "Name Of Scheme",
        schemes,
        default=schemes
    )

    df = df[df["Name Of Scheme"].isin(scheme_sel)]

    sr_types = sorted(df["SR Type"].dropna().unique())

    sr_sel = st.sidebar.multiselect(
        "SR Type",
        sr_types,
        default=sr_types
    )

    df = df[df["SR Type"].isin(sr_sel)]

    survey = sorted(df["Survey Category"].dropna().unique())

    survey_sel = st.sidebar.multiselect(
        "Survey Category",
        survey,
        default=survey
    )

    df = df[df["Survey Category"].isin(survey_sel)]

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
            is_open_status(df["SR Status"]) &
            (~df["Date Of FQ Paid"].apply(is_blank)) &
            (df["Date Of WCC"].apply(is_blank))
        ]

        st.metric("Paid Pending",len(ppr_df))

        st.dataframe(ppr_df,use_container_width=True)


# ---------------------------------------------------
# TAB 2 : TMN PENDING
# ---------------------------------------------------

    with tab2:

        tmn_df = df[
            is_open_status(df["SR Status"]) &
            (~df["Date Of WCC"].apply(is_blank)) &
            (df["Date Of TMN Issued"].apply(is_blank))
        ]

        st.metric("Pending to Issue TMN",len(tmn_df))

        st.dataframe(tmn_df,use_container_width=True)


# ---------------------------------------------------
# TAB 3 : RELEASE PENDING
# ---------------------------------------------------

    with tab3:

        release_df = df[
            is_open_status(df["SR Status"]) &
            (~df["TR MR No"].apply(is_blank)) &
            (df["Date Of Release Conn"].apply(is_blank))
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
 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/streamlit_app.py b/streamlit_app.py
index 9772220e662418676fc649a2a0d5732b72ee840b..aadb503424f1bde94ffda0f28cee9ca3a1136507 100644
--- a/streamlit_app.py
+++ b/streamlit_app.py
@@ -13,50 +13,54 @@ st.title("⚡ PPR Monitoring Dashboard")
 def load_file(file):
 
     if file.name.endswith(".csv"):
         df = pd.read_csv(file, low_memory=False)
     else:
         df = pd.read_excel(file)
 
     df.columns = df.columns.str.strip()
 
     # convert NULL → blank
     df = df.replace(r'^\s*NULL\s*$', '', regex=True)
 
     df = df.fillna("")
 
     return df
 
 
 # ---------------------------------------------------
 # CHECK BLANK FUNCTION
 # ---------------------------------------------------
 
 def is_blank(value):
     return str(value).strip() == "" or str(value).strip().upper() == "NULL"
 
 
+def normalized_text(series):
+    return series.astype(str).str.strip().str.upper()
+
+
 # ---------------------------------------------------
 # RELEASE FORM HTML
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
@@ -156,85 +160,85 @@ if file:
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
-            (df["SR Status"].str.upper()=="OPEN") &
+            (normalized_text(df["SR Status"])=="OPEN") &
             (~df["Date Of FQ Paid"].apply(is_blank)) &
             (df["Date Of WCC"].apply(is_blank))
         ]
 
         st.metric("Paid Pending",len(ppr_df))
 
         st.dataframe(ppr_df,use_container_width=True)
 
 
 # ---------------------------------------------------
 # TAB 2 : TMN PENDING
 # ---------------------------------------------------
 
     with tab2:
 
         tmn_df = df[
-            (df["SR Status"].str.upper()=="OPEN") &
+            (normalized_text(df["SR Status"])=="OPEN") &
             (~df["Date Of WCC"].apply(is_blank)) &
             (df["Date Of TMN Issued"].apply(is_blank))
         ]
 
         st.metric("Pending to Issue TMN",len(tmn_df))
 
         st.dataframe(tmn_df,use_container_width=True)
 
 
 # ---------------------------------------------------
 # TAB 3 : RELEASE PENDING
 # ---------------------------------------------------
 
     with tab3:
 
         release_df = df[
-            (df["SR Status"].str.upper()=="OPEN") &
+            (normalized_text(df["SR Status"])=="OPEN") &
             (~df["TR MR No"].apply(is_blank)) &
             (df["Date Of Release Conn"].apply(is_blank))
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
 
 
EOF
)
