import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PIL import Image

# Set up Streamlit app with custom styling
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom CSS for UI styling
st.markdown("""
    <style>
        .main {
            background-color: #f0f2f6;
        }
        .stTitle {
            color: #ffffff;
            background-color: #FF4B4B;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            font-size: 30px;
            font-weight: bold;
        }
        .uploadedFile {
            border: 2px solid #FF4B4B;
            padding: 10px;
            border-radius: 5px;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown('<p class="stTitle">🚀 Data Sweeper: Clean and Visualize Your Data</p>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("🔧 Options")
st.sidebar.write("Upload and manage your data easily!")

# File uploader
uploaded_files = st.file_uploader("📂 Upload your files:", type=None, accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        # Display file details in a box
        st.markdown(f"""
            <div class="uploadedFile">
                <strong>📄 File Name:</strong> {file.name} <br>
                <strong>📏 File Size:</strong> {file.size / 1024:.2f} KB <br>
                <strong>📂 File Type:</strong> {file_ext}
            </div>
        """, unsafe_allow_html=True)

        # Process CSV & Excel
        if file_ext == ".csv":
            df = pd.read_csv(file)
            st.write("### 📊 CSV File Preview:")
            st.dataframe(df.head())

        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
            st.write("### 📊 Excel File Preview:")
            st.dataframe(df.head())

        # Display Image
        elif file_ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file)
            st.image(img, caption=f"🖼️ Uploaded Image: {file.name}", use_column_width=True)

        # Read and display text content
        elif file_ext in [".txt", ".json", ".html"]:
            content = file.read().decode("utf-8")
            st.write("### 📜 File Content:")
            st.code(content[:1000])  # Show first 1000 characters

        # Data Cleaning Options
        if file_ext in [".csv", ".xlsx"]:
            st.subheader(f"🧹 Data Cleaning for {file.name}")
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Handle Missing Values in {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing values handled!")

            # Select Columns to Keep
            st.subheader("📝 Select Columns to Keep")
            selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]

            # Data Visualization
            st.subheader("📈 Data Visualization")
            if st.checkbox(f"📊 Show Visualization for {file.name}"):
                num_cols = df.select_dtypes(include='number').iloc[:, :2]
                if not num_cols.empty:
                    st.bar_chart(num_cols)
                else:
                    st.warning(f"⚠ No numeric columns found for visualization.")

            # File Conversion
            st.subheader("🔄 File Conversion")
            conversions_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"radio_{file.name}")

            if st.button(f"🔽 Convert {file.name}"):
                buffer = BytesIO()
                file_name = file.name.replace(file_ext, f".{conversions_type.lower()}")
                mime_type = "text/csv" if conversions_type == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                if conversions_type == "CSV":
                    df.to_csv(buffer, index=False)
                else:
                    df.to_excel(buffer, index=False)

                buffer.seek(0)
                st.download_button(
                    label=f"⬇️ Download {file.name} as {conversions_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

st.success("✅ All files processed successfully!")
