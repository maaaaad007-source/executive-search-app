import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Executive Sourcing Portal", layout="wide")

st.title("🏢 Automated Executive Sourcing Portal")
st.write("Find key decision-makers (CEO, Design, UX, Product, HR) across targeted organizations.")

company_domain = st.text_input("Company Domain (e.g., ikea.com, spotify.com):", "")
api_key = st.text_input("Hunter.io API Key:", type="password")

if st.button("Search Personnel"):
    if not company_domain:
        st.warning("Please enter a company domain.")
    elif not api_key:
        st.warning("Please enter your Hunter.io API Key.")
    else:
        domain = company_domain.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip()
        st.info(f"Searching key personnel for: **{domain}**...")

        # Hunter.io Domain Search API
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key.strip()}"

        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                emails = data.get("emails", [])

                if emails:
                    target_roles = ["ceo", "chief executive", "founder", "director", "human resource", "user experience", "design", "ux", "product", "hr", "people", "talent"]
                    filtered_people = []

                    for person in emails:
                        position = (person.get("position") or "").lower()
                        # Filter for target decision-makers or list executives
                        if any(role in position for role in target_roles) or not position:
                            filtered_people.append({
                                "Name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip() or "N/A",
                                "Title": person.get("position") or "N/A",
                                "Company": data.get("organization", domain),
                                "Email": person.get("value", "N/A"),
                                "Confidence": f"{person.get('confidence', 0)}%",
                                "LinkedIn": person.get("linkedin") or ""
                            })

                    if filtered_people:
                        st.success(f"Found {len(filtered_people)} personnel record(s)!")
                        df = pd.DataFrame(filtered_people)
                        st.dataframe(
                            df, 
                            column_config={
                                "LinkedIn": st.column_config.LinkColumn("LinkedIn Profile")
                            },
                            use_container_width=True
                        )
                    else:
                        st.warning("No personnel found matching the target executive titles.")
                else:
                    st.warning("No emails found for this domain.")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
