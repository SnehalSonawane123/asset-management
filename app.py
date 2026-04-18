import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

from db import init_db, fetch_all, fetch_by_id, insert_asset, update_asset, delete_asset

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asset Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a365d 0%, #2b6cb0 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stRadio label { color: white !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #2b6cb0;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a365d, #2b6cb0);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .main-header p  { color: rgba(255,255,255,0.8); margin: 4px 0 0; }

    /* Status badges */
    .badge {
        display: inline-block; padding: 3px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600;
    }

    /* Divider */
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 16px 0; }

    /* Section title */
    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #1a365d;
        margin-bottom: 16px; padding-bottom: 8px;
        border-bottom: 2px solid #2b6cb0;
    }
</style>
""", unsafe_allow_html=True)

init_db()  # initialise DB from setup.sql on first run

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Asset Manager")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📋 All Assets", "➕ Add Asset", "✏️ Edit Asset", "📊 Reports"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    df_all = fetch_all()
    total = len(df_all)
    st.metric("Total Assets", total)
    if total:
        available = len(df_all[df_all.status == "Available"])
        st.metric("Available", available)
        st.metric("In Use", len(df_all[df_all.status == "In Use"]))

# ─── Helpers ─────────────────────────────────────────────────────────────────
CATEGORIES = ["Electronics", "Furniture", "Vehicles", "Tools", "Other"]
STATUSES   = ["Available", "In Use", "Maintenance", "Retired"]

STATUS_COLORS = {
    "Available":   "#276749",
    "In Use":      "#2a69ac",
    "Maintenance": "#c05621",
    "Retired":     "#718096",
}
STATUS_BG = {
    "Available":   "#c6f6d5",
    "In Use":      "#bee3f8",
    "Maintenance": "#feebc8",
    "Retired":     "#e2e8f0",
}

CAT_COLORS = px.colors.qualitative.Bold

def status_badge(s):
    bg = STATUS_BG.get(s, "#e2e8f0")
    fg = STATUS_COLORS.get(s, "#718096")
    return f"<span style='background:{bg};color:{fg};padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600'>{s}</span>"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📦 Asset Management System</h1>
        <p>Overview of all assets across your organisation</p>
    </div>
    """, unsafe_allow_html=True)

    df = fetch_all()

    if df.empty:
        st.info("No assets yet. Head to **➕ Add Asset** to get started.")
    else:
        # ── KPI Row ──────────────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📦 Total Assets",    len(df))
        c2.metric("✅ Available",        len(df[df.status == "Available"]))
        c3.metric("🔵 In Use",           len(df[df.status == "In Use"]))
        c4.metric("🔧 Maintenance",      len(df[df.status == "Maintenance"]))
        c5.metric("📦 Total Units",      int(df.quantity.sum()))

        st.markdown("---")

        # ── Charts Row 1 ─────────────────────────────────────────────────────
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-title">Assets by Status</div>', unsafe_allow_html=True)
            status_counts = df.groupby("status").size().reset_index(name="count")
            fig_status = px.pie(
                status_counts, values="count", names="status",
                color="status",
                color_discrete_map={
                    "Available": "#48bb78", "In Use": "#4299e1",
                    "Maintenance": "#ed8936", "Retired": "#a0aec0"
                },
                hole=0.45,
            )
            fig_status.update_traces(textposition="inside", textinfo="percent+label")
            fig_status.update_layout(margin=dict(t=10, b=10), showlegend=True,
                                     legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            st.plotly_chart(fig_status, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-title">Assets by Category</div>', unsafe_allow_html=True)
            cat_counts = df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=True)
            fig_cat = px.bar(
                cat_counts, x="count", y="category", orientation="h",
                color="category", color_discrete_sequence=CAT_COLORS,
                text="count",
            )
            fig_cat.update_traces(textposition="outside")
            fig_cat.update_layout(margin=dict(t=10, b=10), showlegend=False,
                                   xaxis_title="Number of Assets", yaxis_title="")
            st.plotly_chart(fig_cat, use_container_width=True)

        # ── Charts Row 2 ─────────────────────────────────────────────────────
        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown('<div class="section-title">Quantity by Category</div>', unsafe_allow_html=True)
            qty_cat = df.groupby("category")["quantity"].sum().reset_index().sort_values("quantity", ascending=False)
            fig_qty = px.bar(
                qty_cat, x="category", y="quantity",
                color="category", color_discrete_sequence=CAT_COLORS,
                text="quantity",
            )
            fig_qty.update_traces(textposition="outside")
            fig_qty.update_layout(margin=dict(t=10, b=10), showlegend=False,
                                   xaxis_title="Category", yaxis_title="Total Units")
            st.plotly_chart(fig_qty, use_container_width=True)

        with col_d:
            st.markdown('<div class="section-title">Status × Category Heatmap</div>', unsafe_allow_html=True)
            pivot = df.pivot_table(index="category", columns="status", values="id", aggfunc="count", fill_value=0)
            fig_heat = px.imshow(
                pivot,
                color_continuous_scale="Blues",
                text_auto=True,
                aspect="auto",
            )
            fig_heat.update_layout(margin=dict(t=10, b=10))
            st.plotly_chart(fig_heat, use_container_width=True)

        # ── Recent assets ─────────────────────────────────────────────────────
        st.markdown('<div class="section-title">Recently Added Assets</div>', unsafe_allow_html=True)
        recent = df.head(5)[["id","name","category","quantity","location","status"]]
        st.dataframe(recent, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL ASSETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 All Assets":
    st.markdown('<div class="section-title">📋 All Assets</div>', unsafe_allow_html=True)

    df = fetch_all()

    if df.empty:
        st.info("No assets found. Add one using ➕ Add Asset.")
    else:
        # Filters
        f1, f2, f3 = st.columns(3)
        with f1:
            cats = ["All"] + sorted(df.category.unique().tolist())
            sel_cat = st.selectbox("Filter by Category", cats)
        with f2:
            stats = ["All"] + sorted(df.status.unique().tolist())
            sel_stat = st.selectbox("Filter by Status", stats)
        with f3:
            search = st.text_input("Search by name / location")

        filtered = df.copy()
        if sel_cat  != "All": filtered = filtered[filtered.category == sel_cat]
        if sel_stat != "All": filtered = filtered[filtered.status == sel_stat]
        if search:
            q = search.lower()
            filtered = filtered[
                filtered.name.str.lower().str.contains(q) |
                filtered.location.fillna("").str.lower().str.contains(q)
            ]

        st.caption(f"Showing {len(filtered)} of {len(df)} assets")

        # Display table with action buttons
        for _, row in filtered.iterrows():
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 1, 2, 2, 1.5])
                c1.markdown(f"**{row['name']}**")
                c2.write(row["category"])
                c3.write(f"× {row['quantity']}")
                c4.write(row["location"] or "—")
                c5.markdown(status_badge(row["status"]), unsafe_allow_html=True)
                with c6:
                    col_e, col_d2 = st.columns(2)
                    if col_e.button("✏️", key=f"edit_{row['id']}", help="Edit"):
                        st.session_state["edit_id"] = int(row["id"])
                        st.session_state["_nav"]    = "✏️ Edit Asset"
                        st.rerun()
                    if col_d2.button("🗑️", key=f"del_{row['id']}", help="Delete"):
                        delete_asset(int(row["id"]))
                        st.toast(f"Deleted '{row['name']}'", icon="🗑️")
                        st.rerun()
                st.markdown("<hr/>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD ASSET
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Asset":
    st.markdown('<div class="section-title">➕ Add New Asset</div>', unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name     = c1.text_input("Asset Name *", placeholder="e.g. Dell Laptop XPS 15", max_chars=100)
        category = c2.selectbox("Category", CATEGORIES)
        quantity = c1.number_input("Quantity", min_value=0, value=1, step=1)
        location = c2.text_input("Location", placeholder="e.g. IT Room, Floor 2", max_chars=100)
        status   = st.selectbox("Status", STATUSES)

        submitted = st.form_submit_button("💾 Save Asset", use_container_width=True, type="primary")

    if submitted:
        if not name.strip():
            st.error("Asset name is required.")
        else:
            insert_asset(name, category, int(quantity), location, status)
            st.success(f"✅ Asset **{name}** added successfully!")
            st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EDIT ASSET
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Edit Asset":
    st.markdown('<div class="section-title">✏️ Edit Asset</div>', unsafe_allow_html=True)

    df = fetch_all()
    if df.empty:
        st.info("No assets to edit.")
    else:
        # Let user pick from a selectbox, or pre-select from session state
        options = {f"#{r['id']} – {r['name']}": r["id"] for _, r in df.iterrows()}
        default = 0
        if "edit_id" in st.session_state:
            eid = st.session_state["edit_id"]
            keys = list(options.keys())
            vals = list(options.values())
            if eid in vals:
                default = vals.index(eid)

        selection = st.selectbox("Select Asset to Edit", list(options.keys()), index=default)
        aid = options[selection]
        row = df[df.id == aid].iloc[0]

        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            name     = c1.text_input("Asset Name *", value=row["name"], max_chars=100)
            category = c2.selectbox("Category", CATEGORIES,
                                    index=CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0)
            quantity = c1.number_input("Quantity", min_value=0, value=int(row["quantity"]), step=1)
            location = c2.text_input("Location", value=row["location"] or "", max_chars=100)
            status   = st.selectbox("Status", STATUSES,
                                    index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0)
            submitted = st.form_submit_button("🔄 Update Asset", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Asset name is required.")
            else:
                update_asset(aid, name, category, int(quantity), location, status)
                st.success(f"✅ Asset **{name}** updated!")
                if "edit_id" in st.session_state:
                    del st.session_state["edit_id"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Reports":
    st.markdown('<div class="section-title">📊 Asset Reports</div>', unsafe_allow_html=True)

    df = fetch_all()

    if df.empty:
        st.info("No data available to generate reports.")
    else:
        tab1, tab2, tab3 = st.tabs(["📈 Summary Report", "📍 Location Analysis", "⬇️ Export"])

        # ── Tab 1: Summary ───────────────────────────────────────────────────
        with tab1:
            st.subheader("Overall Summary")

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Asset Types", len(df))
            k2.metric("Total Units",       int(df.quantity.sum()))
            k3.metric("Categories",        df.category.nunique())
            k4.metric("Locations",         df.location.nunique())

            st.markdown("---")

            # Status breakdown table
            st.subheader("Status Breakdown")
            status_summary = df.groupby("status").agg(
                Assets=("id", "count"),
                Total_Units=("quantity", "sum"),
            ).reset_index()
            status_summary["% of Assets"] = (status_summary["Assets"] / len(df) * 100).round(1).astype(str) + "%"
            st.dataframe(status_summary, use_container_width=True, hide_index=True)

            # Category breakdown
            st.subheader("Category Breakdown")
            cat_summary = df.groupby("category").agg(
                Assets=("id", "count"),
                Total_Units=("quantity", "sum"),
                Avg_Qty=("quantity", "mean"),
            ).reset_index()
            cat_summary["Avg_Qty"] = cat_summary["Avg_Qty"].round(1)
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)

            # Treemap
            st.subheader("Treemap: Category → Status")
            df_tree = df.groupby(["category","status"]).agg(count=("id","count")).reset_index()
            fig_tree = px.treemap(
                df_tree, path=["category","status"], values="count",
                color="status",
                color_discrete_map={
                    "Available":"#48bb78","In Use":"#4299e1",
                    "Maintenance":"#ed8936","Retired":"#a0aec0"
                },
            )
            st.plotly_chart(fig_tree, use_container_width=True)

            # Sunburst
            st.subheader("Sunburst: Category → Status")
            fig_sun = px.sunburst(
                df_tree, path=["category","status"], values="count",
                color="status",
                color_discrete_map={
                    "Available":"#48bb78","In Use":"#4299e1",
                    "Maintenance":"#ed8936","Retired":"#a0aec0"
                },
            )
            st.plotly_chart(fig_sun, use_container_width=True)

        # ── Tab 2: Location Analysis ──────────────────────────────────────────
        with tab2:
            st.subheader("Assets by Location")
            df_loc = df.copy()
            df_loc["location"] = df_loc["location"].fillna("Unknown").replace("", "Unknown")

            loc_summary = df_loc.groupby("location").agg(
                Assets=("id","count"),
                Total_Units=("quantity","sum"),
            ).reset_index().sort_values("Assets", ascending=False)

            st.dataframe(loc_summary, use_container_width=True, hide_index=True)

            fig_loc = px.bar(
                loc_summary.head(15), x="location", y="Assets",
                color="Total_Units", color_continuous_scale="Blues",
                text="Assets",
            )
            fig_loc.update_traces(textposition="outside")
            fig_loc.update_layout(xaxis_title="Location", yaxis_title="Number of Assets")
            st.plotly_chart(fig_loc, use_container_width=True)

            # Status distribution per location
            st.subheader("Status Distribution per Location")
            loc_stat = df_loc.groupby(["location","status"]).size().reset_index(name="count")
            fig_ls = px.bar(
                loc_stat, x="location", y="count", color="status",
                barmode="stack",
                color_discrete_map={
                    "Available":"#48bb78","In Use":"#4299e1",
                    "Maintenance":"#ed8936","Retired":"#a0aec0"
                },
            )
            fig_ls.update_layout(xaxis_title="Location", yaxis_title="Assets")
            st.plotly_chart(fig_ls, use_container_width=True)

        # ── Tab 3: Export ─────────────────────────────────────────────────────
        with tab3:
            st.subheader("Export Asset Data")

            export_cols = ["id","name","category","quantity","location","status","created_at"]
            export_df   = df[export_cols].copy()

            # CSV
            csv_buf = io.StringIO()
            export_df.to_csv(csv_buf, index=False)
            st.download_button(
                "⬇️ Download CSV",
                data=csv_buf.getvalue(),
                file_name=f"assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary",
            )

            st.markdown("---")

            # Summary report as text
            report_lines = [
                "=" * 50,
                "      ASSET MANAGEMENT SYSTEM — REPORT",
                f"      Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
                "=" * 50,
                f"\nTotal Asset Types : {len(df)}",
                f"Total Units       : {int(df.quantity.sum())}",
                f"Categories        : {df.category.nunique()}",
                f"Locations         : {df.location.nunique()}",
                "\n── Status Breakdown ──",
            ]
            for _, r in df.groupby("status").agg(count=("id","count"), units=("quantity","sum")).reset_index().iterrows():
                report_lines.append(f"  {r['status']:<15} {r['count']:>3} assets  |  {r['units']:>4} units")
            report_lines.append("\n── Category Breakdown ──")
            for _, r in df.groupby("category").agg(count=("id","count"), units=("quantity","sum")).reset_index().iterrows():
                report_lines.append(f"  {r['category']:<15} {r['count']:>3} assets  |  {r['units']:>4} units")
            report_lines.append("\n── Asset List ──")
            for _, r in df.iterrows():
                report_lines.append(f"  #{r['id']}  {r['name']:<30} [{r['status']}]  Qty:{r['quantity']}  Loc:{r['location'] or '—'}")
            report_lines.append("\n" + "=" * 50)

            report_text = "\n".join(report_lines)
            st.text_area("Report Preview", report_text, height=320)
            st.download_button(
                "⬇️ Download Text Report",
                data=report_text,
                file_name=f"asset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
