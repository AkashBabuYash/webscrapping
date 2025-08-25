import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from io import BytesIO  

st.title("🕸️ Flexible Web Scraper and Data Exporter")

url = st.text_input("Enter a URL to scrape from", "")

scrape_type = st.radio("What do you want to scrape?", ["Tag", "Class Name", "ID"])

if scrape_type == "Tag":
    user_input = st.text_input("Enter HTML tag (e.g. h1, h2, p, div)", "h2")
elif scrape_type == "Class Name":
    user_input = st.text_input("Enter class name (e.g. post-title, entry-content)", "")
elif scrape_type == "ID":
    user_input = st.text_input("Enter ID (e.g. main-header, content-box)", "")

uploaded_file = st.file_uploader("Upload existing CSV or Excel file (optional)", type=["csv", "xlsx"])

output_format = st.selectbox("Select output format", ["CSV", "Excel"])

if st.button("Scrape and Save"):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        if scrape_type == "Tag":
            elements = soup.find_all(user_input)
        elif scrape_type == "Class Name":
            elements = soup.find_all(class_=user_input)
        elif scrape_type == "ID":
            el = soup.find(id=user_input)
            elements = [el] if el else []

        extracted_text = [el.get_text(strip=True) for el in elements if el and el.get_text(strip=True)]

        scraped_df = pd.DataFrame(extracted_text, columns=["Extracted_Text"])

        if scraped_df.empty:
            st.warning("No data found with the given input.")
            st.stop()

        st.success(f"Scraped {len(scraped_df)} items.")
        st.dataframe(scraped_df)

        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format.")
                st.stop()

            if len(df) == len(scraped_df):
                df["Scraped_Data"] = scraped_df["Extracted_Text"]
            elif len(df) > len(scraped_df):
                padded = extracted_text + [np.nan] * (len(df) - len(scraped_df))
                df["Scraped_Data"] = padded
            else:
                df["Scraped_Data"] = extracted_text[:len(df)]

            st.success("Merged scraped data into uploaded file.")
            st.dataframe(df)

            if output_format == "CSV":
                st.download_button("Download Merged CSV",
                                   data=df.to_csv(index=False),
                                   file_name="merged_output.csv",
                                   mime="text/csv")
            else:
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button("Download Merged Excel",
                                   data=output,
                                   file_name="merged_output.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        else:
            if output_format == "CSV":
                st.download_button("Download CSV",
                                   data=scraped_df.to_csv(index=False),
                                   file_name="scraped_data.csv",
                                   mime="text/csv")
            else:
                output = BytesIO()
                scraped_df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button("Download Excel",
                                   data=output,
                                   file_name="scraped_data.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"An error occurred: {e}")
