import streamlit as st
import pandas as pd
from datetime import date

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Lutte Calendar",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #f7f8fa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 2rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #111827, #374151);
            color: white;
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 0.3rem;
        }

        .hero p {
            color: #d1d5db;
            font-size: 1.05rem;
        }

        .metric-card {
            background: white;
            padding: 1.2rem;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            text-align: center;
        }

        .metric-number {
            font-size: 2rem;
            font-weight: 700;
            color: #111827;
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.9rem;
        }

        .competition-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1.2rem;
            margin-bottom: 0.8rem;
        }

        .competition-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #111827;
        }

        .competition-meta {
            color: #6b7280;
            margin-top: 0.3rem;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.3rem;
        }

        .badge-green {
            background: #dcfce7;
            color: #166534;
        }

        .badge-orange {
            background: #ffedd5;
            color: #9a3412;
        }

        .badge-red {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge-blue {
            background: #dbeafe;
            color: #1e40af;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DONNÉES PAR DÉFAUT
# ============================================================

DEFAULT_COMPETITIONS = [
    {
        "Nom": "Tournoi de rentrée",
        "Date": date(2026, 9, 20),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U17",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Préparation",
        "Organisateur": "Comité régional",
        "Inscription": "",
        "Description": "Tournoi de rentrée.",
    },
    {
        "Nom": "Championnat régional",
        "Date": date(2026, 10, 18),
        "Ville": "Rennes",
        "Département": "Ille-et-Vilaine",
        "Région": "Bretagne",
        "Style": "Lutte gréco-romaine",
        "Niveau": "Régional",
        "Categorie": "U20",
        "Latitude": 48.1173,
        "Longitude": -1.6778,
        "Importance": "Objectif intermédiaire",
        "Organisateur": "Ligue régionale",
        "Inscription": "",
        "Description": "Championnat régional.",
    },
    {
        "Nom": "Championnat de France",
        "Date": date(2027, 2, 20),
        "Ville": "Paris",
        "Département": "Paris",
        "Région": "Île-de-France",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 48.8566,
        "Longitude": 2.3522,
        "Importance": "Objectif principal",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Championnat national.",
    },
]

REQUIRED_COLUMNS = [
    "Nom",
    "Date",
    "Ville",
    "Département",
    "Région",
    "Style",
    "Niveau",
    "Categorie",
    "Latitude",
    "Longitude",
    "Importance",
    "Organisateur",
    "Inscription",
    "Description",
]

# ============================================================
# INITIALISATION DES DONNÉES
# ============================================================

def create_default_dataframe():
    return pd.DataFrame(DEFAULT_COMPETITIONS)


if "competitions" not in st.session_state:
    st.session_state.competitions = create_default_dataframe()

else:
    current = st.session_state.competitions

    # Si une ancienne version de l'application
    # est encore en mémoire, on repart sur la
    # nouvelle structure.
    if not isinstance(current, pd.DataFrame):
        st.session_state.competitions = create_default_dataframe()

    elif not all(
        column in current.columns
        for column in REQUIRED_COLUMNS
    ):
        st.session_state.competitions = create_default_dataframe()


df = st.session_state.competitions.copy()

# ============================================================
# FONCTIONS
# ============================================================

def importance_badge(importance):

    if importance == "Objectif principal":
        return "badge-red"

    if importance == "Objectif intermédiaire":
        return "badge-orange"

    if importance == "Préparation":
        return "badge-green"

    return "badge-blue"


def phase_planification(jours):

    if jours > 56:
        return "🟢 Préparation générale"

    if jours > 28:
        return "🟡 Préparation spécifique"

    if jours > 7:
        return "🟠 Pré-compétition"

    if jours >= 0:
        return "🔴 Affûtage / compétition"

    return "🔵 Récupération"


def format_date(d):
    return d.strftime("%d/%m/%Y")


# ============================================================
# MENU
# ============================================================

st.sidebar.title("🤼 Lutte Calendar")

st.sidebar.caption(
    "Calendrier & planification sportive"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Tableau de bord",
        "📅 Calendrier",
        "🗺️ Carte",
        "➕ Ajouter une compétition",
        "🎯 Planification",
    ],
)

# ============================================================
# TABLEAU DE BORD
# ============================================================

if page == "🏠 Tableau de bord":

    st.markdown(
        """
        <div class="hero">
            <h1>🤼 Lutte Calendar</h1>
            <p>
                Calendrier partagé des compétitions
                de lutte et planification sportive.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    today = date.today()

    upcoming = df[
        df["Date"] >= today
    ].sort_values("Date")

    total = len(df)
    upcoming_count = len(upcoming)
    regions = df["Région"].nunique()
    cities = df["Ville"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    data = [
        (total, "Compétitions"),
        (upcoming_count, "À venir"),
        (regions, "Régions"),
        (cities, "Villes"),
    ]

    for col, (number, label) in zip(
        [c1, c2, c3, c4],
        data,
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">
                        {number}
                    </div>
                    <div class="metric-label">
                        {label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader("📅 Prochaines compétitions")

    if upcoming.empty:

        st.info(
            "Aucune compétition à venir."
        )

    else:

        for _, competition in upcoming.head(5).iterrows():

            days = (
                competition["Date"] - today
            ).days

            if days == 0:
                countdown = "Aujourd'hui"
            else:
                countdown = f"dans {days} jours"

            badge = importance_badge(
                competition["Importance"]
            )

            st.markdown(
                f"""
                <div class="competition-card">

                    <div class="competition-title">
                        {competition["Nom"]}
                    </div>

                    <div class="competition-meta">
                        📅 {format_date(competition["Date"])}
                        · 📍 {competition["Ville"]}
                        · 🥋 {competition["Style"]}
                    </div>

                    <br>

                    <span class="badge {badge}">
                        {competition["Importance"]}
                    </span>

                    <span class="badge badge-blue">
                        {competition["Niveau"]}
                    </span>

                    <span class="badge badge-blue">
                        {competition["Categorie"]}
                    </span>

                    <br><br>

                    <strong>{countdown}</strong>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("🎯 Objectifs principaux")

    objectives = df[
        df["Importance"] == "Objectif principal"
    ].sort_values("Date")

    if objectives.empty:

        st.info(
            "Aucun objectif principal enregistré."
        )

    else:

        for _, competition in objectives.iterrows():

            days = (
                competition["Date"] - today
            ).days

            st.success(
                f"🎯 **{competition['Nom']}** — "
                f"{format_date(competition['Date'])} — "
                f"{competition['Ville']} "
                f"({days} jours)"
            )


# ============================================================
# CALENDRIER
# ============================================================

elif page == "📅 Calendrier":

    st.title("📅 Calendrier des compétitions")

    col1, col2, col3 = st.columns(3)

    with col1:

        styles = [
            "Tous"
        ] + sorted(
            df["Style"].dropna().unique().tolist()
        )

        selected_style = st.selectbox(
            "🥋 Style",
            styles,
        )

    with col2:

        levels = [
            "Tous"
        ] + sorted(
            df["Niveau"].dropna().unique().tolist()
        )

        selected_level = st.selectbox(
            "🏆 Niveau",
            levels,
        )

    with col3:

        categories = [
            "Toutes"
        ] + sorted(
            df["Categorie"].dropna().unique().tolist()
        )

        selected_category = st.selectbox(
            "👤 Catégorie",
            categories,
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        regions = [
            "Toutes"
        ] + sorted(
            df["Région"].dropna().unique().tolist()
        )

        selected_region = st.selectbox(
            "📍 Région",
            regions,
        )

    with col5:

        importances = [
            "Toutes"
        ] + sorted(
            df["Importance"].dropna().unique().tolist()
        )

        selected_importance = st.selectbox(
            "🎯 Importance",
            importances,
        )

    with col6:

        only_future = st.checkbox(
            "Uniquement les compétitions à venir",
            value=True,
        )

    filtered = df.copy()

    if selected_style != "Tous":
        filtered = filtered[
            filtered["Style"] == selected_style
        ]

    if selected_level != "Tous":
        filtered = filtered[
            filtered["Niveau"] == selected_level
        ]

    if selected_category != "Toutes":
        filtered = filtered[
            filtered["Categorie"] == selected_category
        ]

    if selected_region != "Toutes":
        filtered = filtered[
            filtered["Région"] == selected_region
        ]

    if selected_importance != "Toutes":
        filtered = filtered[
            filtered["Importance"] == selected_importance
        ]

    if only_future:
        filtered = filtered[
            filtered["Date"] >= date.today()
        ]

    filtered = filtered.sort_values("Date")

    st.divider()

    st.subheader(
        f"{len(filtered)} compétition(s)"
    )

    if filtered.empty:

        st.info(
            "Aucune compétition ne correspond aux filtres."
        )

    else:

        for _, competition in filtered.iterrows():

            days = (
                competition["Date"] - date.today()
            ).days

            if days > 0:
                countdown = f"dans {days} jours"
            elif days == 0:
                countdown = "Aujourd'hui"
            else:
                countdown = f"il y a {-days} jours"

            with st.container(border=True):

                c1, c2, c3 = st.columns(
                    [2.2, 1.5, 1.5]
                )

                with c1:

                    st.subheader(
                        competition["Nom"]
                    )

                    st.write(
                        f"📅 {format_date(competition['Date'])}"
                        f" — {countdown}"
                    )

                    st.write(
                        f"📍 {competition['Ville']} "
                        f"({competition['Région']})"
                    )

                with c2:

                    st.write(
                        f"🥋 {competition['Style']}"
                    )

                    st.write(
                        f"👤 {competition['Categorie']}"
                    )

                    st.write(
                        f"🏆 {competition['Niveau']}"
                    )

                with c3:

                    st.write(
                        f"🎯 {competition['Importance']}"
                    )

                    st.write(
                        f"Organisateur : "
                        f"{competition['Organisateur']}"
                    )

                if competition["Description"]:

                    st.caption(
                        competition["Description"]
                    )

                if competition["Inscription"]:

                    st.link_button(
                        "🔗 Inscription",
                        competition["Inscription"],
                    )


# ============================================================
# CARTE
# ============================================================

elif page == "🗺️ Carte":

    st.title("🗺️ Carte des compétitions")

    col1, col2 = st.columns(2)

    with col1:

        map_level = st.selectbox(
            "🏆 Niveau",
            ["Tous"] + sorted(
                df["Niveau"].unique().tolist()
            ),
        )

    with col2:

        map_style = st.selectbox(
            "🥋 Style",
            ["Tous"] + sorted(
                df["Style"].unique().tolist()
            ),
        )

    map_df = df.copy()

    if map_level != "Tous":

        map_df = map_df[
            map_df["Niveau"] == map_level
        ]

    if map_style != "Tous":

        map_df = map_df[
            map_df["Style"] == map_style
        ]

    map_df = map_df.dropna(
        subset=[
            "Latitude",
            "Longitude",
        ]
    )

    st.subheader(
        f"📍 {len(map_df)} compétition(s)"
    )

    if not map_df.empty:

        st.map(
            map_df,
            latitude="Latitude",
            longitude="Longitude",
            zoom=5,
        )

        st.divider()

        for _, competition in map_df.sort_values(
            "Date"
        ).iterrows():

            st.write(
                f"📍 **{competition['Nom']}** — "
                f"{competition['Ville']} — "
                f"{format_date(competition['Date'])}"
            )

    else:

        st.info(
            "Aucune compétition géolocalisée."
        )


# ============================================================
# AJOUT
# ============================================================

elif page == "➕ Ajouter une compétition":

    st.title("➕ Ajouter une compétition")

    with st.form("competition_form"):

        name = st.text_input(
            "Nom de la compétition *"
        )

        description = st.text_area(
            "Description"
        )

        col1, col2 = st.columns(2)

        with col1:

            competition_date = st.date_input(
                "Date *",
                value=date.today(),
            )

            city = st.text_input(
                "Ville *"
            )

            department = st.text_input(
                "Département"
            )

            region = st.text_input(
                "Région"
            )

        with col2:

            style = st.selectbox(
                "Style",
                [
                    "Lutte libre",
                    "Lutte gréco-romaine",
                    "Lutte féminine",
                ],
            )

            level = st.selectbox(
                "Niveau",
                [
                    "Départemental",
                    "Régional",
                    "National",
                    "International",
                ],
            )

            category = st.text_input(
                "Catégorie"
            )

            importance = st.selectbox(
                "Importance",
                [
                    "Préparation",
                    "Compétition secondaire",
                    "Objectif intermédiaire",
                    "Objectif principal",
                ],
            )

        st.subheader("📍 Géolocalisation")

        col3, col4 = st.columns(2)

        with col3:

            latitude = st.number_input(
                "Latitude",
                value=49.1829,
                format="%.6f",
            )

        with col4:

            longitude = st.number_input(
                "Longitude",
                value=-0.3707,
                format="%.6f",
            )

        organizer = st.text_input(
            "Organisateur"
        )

        registration = st.text_input(
            "Lien d'inscription"
        )

        submitted = st.form_submit_button(
            "➕ Ajouter",
            use_container_width=True,
        )

        if submitted:

            if not name or not city:

                st.error(
                    "Le nom et la ville sont obligatoires."
                )

            else:

                new_competition = {
                    "Nom": name,
                    "Date": competition_date,
                    "Ville": city,
                    "Département": department,
                    "Région": region,
                    "Style": style,
                    "Niveau": level,
                    "Categorie": category,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Importance": importance,
                    "Organisateur": organizer,
                    "Inscription": registration,
                    "Description": description,
                }

                st.session_state.competitions = pd.concat(
                    [
                        st.session_state.competitions,
                        pd.DataFrame(
                            [new_competition]
                        ),
                    ],
                    ignore_index=True,
                )

                st.success(
                    "✅ Compétition ajoutée !"
                )


# ============================================================
# PLANIFICATION
# ============================================================

elif page == "🎯 Planification":

    st.title("🎯 Planification sportive")

    athlete = st.text_input(
        "Nom du lutteur",
        placeholder="Ex : Jean Dupont",
    )

    if athlete:

        objective = st.selectbox(
            "🎯 Objectif principal",
            [
                "Développement / apprentissage",
                "Championnat régional",
                "Championnat de France",
                "Compétition internationale",
                "Autre",
            ],
        )

        st.success(
            f"Objectif : **{objective}**"
        )

        selected = st.multiselect(
            "Sélectionner les compétitions",
            options=df["Nom"].tolist(),
        )

        if selected:

            planning = df[
                df["Nom"].isin(selected)
            ].copy()

            planning["Jours avant"] = planning[
                "Date"
            ].apply(
                lambda x:
                (x - date.today()).days
            )

            planning["Phase"] = planning[
                "Jours avant"
            ].apply(
                phase_planification
            )

            planning = planning.sort_values(
                "Date"
            )

            st.dataframe(
                planning[
                    [
                        "Nom",
                        "Date",
                        "Ville",
                        "Importance",
                        "Jours avant",
                        "Phase",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.subheader(
                "📈 Chronologie"
            )

            for _, competition in planning.iterrows():

                st.write(
                    f"**{format_date(competition['Date'])}** "
                    f"— {competition['Nom']} "
                    f"→ {competition['Phase']}"
                )

        else:

            st.info(
                "Sélectionne les compétitions "
                "de la saison."
            )

    else:

        st.info(
            "Entre le nom d'un lutteur."
        )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤼 Lutte Calendar V1.1"
)
