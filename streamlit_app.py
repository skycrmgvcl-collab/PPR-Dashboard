import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
from datetime import datetime

st.set_page_config(page_title="PPR Release Dashboard", layout="wide")

st.title("💰 PPR Release Form Dashboard")

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

file = st.file_uploader("Upload PPR File", type=["xlsx","xls","csv"])

# ---------------------------------------------------
# RELEASE FORM HTML
# ---------------------------------------------------

def create_release_html(row):

    html=f"""
    <html>
    <head>
    <meta charset="UTF-8">

    <style>

    @page {{ size:A4; margin:10mm; }}

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
    <td width="30%">SR No</td>
    <td class="line">{row.get("SR Number","")}</td>
    </tr>

    <tr>
    <td>Applicant</td>
    <td class="line">{row.get("Name Of Applicant","")}</td>
    </tr>

    <tr>
    <td>Scheme</td>
    <td class="line">{row.get("Name Of Scheme","")}</td>
    </tr>

    <tr>
    <td>Load</td>
    <td class="line">{row.get("Demand Load","")}</td>
    </tr>

    <tr>
    <td>Survey Category</td>
    <td class="line">{row.get("Survey Category","")}</td>
    </tr>

    <tr>
    <td>Test Report Date</td>
    <td class="line">{row.get("Date of TR Revc","")}</td>
    </tr>

    <tr>
    <td>Receipt No</td>
    <td class="line">{row.get("TR MR No","")}</td>
    </tr>

    </table>

    <br>

    <div>
    મીટર / મીટર પેટી / સીલિંગ તથા સર્વિસ લાઇન ગ્રાહક તરીકે સાચવવાની સંપૂર્ણ જવાબદારી મારી છે.
    </div>

    <br>

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

    return base64.b64encode(html.encode()).decode()


# ---------------------------------------------------
# PROCESS FILE
# ---------------------------------------------------

if file:

    if file.name.endswith(".csv"):
        df=pd.read_csv(file)
    else:
        df=pd.read_excel(file)

    df.columns=df.columns.str.strip()

    df.insert(0,"Sr No",range(1,len(df)+1))

# ---------------------------------------------------
# SEARCH SR NUMBER
# ---------------------------------------------------

    search=st.text_input("🔎 Search SR Number")

    if search:
        df=df[df["SR Number"].astype(str).str.contains(search)]

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

    schemes=sorted(df["Name Of Scheme"].dropna().unique())

    scheme=st.sidebar.selectbox("Name Of Scheme",["All"]+schemes)

    if scheme!="All":
        df=df[df["Name Of Scheme"]==scheme]

    sr_types=sorted(df["SR Type"].dropna().unique())

    sr=st.sidebar.selectbox("SR Type",["All"]+sr_types)

    if sr!="All":
        df=df[df["SR Type"]==sr]

# ---------------------------------------------------
# DATE CONVERSION
# ---------------------------------------------------

    df["Date of TR Revc"]=pd.to_datetime(df["Date of TR Revc"],errors="coerce")

    if "Date Of Release Conn" in df.columns:
        df["Date Of Release Conn"]=pd.to_datetime(df["Date Of Release Conn"],errors="coerce")

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

    tab1,tab2=st.tabs(["All Records","Release Pending"])

# ---------------------------------------------------
# ALL RECORDS
# ---------------------------------------------------

    with tab1:

        st.subheader("All Records")

        AgGrid(df,height=600,fit_columns_on_grid_load=True)

# ---------------------------------------------------
# RELEASE PENDING
# ---------------------------------------------------

    with tab2:

        release_df=df[
        (df["Date of TR Revc"].notna()) &
        (df["Date Of Release Conn"].isna())
        ].copy()

# ---------------------------------------------------
# AGING DAYS
# ---------------------------------------------------

        today=pd.Timestamp.today()

        release_df["Aging Days"]=(today-release_df["Date of TR Revc"]).dt.days

# ---------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------

        c1,c2,c3=st.columns(3)

        c1.metric("Total Release Pending",len(release_df))

        c2.metric("TR Received",release_df["Date of TR Revc"].notna().sum())

        c3.metric("Average Aging",int(release_df["Aging Days"].mean()) if len(release_df)>0 else 0)

# ---------------------------------------------------
# EXPORT BUTTON
# ---------------------------------------------------

        st.download_button(
        "📥 Export Release Pending List",
        release_df.to_csv(index=False),
        file_name="release_pending.csv"
        )

# ---------------------------------------------------
# BULK PRINT DATA
# ---------------------------------------------------

        release_df["release_html"]=release_df.apply(create_release_html,axis=1)

        release_df.insert(1,"Print","")

# ---------------------------------------------------
# PRINT ICON
# ---------------------------------------------------

        renderer=JsCode("""

class Renderer{

init(params){

this.eGui=document.createElement('span');
this.eGui.innerHTML='🖨';
this.eGui.style.cursor='pointer';

this.eGui.addEventListener('click',()=>{

const b64=params.data.release_html;

if(!b64) return;

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

# ---------------------------------------------------
# GRID
# ---------------------------------------------------

        gb=GridOptionsBuilder.from_dataframe(release_df)

        gb.configure_default_column(filter=True,sortable=True,resizable=True)

        gb.configure_column("Print",cellRenderer=renderer,width=70)

        gb.configure_column("release_html",hide=True)

        AgGrid(
        release_df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        height=650,
        fit_columns_on_grid_load=True
        )

else:

    st.info("Upload PPR file to begin")
