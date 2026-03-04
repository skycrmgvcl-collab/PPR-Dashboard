import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="PPR Release Form Dashboard", layout="wide")

st.title("💰 Paid Pending Report (PPR) Dashboard")

# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

file = st.file_uploader("Upload PPR Excel/CSV File", type=["xlsx","xls","csv"])

# ---------------------------------------------------------
# RELEASE FORM HTML
# ---------------------------------------------------------

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
font-size:16px;
}}

.title {{
text-align:center;
font-weight:bold;
font-size:17px;
margin-bottom:8px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
padding:6px;
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
padding-top:24px;
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

<div class="section">માલ સામાન વપરાશની નોંધ</div>

<div>
સર્વિસ વાયર પી.વી.સી. ______ કોર ______ એમ.એમ. ______ મીટર
</div>

<div>
ELCB Make _________ &nbsp;&nbsp; Capacity _________
</div>

<div>
1-Ph SMC બોક્ષ ______ નંગ &nbsp;&nbsp; | &nbsp;&nbsp; 3-Ph SMC બોક્ષ ______ નંગ
</div>

<br>

<div class="box">

<div class="box-title">મીટર વિગતો</div>

<table>

<tr><td width="40%">કંપની</td><td>____________</td></tr>
<tr><td>ટાઈપ</td><td>____________</td></tr>
<tr><td>કેપેસિટી</td><td>____________</td></tr>
<tr><td>આંટા</td><td>____________</td></tr>
<tr><td>મીટર નંબર</td><td>____________</td></tr>
<tr><td>લેબ નંબર</td><td>____________</td></tr>
<tr><td>રીડિંગ</td><td>____________</td></tr>
<tr><td>બોડી સીલ</td><td>____________</td></tr>

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
# ---------------------------------------------------------
# PROCESS FILE
# ---------------------------------------------------------

if file:

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    df.insert(0,"Sr No",range(1,len(df)+1))

    sr_types=sorted(df["SR Type"].dropna().unique())
    selected_sr=st.sidebar.multiselect("SR Type",sr_types,default=sr_types)

    df=df[df["SR Type"].isin(selected_sr)]

    schemes=sorted(df["Name Of Scheme"].dropna().unique())
    selected_scheme=st.sidebar.multiselect("Name Of Scheme",schemes,default=schemes)

    df=df[df["Name Of Scheme"].isin(selected_scheme)]

    def generate_print(row):

        if pd.notna(row.get("Date Of TR Recv")) and pd.notna(row.get("TR MR No")):
            return create_release_html(row)

        return ""

    df["release_html"]=df.apply(generate_print,axis=1)

    df.insert(1,"Print","")

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

    gb.configure_default_column(filter=True,sortable=True,resizable=True,flex=1,minWidth=120)

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
