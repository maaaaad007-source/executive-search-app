import streamlit as st
import requests
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Executive Personnel Finder", layout="wide")

st.title("🏢 Automated Executive Sourcing Portal")
st.subheader("Enter a company name to find key decision-makers (CEO, Design, UX, Product, HR)")

# User Inputs
company_input = st.text_input("Company Name or Domain (e.g., Spotify, Volvo, spotify.com):", "")
api_key = st.text_input("Apollo.io API Key:", type="password", help="Get a free API key at apollo.io")

# Target Job Titles
TARGET_TITLES = [
    "Chief Executive Officer", "CEO", "Managing Director",
    "Design Director", "Head of Design",
    "UX Director", "Head of UX",
    "Product Design Director", "Head of Product Design",
    "Head of HR", "Chief People Officer", "VP Human Resources"
]

def search_executives(company_name, apollo_key):
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": apollo_key,
        "q_organization_domains": [company_name] if "." in company_name else [],
        "q_keywords": company_name if "." not in company_name else "",
        "person_titles": TARGET_TITLES,
        "page": 1,
        "per_page": 25
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        people = data.get("people", [])
        
        results = []
        for person in people:
            results.append({
                "Name": person.get("name", "N/A"),
                "Title": person.get("title", "N/A"),
                "Company": person.get("organization", {}).get("name", company_name),
                "Email Status": person.get("email_status", "N/A"),
                "LinkedIn": person.get("linkedin_url", "N/A"),
                "Location": f"{person.get('city', '')}, {person.get('country', '')}".strip(", ")
            })
        return pd.DataFrame(results)
        
    else:
        st.error(f"API Error {response.status_code}: {response.text}")
        return pd.DataFrame()

if st.button("Search Personnel"):
    if not company_input:
        st.warning("Please enter a company name or domain.")
    elif not api_key:
        st.warning("Please enter your API Key to fetch live contacts.")
    else:
        with st.spinner(f"Searching key personnel for '{company_input}'..."):
            df_results = search_executives(company_input, api_key)
            
            if not df_results.empty:
                st.success(f"Found {len(df_results)} key executive profiles!")
                st.dataframe(df_results, use_container_width=True)
                
                # CSV Export Option
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Personnel Results as CSV",
                    data=csv,
                    file_name=f"{company_input}_executives.csv",
                    mime="text/csv"
                )
            else:
                st.info("No matching profiles found for the target titles. Try entering the exact domain name (e.g., spotify.com).")
