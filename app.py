import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Executive Sourcing Portal", layout="wide")

st.title("🏢 Automated Executive Sourcing Portal")
st.write("Find key decision-makers (CEO, Design, UX, Product, HR) across targeted organizations.")

# Input fields
company_domain = st.text_input("Company Name or Domain (e.g., spotify.com, volvo.com):", "")
api_key = st.text_input("Apollo.io API Key:", type="password")

if st.button("Search Personnel"):
    if not company_domain:
        st.warning("Please enter a company name or domain.")
    elif not api_key:
        st.warning("Please enter your Apollo.io API Key.")
    else:
        # Clean domain input
        domain = company_domain.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip()

        st.info(f"Searching key personnel for: **{domain}**...")

        # Apollo.io API endpoint
        url = "https://api.apollo.io/api/v1/mixed_people/search"

        # Headers requiring X-Api-Key
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": api_key.strip()
        }

        # Query payload targeted at key executive roles
        payload = {
            "q_organization_domains": [domain],
            "page": 1,
            "per_page": 25,
            "person_titles": [
                "Chief Executive Officer", "CEO", 
                "Design Director", "Director of Design", 
                "UX Director", "Director of UX", "Head of UX",
                "Product Design Director", "Director of Product Design", 
                "Head of HR", "HR Director", "VP of HR", "Chief People Officer"
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                people = data.get("people", [])

                if people:
                    st.success(f"Found {len(people)} key executive profile(s)!")

                    # Process results into a clean table
                    results = []
                    for person in people:
                        name = person.get("name", "N/A")
                        title = person.get("title", "N/A")
                        org_name = person.get("organization", {}).get("name", domain)
                        email = person.get("email", "Not available")
                        linkedin_url = person.get("linkedin_url", "")

                        results.append({
                            "Name": name,
                            "Title": title,
                            "Company": org_name,
                            "Email": email,
                            "LinkedIn": linkedin_url
                        })

                    df = pd.DataFrame(results)
                    st.dataframe(
                        df, 
                        column_config={
                            "LinkedIn": st.column_config.LinkColumn("LinkedIn Profile")
                        },
                        use_container_width=True
                    )
                else:
                    st.warning("No matching executive profiles found for target roles. Try using the exact domain name (e.g., spotify.com).")

            else:
                st.error(f"API Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"An error occurred while making the request: {e}")
