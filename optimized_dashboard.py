import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📸 Optimized Auditor Image Review Dashboard")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.stop()

try:
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time Stamp'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
df.dropna(subset=['Date'], inplace=True)
df.fillna("Not Available", inplace=True)
df.sort_values(by="DateTime", inplace=True)

with st.form("filters"):
    st.subheader("Filter Panel")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cluster = st.selectbox("🌍 Cluster", ['All'] + sorted(df['Cluster'].unique()))
    df1 = df if cluster == 'All' else df[df['Cluster'] == cluster]

    with c2:
        asm = st.selectbox("👔 ASM", ['All'] + sorted(df1['ASM'].unique()))
    df2 = df1 if asm == 'All' else df1[df1['ASM'] == asm]

    with c3:
        sde = st.selectbox("👨‍💼 SDE", ['All'] + sorted(df2['SDE'].unique()))
    df3 = df2 if sde == 'All' else df2[df2['SDE'] == sde]

    with c4:
        auditor = st.selectbox("🕵️ Auditor", ['All'] + sorted(df3['Auditor Name'].unique()))
    df4 = df3 if auditor == 'All' else df3[df3['Auditor Name'] == auditor]

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        dist = st.selectbox("🏢 Distributor Code", ['All'] + sorted(df4['Distributor Code'].astype(str).unique()))
    df5 = df4 if dist == 'All' else df4[df4['Distributor Code'].astype(str) == dist]

    with c6:
        salesman = st.selectbox("🧍 Salesman", ['All'] + sorted(df5['Salesman'].unique()))
    df6 = df5 if salesman == 'All' else df5[df5['Salesman'] == salesman]

    with c7:
        route = st.selectbox("🛣️ Route", ['All'] + sorted(df6['route_name'].unique()))
    df7 = df6 if route == 'All' else df6[df6['route_name'] == route]

    with c8:
        outlet = st.selectbox("🏬 Outlet Name", ['All'] + sorted(df7['Outlet Name'].unique()))
    df8 = df7 if outlet == 'All' else df7[df7['Outlet Name'] == outlet]

    c9, c10 = st.columns(2)
    with c9:
        absent = st.selectbox("❌ Absent Reason", ['All'] + sorted(df8['Absent Reason'].unique()))
    with c10:
        search = st.text_input("🔍 Global Search")

    from_date = st.date_input("📅 From Date", value=df8['Date'].min().date())
    to_date = st.date_input("📅 To Date", value=df8['Date'].max().date())

    col_submit = st.columns(2)
    with col_submit[0]:
        submit = st.form_submit_button("✅ Apply")
    with col_submit[1]:
        reset = st.form_submit_button("🔄 Reset")

if reset:
    st.experimental_rerun()

filtered = df8.copy()
if submit:
    if absent != 'All':
        filtered = filtered[filtered['Absent Reason'] == absent]
    filtered = filtered[(filtered['Date'].dt.date >= from_date) & (filtered['Date'].dt.date <= to_date)]
    if search:
        search = search.lower()
        filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)]

page_size = 10
total_pages = max(1, (len(filtered) - 1) // page_size + 1)
page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
start = (page - 1) * page_size
end = start + page_size
paginated = filtered.iloc[start:end]

buffer = BytesIO()
filtered.to_excel(buffer, index=False)
st.download_button("📥 Download Filtered Excel", data=buffer.getvalue(),
                   file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

for i, row in paginated.iterrows():
    st.markdown("---")
    st.markdown(f"<div style='font-size:12px;'>🔢 S.No: {i+1}</div>", unsafe_allow_html=True)
    st.markdown(f"### 🕵️ Auditor: **{row['Auditor Name']}**")
    st.markdown(f"""
    - 📅 DateTime: {row['DateTime']}
    - 🏢 Distributor: {row['Distributor Name']} ({row['Distributor Code']})
    - 🛣️ Route: {row['route_name']}
    - 🧍 Salesman: {row['Salesman']}
    - 🧑‍💼 SDE: {row['SDE']} | 👔 ASM: {row['ASM']}
    - 🌍 Cluster: {row['Cluster']}
    - 🏬 Outlet: {row['Outlet Name']} | Code: {row['Outlet Code']}
    - ❌ Absent Reason: {row['Absent Reason']}
    """)

    img_fields = ['Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Image 6']
    for j in range(0, len(img_fields), 3):
        cols = st.columns(3)
        for k, img_col in enumerate(img_fields[j:j+3]):
            img_url = row[img_col]
            if img_url != "Not Available" and str(img_url).strip():
                cols[k].image(img_url, caption=img_col, width=200)
            else:
                cols[k].write("📷 Image not available")
