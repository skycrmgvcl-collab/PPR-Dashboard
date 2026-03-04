import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="PPR Paid Pending Dashboard", layout="wide")

st.markdown("## 💰 Paid Pending Report (PPR) Dashboard")
st.caption("Survey Category Wise Monitoring")

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("Filters")

show_shift = st.sidebar.checkbox("Connection Shifting (Non Cons)")
show_pmsy = st.sidebar.checkbox("PMSY RTS")
show_rooftop = st.sidebar.checkbox("LT Rooftop")

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader("Upload PPR Excel/CSV File", type=["xlsx","xls","csv"])


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
margin:12mm;
}}

body {{
font-family:'Shruti','Nirmala UI';
font-size:13px;
line-height:1.4;
}}

.header {{
text-align:center;
font-weight:bold;
font-size:20px;
}}

.subheader {{
text-align:center;
font-size:14px;
margin-bottom:10px;
}}

.title {{
text-align:center;
font-weight:bold;
font-size:16px;
margin-bottom:10px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
border:1px solid black;
padding:6px;
vertical-align:top;
}}

.section {{
font-weight:bold;
background:#f2f2f2;
}}

.bold {{
font-weight:bold;
}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">વિરપુર</div>

<div class="title">નવું કનેક્શન ચાલુ કર્યા અંગેનો રિપોર્ટ</div>

<table>

<tr>
<td width="30%">ગ્રાહકનું નામ</td>
<td>{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td class="bold">SR No</td>
<td class="bold">{row.get("SR Number","")}</td>
</tr>

<tr>
<td>લોડ</td>
<td>{row.get("Demand Load","")} {row.get("Load Uom","")}</td>
</tr>

<tr>
<td>સરનામું</td>
<td>
{row.get("Address1","")} 
{row.get("Address2","")} 
{row.get("Village Or City","")}
</td>
</tr>

<tr>
<td>Tariff</td>
<td>{row.get("Tariff","")}</td>
</tr>

<tr>
<td>Survey Category</td>
<td>{row.get("Survey Category","")}</td>
</tr>

<tr>
<td>FQ Amount</td>
<td>{row.get("FQ Amount","")}</td>
</tr>

<tr>
<td>FQ Paid Date</td>
<td>{row.get("Date Of FQ Paid","")}</td>
</tr>

<tr>
<td>ટેસ્ટ રીપોર્ટ તા.</td>
<td>{row.get("Date Of TR Recv","")}</td>
</tr>

<tr>
<td>રસીદ નં</td>
<td>{row.get("TR MR No","")}</td>
</tr>

<tr>
<td>મોબાઇલ નંબર</td>
<td>{mobile}</td>
</tr>

</table>

<br>

<table>

<tr class="section">
<td colspan="3">૫. માલ સામાન વપરાશની નોંધ</td>
</tr>

<tr>
<td colspan="3">સર્વિસ વાયર પી.વી.સી. ______ કોર ______ એમ.એમ. ______ મીટર</td>
</tr>

<tr>
<td colspan="3">ELCB Make _________ &nbsp;&nbsp;&nbsp; Capacity _________</td>
</tr>

<tr>
<td colspan="3">1-Ph SMC બોક્ષ ______ નંગ | 3-Ph SMC બોક્ષ ______ નંગ</td>
</tr>

<tr class="section">
<td colspan="3">મીટર વિગતો (Meter Details)</td>
</tr>

<tr>
<td width="30%">કંપની</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>ટાઈપ</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>કેપેસિટી</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>આંટા</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>મીટર નંબર</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>લેબ નંબર</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>રીડિંગ</td>
<td colspan="2">________________</td>
</tr>

<tr>
<td>બોડી સીલ</td>
<td colspan="2">________________</td>
</tr>

</table>

<br>

<table>

<tr class="section">
<td colspan="3">૬. સીલ ની વિગત</td>
</tr>

<tr>
<td width="30%">ટર્મિનલ સીલ</td>
<td colspan="2">______________________</td>
</tr>

<tr>
<td>SMC Box સીલ</td>
<td colspan="2">______________________</td>
</tr>

<tr>
<td colspan="3" class="section">૭. મીટર બોર્ડ</td>
</tr>

<tr>
<td colspan="3">મીટર બોર્ડ __________ નંગ (TKJ / ZP Only)</td>
</tr>

<tr>
<td colspan="3" class="section">૮. ઇન્સ્યુલેટર વિગતો</td>
</tr>

<tr>
<td colspan="3">
રીલ ઇન્સ્યુલેટર ______ નંગ | એગ ઇન્સ્યુલેટર ______ નંગ | GI વાયર 10 ______ મીટર
</td>
</tr>

<tr>
<td colspan="3" class="section">૯. અર્થિંગ</td>
</tr>

<tr>
<td colspan="3">
અરથીંગ વાયર ______ મીટર | અરથીંગ પાઇપ ______ નંગ
</td>
</tr>

<tr>
<td colspan="3" class="section">૧૦. મીટર પેટી</td>
</tr>

<tr>
<td colspan="3">
મીટર પેટી ની ઊંચાઈ ૫ ફિટ કરતાં વધારે નથી (હા/ના)? __________
</td>
</tr>

<tr>
<td colspan="3">
મીટર / મીટર પેટી / સીલિંગ તથા સર્વિસ લાઇન ગ્રાહક તરીકે સાચવવાની સંપૂર્ણ જવાબદારી મારી છે.
</td>
</tr>

</table>

<br><br>

<table>

<tr>
<td style="text-align:center">ગ્રાહકની સહી</td>
<td style="text-align:center">કર્મચારી ની સહી</td>
<td style="text-align:center">જુ.ઇ. સહી</td>
<td style="text-align:center">ના.ઇ. સહી</td>
</tr>

</table>

</body>
</html>
"""

    return base64.b64encode(html.encode("utf-8")).decode()

# ---------------------------------------------------
# PROCESS FILE
# ---------------------------------------------------

if file:

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    df["SR Type"] = df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"] = df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()

    df = df[df["SR Type"].str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].str.lower() != "spa schemes"]

# ---------------------------------------------------
# SR TYPE FILTER
# ---------------------------------------------------

    selected_types=[]

    if show_shift:
        selected_types.append("Connection Shifting(Non Cons)")
    if show_pmsy:
        selected_types.append("PMSY RTS")
    if show_rooftop:
        selected_types.append("LT Rooftop")

    if selected_types:
        df=df[df["SR Type"].isin(selected_types)]

# ---------------------------------------------------
# SCHEME FILTER
# ---------------------------------------------------

    scheme_list=sorted(df["Name Of Scheme"].dropna().unique())

    scheme_filter=st.sidebar.selectbox("Name Of Scheme",["All"]+scheme_list)

    if scheme_filter!="All":
        df=df[df["Name Of Scheme"]==scheme_filter]

# ---------------------------------------------------
# SURVEY CATEGORY FILTER
# ---------------------------------------------------

    survey_list=sorted(df["Survey Category"].dropna().unique())

    survey_filter=st.selectbox("Select Survey Category",["All"]+survey_list)

    if survey_filter!="All":
        df=df[df["Survey Category"]==survey_filter]

# ---------------------------------------------------
# SERIAL NUMBER
# ---------------------------------------------------

    df.insert(0,"Sr No",range(1,len(df)+1))

# ---------------------------------------------------
# PRINT DATA
# ---------------------------------------------------

    def generate_print(row):

        if pd.notna(row.get("Date Of TR Recv")) and pd.notna(row.get("TR MR No")):
            return create_release_html(row)

        return ""

    df["release_html"]=df.apply(generate_print,axis=1)

    df.insert(1,"Print","")

    st.metric("Total Records",len(df))

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

if(b64=="") return;

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

    gb=GridOptionsBuilder.from_dataframe(df)

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
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=650
    )

else:
    st.info("Upload PPR file to begin")
