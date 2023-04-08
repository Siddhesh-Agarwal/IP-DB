import socket

import pymongo
import requests
import streamlit as st


def get_domain(url: str) -> str:
    url = url.lower()
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = url.split("/", 1)[0]
    return domain


@st.cache_resource
def get_mongo_collection(uri: str):
    # Connect to MongoDB
    client = pymongo.MongoClient(uri)
    # Create database
    db = client["ipdb"]
    # Create collection
    collection = db["ipdb"]
    # Return collection
    return collection


def get_location(ip_address: str) -> dict:
    url = requests.get(f"http://ip-api.com/json/{ip_address}")
    return url.json()


st.set_page_config(
    page_title="IP DB",
    page_icon=":mag_right:",
    menu_items={
        "Get Help": "https://github.com/Siddhesh-Agarwal/IP-DB/issues",
        "Report a bug": "https://github.com/Siddhesh-Agarwal/IP-DB/issues",
        "About": open("./README.md").read(),
    },
)

st.title(":mag_right: IP DB")

tabs = st.tabs(["Add", "Search"])
with st.spinner("Connecting to database..."):
    collection = get_mongo_collection(st.secrets["uri"])

with tabs[0]:
    url = st.text_input(
        label="Enter URL",
        placeholder="https://www.google.com",
    ).strip()
    if st.button("Find"):
        with st.spinner("Finding IP Address..."):
            # get domain
            domain = get_domain(url)
            try:
                # get ip address
                ip_address = socket.gethostbyname(domain)
                # show ip address
                st.info(ip_address)
                with st.spinner("Checking database..."):
                    data = {"domain": domain, "ip_address": ip_address}
                    if collection.find_one(data):
                        st.info(f"Data already exists in the database")
                    else:
                        collection.insert_one(data)
                        st.success(f"Data added to the database")
            except socket.gaierror:
                st.error("Invalid URL")
            except Exception as e:
                st.error(e)
                st.info(
                    "Refresh the site. If this problem continues to persist, report this issue [here](https://github.com/Siddhesh-Agarwal/IP-DB/issues)"
                )
                st.stop()


with tabs[1]:
    # get IP address
    ip_address = st.text_input("Enter IP Address").strip()
    if st.button("Search"):
        if ip_address:
            with st.spinner("Searching..."):
                # number of times ip_address exists
                res = collection.find({"ip_address": ip_address})
                if res:
                    count = 0
                    domains = []
                    for i in res:
                        count += 1
                        domains.append(i["domain"])
                    location = get_location(ip_address)
                    st.success(f"IP Address {ip_address} exists {count} times")
                    st.info(
                        f"**Location:** {location['city']}, {location['country']} ({location['countryCode']})"
                    )
                    if count == 1:
                        st.info(f"**Domain:** {domains[0]}")
                    if count > 1:
                        with st.expander("Domains"):
                            st.write(domains)
                    with st.expander("Details"):
                        st.write(location)
                else:
                    st.error(f"IP Address {ip_address} does not exist")
        else:
            st.error("Please enter an IP Address")
