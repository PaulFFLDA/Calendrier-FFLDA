import streamlit as st
import pandas as pd
from datetime import date
import math

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

    .month-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .month-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }

    .event {
        border-left: 5px solid #2563eb;
        padding: 0.8rem 1rem;
        margin-bottom: 0.7rem;
        background: #f9fafb;
        border-radius: 8px;
    }

    .event-preparation {
        border-left-color: #16a34a;
    }

    .event-ranking {
        border-left-color: #f59e0b;
    }

    .event-objective {
        border-left-color: #dc2626;
    }

    .event-stage {
        border-left-color: #7c3aed;
    }

    .event-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #111827;
    }

    .event-meta {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }

    .green {
        background: #dcfce7;
        color: #166534;
    }

    .orange {
        background: #ffedd5;
        color: #9a3412;
    }

    .red {
        background: #fee2e2;
        color: #991b1b;
    }

    .blue {
        background: #dbeafe;
        color: #1e40af;
    }

    .purple {
        background: #ede9fe;
        color: #6d28d9;
    }

    .gray {
        background: #f3f4f6;
        color: #374151;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PARAMÈTRES CLUB
# ============================================================

if "club_settings" not in st.session_state:

    st.session_state.club_settings = {
        "Nom": "Mon club de lutte",
        "Adresse": "Caen, France",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Prix_essence": 1.80,
        "Consommation": 7.0,
    }

settings = st.session_state.club_settings

# ============================================================
# DONNÉES D'EXEMPLE
# ============================================================

DEFAULT_COMPETITIONS = [

    # SEPTEMBRE
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
        "Type": "Tournoi",
        "Phase": "Reprise",
        "Statut": "Prévisionnel",
        "Organisateur": "Comité régional",
        "Inscription": "",
        "Description": "Tournoi de rentrée.",
    },

    {
        "Nom": "TNR de rentrée",
        "Date": date(2026, 9, 29),
        "Ville": "Besançon",
        "Département": "Doubs",
        "Région": "Bourgogne-Franche-Comté",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 47.2378,
        "Longitude": 6.0241,
        "Importance": "Objectif intermédiaire",
        "Type": "TNR",
        "Phase": "Préparation générale",
        "Statut": "Officiel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
    },

    # OCTOBRE
    {
        "Nom": "Championnat de Normandie",
        "Date": date(2026, 10, 18),
        "Ville": "Rennes",
        "Département": "Ille-et-Vilaine",
        "Région": "Normandie",
        "Style": "Lutte gréco-romaine",
        "Niveau": "Régional",
        "Categorie": "U20",
        "Latitude": 48.1173,
        "Longitude": -1.6778,
        "Importance": "Objectif intermédiaire",
        "Type": "Championnat régional",
        "Phase": "Préparation spécifique",
        "Statut": "Prévisionnel",
        "Organisateur": "Ligue régionale",
        "Inscription": "",
        "Description": "Date indicative à confirmer.",
    },

    {
        "Nom": "Tournoi National d'Automne",
        "Date": date(2026, 10, 25),
        "Ville": "Paris",
        "Département": "Paris",
        "Région": "Île-de-France",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 48.8566,
        "Longitude": 2.3522,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Préparation spécifique",
        "Statut": "Prévisionnel",
        "Organisateur": "Organisation nationale",
        "Inscription": "",
        "Description": "Tournoi national d'automne.",
    },

    # NOVEMBRE
    {
        "Nom": "TNR Novembre",
        "Date": date(2026, 11, 14),
        "Ville": "Dijon",
        "Département": "Côte-d'Or",
        "Région": "Bourgogne-Franche-Comté",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 47.3220,
        "Longitude": 5.0415,
        "Importance": "Objectif intermédiaire",
        "Type": "TNR",
        "Phase": "Préparation spécifique",
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Ranking national.",
    },

    {
        "Nom": "Tournoi de Rouen",
        "Date": date(2026, 11, 28),
        "Ville": "Rouen",
        "Département": "Seine-Maritime",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U15",
        "Latitude": 49.4432,
        "Longitude": 1.0993,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Préparation",
        "Statut": "Prévisionnel",
        "Organisateur": "Club local",
        "Inscription": "",
        "Description": "Tournoi régional.",
    },

    # DÉCEMBRE
    {
        "Nom": "Tournoi de Noël",
        "Date": date(2026, 12, 12),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U13",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Préparation",
        "Statut": "Prévisionnel",
        "Organisateur": "Club local",
        "Inscription": "",
        "Description": "Tournoi de fin d'année.",
    },

    # JANVIER
    {
        "Nom": "TNR Janvier",
        "Date": date(2027, 1, 16),
        "Ville": "Lyon",
        "Département": "Rhône",
        "Région": "Auvergne-Rhône-Alpes",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 45.7640,
        "Longitude": 4.8357,
        "Importance": "Objectif intermédiaire",
        "Type": "TNR",
        "Phase": "Préparation spécifique",
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Ranking national.",
    },

    {
        "Nom": "Tournoi National de préparation",
        "Date": date(2027, 1, 30),
        "Ville": "Nantes",
        "Département": "Loire-Atlantique",
        "Région": "Pays de la Loire",
        "Style": "Lutte gréco-romaine",
        "Niveau": "National",
        "Categorie": "U20",
        "Latitude": 47.2184,
        "Longitude": -1.5536,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Préparation spécifique",
        "Statut": "Prévisionnel",
        "Organisateur": "Organisation nationale",
        "Inscription": "",
        "Description": "Préparation aux échéances nationales.",
    },

    # FÉVRIER
    {
        "Nom": "Championnat de Normandie",
        "Date": date(2027, 2, 7),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U17",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Objectif principal",
        "Type": "Championnat régional",
        "Phase": "Objectif principal",
        "Statut": "Prévisionnel",
        "Organisateur": "Ligue régionale",
        "Inscription": "",
        "Description": "Échéance régionale.",
    },

    {
        "Nom": "TNR Février",
        "Date": date(2027, 2, 13),
        "Ville": "Paris",
        "Département": "Paris",
        "Région": "Île-de-France",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 48.8566,
        "Longitude": 2.3522,
        "Importance": "Préparation",
        "Type": "TNR",
        "Phase": "Pré-compétition",
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Dernière évaluation avant championnat.",
    },

    # MARS
    {
        "Nom": "Championnat de France U17",
        "Date": date(2027, 3, 20),
        "Ville": "Paris",
        "Département": "Paris",
        "Région": "Île-de-France",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 48.8566,
        "Longitude": 2.3522,
        "Importance": "Objectif principal",
        "Type": "Championnat de France",
        "Phase": "Objectif principal",
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Objectif principal de la saison.",
    },

    # AVRIL
    {
        "Nom": "Tournoi National de Printemps",
        "Date": date(2027, 4, 10),
        "Ville": "Reims",
        "Département": "Marne",
        "Région": "Grand Est",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 49.2583,
        "Longitude": 4.0317,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Récupération",
        "Statut": "Prévisionnel",
        "Organisateur": "Organisation nationale",
        "Inscription": "",
        "Description": "Tournoi de reprise.",
    },

    # MAI
    {
        "Nom": "Championnat de France Seniors",
        "Date": date(2027, 5, 15),
        "Ville": "Toulouse",
        "Département": "Haute-Garonne",
        "Région": "Occitanie",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 43.6047,
        "Longitude": 1.4442,
        "Importance": "Objectif principal",
        "Type": "Championnat de France",
        "Phase": "Objectif principal",
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Exemple d'objectif national.",
    },

    # JUIN
    {
        "Nom": "Tournoi de fin de saison",
        "Date": date(2027, 6, 12),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U15",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Préparation",
        "Type": "Tournoi",
        "Phase": "Transition",
        "Statut": "Prévisionnel",
        "Organisateur": "Club local",
        "Inscription": "",
        "Description": "Fin de saison.",
    },
]

# ============================================================
# COLONNES
# ============================================================

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
    "Type",
    "Phase",
    "Statut",
    "Organisateur",
    "Inscription",
    "Description",
]

# ============================================================
# INITIALISATION
# ============================================================

def create_default_dataframe():
    return pd.DataFrame(DEFAULT_COMPETITIONS)


if "competitions" not in st.session_state:
    st.session_state.competitions = create_default_dataframe()

else:

    current = st.session_state.competitions

    if not isinstance(current, pd.DataFrame):
        st.session_state.competitions = create_default_dataframe()

    elif not all(
        column in current.columns
        for column in REQUIRED_COLUMNS
    ):
        st.session_state.competitions = create_default_dataframe()


df = st.session_state.competitions.copy()

# ============================================================
# UTILITAIRES
# ============================================================

MONTHS = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
}


def format_date(value):

    if pd.isna(value):
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")

    return str(value)


def event_class(importance):

    if importance == "Objectif principal":
        return "event-objective"

    if importance == "Objectif intermédiaire":
        return "event-ranking"

    if importance == "Préparation":
        return "event-preparation"

    return ""


def badge_class(importance):

    if importance == "Objectif principal":
        return "red"

    if importance == "Objectif intermédiaire":
        return "orange"

    if importance == "Préparation":
        return "green"

    return "blue"


def distance_km(lat1, lon1, lat2, lon2):

    if any(
        pd.isna(x)
        for x in [lat1, lon1, lat2, lon2]
    ):
        return None

    radius = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius * c


def travel_cost(distance):

    if distance is None:
        return None

    round_trip = distance * 2

    liters = (
        round_trip
        / 100
        * settings["Consommation"]
    )

    return liters * settings["Prix_essence"]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤼 Lutte Calendar")

st.sidebar.caption(
    "Calendrier & planification sportive"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Tableau de bord",
        "📅 Calendrier saison",
        "📋 Liste des compétitions",
        "🗺️ Carte",
        "➕ Ajouter une compétition",
        "🎯 Planification",
        "⚙️ Paramètres club",
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
                Calendrier des compétitions,
                déplacements et planification sportive.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    today = date.today()

    upcoming = df[
        df["Date"] >= today
    ].sort_values("Date")

    objectives = df[
        df["Importance"] == "Objectif principal"
    ]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Compétitions",
            len(df),
        )

    with c2:
        st.metric(
            "À venir",
            len(upcoming),
        )

    with c3:
        st.metric(
            "Objectifs",
            len(objectives),
        )

    with c4:
        st.metric(
            "Villes",
            df["Ville"].nunique(),
        )

    st.divider()

    st.subheader("🎯 Prochain objectif")

    future_objectives = objectives[
        objectives["Date"] >= today
    ].sort_values("Date")

    if future_objectives.empty:

        st.info(
            "Aucun objectif principal à venir."
        )

    else:

        competition = future_objectives.iloc[0]

        days = (
            competition["Date"] - today
        ).days

        st.success(
            f"🎯 **{competition['Nom']}**\n\n"
            f"📅 {format_date(competition['Date'])}  \n"
            f"📍 {competition['Ville']}  \n"
            f"⏱️ Dans **{days} jours**"
        )

    st.divider()

    st.subheader("📅 Prochaines compétitions")

    for _, competition in upcoming.head(5).iterrows():

        days = (
            competition["Date"] - today
        ).days

        cls = event_class(
            competition["Importance"]
        )

        badge = badge_class(
            competition["Importance"]
        )

        st.markdown(
            f"""
            <div class="event {cls}">
                <div class="event-title">
                    {competition["Nom"]}
                </div>

                <div class="event-meta">
                    📅 {format_date(competition["Date"])}
                    · 📍 {competition["Ville"]}
                    · 🥋 {competition["Categorie"]}
                </div>

                <br>

                <span class="badge {badge}">
                    {competition["Importance"]}
                </span>

                <span class="badge blue">
                    {competition["Type"]}
                </span>

                <span class="badge gray">
                    {competition["Statut"]}
                </span>

                <br><br>

                ⏱️ Dans {days} jours
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# CALENDRIER SAISON
# ============================================================

elif page == "📅 Calendrier saison":

    st.title("📅 Calendrier de la saison")

    st.caption(
        "Saison 2026 / 2027 — exemple de calendrier "
        "à adapter aux dates officielles."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_type = st.selectbox(
            "Type",
            [
                "Tous",
            ]
            + sorted(
                df["Type"].dropna().unique()
            ),
        )

    with col2:

        selected_category = st.selectbox(
            "Catégorie",
            [
                "Toutes",
            ]
            + sorted(
                df["Categorie"].dropna().unique()
            ),
        )

    with col3:

        show_past = st.checkbox(
            "Afficher les compétitions passées",
            value=True,
        )

    calendar_df = df.copy()

    if selected_type != "Tous":

        calendar_df = calendar_df[
            calendar_df["Type"] == selected_type
        ]

    if selected_category != "Toutes":

        calendar_df = calendar_df[
            calendar_df["Categorie"]
            == selected_category
        ]

    if not show_past:

        calendar_df = calendar_df[
            calendar_df["Date"] >= date.today()
        ]

    calendar_df = calendar_df.sort_values(
        "Date"
    )

    for month_number in range(1, 13):

        month_df = calendar_df[
            calendar_df["Date"].apply(
                lambda x: x.month
                == month_number
            )
        ]

        if month_df.empty:
            continue

        st.markdown(
            f"""
            <div class="month-card">

                <div class="month-title">
                    📅 {MONTHS[month_number]}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        for _, competition in month_df.iterrows():

            cls = event_class(
                competition["Importance"]
            )

            badge = badge_class(
                competition["Importance"]
            )

            st.markdown(
                f"""
                <div class="event {cls}">

                    <div class="event-title">
                        {competition["Nom"]}
                    </div>

                    <div class="event-meta">
                        📅 {format_date(competition["Date"])}
                        · 📍 {competition["Ville"]}
                        · 👤 {competition["Categorie"]}
                    </div>

                    <br>

                    <span class="badge {badge}">
                        {competition["Importance"]}
                    </span>

                    <span class="badge blue">
                        {competition["Type"]}
                    </span>

                    <span class="badge purple">
                        {competition["Phase"]}
                    </span>

                    <span class="badge gray">
                        {competition["Statut"]}
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# LISTE
# ============================================================

elif page == "📋 Liste des compétitions":

    st.title("📋 Toutes les compétitions")

    filtered = df.copy()

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_region = st.selectbox(
            "Région",
            ["Toutes"]
            + sorted(
                df["Région"].dropna().unique()
            ),
        )

    with col2:

        selected_type = st.selectbox(
            "Type",
            ["Tous"]
            + sorted(
                df["Type"].dropna().unique()
            ),
        )

    with col3:

        selected_importance = st.selectbox(
            "Importance",
            ["Toutes"]
            + sorted(
                df["Importance"].dropna().unique()
            ),
        )

    if selected_region != "Toutes":

        filtered = filtered[
            filtered["Région"]
            == selected_region
        ]

    if selected_type != "Tous":

        filtered = filtered[
            filtered["Type"]
            == selected_type
        ]

    if selected_importance != "Toutes":

        filtered = filtered[
            filtered["Importance"]
            == selected_importance
        ]

    filtered = filtered.sort_values("Date")

    st.write(
        f"**{len(filtered)} compétition(s)**"
    )

    for _, competition in filtered.iterrows():

        with st.container(border=True):

            st.subheader(
                competition["Nom"]
            )

            st.write(
                f"📅 {format_date(competition['Date'])}"
            )

            st.write(
                f"📍 {competition['Ville']} "
                f"({competition['Région']})"
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(
                    f"🥋 {competition['Style']}"
                )

            with c2:
                st.write(
                    f"🏆 {competition['Niveau']}"
                )

            with c3:
                st.write(
                    f"👤 {competition['Categorie']}"
                )

            st.write(
                f"🎯 {competition['Importance']}"
            )

            st.write(
                f"📌 {competition['Type']} "
                f"— {competition['Phase']}"
            )

            if competition["Description"]:

                st.caption(
                    competition["Description"]
                )

            # DISTANCE
            dist = distance_km(
                settings["Latitude"],
                settings["Longitude"],
                competition["Latitude"],
                competition["Longitude"],
            )

            cost = travel_cost(dist)

            if dist is not None:

                st.info(
                    f"🚗 {dist:.0f} km aller "
                    f"· {dist * 2:.0f} km A/R "
                    f"· 💰 {cost:.2f} € carburant"
                )


# ============================================================
# CARTE
# ============================================================

elif page == "🗺️ Carte":

    st.title("🗺️ Carte interactive")

    st.caption(
        "Les points représentent les compétitions."
        " Les informations détaillées apparaissent"
        " dans le tableau situé sous la carte."
    )

    map_df = df.dropna(
        subset=[
            "Latitude",
            "Longitude",
        ]
    ).copy()

    st.map(
        map_df,
        latitude="Latitude",
        longitude="Longitude",
        zoom=5,
    )

    st.divider()

    st.subheader("📍 Compétitions")

    for _, competition in map_df.sort_values(
        "Date"
    ).iterrows():

        dist = distance_km(
            settings["Latitude"],
            settings["Longitude"],
            competition["Latitude"],
            competition["Longitude"],
        )

        cost = travel_cost(dist)

        with st.expander(
            f"📍 {competition['Nom']} — "
            f"{competition['Ville']}"
        ):

            st.write(
                f"📅 {format_date(competition['Date'])}"
            )

            st.write(
                f"🥋 {competition['Style']}"
            )

            st.write(
                f"👤 {competition['Categorie']}"
            )

            st.write(
                f"🏆 {competition['Niveau']}"
            )

            st.write(
                f"🎯 {competition['Importance']}"
            )

            if dist is not None:

                st.write(
                    f"🚗 {dist:.0f} km aller"
                )

                st.write(
                    f"🔄 {dist * 2:.0f} km A/R"
                )

                st.write(
                    f"💰 {cost:.2f} € de carburant"
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

        competition_date = st.date_input(
            "Date *",
            value=date.today(),
        )

        col1, col2 = st.columns(2)

        with col1:

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

            category = st.text_input(
                "Catégorie",
                value="U17",
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

        competition_type = st.selectbox(
            "Type",
            [
                "Tournoi",
                "TNR",
                "Championnat départemental",
                "Championnat régional",
                "Championnat de France",
                "International",
                "Stage",
                "Autre",
            ],
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

        phase = st.selectbox(
            "Phase de planification",
            [
                "Reprise",
                "Préparation générale",
                "Préparation spécifique",
                "Pré-compétition",
                "Compétition",
                "Récupération",
                "Objectif principal",
                "Transition",
            ],
        )

        status = st.selectbox(
            "Statut",
            [
                "Prévisionnel",
                "Officiel",
            ],
        )

        st.subheader(
            "📍 Géolocalisation"
        )

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

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "➕ Ajouter la compétition",
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
                    "Type": competition_type,
                    "Phase": phase,
                    "Statut": status,
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

                st.rerun()


# ============================================================
# PLANIFICATION
# ============================================================

elif page == "🎯 Planification":

    st.title("🎯 Planification sportive")

    st.write(
        "Sélectionne les compétitions qui font partie "
        "de la saison de ton lutteur."
    )

    athlete = st.text_input(
        "Nom du lutteur",
        placeholder="Ex : Jean Dupont",
    )

    if athlete:

        selected = st.multiselect(
            "Compétitions de la saison",
            options=df["Nom"].tolist(),
        )

        if selected:

            planning = df[
                df["Nom"].isin(selected)
            ].copy()

            planning["Jours avant"] = (
                planning["Date"]
                .apply(
                    lambda x:
                    (x - date.today()).days
                )
            )

            def planning_phase(days):

                if days < 0:
                    return "⚪ Passée"

                if days > 56:
                    return "🟢 Préparation générale"

                if days > 28:
                    return "🟡 Préparation spécifique"

                if days > 7:
                    return "🟠 Pré-compétition"

                return "🔴 Affûtage"

            planning["Phase actuelle"] = (
                planning["Jours avant"]
                .apply(planning_phase)
            )

            planning = planning.sort_values(
                "Date"
            )

            st.subheader(
                f"📈 Saison de {athlete}"
            )

            st.dataframe(
                planning[
                    [
                        "Nom",
                        "Date",
                        "Ville",
                        "Importance",
                        "Type",
                        "Phase",
                        "Jours avant",
                        "Phase actuelle",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            st.subheader(
                "🗓️ Chronologie"
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
# PARAMÈTRES CLUB
# ============================================================

elif page == "⚙️ Paramètres club":

    st.title("⚙️ Paramètres du club")

    st.write(
        "Ces paramètres servent à calculer automatiquement "
        "les distances et les coûts de déplacement."
    )

    with st.form("club_settings"):

        club_name = st.text_input(
            "Nom du club",
            value=settings["Nom"],
        )

        address = st.text_input(
            "Adresse du club",
            value=settings["Adresse"],
        )

        st.subheader(
            "📍 Position du club"
        )

        col1, col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude",
                value=float(
                    settings["Latitude"]
                ),
                format="%.6f",
            )

        with col2:

            longitude = st.number_input(
                "Longitude",
                value=float(
                    settings["Longitude"]
                ),
                format="%.6f",
            )

        st.subheader(
            "⛽ Paramètres véhicule"
        )

        fuel_price = st.number_input(
            "Prix de l'essence (€ / litre)",
            min_value=0.0,
            value=float(
                settings["Prix_essence"]
            ),
            step=0.01,
        )

        consumption = st.number_input(
            "Consommation (L / 100 km)",
            min_value=0.1,
            value=float(
                settings["Consommation"]
            ),
            step=0.1,
        )

        submitted = st.form_submit_button(
            "💾 Enregistrer",
            use_container_width=True,
        )

        if submitted:

            st.session_state.club_settings = {
                "Nom": club_name,
                "Adresse": address,
                "Latitude": latitude,
                "Longitude": longitude,
                "Prix_essence": fuel_price,
                "Consommation": consumption,
            }

            st.success(
                "✅ Paramètres enregistrés."
            )

            st.rerun()

    st.divider()

    st.subheader(
        "💰 Exemple de calcul"
    )

    st.write(
        f"Prix essence : "
        f"**{settings['Prix_essence']:.2f} €/L**"
    )

    st.write(
        f"Consommation : "
        f"**{settings['Consommation']:.1f} L/100 km**"
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤼 Lutte Calendar V1.5"
)

st.sidebar.caption(
    "Calendrier sportif & planification"
)
