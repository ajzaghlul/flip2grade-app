# Flip2Grade MVP: Card Analyzer Backend + Frontend (Streamlit UI)

import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# --- Core Function to Get eBay Sold Listings ---
def get_ebay_sold_listings(query, max_results=10):
    base_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=13&LH_Sold=1&LH_Complete=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.select(".s-item")[:max_results]:
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        date = item.select_one(".s-item__title--tagblock")
        link = item.select_one(".s-item__link")

        if title and price and link:
            results.append({
                "Title": title.get_text(),
                "Price": price.get_text(),
                "Date": date.get_text() if date else "",
                "URL": link['href']
            })

    return pd.DataFrame(results)

# --- Streamlit Frontend ---
st.set_page_config(page_title="Flip2Grade MVP", layout="wide")
st.title("📈 Flip2Grade - Card Value Analyzer")

st.write("""
Compare raw and PSA 10 card prices to find flip opportunities.
Start by entering a search term below (e.g., "2024 Bowman Chrome Jackson Holliday PSA 10").
""")

query = st.text_input("Enter your search query:", "2024 Bowman Chrome Jackson Holliday PSA 10")
max_results = st.slider("Max number of results to show:", 5, 50, 15)

if st.button("Search eBay Sold Listings"):
    with st.spinner("Fetching data from eBay..."):
        results_df = get_ebay_sold_listings(query, max_results)
        if not results_df.empty:
            st.success(f"Found {len(results_df)} sold listings.")
            st.dataframe(results_df, use_container_width=True)
        else:
            st.warning("No sold listings found. Try a different search.")
