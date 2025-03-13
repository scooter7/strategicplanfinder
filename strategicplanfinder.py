import streamlit as st
import requests
import re
import pandas as pd
from urllib.parse import urlparse

# Helper: perform a Google Custom Search API request
def google_search(query):
    api_key = st.secrets["GOOGLE_API_KEY"]
    cse_id = st.secrets["GOOGLE_CSE_ID"]
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Google API error: {response.status_code}")
        return {}

# Helper: extract a years range (e.g. "2025-2030") from a text snippet
def extract_years(text):
    # Match patterns like "2025-2030" or "2025 - 2030"
    pattern = r'\b(20\d{2}\s*-\s*20\d{2})\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

# Helper: search for enrollment information from a domain
def search_enrollment(domain):
    # Query enrollment info on the given domain.
    query = f"site:{domain} enrollment"
    result = google_search(query)
    enrollment = ""
    if "items" in result:
        for item in result["items"]:
            snippet = item.get("snippet", "")
            # Look for a number formatted with or without commas, e.g. "15,000" or "15000"
            num_match = re.search(r'(\d{1,3}(?:,\d{3})+|\d{4,})', snippet)
            if num_match:
                enrollment = num_match.group(1)
                break
    return enrollment

def main():
    st.title("Community College Strategic Plan Search")
    st.write(
        "This app uses a custom Google search engine (configured to search community college websites) "
        "to look for the term 'strategic plan.' For each result, it extracts the URL, a text snippet referencing the plan, "
        "a years range (e.g., 2025-2030), and then performs a secondary search on the website to find enrollment numbers. "
        "Only results from .edu domains are considered."
    )

    # Optionally, you could include site:.edu in the search query
    search_query = "strategic plan site:.edu"
    st.info("Searching for strategic plan references on .edu websites...")
    search_results = google_search(search_query)
    
    results_data = []
    if "items" in search_results:
        for item in search_results["items"]:
            url = item.get("link", "")
            # Check if the URL is from a .edu domain
            domain = urlparse(url).netloc
            if not domain.endswith(".edu"):
                continue  # Skip if not a .edu domain
            snippet = item.get("snippet", "")
            years_range = extract_years(snippet)
            enrollment = search_enrollment(domain)
            results_data.append({
                "URL": url,
                "Enrollment Size": enrollment,
                "Strategic Plan Text": snippet,
                "Years Referenced": years_range,
            })
    else:
        st.warning("No results found. Check your custom search engine configuration or API keys.")

    if results_data:
        df = pd.DataFrame(results_data)
        st.subheader("Search Results")
        st.dataframe(df)
    else:
        st.info("No data to display.")

if __name__ == "__main__":
    main()
