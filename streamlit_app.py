import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="PPR Release Dashboard", layout="wide")

st.title("⚡ PPR Release Monitoring Dashboard")

# ---------------------------------------------------
# RELEASE FORM HTML
# ---------------------------------------------------

def create_release_html(row):

    mobile=""

    for c in row.index:
        if "mob" in c.lower():
            mobile=row[c]

    html=f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>

@page {{
size:A4;
margin:8mm;
}}

body {{
font-family:'Shruti','Nirmala UI';
font-size:14px;
line-height:1.25;
}}

.header {{
text-align:center;
font-weight:bold;
font-size:22px;
}}

.subheader {{
text-align:center;
font-size:15px;
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
padding:5px;
vertical-align:top;
}}

.line {{
border-bottom:1px solid black;
display:inline-block;
width:100%;
}}

.bold {{
font-weight:bold;
font-size:16px;
}}

.section {{
font-weight:bold;
margin-top:6px;
}}

.box-row {{
display:flex;
gap:8px;
margin-top:8px;
}}

.box {{
border:1.5px solid black;
padding:8px;
flex:1;
font-size:13px;
}}

.box-title {{
font-weight:bold;
border-bottom:1px solid black;
margin-bottom:6px;
padding-bottom:3px;
}}

.signature td {{
text-align:center;
padding-top:26px;
}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">વિરપુર</div>

<div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>

<table>

<tr>
<td width="35%">ગ્રાહકનું નામ</td>
<td class="line">{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td class="bold">SR No.</td>
<td class="bold">{row.get("SR Number","")}</td>
</tr>

<tr>
<td>SR Type</td>
<td class="line">{row.get("SR Type","")}</td>
</tr>

<tr>
<td>Name Of Scheme</td>
<td class="line">{row.get("Name Of Scheme","")}</td>
</tr>

<tr>
<td>લોડ</td>
<td class="line">{row.get("Demand Load","")} {row.get("Load Uom","")}</td>
</tr>

<tr>
<td>સરનામું</td>
<td class="line">
{row.get("Address1","")}
{row.get("Address2","")}
{row.get("Village Or City","")}
</td>
</tr>

<tr>
<td>Tariff</td>
<td class="line">{row.get("Tariff","")}</td>
</tr>

<tr>
<td>Survey Category</td>
<td class="line">{row.get("Survey Category","")}</td>
</tr>

<tr>
<td>ટેસ્ટ રીપોર્ટ તા.</td>
<td class="line">{row.get("Date Of TR Recv","")}</td>
</tr>

<tr>
<td>રસીદ નં</td>
<td class="line">{row.get("TR MR No","")}</td>
</tr>

<tr>
<td>મોબાઇલ નંબર</td>
<td class="line">{mobile}</td>
</tr>

</table>

<div class="section">૫  માલ સામાન વપરાશની નોંધ</div>

<div>
(૧) સર્વિસ વાયર પી.વી.સી. ______ કોર ______ એમ.એમ. ______ મીટર
</div>

<div>
(૨) ELCB Make _________ &nbsp;&nbsp;&nbsp; Capacity _________
</div>

<div>
(૩) 1-Ph SMC બોક્ષ ______ નંગ &nbsp;&nbsp; | &nbsp;&nbsp; 3-Ph SMC બોક્ષ ______ નંગ
</div>

<br>

<div class="box">

<div class="box-title">મીટર વિગતો</div>

<table>

<tr><td width="40%">કંપની</td><td>___________</td></tr>
<tr><td>ટાઈપ</td><td>___________</td></tr>
<tr><td>કેપેસિટી</td><td>___________</td></tr>
<tr><td>આંટા</td><td>___________</td></tr>
<tr><td>મીટર નંબર</td><td>___________</td></tr>
<tr><td>લેબ નંબર</td><td>___________</td></tr>
<tr><td>રીડિંગ</td><td>___________</td></tr>
<tr><td>બોડી સીલ</td><td>___________</td></tr>

</table>

</div>

<div class="box-row">

<div class="box">

<div class="box-title">સીલ ની વિગત</div>

ટર્મિનલ સીલ : __________<br>
SMC Box સીલ : __________

</div>

<div class="box">

<div class="box-title">મીટર બોર્ડ</div>

મીટર બોર્ડ ______ નંગ

</div>

<div class="box">

<div class="box-title">ઇન્સ્યુલેટર</div>

રીલ ઇન્સ્યુલેટર ______<br>
એગ ઇન્સ્યુલેટર ______<br>
GI વાયર 10 ______ મીટર

</div>

<div class="box">

<div class="box-title">અન્ય વિગતો</div>

અર્થિંગ વાયર ______ મીટર<br>
અર્થિંગ પાઇપ ______ નંગ<br><br>

મીટર પેટી ૫ ફિટ કરતાં વધારે નથી ? ______

</div>

</div>

<br>

<div style="font-size:13px;margin-top:6px;">
મીટર / મીટર પેટી / સીલિંગ તથા સર્વિસ લાઇન ગ્રાહક તરીકે સાચવવાની સંપૂર્ણ જવાબદારી મારી છે.
</div>

<br>

<table class="signature">

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

    return base64.b64encode(html.encode()).decode()

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Excel / CSV", type=["xlsx","xls","csv"])

if file:

    if file.name.endswith(".csv"):
        df=pd.read_csv(file)
    else:
        df=pd.read_excel(file)

    df.columns=df.columns.str.strip()

    df.replace("NULL","",inplace=True)

    df=df.fillna("")

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------

    search=st.text_input("🔎 Search SR Number")

    if search:
        df=df[df["SR Number"].astype(str).str.contains(search,case=False)]

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

    schemes=sorted(df["Name Of Scheme"].unique())

    scheme=st.sidebar.selectbox("Name Of Scheme",["All"]+schemes)

    if scheme!="All":
        df=df[df["Name Of Scheme"]==scheme]


    sr_types=sorted(df["SR Type"].unique())

    sr=st.sidebar.selectbox("SR Type",["All"]+sr_types)

    if sr!="All":
        df=df[df["SR Type"]==sr]

# ---------------------------------------------------
# RELEASE PENDING LOGIC
# ---------------------------------------------------

    release_df=df[
        (df["TR MR No"].astype(str).str.strip()!="") &
        ((df["Date Of Release Conn"].astype(str).str.strip()=="") |
         (df["Date Of Release Conn"].isna())) &
        (df["SR Status"].astype(str).str.upper()=="OPEN")
    ].copy()

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------

    col1,col2=st.columns(2)

    col1.metric("Release Pending",len(release_df))
    col2.metric("TR Received",(df["TR MR No"].astype(str).str.strip()!="").sum())

# ---------------------------------------------------
# GENERATE HTML DATA
# ---------------------------------------------------

    release_df["release_html"]=release_df.apply(create_release_html,axis=1)

    release_df.insert(0,"Print","")

# ---------------------------------------------------
# GRID
# ---------------------------------------------------

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

    display_cols=[
        "Print",
        "SR Number",
        "Name Of Applicant",
        "Village Or City",
        "SR Type",
        "Name Of Scheme",
        "Demand Load",
        "Survey Category",
        "TR MR No",
        "Consumer No",
        "SR Status"
    ]

    display_cols=[c for c in display_cols if c in release_df.columns]

    grid_df=release_df[display_cols+["release_html"]]

    gb=GridOptionsBuilder.from_dataframe(grid_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=120
    )

    gb.configure_column("Print",cellRenderer=renderer,width=70)

    gb.configure_column("release_html",hide=True)

    AgGrid(
        grid_df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        height=650,
        fit_columns_on_grid_load=True
    )

# ---------------------------------------------------
# EXPORT
# ---------------------------------------------------

    st.download_button(
        "📥 Export Release Pending List",
        release_df.to_csv(index=False),
        file_name="release_pending.csv"
    )

else:

    st.info("Upload PPR file to begin")
