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
