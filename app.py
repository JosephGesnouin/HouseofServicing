import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

DATA_DIR = Path(__file__).parent / "data"
SERVICES_FILE = DATA_DIR / "services.json"
REQUESTS_FILE = DATA_DIR / "requests.json"
COUNTS_FILE = DATA_DIR / "counts.json"

CONTACT_EMAIL = "servicing@houseofservicing.com"

STATUS_LABELS = {
    "live": ("En production", "#16a34a"),
    "beta": ("Bêta", "#d97706"),
    "dev": ("En développement", "#64748b"),
}

CATEGORY_THEMES = {
    "Réconciliation": "#2563eb",
    "Reporting & Pilotage": "#7c3aed",
    "Paiements & Encaissements": "#0891b2",
    "Conformité & Contrôle": "#dc2626",
    "Relation Client": "#db2777",
    "Gestion des Données": "#059669",
}
DEFAULT_THEME = "#475569"

st.set_page_config(
    page_title="House of Servicing — Portail des Services",
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


def increment_count(service_id, url):
    counts = load_counts()
    counts[service_id] = counts.get(service_id, 0) + 1
    COUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
    st.session_state["_pending_open"] = url


def category_color(category):
    return CATEGORY_THEMES.get(category, DEFAULT_THEME)


def inject_styles():
    st.markdown(
        """
        <style>
        /* Theme forcé en CSS : indépendant de config.toml (Domino, proxys, etc.) */
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
        /* CTA natif Streamlit stylé en bouton bleu */
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
        service["status"], ("Inconnu", "#64748b")
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
                <div class="hos-meta">⏱️ {service['frequency']} · 💪 ~{service['time_saved_h']} h/exécution économisées</div>
                <div class="hos-meta">👥 {service['owner']}</div>
                <div>{tags_html}</div>
                <div class="hos-count">👆 {n_clicks} ouverture(s)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if is_live:
            st.button(
                "Accéder au service →",
                key=f"open_{sid}",
                on_click=increment_count,
                args=(sid, service["url"]),
                use_container_width=True,
            )
        else:
            st.button(
                "Bientôt disponible",
                key=f"open_{sid}",
                disabled=True,
                use_container_width=True,
            )


def page_marketplace(services):
    st.markdown(
        f"""
        <div class="hos-hero">
            <h1>🏛️ Portail des Services — House of Servicing</h1>
            <p>La marketplace de l'équipe Servicing. Vos macros d'hier deviennent des services
            centralisés, fiables et accessibles en un clic.</p>
            <p style="font-size:.92rem;opacity:.85;margin-top:.6rem;">
                ✉️ Une question, une demande&nbsp;? Écrivez-nous :
                <a href="mailto:{CONTACT_EMAIL}" style="color:#bfdbfe;font-weight:600;">{CONTACT_EMAIL}</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        #### À quoi sert ce portail&nbsp;?
        L'équipe Servicing s'appuie sur de nombreuses **macros Excel/VBA** dispersées sur les postes.
        Ce portail les **rassemble en un point d'entrée unique** : chaque traitement est progressivement
        **industrialisé en service Python**, puis publié ici sous forme de vignette renvoyant directement
        vers l'outil en ligne.
        """
    )
    st.markdown(
        """
        - 🎯 **Trouver** le bon outil sans chercher dans les fichiers partagés
        - 🛡️ **Fiabiliser** : des services maintenus et versionnés, plus des macros locales
        - 📊 **Mesurer** le temps gagné et savoir qui maintient quoi
        - ➕ **Proposer** une nouvelle macro à industrialiser via l'onglet dédié
        """
    )
    st.divider()

    counts = load_counts()
    categories = sorted({s["category"] for s in services})
    total_saved = sum(s["time_saved_h"] for s in services)
    live_count = sum(1 for s in services if s["status"] == "live")
    total_clicks = sum(counts.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Services au catalogue", len(services))
    c2.metric("En production", live_count)
    c3.metric("Ouvertures cumulées", total_clicks)
    c4.metric("Heures économisées / cycle", f"~{total_saved} h")

    st.divider()

    fcol1, fcol2, fcol3 = st.columns([2, 1.3, 1.3])
    query = fcol1.text_input("🔎 Rechercher un service", placeholder="nom, mot-clé, tag...")
    cat_filter = fcol2.selectbox("Catégorie", ["Toutes"] + categories)
    status_filter = fcol3.selectbox(
        "Statut", ["Tous", "En production", "Bêta", "En développement"]
    )

    status_map = {"En production": "live", "Bêta": "beta", "En développement": "dev"}

    def matches(s):
        if cat_filter != "Toutes" and s["category"] != cat_filter:
            return False
        if status_filter != "Tous" and s["status"] != status_map[status_filter]:
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
        st.info("Aucun service ne correspond à votre recherche.")
        return

    st.caption(f"{len(filtered)} service(s) affiché(s)")
    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        row = st.columns(cols_per_row)
        for col, service in zip(row, filtered[i : i + cols_per_row]):
            with col:
                render_card(service, counts)

    pending = st.session_state.pop("_pending_open", None)
    if pending:
        components.html(
            f"""
            <script>window.open({json.dumps(pending)}, "_blank");</script>
            <div style="font-family:sans-serif;font-size:.85rem;">
                ↗ Le service s'ouvre dans un nouvel onglet.
                <a href={json.dumps(pending)} target="_blank">Cliquez ici si rien ne se passe.</a>
            </div>
            """,
            height=40,
        )


def page_propose(services):
    st.header("➕ Proposer un nouveau service")
    st.write(
        "Une macro à industrialiser ? Décrivez le besoin : l'équipe d'industrialisation "
        "le transformera en service Python centralisé."
    )

    categories = sorted({s["category"] for s in services})

    with st.form("propose_form", clear_on_submit=True):
        name = st.text_input("Nom du service *")
        col1, col2 = st.columns(2)
        category = col1.selectbox("Catégorie *", categories + ["Autre"])
        frequency = col2.selectbox(
            "Fréquence d'utilisation", ["Quotidien", "Hebdomadaire", "Mensuel", "Ponctuel"]
        )
        description = st.text_area("Description du besoin *")
        col3, col4 = st.columns(2)
        origin_macro = col3.text_input("Macro d'origine (fichier .xlsm)")
        time_saved = col4.number_input(
            "Temps économisé estimé (h / exécution)", min_value=0.0, value=1.0, step=0.5
        )
        requester = st.text_input("Votre nom / pôle *")
        submitted = st.form_submit_button("Soumettre la demande")

        if submitted:
            if not (name and description and requester):
                st.error("Merci de renseigner les champs obligatoires (*).")
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
                        "status": "demandé",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                st.success(f"Demande « {name} » enregistrée. Merci !")

    requests = load_requests()
    if requests:
        st.divider()
        st.subheader(f"📋 Demandes en cours ({len(requests)})")
        df = pd.DataFrame(requests)
        cols = [
            c
            for c in ["submitted_at", "name", "category", "requester", "status"]
            if c in df.columns
        ]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)


def page_dashboard(services):
    st.header("📈 Tableau de bord du catalogue")
    df = pd.DataFrame(services)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total services", len(df))
    c2.metric("Heures économisées / cycle", f"~{int(df['time_saved_h'].sum())} h")
    c3.metric("Catégories couvertes", df["category"].nunique())

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Services par catégorie")
        st.bar_chart(df["category"].value_counts())
    with col2:
        st.subheader("Heures économisées par catégorie")
        st.bar_chart(df.groupby("category")["time_saved_h"].sum())

    st.divider()
    st.subheader("Répartition par statut")
    status_names = df["status"].map(lambda s: STATUS_LABELS.get(s, ("?",))[0])
    st.bar_chart(status_names.value_counts())

    counts = load_counts()
    if counts:
        st.divider()
        st.subheader("Services les plus ouverts")
        id_to_name = {s["id"]: s["name"] for s in services}
        ranking = (
            pd.Series({id_to_name.get(k, k): v for k, v in counts.items()})
            .sort_values(ascending=False)
        )
        st.bar_chart(ranking)

    st.divider()
    st.subheader("Détail du catalogue")
    view = df[
        ["name", "category", "status", "frequency", "time_saved_h", "owner", "origin_macro"]
    ].rename(
        columns={
            "name": "Service",
            "category": "Catégorie",
            "status": "Statut",
            "frequency": "Fréquence",
            "time_saved_h": "Heures éco.",
            "owner": "Pôle",
            "origin_macro": "Macro d'origine",
        }
    )
    st.dataframe(view, use_container_width=True, hide_index=True)


def page_about():
    st.header("ℹ️ À propos du portail")
    st.markdown(
        """
        **House of Servicing — Portail des Services** centralise les traitements de
        l'équipe Servicing au sein d'une marketplace unique.

        ### Le principe
        L'équipe maintient de nombreuses **macros Excel/VBA**. Chaque macro est
        progressivement **industrialisée en service Python** puis publiée ici sous
        forme de vignette renvoyant vers le service en ligne.

        ### Pourquoi
        - **Centraliser** : un point d'entrée unique au lieu de fichiers éparpillés.
        - **Fiabiliser** : des services versionnés et maintenus, plutôt que des macros locales.
        - **Tracer** : visibilité sur l'usage, les pôles propriétaires et les gains de temps.
        - **Industrialiser** : un parcours clair du VBA vers le service Python.

        ### Cycle de vie d'un service
        `Macro VBA` → `Demande d'industrialisation` → `En développement` →
        `Bêta` → `En production`

        ### Ajouter / modifier un service
        Le catalogue est piloté par le fichier `data/services.json`. Ajoutez-y une entrée
        et elle apparaîtra automatiquement dans la marketplace.
        """
    )
    st.divider()
    st.markdown(f"### 📬 Contact\nUne question ou une demande&nbsp;? Écrivez à **[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})**")


def main():
    inject_styles()
    services = load_services()

    with st.sidebar:
        st.markdown("## 🏛️ House of Servicing")
        st.caption("Portail des Services")
        page = st.radio(
            "Navigation",
            ["🏪 Marketplace", "➕ Proposer un service", "📈 Tableau de bord", "ℹ️ À propos"],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Catégories du catalogue")
        for cat in sorted({s["category"] for s in services}):
            st.markdown(
                f"<span style='color:{category_color(cat)};'>●</span> {cat}",
                unsafe_allow_html=True,
            )
        st.divider()
        st.caption("📬 Contact")
        st.markdown(f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")

    if page == "🏪 Marketplace":
        page_marketplace(services)
    elif page == "➕ Proposer un service":
        page_propose(services)
    elif page == "📈 Tableau de bord":
        page_dashboard(services)
    else:
        page_about()


if __name__ == "__main__":
    main()
