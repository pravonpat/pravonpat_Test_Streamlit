import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

st.set_page_config(page_title="📊 Data Explorer", layout="wide")

st.title("📁 Data Viewer + Custom Graph Generator")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV หรือ Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # อ่านไฟล์ CSV หรือ Excel พร้อมให้แถวแรกเป็น header
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, header=0)  # แถวแรกเป็น header
        else:
            df = pd.read_excel(uploaded_file, header=0)  # แถวแรกเป็น header

        # ปรับดัชนี (index) ให้เริ่มจาก 1 แทน 0
        df.index = df.index + 1

        st.success("✅ โหลดข้อมูลสำเร็จแล้ว")
        st.caption(f"🔢 จำนวนข้อมูล: {df.shape[0]:,} แถว | {df.shape[1]} คอลัมน์")
        st.dataframe(df, use_container_width=True)

        # เลือกคอลัมน์ที่ต้องการแสดง
        with st.expander("🧮 เลือกคอลัมน์"):
            selected_columns = st.multiselect(
                "เลือกคอลัมน์ที่จะแสดง", options=df.columns.tolist(), default=df.columns.tolist()
            )
            df_selected = df[selected_columns]
            st.dataframe(df_selected, use_container_width=True)

        # กรองแถวก่อนพล็อต
        st.subheader("🔍 เลือกข้อมูลที่ต้องการพล็อต")
        transpose = st.checkbox("🔄 สลับแถวกับคอลัมน์", value=False)
        df_numeric = df_selected.select_dtypes(include="number")

        if transpose:
            df_numeric = df_numeric.T
            df_numeric["column_id"] = df_numeric.index.astype(str)
            row_ids = df_numeric["column_id"].tolist()
        else:
            df_numeric["row_id"] = df_numeric.index.astype(str)
            row_ids = df_numeric["row_id"].tolist()

        selected_rows = st.multiselect("เลือกแถวที่จะแสดงกราฟ", options=row_ids, default=row_ids[:30])

        # เลือกชนิดกราฟ
        chart_type = st.selectbox("📈 เลือกชนิดกราฟ", ["line", "bar", "area"])

        # เตรียมข้อมูลสำหรับพล็อต
        if transpose:
            df_numeric = df_numeric[df_numeric["column_id"].isin(selected_rows)]
            df_melted = df_numeric.reset_index().melt(id_vars="column_id", var_name="row", value_name="value")
            x_col, y_col, group_col = "value", "row", "column_id"
            orientation = "h"
        else:
            df_numeric = df_numeric[df_numeric["row_id"].isin(selected_rows)]
            df_melted = df_numeric.melt(id_vars="row_id", var_name="column", value_name="value")
            x_col, y_col, group_col = "value", "column", "row_id"
            orientation = "h"

        # วาดกราฟ
        if chart_type == "line":
            fig = px.line(df_melted, x=x_col, y=y_col, color=group_col, markers=True, orientation=orientation)
        elif chart_type == "bar":
            fig = px.bar(df_melted, x=x_col, y=y_col, color=group_col, orientation=orientation)
        else:
            fig = px.area(df_melted, x=x_col, y=y_col, color=group_col, orientation=orientation)

        fig.update_layout(height=600, title="📊 กราฟตามข้อมูลที่เลือก", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
else:
    st.info("⏳ กรุณาอัปโหลดไฟล์ข้อมูลก่อน")
