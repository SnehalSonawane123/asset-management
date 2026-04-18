import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

from db import init_db, fetch_all, insert_asset, update_asset, delete_asset

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asset Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Colour Tokens ────────────────────────────────────────────────────────────
ACCENT      = "#2dd4bf"
ACCENT_DARK = "#14b8a6"
SIDEBAR_TOP = "#0a0f1e"
SIDEBAR_BOT = "#0f172a"
BG          = "#0f172a"
BG2         = "#1e293b"
BG3         = "#263044"
TEXT        = "#e2e8f0"
MUTED       = "#94a3b8"
BORDER      = "#2d3f55"

STATUS_HEX = {
    "Available":   "#34d399",
    "In Use":      "#60a5fa",
    "Maintenance": "#fbbf24",
    "Retired":     "#94a3b8",
}
STATUS_BG = {
    "Available":   "#064e3b",
    "In Use":      "#1e3a5f",
    "Maintenance": "#451a03",
    "Retired":     "#1e293b",
}
STATUS_FG = {
    "Available":   "#6ee7b7",
    "In Use":      "#93c5fd",
    "Maintenance": "#fcd34d",
    "Retired":     "#94a3b8",
}

CAT_PALETTE = ["#0d9488","#6366f1","#f59e0b","#ef4444","#8b5cf6"]
CATEGORIES  = ["Electronics", "Furniture", "Vehicles", "Tools", "Other"]
STATUSES    = ["Available", "In Use", "Maintenance", "Retired"]

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"],
  [data-testid="stMain"], .main, .block-container {{
      background:{BG} !important; color:{TEXT};
      font-family:'Inter','Segoe UI',sans-serif;
  }}
  /* All text defaults */
  p, span, div, label, li {{ color:{TEXT}; }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] > div:first-child {{
      background:linear-gradient(180deg,{SIDEBAR_TOP} 0%,{SIDEBAR_BOT} 100%) !important;
  }}
  [data-testid="stSidebar"] * {{ color:#e2e8f0 !important; }}
  [data-testid="stSidebar"] hr {{ border-color:#1e293b !important; }}
  [data-testid="stSidebar"] [data-baseweb="radio"] label {{
      padding:8px 14px !important; border-radius:8px !important;
      color:#cbd5e1 !important; font-size:0.9rem !important; transition:background .15s;
  }}
  [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {{
      background:rgba(255,255,255,0.06) !important;
  }}

  /* ── Metric cards ── */
  [data-testid="metric-container"] {{
      background:{BG2}; border-radius:14px; padding:20px 18px 14px;
      box-shadow:0 1px 3px rgba(0,0,0,0.4),0 4px 16px rgba(0,0,0,0.3);
      border-top:3px solid {ACCENT};
  }}
  [data-testid="stMetricValue"] {{ color:{TEXT} !important; font-weight:700; }}
  [data-testid="stMetricLabel"] {{ color:{MUTED} !important; font-size:0.8rem; }}

  /* ── Page banner ── */
  .page-banner {{
      background:linear-gradient(135deg,{SIDEBAR_TOP} 0%,#0d2d2a 100%);
      color:white; padding:24px 32px; border-radius:16px; margin-bottom:28px;
      border:1px solid {BORDER};
      box-shadow:0 4px 24px rgba(45,212,191,0.12);
  }}
  .page-banner h1 {{ color:white; margin:0; font-size:1.6rem; font-weight:800; letter-spacing:-.02em; }}
  .page-banner p  {{ color:rgba(255,255,255,0.5); margin:5px 0 0; font-size:0.88rem; }}

  /* ── Section heading ── */
  .sec-head {{
      font-size:0.68rem; font-weight:700; letter-spacing:.1em;
      text-transform:uppercase; color:{MUTED}; margin-bottom:12px;
  }}

  /* ── Generic card ── */
  .ams-card {{
      background:{BG2}; border-radius:16px; padding:24px 26px;
      border:1px solid {BORDER};
      box-shadow:0 1px 3px rgba(0,0,0,0.4); margin-bottom:18px;
  }}

  /* ── Inline edit panel ── */
  .edit-panel {{
      background:#0d2d2a; border:1.5px solid {ACCENT};
      border-radius:14px; padding:20px 24px; margin:2px 0 14px;
  }}

  /* ── Asset divider ── */
  .asset-divider {{ border:none; border-top:1px solid {BORDER}; margin:4px 0; }}

  /* ── Inputs / selects ── */
  [data-baseweb="input"] input,
  [data-baseweb="select"] div[data-baseweb="select"],
  [data-baseweb="textarea"] textarea {{
      background:{BG3} !important; color:{TEXT} !important;
      border-color:{BORDER} !important; border-radius:8px !important;
  }}
  [data-baseweb="input"]:focus-within,
  [data-baseweb="select"]:focus-within {{
      border-color:{ACCENT} !important;
      box-shadow:0 0 0 3px rgba(45,212,191,0.15) !important;
  }}

  /* ── Number input ── */
  [data-testid="stNumberInput"] input {{
      background:{BG3} !important; color:{TEXT} !important;
      border-color:{BORDER} !important;
  }}

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] {{ background:{BG2} !important; border-radius:12px; }}

  /* ── Primary button ── */
  [data-testid="stFormSubmitButton"] button[kind="primary"],
  .stButton button[kind="primary"] {{
      background:{ACCENT} !important; color:#0f172a !important;
      border:none !important; border-radius:9px !important; font-weight:700 !important;
  }}
  [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
  .stButton button[kind="primary"]:hover {{
      background:{ACCENT_DARK} !important;
  }}

  /* ── Secondary / default button ── */
  .stButton button {{
      background:{BG3} !important; color:{TEXT} !important;
      border:1px solid {BORDER} !important; border-radius:9px !important;
  }}
  .stButton button:hover {{
      border-color:{ACCENT} !important;
      color:{ACCENT} !important;
  }}

  /* ── PENCIL / DELETE icon buttons — centered square ── */
  .stButton button[title="Edit"],
  .stButton button[title="Delete"],
  div[data-testid="column"] .stButton button {{
      width:36px !important; height:36px !important;
      padding:0 !important; min-height:36px !important;
      display:flex !important; align-items:center !important;
      justify-content:center !important;
      font-size:1rem !important; line-height:1 !important;
  }}

  /* ── Tabs ── */
  [data-baseweb="tab-list"] {{
      background:{BG2} !important; border-radius:10px !important; padding:4px !important;
      border:1px solid {BORDER} !important;
  }}
  [data-baseweb="tab"] {{ border-radius:7px !important; font-weight:600 !important; font-size:.88rem !important; color:{MUTED} !important; }}
  [aria-selected="true"][data-baseweb="tab"] {{
      background:{BG3} !important; color:{ACCENT} !important;
      box-shadow:0 1px 4px rgba(0,0,0,0.3) !important;
  }}

  /* ── Selectbox dropdown ── */
  [data-baseweb="popover"] ul {{ background:{BG2} !important; border:1px solid {BORDER} !important; }}
  [data-baseweb="popover"] li {{ color:{TEXT} !important; }}
  [data-baseweb="popover"] li:hover {{ background:{BG3} !important; }}

  /* ── Caption / small text ── */
  [data-testid="stCaptionContainer"] {{ color:{MUTED} !important; }}

  /* ── Alert ── */
  [data-testid="stAlert"] {{ border-radius:10px !important; }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width:6px; height:6px; }}
  ::-webkit-scrollbar-track {{ background:{BG}; }}
  ::-webkit-scrollbar-thumb {{ background:{BG3}; border-radius:3px; }}

  hr {{ border:none; border-top:1px solid {BORDER}; margin:18px 0; }}
</style>
""", unsafe_allow_html=True)

# ─── Init ─────────────────────────────────────────────────────────────────────
init_db()
if "edit_id" not in st.session_state: st.session_state.edit_id = None
if "page"    not in st.session_state: st.session_state.page    = "🏠 Dashboard"

# ─── Helpers ─────────────────────────────────────────────────────────────────
def badge(s):
    bg = STATUS_BG.get(s, "#f1f5f9")
    fg = STATUS_FG.get(s, "#475569")
    return f"<span style='background:{bg};color:{fg};padding:3px 11px;border-radius:20px;font-size:0.74rem;font-weight:600;display:inline-block'>{s}</span>"

def chart_base(fig, **kw):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter,Segoe UI,sans-serif", font_color=TEXT,
        margin=dict(t=16, b=16, l=8, r=8),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        **kw
    )
    return fig

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:10px 4px 18px'>
      <div style='font-size:1.4rem;font-weight:800;color:white;letter-spacing:-.02em'>📦 AssetTrack</div>
      <div style='font-size:.75rem;color:#64748b;margin-top:2px'>Inventory Management</div>
    </div>""", unsafe_allow_html=True)

    NAV = ["🏠 Dashboard", "📋 All Assets", "➕ Add Asset", "📊 Reports"]
    st.markdown('<div style="font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#475569!important;margin-bottom:6px">Menu</div>', unsafe_allow_html=True)
    sel = st.radio("nav", NAV,
                   index=NAV.index(st.session_state.page) if st.session_state.page in NAV else 0,
                   label_visibility="collapsed")
    if sel != st.session_state.page:
        st.session_state.page    = sel
        st.session_state.edit_id = None
        st.rerun()

    st.markdown("---")
    df_side = fetch_all()
    st.markdown('<div style="font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#475569!important;margin-bottom:6px">Quick Stats</div>', unsafe_allow_html=True)
    st.metric("Total Assets", len(df_side))
    if not df_side.empty:
        st.metric("Available", int((df_side.status == "Available").sum()))
        st.metric("In Use",    int((df_side.status == "In Use").sum()))

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="page-banner">
      <h1>📦 Asset Management System</h1>
      <p>Real-time overview of all assets across your organisation</p>
    </div>""", unsafe_allow_html=True)

    df = fetch_all()
    if df.empty:
        st.info("No assets yet — head to **➕ Add Asset** to get started.")
    else:
        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("Total Assets",  len(df))
        k2.metric("✅ Available",   int((df.status=="Available").sum()))
        k3.metric("🔵 In Use",      int((df.status=="In Use").sum()))
        k4.metric("🔧 Maintenance", int((df.status=="Maintenance").sum()))
        k5.metric("📦 Total Units", int(df.quantity.sum()))

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="sec-head">Assets by Status</div>', unsafe_allow_html=True)
            sc = df.groupby("status").size().reset_index(name="n")
            fig = px.pie(sc, values="n", names="status", hole=0.52,
                         color="status", color_discrete_map=STATUS_HEX)
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              marker=dict(line=dict(color="white",width=2)))
            chart_base(fig, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="sec-head">Assets by Category</div>', unsafe_allow_html=True)
            cc = df.groupby("category").size().reset_index(name="n").sort_values("n")
            fig = px.bar(cc, x="n", y="category", orientation="h",
                         color="category", color_discrete_sequence=CAT_PALETTE, text="n")
            fig.update_traces(textposition="outside")
            chart_base(fig, showlegend=False, xaxis_title="Assets", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown('<div class="sec-head">Total Units by Category</div>', unsafe_allow_html=True)
            qc = df.groupby("category")["quantity"].sum().reset_index().sort_values("quantity", ascending=False)
            fig = px.bar(qc, x="category", y="quantity",
                         color="category", color_discrete_sequence=CAT_PALETTE, text="quantity")
            fig.update_traces(textposition="outside")
            chart_base(fig, showlegend=False, xaxis_title="", yaxis_title="Units")
            st.plotly_chart(fig, use_container_width=True)

        with col_d:
            st.markdown('<div class="sec-head">Status × Category Heatmap</div>', unsafe_allow_html=True)
            pivot = df.pivot_table(index="category", columns="status",
                                   values="id", aggfunc="count", fill_value=0)
            fig = px.imshow(pivot, text_auto=True, aspect="auto",
                            color_continuous_scale=[[0,BG2],[1,ACCENT]])
            chart_base(fig)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sec-head">Recently Added</div>', unsafe_allow_html=True)
        st.dataframe(df.head(6)[["id","name","category","quantity","location","status"]],
                     use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# ALL ASSETS  — inline edit
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 All Assets":
    st.markdown("""
    <div class="page-banner">
      <h1>📋 All Assets</h1>
      <p>Browse, filter, edit and delete assets inline</p>
    </div>""", unsafe_allow_html=True)

    df = fetch_all()
    if df.empty:
        st.info("No assets found. Add one using **➕ Add Asset**.")
    else:
        # Filters
        f1, f2, f3 = st.columns([1,1,2])
        sel_cat  = f1.selectbox("Category", ["All"] + sorted(df.category.unique().tolist()))
        sel_stat = f2.selectbox("Status",   ["All"] + sorted(df.status.unique().tolist()))
        search   = f3.text_input("Search", placeholder="🔍  Name or location…", label_visibility="collapsed")

        filtered = df.copy()
        if sel_cat  != "All": filtered = filtered[filtered.category == sel_cat]
        if sel_stat != "All": filtered = filtered[filtered.status   == sel_stat]
        if search:
            q = search.lower()
            filtered = filtered[
                filtered.name.str.lower().str.contains(q, na=False) |
                filtered.location.fillna("").str.lower().str.contains(q, na=False)
            ]

        st.caption(f"Showing **{len(filtered)}** of **{len(df)}** assets")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Column header
        hcols = st.columns([3,2,1,2,2,1])
        for col, lbl in zip(hcols, ["Asset","Category","Qty","Location","Status","Actions"]):
            col.markdown(f"<div style='font-size:.7rem;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:.07em;padding-bottom:4px'>{lbl}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:0 0 8px'/>", unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            rid        = int(row["id"])
            is_editing = st.session_state.edit_id == rid

            rc = st.columns([3,2,1,2,2,1])
            rc[0].markdown(f"**{row['name']}** <span style='font-size:.76rem;color:{MUTED}'>#{rid}</span>", unsafe_allow_html=True)
            rc[1].write(row["category"])
            rc[2].write(int(row["quantity"]))
            rc[3].write(row["location"] or "—")
            rc[4].markdown(badge(row["status"]), unsafe_allow_html=True)

            with rc[5]:
                st.markdown("""
                <style>
                  div[data-testid="column"] .stButton button {
                    width:34px !important; height:34px !important;
                    padding:0 !important; min-height:34px !important;
                    display:flex !important; align-items:center !important;
                    justify-content:center !important; font-size:1rem !important;
                    line-height:1 !important;
                  }
                </style>""", unsafe_allow_html=True)
                btn_e, btn_d = st.columns(2)
                if btn_e.button("✏️", key=f"e{rid}", help="Edit"):
                    st.session_state.edit_id = None if is_editing else rid
                    st.rerun()
                if btn_d.button("🗑️", key=f"d{rid}", help="Delete"):
                    delete_asset(rid)
                    if st.session_state.edit_id == rid:
                        st.session_state.edit_id = None
                    st.toast(f"Deleted '{row['name']}'", icon="🗑️")
                    st.rerun()

            # Inline edit panel — slides open below the row
            if is_editing:
                st.markdown(f"""
                <div class="edit-panel">
                  <span style='font-size:.8rem;font-weight:700;color:{ACCENT}'>✏️ Editing asset #{rid}</span>
                </div>""", unsafe_allow_html=True)

                with st.form(key=f"form_{rid}"):
                    e1, e2 = st.columns(2)
                    n_name = e1.text_input("Asset Name *", value=row["name"], max_chars=100)
                    n_cat  = e2.selectbox("Category", CATEGORIES,
                                          index=CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0)
                    n_qty  = e1.number_input("Quantity", min_value=0, value=int(row["quantity"]), step=1)
                    n_loc  = e2.text_input("Location", value=row["location"] or "", max_chars=100)
                    n_stat = st.selectbox("Status", STATUSES,
                                          index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0)
                    sa, sb = st.columns(2)
                    saved    = sa.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                    cancelled = sb.form_submit_button("✕ Cancel", use_container_width=True)

                if saved:
                    if not n_name.strip():
                        st.error("Asset name is required.")
                    else:
                        update_asset(rid, n_name, n_cat, int(n_qty), n_loc, n_stat)
                        st.session_state.edit_id = None
                        st.toast(f"✅ '{n_name}' updated!", icon="✅")
                        st.rerun()
                if cancelled:
                    st.session_state.edit_id = None
                    st.rerun()

            st.markdown("<hr class='asset-divider'/>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADD ASSET
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Asset":
    st.markdown("""
    <div class="page-banner">
      <h1>➕ Add New Asset</h1>
      <p>Fill in the details to register a new asset</p>
    </div>""", unsafe_allow_html=True)

    col_form, col_tip = st.columns([1.8, 1])
    with col_form:
        with st.form("add_form", clear_on_submit=True):
            r1, r2 = st.columns(2)
            name     = r1.text_input("Asset Name *", placeholder="e.g. Dell Laptop XPS 15", max_chars=100)
            category = r2.selectbox("Category", CATEGORIES)
            r3, r4 = st.columns(2)
            quantity = r3.number_input("Quantity", min_value=0, value=1, step=1)
            location = r4.text_input("Location", placeholder="e.g. IT Room, Floor 2", max_chars=100)
            status   = st.selectbox("Status", STATUSES)
            submitted = st.form_submit_button("💾 Save Asset", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Asset name is required.")
            else:
                insert_asset(name, category, int(quantity), location, status)
                st.success(f"✅ **{name}** added successfully.")

    with col_tip:
        st.markdown(f"""
        <div class="ams-card" style="margin-top:0">
          <div class="sec-head">Tips</div>
          <ul style="font-size:.86rem;color:{MUTED};line-height:2;padding-left:18px">
            <li>Use clear, descriptive names</li>
            <li>Set the correct location for easy tracking</li>
            <li>Mark status accurately to reflect real state</li>
            <li>Update quantity after stock changes</li>
          </ul>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Reports":
    st.markdown("""
    <div class="page-banner">
      <h1>📊 Reports & Analytics</h1>
      <p>Deep-dive into asset distribution, locations, and trends</p>
    </div>""", unsafe_allow_html=True)

    df = fetch_all()
    if df.empty:
        st.info("No data available. Add some assets first.")
    else:
        tab1, tab2, tab3 = st.tabs(["📈  Summary", "📍  Location Analysis", "⬇️  Export"])

        with tab1:
            k1,k2,k3,k4 = st.columns(4)
            k1.metric("Asset Types",  len(df))
            k2.metric("Total Units",  int(df.quantity.sum()))
            k3.metric("Categories",   df.category.nunique())
            k4.metric("Locations",    df.location.nunique())
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                st.markdown('<div class="sec-head">Status Breakdown</div>', unsafe_allow_html=True)
                ss = df.groupby("status").agg(Assets=("id","count"), Units=("quantity","sum")).reset_index()
                ss["Share"] = (ss.Assets / len(df) * 100).round(1).astype(str) + "%"
                st.dataframe(ss, use_container_width=True, hide_index=True)
            with cb:
                st.markdown('<div class="sec-head">Category Breakdown</div>', unsafe_allow_html=True)
                cs = df.groupby("category").agg(Assets=("id","count"), Units=("quantity","sum"),
                                                 Avg=("quantity","mean")).reset_index()
                cs["Avg"] = cs["Avg"].round(1)
                st.dataframe(cs, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="sec-head">Category → Status Treemap</div>', unsafe_allow_html=True)
            df_t = df.groupby(["category","status"]).size().reset_index(name="n")
            fig = px.treemap(df_t, path=["category","status"], values="n",
                             color="status", color_discrete_map=STATUS_HEX)
            chart_base(fig)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="sec-head">Sunburst</div>', unsafe_allow_html=True)
            fig2 = px.sunburst(df_t, path=["category","status"], values="n",
                               color="status", color_discrete_map=STATUS_HEX)
            chart_base(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            df_loc = df.copy()
            df_loc["location"] = df_loc["location"].fillna("Unknown").replace("","Unknown")
            ls = df_loc.groupby("location").agg(Assets=("id","count"),
                                                  Units=("quantity","sum")).reset_index().sort_values("Assets", ascending=False)
            st.markdown('<div class="sec-head">Assets per Location</div>', unsafe_allow_html=True)
            st.dataframe(ls, use_container_width=True, hide_index=True)
            fig = px.bar(ls.head(15), x="location", y="Assets",
                         color="Units", color_continuous_scale=[[0,BG3],[1,ACCENT]], text="Assets")
            fig.update_traces(textposition="outside")
            chart_base(fig, xaxis_title="Location", yaxis_title="Assets")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="sec-head">Status Distribution per Location</div>', unsafe_allow_html=True)
            lstat = df_loc.groupby(["location","status"]).size().reset_index(name="n")
            fig2 = px.bar(lstat, x="location", y="n", color="status", barmode="stack",
                          color_discrete_map=STATUS_HEX)
            chart_base(fig2, xaxis_title="Location", yaxis_title="Assets")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.markdown('<div class="sec-head">Download Data</div>', unsafe_allow_html=True)
            export_df = df[["id","name","category","quantity","location","status","created_at"]].copy()
            csv_buf = io.StringIO()
            export_df.to_csv(csv_buf, index=False)
            st.download_button("⬇️ Download CSV", data=csv_buf.getvalue(),
                               file_name=f"assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv", use_container_width=True, type="primary")
            st.markdown("---")

            lines = [
                "="*52,
                "     ASSET MANAGEMENT SYSTEM — REPORT",
                f"     Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}",
                "="*52,
                f"\n  Total Asset Types : {len(df)}",
                f"  Total Units       : {int(df.quantity.sum())}",
                f"  Categories        : {df.category.nunique()}",
                f"  Locations         : {df.location.nunique()}",
                "\n── Status Breakdown ─────────────────────────────────",
            ]
            for _, r in df.groupby("status").agg(c=("id","count"),u=("quantity","sum")).reset_index().iterrows():
                lines.append(f"  {r['status']:<16} {r['c']:>3} assets   {r['u']:>5} units")
            lines.append("\n── Category Breakdown ───────────────────────────────")
            for _, r in df.groupby("category").agg(c=("id","count"),u=("quantity","sum")).reset_index().iterrows():
                lines.append(f"  {r['category']:<16} {r['c']:>3} assets   {r['u']:>5} units")
            lines.append("\n── Asset List ───────────────────────────────────────")
            for _, r in df.iterrows():
                lines.append(f"  #{r['id']:<4} {r['name']:<28} [{r['status']:<12}] Qty:{r['quantity']:<5} Loc:{r['location'] or '—'}")
            lines.append("\n"+"="*52)

            report = "\n".join(lines)
            st.text_area("Preview", report, height=300)
            st.download_button("⬇️ Download Text Report", data=report,
                               file_name=f"asset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                               mime="text/plain", use_container_width=True)
