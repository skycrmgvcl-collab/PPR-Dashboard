import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="PPR Paid Pending Dashboard", layout="wide")

st.markdown("## 💰 Paid Pending Report (PPR) Dashboard")
st.caption("Survey Category Wise Monitoring")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

show_shift = st.sidebar.checkbox("Connection Shifting (Non Cons)")
show_pmsy = st.sidebar.checkbox("PMSY RTS")
show_rooftop = st.sidebar.checkbox("LT Rooftop")

# =====================================================
# FILE UPLOAD
# =====================================================

file = st.file_uploader("Upload PPR Excel/CSV File", type=["xlsx","xls","csv"])

if file:

    # ================= READ FILE =================

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file, engine="openpyxl")
    else:
        df = pd.read_excel(file, engine="xlrd")

    # ================= CLEAN IMPORTANT COLUMNS =================

    df["SR Type"] = df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"] = df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()
    df["SR Status"] = df["SR Status"].astype(str).str.strip()

    # ================= REMOVE EXCLUDED =================

    df = df[df["SR Type"].str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].str.lower() != "spa schemes"]

    # ================= SR TYPE FILTER =================

    selected_types = []

    if show_shift:
        selected_types.append("Connection Shifting(Non Cons)")
    if show_pmsy:
        selected_types.append("PMSY RTS")
    if show_rooftop:
        selected_types.append("LT Rooftop")

    if selected_types:
        df = df[df["SR Type"].isin(selected_types)]
    else:
        df = df[
            ~df["SR Type"].isin([
                "Connection Shifting(Non Cons)",
                "PMSY RTS",
                "LT Rooftop"
            ])
        ]

    # ================= SCHEME FILTER =================

    scheme_list = sorted(df["Name Of Scheme"].dropna().unique())

    scheme_filter = st.sidebar.selectbox(
        "Name Of Scheme",
        ["All"] + scheme_list
    )

    if scheme_filter != "All":
        df = df[df["Name Of Scheme"] == scheme_filter]

    # =====================================================
    # SURVEY CATEGORY FILTER (TOP)
    # =====================================================

    survey_list = sorted(df["Survey Category"].dropna().unique())

    survey_filter = st.selectbox(
        "Select Survey Category",
        ["All"] + survey_list
    )

    if survey_filter != "All":
        df = df[df["Survey Category"] == survey_filter]

    # =====================================================
    # REQUIRED DISPLAY COLUMNS (AS PROVIDED)
    # =====================================================

    display_columns = [
        "Name Of Subdivision","SR Number","SR Type","Name Of Applicant",
        "Address1","Address2","District","Taluka","Village Or City",
        "Consumer Category","Sub Category","Name Of Scheme",
        "Demand Load","Load Uom","Tariff","RC Date","RC MR NO",
        "RC Charge","Survey Category","Date Of Survey",
        "Date Of Est Appr Launch","Date Of Est Appr Recv",
        "TS Amount","TS No","Date Of FQ Issued","Date Of FQ Paid",
        "SD Amount","SD MR NO","HT Line Lenght","HT Line Cons Total",
        "HT Line Board Total","LT Line Lenght","LT Line Cons Total",
        "LT Line Board Total","TC Capacity","TC Board Cost",
        "Fixed Charge Consumer","Fixed Charge Board",
        "Service Conn Cons Charge","Service Conn Board Charge",
        "FQ Amount","Date Of Agreement","Date Of Int To Ei",
        "Date Of TMN Issued","Date Of TR Recv","TR MR No",
        "TR Amount","Date Of Release Conn","Consumer No",
        "Date Of WCC","Date Of H3","Date Crt Cons Ltbill",
        "SR Status","GPR No","PPR No","Area Type",
        "Rev Land Syrvey No","DT No","Feeder Code",
        "Cons Class","Agreement Charge","Agreement Receipt",
        "Fixed Charge Receipt","TC Cons Cost","Workflow Type"
    ]

    # Keep only available columns
    display_columns = [col for col in display_columns if col in df.columns]

    df = df[display_columns]

    df.insert(0, "Sr. No.", range(1, len(df)+1))

    # =====================================================
    # SUMMARY
    # =====================================================

    st.metric("Total Records", len(df))

    # =====================================================
    # GRID DISPLAY
    # =====================================================

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=130
    )

    AgGrid(
        df,
        gridOptions=gb.build(),
        fit_columns_on_grid_load=True,
        height=600,
        theme="streamlit"
    )

else:
    st.info("Upload PPR file to begin")
