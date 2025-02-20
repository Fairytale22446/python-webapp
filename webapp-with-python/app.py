# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PIL import Image

# Set up Streamlit app
st.set_page_config(page_title="Data Sweeper", layout='wide')

# Title for the app
st.title("Data Sweeper: Clean and Visualize Your Data")

# Add a description
st.write("Upload any file (CSV, Excel, Images, PDFs, HTML, JSON, etc.) and interact with the content!")

# File uploader (Allows all file types)
uploaded_files = st.file_uploader("Upload your files:", type=None, accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.write(f"**File Type:** {file_ext}")

        # Process CSV & Excel
        if file_ext == ".csv":
            df = pd.read_csv(file)
            st.write("### Preview of CSV File:")
            st.dataframe(df.head())

        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
            st.write("### Preview of Excel File:")
            st.dataframe(df.head())

        # Display Image
        elif file_ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file)
            st.image(img, caption=f"Uploaded Image: {file.name}", use_column_width=True)

        # Read and display text content
        elif file_ext in [".txt", ".json", ".html"]:
            content = file.read().decode("utf-8")
            st.write("### File Content:")
            st.code(content[:1000])  # Show first 1000 characters

        # Unsupported file message
        else:
            st.warning(f"Uploaded {file_ext} file is accepted, but not directly previewable.")

        # Data Cleaning Options (Only for CSV/Excel)
        if file_ext in [".csv", ".xlsx"]:
            st.subheader(f"Data Cleaning Options for {file.name}")
            if st.checkbox(f"Clean Data for {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Remove Duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.write("✅ Duplicates Removed!")

                with col2:
                    if st.button(f"Handle Missing Values in {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("✅ Missing values have been filled!")

            # Select specific columns for processing
            st.subheader("Select Columns to Keep")
            selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]

            # Data Visualization
            st.subheader("Data Visualization")
            if st.checkbox(f"Show Visualization for {file.name}"):
                num_cols = df.select_dtypes(include='number').iloc[:, :2]
                if not num_cols.empty:
                    st.bar_chart(num_cols)
                else:
                    st.warning(f"No numeric columns found in {file.name} for visualization.")

            # File Conversion
            st.subheader("File Conversion Options")
            conversions_type = st.radio(
                f"Convert {file.name} to:", ["CSV", "Excel"], key=f"radio_{file.name}"
            )

            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversions_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversions_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)  # ✅ Ensure correct file writing
                st.download_button(
                    label=f"Download {file.name} as {conversions_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

st.success("✅ All files processed successfully!")
