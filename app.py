import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
SERVICES_FILE = DATA_DIR / "services.json"
REQUESTS_FILE = DATA_DIR / "requests.json"
COUNTS_FILE = DATA_DIR / "counts.json"

CONTACT_EMAIL = "servicing@houseofservicing.com"

STATUS_LABELS = {
    "live": ("Live", "#16a34a"),
    "beta": ("Beta", "#d97706"),
    "dev": ("In development", "#64748b"),
}

CATEGORY_THEMES = {
    "Data Management": "#059669",
    "Client Relations": "#db2777",
    "Document Generation": "#f59e0b",
    "Payments & Collections": "#0891b2",
    "Reconciliation": "#2563eb",
    "Reporting & Monitoring": "#7c3aed",
    "Compliance & Controls": "#dc2626",
}
DEFAULT_THEME = "#475569"

st.set_page_config(
    page_title="House of Servicing — Service Portal",
    page_icon="🏛️",
    layout="wide",
)


def load_services():
    with open(SERVICES_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_requests():
    if REQUESTS_FILE.exists():
        with open(REQUESTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_request(entry):
    requests = load_requests()
    requests.append(entry)
    REQUESTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)


def load_counts():
    if COUNTS_FILE.exists():
        with open(COUNTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def increment_count(service_id):
    counts = load_counts()
    counts[service_id] = counts.get(service_id, 0) + 1
    COUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)


def open_service(service_id):
    increment_count(service_id)
    st.query_params["service"] = service_id


def go_back():
    if "service" in st.query_params:
        del st.query_params["service"]


def category_color(category):
    return CATEGORY_THEMES.get(category, DEFAULT_THEME)


def inject_styles():
    st.markdown(
        """
        <style>
        /* Theme forced via CSS: independent of config.toml (Domino, proxies, etc.) */
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0f172a; color: #e2e8f0; }
        [data-testid="stHeader"] { background: transparent; }
        section[data-testid="stSidebar"] { background-color: #1e293b; }
        section[data-testid="stSidebar"] * { color: #e2e8f0; }
        .stApp p, .stApp li, .stApp span, .stApp label, .stApp h1, .stApp h2,
        .stApp h3, .stApp h4 { color: #e2e8f0; }
        .hos-hero {
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #7c3aed 100%);
            border-radius: 18px;
            padding: 2.2rem 2.4rem;
            margin-bottom: 1.6rem;
            color: #f8fafc;
        }
        .hos-hero h1 { margin: 0; font-size: 2.1rem; font-weight: 700; }
        .hos-hero p { margin: .5rem 0 0; font-size: 1.02rem; opacity: .92; }
        .hos-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 1.2rem 1.3rem 1.3rem;
            height: 100%;
            transition: transform .15s ease, border-color .15s ease;
        }
        .hos-card:hover { transform: translateY(-3px); border-color: #2563eb; }
        .hos-logo {
            width: 56px; height: 56px;
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 28px;
            margin-bottom: .8rem;
        }
        .hos-card h3 { margin: .1rem 0 .3rem; font-size: 1.12rem; color: #f1f5f9; }
        .hos-cat { font-size: .74rem; font-weight: 600; letter-spacing: .03em;
                   text-transform: uppercase; opacity: .85; }
        .hos-desc { font-size: .9rem; color: #cbd5e1; line-height: 1.45;
                    min-height: 78px; margin: .4rem 0 .7rem; }
        .hos-badge {
            display: inline-block; padding: .15rem .6rem; border-radius: 999px;
            font-size: .72rem; font-weight: 600; color: #fff;
        }
        .hos-meta { font-size: .78rem; color: #94a3b8; margin: .55rem 0 .2rem; }
        .hos-tag {
            display: inline-block; background: #334155; color: #cbd5e1;
            padding: .1rem .5rem; border-radius: 6px; font-size: .72rem;
            margin: .15rem .2rem 0 0;
        }
        .hos-count {
            font-size: .78rem; color: #38bdf8; font-weight: 600; margin: .6rem 0 .1rem;
        }
        .hos-section {
            background: #1e293b; border: 1px solid #334155; border-radius: 14px;
            padding: 1.1rem 1.3rem; margin-bottom: 1rem;
        }
        .hos-section h4 { margin: 0 0 .5rem; font-size: 1rem; color: #f1f5f9; }
        .hos-section ul { margin: 0; padding-left: 1.1rem; }
        .hos-section li { color: #cbd5e1; margin: .25rem 0; }
        .hos-detail-logo {
            width: 76px; height: 76px; border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-size: 38px; margin-bottom: .6rem;
        }
        /* Native Streamlit CTA styled as a blue button */
        div[data-testid="stButton"] > button {
            background: #2563eb; color: #fff; font-weight: 600; border: none;
            border-radius: 10px; padding: .5rem; width: 100%;
        }
        div[data-testid="stButton"] > button:hover { background: #1d4ed8; color: #fff; }
        div[data-testid="stButton"] > button:disabled { background: #475569; opacity: .7; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(service, counts):
    color = category_color(service["category"])
    status_label, status_color = STATUS_LABELS.get(
        service["status"], ("Unknown", "#64748b")
    )
    tags_html = "".join(
        f"<span class='hos-tag'>#{t}</span>" for t in service.get("tags", [])
    )
    is_live = service["status"] != "dev"
    sid = service["id"]
    n_clicks = counts.get(sid, 0)

    with st.container():
        st.markdown(
            f"""
            <div class="hos-card">
                <div class="hos-logo" style="background:{color}22;border:1px solid {color}55;">
                    {service['icon']}
                </div>
                <div class="hos-cat" style="color:{color};">{service['category']}</div>
                <h3>{service['name']}</h3>
                <span class="hos-badge" style="background:{status_color};">{status_label}</span>
                <div class="hos-desc">{service['description']}</div>
                <div class="hos-meta">⏱️ {service['frequency']} · 💪 ~{service['time_saved_h']} h saved/run</div>
                <div class="hos-meta">👥 {service['owner']}</div>
                <div>{tags_html}</div>
                <div class="hos-count">👆 {n_clicks} open(s)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if is_live:
            st.button(
                "Open service →",
                key=f"open_{sid}",
                on_click=open_service,
                args=(sid,),
                use_container_width=True,
            )
        else:
            st.button(
                "Coming soon",
                key=f"open_{sid}",
                disabled=True,
                use_container_width=True,
            )


def page_marketplace(services):
    st.markdown(
        f"""
        <div class="hos-hero">
            <h1>🏛️ Service Portal — House of Servicing</h1>
            <p>The Servicing team's marketplace. Yesterday's macros become centralized,
            reliable services available in a single click.</p>
            <p style="font-size:.92rem;opacity:.85;margin-top:.6rem;">
                ✉️ A question or a request? Reach us at:
                <a href="mailto:{CONTACT_EMAIL}" style="color:#bfdbfe;font-weight:600;">{CONTACT_EMAIL}</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        #### What is this portal for?
        The Servicing team relies on many **Excel/VBA macros** scattered across workstations.
        This portal **brings them together in a single entry point**: each process is gradually
        **industrialized into a Python service**, then published here with its own dedicated page
        explaining what it does, its inputs and its outputs.
        """
    )
    st.markdown(
        """
        - 🎯 **Find** the right tool without digging through shared drives
        - 🛡️ **Trust** maintained, versioned services instead of local macros
        - 📊 **Measure** time saved and know who owns what
        - ➕ **Request** a new macro to industrialize via the dedicated tab
        """
    )
    st.divider()

    counts = load_counts()
    categories = sorted({s["category"] for s in services})
    total_saved = sum(s["time_saved_h"] for s in services)
    live_count = sum(1 for s in services if s["status"] == "live")
    total_clicks = sum(counts.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Services in catalog", len(services))
    c2.metric("Live", live_count)
    c3.metric("Total opens", total_clicks)
    c4.metric("Hours saved / cycle", f"~{total_saved} h")

    st.divider()

    fcol1, fcol2, fcol3 = st.columns([2, 1.3, 1.3])
    query = fcol1.text_input("🔎 Search a service", placeholder="name, keyword, tag...")
    cat_filter = fcol2.selectbox("Category", ["All"] + categories)
    status_filter = fcol3.selectbox(
        "Status", ["All", "Live", "Beta", "In development"]
    )

    status_map = {"Live": "live", "Beta": "beta", "In development": "dev"}

    def matches(s):
        if cat_filter != "All" and s["category"] != cat_filter:
            return False
        if status_filter != "All" and s["status"] != status_map[status_filter]:
            return False
        if query:
            blob = " ".join(
                [s["name"], s["description"], s["category"], " ".join(s.get("tags", []))]
            ).lower()
            if query.lower() not in blob:
                return False
        return True

    filtered = [s for s in services if matches(s)]

    if not filtered:
        st.info("No service matches your search.")
        return

    st.caption(f"{len(filtered)} service(s) shown")
    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        row = st.columns(cols_per_row)
        for col, service in zip(row, filtered[i : i + cols_per_row]):
            with col:
                render_card(service, counts)


def page_service_detail(service):
    color = category_color(service["category"])
    status_label, status_color = STATUS_LABELS.get(
        service["status"], ("Unknown", "#64748b")
    )
    sid = service["id"]
    counts = load_counts()
    n_clicks = counts.get(sid, 0)

    top_left, top_right = st.columns([1, 5])
    with top_left:
        st.button("← Back", key="back_btn", on_click=go_back, use_container_width=True)

    tags_html = "".join(
        f"<span class='hos-tag'>#{t}</span>" for t in service.get("tags", [])
    )

    st.markdown(
        f"""
        <div class="hos-hero" style="background: linear-gradient(135deg, {color} 0%, #1e293b 100%);">
            <div class="hos-detail-logo" style="background:{color}33;border:1px solid {color}88;">
                {service['icon']}
            </div>
            <div class="hos-cat" style="color:#e0e7ff;">{service['category']}</div>
            <h1>{service['name']}</h1>
            <p>
                <span class="hos-badge" style="background:{status_color};">{status_label}</span>
                &nbsp;·&nbsp; ⏱️ {service['frequency']}
                &nbsp;·&nbsp; 💪 ~{service['time_saved_h']} h saved per run
                &nbsp;·&nbsp; 👆 {n_clicks} open(s)
            </p>
            <p style="margin-top:.6rem;">{tags_html}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hos-section">
            <h4>🎯 What it does</h4>
            <p style="color:#cbd5e1;margin:0;">{service.get('purpose', service['description'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        inputs_html = "".join(f"<li>{i}</li>" for i in service.get("inputs", []))
        st.markdown(
            f"""
            <div class="hos-section">
                <h4>📥 Input(s)</h4>
                <ul>{inputs_html or '<li>—</li>'}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        outputs_html = "".join(f"<li>{o}</li>" for o in service.get("outputs", []))
        st.markdown(
            f"""
            <div class="hos-section">
                <h4>📤 Output(s)</h4>
                <ul>{outputs_html or '<li>—</li>'}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    benefits_html = "".join(f"<li>{b}</li>" for b in service.get("benefits", []))
    if benefits_html:
        st.markdown(
            f"""
            <div class="hos-section">
                <h4>💎 Value &amp; benefits</h4>
                <ul>{benefits_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="hos-section">
            <h4>📌 Service info</h4>
            <ul>
                <li><strong>Owner:</strong> {service['owner']}</li>
                <li><strong>Frequency:</strong> {service['frequency']}</li>
                <li><strong>Estimated time saved:</strong> ~{service['time_saved_h']} h per run</li>
                <li><strong>Source macro:</strong> <code>{service.get('origin_macro', '—')}</code></li>
                <li><strong>Total opens:</strong> {n_clicks}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Need help with this service? Contact {CONTACT_EMAIL}")


def page_request(services):
    st.header("➕ Request a new service")
    st.write(
        "Have a macro to industrialize? Describe the need: the industrialization team "
        "will turn it into a centralized Python service."
    )

    categories = sorted({s["category"] for s in services})

    with st.form("request_form", clear_on_submit=True):
        name = st.text_input("Service name *")
        col1, col2 = st.columns(2)
        category = col1.selectbox("Category *", categories + ["Other"])
        frequency = col2.selectbox(
            "Usage frequency", ["Daily", "Weekly", "Monthly", "Ad hoc"]
        )
        description = st.text_area("Describe the need *")
        col3, col4 = st.columns(2)
        origin_macro = col3.text_input("Source macro (.xlsm file)")
        time_saved = col4.number_input(
            "Estimated time saved (h / run)", min_value=0.0, value=1.0, step=0.5
        )
        requester = st.text_input("Your name / team *")
        submitted = st.form_submit_button("Submit request")

        if submitted:
            if not (name and description and requester):
                st.error("Please fill in the required fields (*).")
            else:
                save_request(
                    {
                        "name": name,
                        "category": category,
                        "frequency": frequency,
                        "description": description,
                        "origin_macro": origin_macro,
                        "time_saved_h": time_saved,
                        "requester": requester,
                        "status": "requested",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                st.success(f"Request “{name}” saved. Thank you!")

    requests = load_requests()
    if requests:
        st.divider()
        st.subheader(f"📋 Open requests ({len(requests)})")
        df = pd.DataFrame(requests)
        cols = [
            c
            for c in ["submitted_at", "name", "category", "requester", "status"]
            if c in df.columns
        ]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)


def page_dashboard(services):
    st.header("📈 Catalog dashboard")
    df = pd.DataFrame(services)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total services", len(df))
    c2.metric("Hours saved / cycle", f"~{int(df['time_saved_h'].sum())} h")
    c3.metric("Categories covered", df["category"].nunique())

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Services by category")
        st.bar_chart(df["category"].value_counts())
    with col2:
        st.subheader("Hours saved by category")
        st.bar_chart(df.groupby("category")["time_saved_h"].sum())

    st.divider()
    st.subheader("Breakdown by status")
    status_names = df["status"].map(lambda s: STATUS_LABELS.get(s, ("?",))[0])
    st.bar_chart(status_names.value_counts())

    counts = load_counts()
    if counts:
        st.divider()
        st.subheader("Most opened services")
        id_to_name = {s["id"]: s["name"] for s in services}
        ranking = (
            pd.Series({id_to_name.get(k, k): v for k, v in counts.items()})
            .sort_values(ascending=False)
        )
        st.bar_chart(ranking)

    st.divider()
    st.subheader("Catalog details")
    view = df[
        ["name", "category", "status", "frequency", "time_saved_h", "owner", "origin_macro"]
    ].rename(
        columns={
            "name": "Service",
            "category": "Category",
            "status": "Status",
            "frequency": "Frequency",
            "time_saved_h": "Hours saved",
            "owner": "Team",
            "origin_macro": "Source macro",
        }
    )
    st.dataframe(view, use_container_width=True, hide_index=True)


def page_about():
    st.header("ℹ️ About this portal")
    st.markdown(
        """
        **House of Servicing — Service Portal** centralizes the Servicing team's
        processes within a single marketplace.

        ### The principle
        The team maintains many **Excel/VBA macros**. Each macro is gradually
        **industrialized into a Python service** and gets its own dedicated page
        in the portal — describing what it does, its inputs and its outputs.

        ### Why
        - **Centralize**: a single entry point instead of scattered files.
        - **Make reliable**: versioned, maintained services rather than local macros.
        - **Track**: visibility on usage, owning teams and time savings.
        - **Industrialize**: a clear path from VBA to Python service.

        ### A service lifecycle
        `VBA macro` → `Industrialization request` → `In development` →
        `Beta` → `Live`

        ### Add / edit a service
        The catalog is driven by the `data/services.json` file. Each entry exposes
        a `purpose`, `inputs`, `outputs` and `benefits` block which feeds the
        dedicated service page.
        """
    )
    st.divider()
    st.markdown(f"### 📬 Contact\nA question or a request? Email **[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})**")


def main():
    inject_styles()
    services = load_services()

    with st.sidebar:
        st.markdown("## 🏛️ House of Servicing")
        st.caption("Service Portal")
        page = st.radio(
            "Navigation",
            ["🏪 Marketplace", "➕ Request a service", "📈 Dashboard", "ℹ️ About"],
            label_visibility="collapsed",
        )
        prev = st.session_state.get("_prev_page")
        if prev is not None and prev != page and "service" in st.query_params:
            del st.query_params["service"]
        st.session_state["_prev_page"] = page

        st.divider()
        st.caption("Catalog categories")
        for cat in sorted({s["category"] for s in services}):
            st.markdown(
                f"<span style='color:{category_color(cat)};'>●</span> {cat}",
                unsafe_allow_html=True,
            )
        st.divider()
        st.caption("📬 Contact")
        st.markdown(f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")

    service_id = st.query_params.get("service")
    if page == "🏪 Marketplace" and service_id:
        service = next((s for s in services if s["id"] == service_id), None)
        if service:
            page_service_detail(service)
            return
        else:
            del st.query_params["service"]

    if page == "🏪 Marketplace":
        page_marketplace(services)
    elif page == "➕ Request a service":
        page_request(services)
    elif page == "📈 Dashboard":
        page_dashboard(services)
    else:
        page_about()


if __name__ == "__main__":
    main()
