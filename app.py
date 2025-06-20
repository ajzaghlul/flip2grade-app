# Flip2Grade MVP: Card Analyzer Using eBay Browse API + Streamlit

import requests
import pandas as pd
import streamlit as st

# --- Replace this with your actual eBay App ID ---
EBAY_APP_ID = "YOUR_EBAY_APP_ID"

# --- eBay Browse API Function ---
def get_ebay_sold_items(query, max_results=10):
    headers = {
        "X-EBAY-C-ENDUSERCTX": "contextualLocation=country=US",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-APP-ID": EBAY_APP_ID,
        "Content-Type": "application/json",
    }
    params = {
        "q": query,
        "limit": max_results,
        "filter": "buyingOptions:{FIXED_PRICE},conditions:{NEW|USED},price:[10..10000]",
        "sort": "price",
    }
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"

    data = response.json()
    items = data.get("itemSummaries", [])

    results = []
    for item in items:
        results.append({
            "Title": item.get("title"),
            "Price": f"{item['price']['value']} {item['price']['currency']}" if 'price' in item else "",
            "Condition": item.get("condition", ""),
            "URL": item.get("itemWebUrl")
        })

    return pd.DataFrame(results)

# --- Streamlit Frontend ---
st.set_page_config(page_title="Flip2Grade MVP", layout="wide")
st.title("📈 Flip2Grade - Card Value Analyzer (eBay API Edition)")

st.write("""
Compare raw and PSA 10 card prices to find flip opportunities.
This version uses the official eBay API for improved reliability.
""")

query = st.text_input("Enter your search query:", "2024 Bowman Chrome Jackson Holliday PSA 10")
max_results = st.slider("Max number of results to show:", 5, 50, 15)

if st.button("Search eBay Listings"):
    with st.spinner("Fetching data from eBay API..."):
        listings = get_ebay_sold_items(query, max_results)

        if isinstance(listings, str) and listings.startswith("ERROR"):
            st.error(f"Failed to fetch listings: {listings}")
        elif not listings.empty:
            st.success(f"Found {len(listings)} listings.")
            st.dataframe(listings, use_container_width=True)
        else:
            st.warning("No listings found. Try a broader search term.")
