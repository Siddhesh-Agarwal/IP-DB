import socket

import pymongo
import streamlit as st


def get_domain(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = url.split("/", 1)[0]
    return domain


@st.cache_resource
def get_mongo_collection():
    uri = st.secrets["mongo_uri"]
    # Connect to MongoDB
    client = pymongo.MongoClient(uri)

    # check if connection is successful
    try:
        client.admin.command("ping")
        # st.success("Connection to MongoDB successful")
    except:
        # st.error("Connection to MongoDB failed")
        return get_mongo_collection()

    # Create database
    db = client["ipdb"]
    # Create collection
    collection = db["ipdb"]
    return collection


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
collection = get_mongo_collection()

with tabs[0]:
    url = st.text_input("Enter URL")
    if st.button("Find"):
        with st.spinner("Finding IP Address..."):
            # get domain
            domain = get_domain(url)
            try:
                # get ip address
                ip_address = socket.gethostbyname(domain)
                # show ip address
                st.success(ip_address)
                # check if domain exists
                if collection.find_one({"domain": domain}):
                    st.info(f"Domain {domain} already exists in the database")
                else:
                    collection.insert_one({"domain": domain, "ip_address": ip_address})
            except socket.gaierror:
                st.error("Invalid URL")


with tabs[1]:
    # get IP address
    ip_address = st.text_input("Enter IP Address")
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
                    st.success(f"IP Address {ip_address} exists {count} times")
                    st.info(
                        "City, Country, ISP, Organization, Timezone, etc. (Coming Soon!)"
                    )
                    with st.expander("Domains"):
                        st.write(domains)
                else:
                    st.error(f"IP Address {ip_address} does not exist")
        else:
            st.error("Please enter an IP Address")
