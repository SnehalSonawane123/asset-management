import streamlit as st
import pandas as pd
from db import get_all_assets, add_asset, update_asset, delete_asset, get_asset_by_id

st.set_page_config(page_title="Asset Management", page_icon="🖥️", layout="wide")

st.markdown("""
<style>
    .main { background: #f8fafc; }
    h1 { color: #1e3a5f; }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

st.title("🖥️ Asset Management System")
st.caption("Track company assets, assign to employees, monitor availability")
st.divider()

menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Add Asset", "Edit Asset", "Delete Asset"])

assets = get_all_assets()
df = pd.DataFrame(assets) if assets else pd.DataFrame(columns=["id","name","status","assigned_to"])

if menu == "Dashboard":
    total     = len(df)
    available = len(df[df["status"] == "Available"]) if not df.empty else 0
    assigned  = len(df[df["status"] == "Assigned"])  if not df.empty else 0
    maintenance = len(df[df["status"] == "Maintenance"]) if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Assets",   total)
    col2.metric("Available",      available)
    col3.metric("Assigned",       assigned)
    col4.metric("In Maintenance", maintenance)

    st.subheader("All Assets")
    if df.empty:
        st.info("No assets found. Add some assets first.")
    else:
        df.columns = ["ID", "Name", "Status", "Assigned To"]
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "Add Asset":
    st.subheader("Add New Asset")
    with st.form("add_form"):
        name        = st.text_input("Asset Name", placeholder="e.g. Dell Laptop")
        status      = st.selectbox("Status", ["Available", "Assigned", "Maintenance"])
        assigned_to = st.text_input("Assigned To", placeholder="Employee name or leave blank")
        submitted   = st.form_submit_button("Add Asset")
        if submitted:
            if not name.strip():
                st.error("Asset name is required!")
            else:
                add_asset(name.strip(), status, assigned_to.strip())
                st.success(f"Asset '{name}' added successfully!")
                st.rerun()

elif menu == "Edit Asset":
    st.subheader("Edit Asset")
    if df.empty:
        st.info("No assets to edit.")
    else:
        asset_ids = df["id"].tolist()
        asset_id  = st.selectbox("Select Asset ID", asset_ids)
        asset     = get_asset_by_id(asset_id)
        if asset:
            with st.form("edit_form"):
                name        = st.text_input("Asset Name",   value=asset["name"])
                status      = st.selectbox("Status", ["Available", "Assigned", "Maintenance"],
                                           index=["Available","Assigned","Maintenance"].index(asset["status"]))
                assigned_to = st.text_input("Assigned To",  value=asset["assigned_to"] or "")
                submitted   = st.form_submit_button("Update Asset")
                if submitted:
                    if not name.strip():
                        st.error("Asset name is required!")
                    else:
                        update_asset(asset_id, name.strip(), status, assigned_to.strip())
                        st.success("Asset updated successfully!")
                        st.rerun()

elif menu == "Delete Asset":
    st.subheader("Delete Asset")
    if df.empty:
        st.info("No assets to delete.")
    else:
        asset_ids = df["id"].tolist()
        asset_id  = st.selectbox("Select Asset ID to Delete", asset_ids)
        asset     = get_asset_by_id(asset_id)
        if asset:
            st.warning(f"You are about to delete: **{asset['name']}** (Status: {asset['status']})")
            if st.button("Confirm Delete", type="primary"):
                delete_asset(asset_id)
                st.success("Asset deleted!")
                st.rerun()
