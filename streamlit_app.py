import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="PPR Monitoring Dashboard", layout="wide")

st.title("⚡ PPR Monitoring Dashboard")

# -------------------------------------------------------
# CACHE FILE LOADING
# -------------------------------------------------------

@st.cache_data
def load_file(file):

    if file.name.endswith(".csv"):
        df = pd.read_csv(file, low_memory=False)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    df.replace("NULL","",inplace=True)
    df.fillna("", inplace=True)

    return df


# -------------------------------------------------------
# SANITIZE DATAFRAME (AGGRID SAFE)
# -------------------------------------------------------

def safe_dataframe(df):

    df = df.copy()

    df = df.fillna("")
    df = df.replace({None:""})

    for col in df.columns:
        df[col] = df[col].astype(str)

    return df


# -------------------------------------------------------
# RELEASE FORM HTML
# -------------------------------------------------------

def create_release_html(row):

    html=f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>

@page {{ size:A4; margin:8mm; }}

body {{
font-family:'Shruti','Nirmala UI';
font-size:14px;
}}

.header {{text-align:center;font-weight:bold;font-size:22px;}}
.subheader {{text-align:center;font-size:15px;}}
.title {{text-align:center;font-weight:bold;font-size:18px;margin-bottom:10px;}}

table {{width:100%;border-collapse:collapse;}}
td {{padding:6px;}}
.line {{border-bottom:1px solid black;width:100%;display:inline-block;}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">વિરપુર</div>

<div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>

<table>

<tr>
<td width="35%">SR Number</td>
<td class="line">{row.get("SR Number","")}</td>
</tr>

<tr>
<td>Applicant</td>
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
<td>Load</td>
<td class="line">{row.get("Demand Load","")} {row.get("Load Uom","")}</td>
</tr>

<tr>
<td>TR MR No</td>
<td class="line">{row.get("TR MR No","")}</td>
</tr>

</table>

<br><br>

ગ્રાહકની સહી &nbsp;&nbsp;&nbsp;&nbsp; કર્મચારી ની સહી &nbsp;&nbsp;&nbsp;&nbsp; જુ.ઇ. સહી &nbsp;&nbsp;&nbsp;&nbsp; ના.ઇ. સહી

</body>
</html>
"""

    return base64.b64encode(html.encode()).decode()


# -------------------------------------------------------
# GRID FUNCTION
# -------------------------------------------------------

def show_grid(data,key):

    data=safe_dataframe(data)

    gb=GridOptionsBuilder.from_dataframe(data)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )

    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=50
    )

    AgGrid(
        data,
        gridOptions=gb.build(),
        height=650,
        fit_columns_on_grid_load=True,
        key=key
    )


# -------------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------------

file=st.file_uploader("Upload PPR Excel / CSV",type=["xlsx","xls","csv"])

if file:

    df=load_file(file)

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------

    st.sidebar.header("Filters")

    schemes=sorted(df["Name Of Scheme"].unique())
    selected_scheme=st.sidebar.multiselect("Name Of Scheme",schemes,default=schemes)

    df=df[df["Name Of Scheme"].isin(selected_scheme)]

    sr_types=sorted(df["SR Type"].unique())
    selected_sr=st.sidebar.multiselect("SR Type",sr_types,default=sr_types)

    df=df[df["SR Type"].isin(selected_sr)]

    survey_cat=sorted(df["Survey Category"].unique())
    selected_survey=st.sidebar.multiselect("Survey Category",survey_cat,default=survey_cat)

    df=df[df["Survey Category"].isin(selected_survey)]

# -------------------------------------------------------
# SEARCH
# -------------------------------------------------------

    search=st.text_input("🔎 Search SR Number")

    if search:
        df=df[df["SR Number"].astype(str).str.contains(search)]

# -------------------------------------------------------
# ONLY OPEN SR
# -------------------------------------------------------

    df=df[df["SR Status"].astype(str).str.upper()=="OPEN"]

# -------------------------------------------------------
# TABS
# -------------------------------------------------------

    tab1,tab2,tab3,tab4=st.tabs([
        "Paid Pending Report",
        "Pending to Issue TMN",
        "Release Pending",
        "All Records"
    ])

# -------------------------------------------------------
# TAB 1 : PAID PENDING
# -------------------------------------------------------

    with tab1:

        ppr_df=df[df["Date Of WCC"]==""]

        st.metric("Paid Pending",len(ppr_df))

        show_grid(ppr_df,"ppr_grid")

# -------------------------------------------------------
# TAB 2 : TMN PENDING
# -------------------------------------------------------

    with tab2:

        tmn_df=df[
            (df["Date Of WCC"]!="") &
            (df["Date Of TMN Issued"]=="")
        ]

        st.metric("TMN Pending",len(tmn_df))

        show_grid(tmn_df,"tmn_grid")

# -------------------------------------------------------
# TAB 3 : RELEASE PENDING
# -------------------------------------------------------

    with tab3:

        release_df=df[
            (df["TR MR No"]!="") &
            (df["Date Of Release Conn"]=="")
        ].copy()

        st.metric("Release Pending",len(release_df))

        release_df["release_html"]=release_df.apply(create_release_html,axis=1)

        release_df.insert(0,"Print","")

        renderer=JsCode("""

class Renderer{

init(params){

this.eGui=document.createElement('span');
this.eGui.innerHTML='🖨';
this.eGui.style.cursor='pointer';

this.eGui.addEventListener('click',()=>{

const b64=params.data.release_html;

const win=window.open("","_blank");

const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
const html=new TextDecoder("utf-8").decode(bytes);

win.document.write(html);
win.document.close();

});

}

getGui(){return this.eGui;}

}
""")

        release_df=safe_dataframe(release_df)

        gb=GridOptionsBuilder.from_dataframe(release_df)

        gb.configure_default_column(filter=True,sortable=True,resizable=True)

        gb.configure_pagination(paginationPageSize=50)

        gb.configure_column("Print",cellRenderer=renderer,width=70)

        gb.configure_column("release_html",hide=True)

        AgGrid(
            release_df,
            gridOptions=gb.build(),
            allow_unsafe_jscode=True,
            height=650,
            fit_columns_on_grid_load=True,
            key="release_grid"
        )

# -------------------------------------------------------
# TAB 4 : ALL RECORDS
# -------------------------------------------------------

    with tab4:

        st.metric("Total Records",len(df))

        show_grid(df,"all_grid")

else:

    st.info("Upload PPR file to begin")
