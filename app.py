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

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MOIS
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


# ============================================================
# PARAMÈTRES DU CLUB
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
# COMPÉTITIONS PAR DÉFAUT
# ============================================================

DEFAULT_COMPETITIONS = [

    # --------------------------------------------------------
    # SEPTEMBRE 2026
    # --------------------------------------------------------

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
        "Statut": "Prévisionnel",
        "Organisateur": "FFLDA",
        "Inscription": "",
        "Description": "Exemple de tournoi national ranking.",
    },


    # --------------------------------------------------------
    # OCTOBRE 2026
    # --------------------------------------------------------

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
        "Description": "Exemple de tournoi national.",
    },


    # --------------------------------------------------------
    # NOVEMBRE 2026
    # --------------------------------------------------------

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
        "Description": "Exemple de ranking national.",
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


    # --------------------------------------------------------
    # DÉCEMBRE 2026
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # JANVIER 2027
    # --------------------------------------------------------

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
        "Description": "Exemple de ranking national.",
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


    # --------------------------------------------------------
    # FÉVRIER 2027
    # --------------------------------------------------------

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
        "Description": "Exemple d'échéance régionale.",
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
        "Description": "Exemple de dernière évaluation.",
    },


    # --------------------------------------------------------
    # MARS 2027
    # --------------------------------------------------------

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
        "Description": "Exemple d'objectif national.",
    },


    # --------------------------------------------------------
    # AVRIL 2027
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # MAI 2027
    # --------------------------------------------------------

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
        "Description": "Exemple d'objectif national senior.",
    },


    # --------------------------------------------------------
    # JUIN 2027
    # --------------------------------------------------------

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
# COLONNES OBLIGATOIRES
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

    return pd.DataFrame(
        DEFAULT_COMPETITIONS
    )


if "competitions" not in st.session_state:

    st.session_state.competitions = (
        create_default_dataframe()
    )

else:

    current = st.session_state.competitions

    if not isinstance(
        current,
        pd.DataFrame,
    ):

        st.session_state.competitions = (
            create_default_dataframe()
        )

    elif not all(
        column in current.columns
        for column in REQUIRED_COLUMNS
    ):

        st.session_state.competitions = (
            create_default_dataframe()
        )


df = st.session_state.competitions.copy()


# ============================================================
# FONCTIONS
# ============================================================

def format_date(value):

    if pd.isna(value):
        return ""

    if hasattr(
        value,
        "strftime",
    ):

        return value.strftime(
            "%d/%m/%Y"
        )

    return str(value)


def distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):

    if any(
        pd.isna(x)
        for x in [
            lat1,
            lon1,
            lat2,
            lon2,
        ]
    ):

        return None

    radius = 6371

    lat1 = math.radians(
        float(lat1)
    )

    lon1 = math.radians(
        float(lon1)
    )

    lat2 = math.radians(
        float(lat2)
    )

    lon2 = math.radians(
        float(lon2)
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
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

    return (
        liters
        * settings["Prix_essence"]
    )


def importance_icon(
    importance,
):

    if importance == "Objectif principal":
        return "🔴"

    if importance == "Objectif intermédiaire":
        return "🟠"

    if importance == "Préparation":
        return "🟢"

    return "🔵"


def planning_phase(
    days,
):

    if days < 0:
        return "⚪ Compétition passée"

    if days > 56:
        return "🟢 Préparation générale"

    if days > 28:
        return "🟡 Préparation spécifique"

    if days > 7:
        return "🟠 Pré-compétition"

    return "🔴 Affûtage"


# ============================================================
# MENU
# ============================================================

st.sidebar.title(
    "🤼 Lutte Calendar"
)

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

    st.title(
        "🤼 Lutte Calendar"
    )

    st.subheader(
        "Calendrier & planification sportive"
    )

    st.write(
        "Une application pour centraliser "
        "les compétitions de lutte, les déplacements "
        "et la planification de la saison."
    )

    today = date.today()

    upcoming = df[
        df["Date"] >= today
    ].sort_values(
        "Date"
    )

    objectives = df[
        df["Importance"]
        == "Objectif principal"
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Compétitions",
            len(df),
        )

    with col2:

        st.metric(
            "À venir",
            len(upcoming),
        )

    with col3:

        st.metric(
            "Objectifs principaux",
            len(objectives),
        )

    with col4:

        st.metric(
            "Villes",
            df["Ville"].nunique(),
        )

    st.divider()

    # --------------------------------------------------------
    # PROCHAIN OBJECTIF
    # --------------------------------------------------------

    st.subheader(
        "🎯 Prochain objectif"
    )

    future_objectives = objectives[
        objectives["Date"] >= today
    ].sort_values(
        "Date"
    )

    if future_objectives.empty:

        st.info(
            "Aucun objectif principal à venir."
        )

    else:

        competition = (
            future_objectives.iloc[0]
        )

        days = (
            competition["Date"]
            - today
        ).days

        st.success(
            f"🎯 **{competition['Nom']}**  \n"
            f"📅 {format_date(competition['Date'])}  \n"
            f"📍 {competition['Ville']}  \n"
            f"⏱️ Dans **{days} jours**"
        )

    st.divider()

    # --------------------------------------------------------
    # PROCHAINES COMPÉTITIONS
    # --------------------------------------------------------

    st.subheader(
        "📅 Prochaines compétitions"
    )

    if upcoming.empty:

        st.info(
            "Aucune compétition à venir."
        )

    else:

        for _, competition in (
            upcoming.head(5).iterrows()
        ):

            days = (
                competition["Date"]
                - today
            ).days

            icon = importance_icon(
                competition["Importance"]
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {icon} {competition['Nom']}"
                )

                st.write(
                    f"📅 **{format_date(competition['Date'])}**"
                    f" · "
                    f"📍 **{competition['Ville']}**"
                )

                st.write(
                    f"🥋 {competition['Style']}"
                    f" · "
                    f"👤 {competition['Categorie']}"
                    f" · "
                    f"🏆 {competition['Niveau']}"
                )

                st.write(
                    f"🎯 {competition['Importance']}"
                    f" · "
                    f"📌 {competition['Type']}"
                )

                st.caption(
                    f"⏱️ Dans {days} jours"
                )


# ============================================================
# CALENDRIER SAISON
# ============================================================

elif page == "📅 Calendrier saison":

    st.title(
        "📅 Calendrier de la saison"
    )

    st.caption(
        "Saison 2026 / 2027 — exemples à adapter "
        "aux dates officielles."
    )

    # --------------------------------------------------------
    # FILTRES
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_type = st.selectbox(
            "Type",
            [
                "Tous"
            ]
            +
            sorted(
                df["Type"]
                .dropna()
                .unique()
                .tolist()
            ),
        )

    with col2:

        selected_category = st.selectbox(
            "Catégorie",
            [
                "Toutes"
            ]
            +
            sorted(
                df["Categorie"]
                .dropna()
                .unique()
                .tolist()
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
            calendar_df["Type"]
            == selected_type
        ]

    if selected_category != "Toutes":

        calendar_df = calendar_df[
            calendar_df["Categorie"]
            == selected_category
        ]

    if not show_past:

        calendar_df = calendar_df[
            calendar_df["Date"]
            >= date.today()
        ]

    calendar_df = calendar_df.sort_values(
        "Date"
    )

    st.divider()

    # --------------------------------------------------------
    # MOIS PAR MOIS
    # --------------------------------------------------------

    for month_number in range(
        1,
        13,
    ):

        month_df = calendar_df[
            calendar_df["Date"].apply(
                lambda x:
                x.month
                == month_number
            )
        ]

        if month_df.empty:
            continue

        # Titre du mois
        st.header(
            f"📅 {MONTHS[month_number]}"
        )

        st.caption(
            f"{len(month_df)} compétition(s)"
        )

        # ----------------------------------------------------
        # COMPÉTITIONS DU MOIS
        # ----------------------------------------------------

        for _, competition in (
            month_df.iterrows()
        ):

            icon = importance_icon(
                competition["Importance"]
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {icon} {competition['Nom']}"
                )

                st.write(
                    f"📅 **{format_date(competition['Date'])}**"
                    f" · "
                    f"📍 **{competition['Ville']}**"
                )

                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.write(
                        f"🥋 {competition['Style']}"
                    )

                    st.write(
                        f"👤 {competition['Categorie']}"
                    )

                with col2:

                    st.write(
                        f"🏆 {competition['Niveau']}"
                    )

                    st.write(
                        f"📌 {competition['Type']}"
                    )

                with col3:

                    st.write(
                        f"🎯 {competition['Importance']}"
                    )

                    st.write(
                        f"📊 {competition['Statut']}"
                    )

                st.info(
                    f"🎯 Phase : {competition['Phase']}"
                )

                if (
                    pd.notna(
                        competition["Description"]
                    )
                    and competition["Description"]
                ):

                    st.caption(
                        competition["Description"]
                    )

                # Distance
                dist = distance_km(
                    settings["Latitude"],
                    settings["Longitude"],
                    competition["Latitude"],
                    competition["Longitude"],
                )

                if dist is not None:

                    cost = travel_cost(
                        dist
                    )

                    st.write(
                        f"🚗 **{dist:.0f} km aller**"
                        f" · "
                        f"🔄 **{dist * 2:.0f} km A/R**"
                        f" · "
                        f"💰 **{cost:.2f} €**"
                    )

                if (
                    pd.notna(
                        competition["Inscription"]
                    )
                    and competition["Inscription"]
                ):

                    st.link_button(
                        "🔗 Inscription",
                        competition["Inscription"],
                    )

        st.divider()


# ============================================================
# LISTE DES COMPÉTITIONS
# ============================================================

elif page == "📋 Liste des compétitions":

    st.title(
        "📋 Liste des compétitions"
    )

    filtered = df.copy()

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_region = st.selectbox(
            "Région",
            [
                "Toutes"
            ]
            +
            sorted(
                df["Région"]
                .dropna()
                .unique()
                .tolist()
            ),
        )

    with col2:

        selected_type = st.selectbox(
            "Type",
            [
                "Tous"
            ]
            +
            sorted(
                df["Type"]
                .dropna()
                .unique()
                .tolist()
            ),
        )

    with col3:

        selected_importance = st.selectbox(
            "Importance",
            [
                "Toutes"
            ]
            +
            sorted(
                df["Importance"]
                .dropna()
                .unique()
                .tolist()
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

    filtered = filtered.sort_values(
        "Date"
    )

    st.write(
        f"**{len(filtered)} compétition(s)**"
    )

    for _, competition in (
        filtered.iterrows()
    ):

        icon = importance_icon(
            competition["Importance"]
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {icon} {competition['Nom']}"
            )

            st.write(
                f"📅 **{format_date(competition['Date'])}**"
            )

            st.write(
                f"📍 **{competition['Ville']}**"
                f" · {competition['Région']}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            with col1:

                st.write(
                    f"🥋 {competition['Style']}"
                )

                st.write(
                    f"👤 {competition['Categorie']}"
                )

            with col2:

                st.write(
                    f"🏆 {competition['Niveau']}"
                )

                st.write(
                    f"📌 {competition['Type']}"
                )

            with col3:

                st.write(
                    f"🎯 {competition['Importance']}"
                )

                st.write(
                    f"📊 {competition['Statut']}"
                )

            st.write(
                f"🎯 Phase : {competition['Phase']}"
            )

            if (
                pd.notna(
                    competition["Description"]
                )
                and competition["Description"]
            ):

                st.caption(
                    competition["Description"]
                )

            dist = distance_km(
                settings["Latitude"],
                settings["Longitude"],
                competition["Latitude"],
                competition["Longitude"],
            )

            if dist is not None:

                cost = travel_cost(
                    dist
                )

                st.info(
                    f"🚗 {dist:.0f} km aller"
                    f" · "
                    f"🔄 {dist * 2:.0f} km A/R"
                    f" · "
                    f"💰 {cost:.2f} € carburant"
                )


# ============================================================
# CARTE
# ============================================================

elif page == "🗺️ Carte":

    st.title(
        "🗺️ Carte des compétitions"
    )

    st.caption(
        "Chaque point correspond à une compétition."
    )

    map_df = df.dropna(
        subset=[
            "Latitude",
            "Longitude",
        ]
    ).copy()

    if map_df.empty:

        st.warning(
            "Aucune compétition géolocalisée."
        )

    else:

        st.map(
            map_df,
            latitude="Latitude",
            longitude="Longitude",
            zoom=5,
        )

        st.divider()

        st.subheader(
            "📍 Détails des compétitions"
        )

        for _, competition in (
            map_df.sort_values(
                "Date"
            ).iterrows()
        ):

            icon = importance_icon(
                competition["Importance"]
            )

            with st.expander(
                f"{icon} "
                f"{competition['Nom']}"
                f" — "
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

                st.write(
                    f"📌 {competition['Type']}"
                )

                st.write(
                    f"📊 {competition['Statut']}"
                )

                dist = distance_km(
                    settings["Latitude"],
                    settings["Longitude"],
                    competition["Latitude"],
                    competition["Longitude"],
                )

                if dist is not None:

                    cost = travel_cost(
                        dist
                    )

                    st.write(
                        f"🚗 {dist:.0f} km aller"
                    )

                    st.write(
                        f"🔄 {dist * 2:.0f} km A/R"
                    )

                    st.write(
                        f"💰 {cost:.2f} € carburant"
                    )


# ============================================================
# AJOUT D'UNE COMPÉTITION
# ============================================================

elif page == "➕ Ajouter une compétition":

    st.title(
        "➕ Ajouter une compétition"
    )

    with st.form(
        "competition_form"
    ):

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
            "Type de compétition",
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

                st.session_state.competitions = (
                    pd.concat(
                        [
                            st.session_state.competitions,
                            pd.DataFrame(
                                [new_competition]
                            ),
                        ],
                        ignore_index=True,
                    )
                )

                st.success(
                    "✅ Compétition ajoutée !"
                )

                st.rerun()


# ============================================================
# PLANIFICATION
# ============================================================

elif page == "🎯 Planification":

    st.title(
        "🎯 Planification sportive"
    )

    st.write(
        "Sélectionne les compétitions qui font "
        "partie de la saison du lutteur."
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
                df["Nom"].isin(
                    selected
                )
            ].copy()

            planning["Jours avant"] = (
                planning["Date"]
                .apply(
                    lambda x:
                    (x - date.today()).days
                )
            )

            planning[
                "Phase actuelle"
            ] = (
                planning["Jours avant"]
                .apply(
                    planning_phase
                )
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

            for _, competition in (
                planning.iterrows()
            ):

                days = (
                    competition["Jours avant"]
                )

                if days > 0:

                    timing = (
                        f"dans {days} jours"
                    )

                elif days == 0:

                    timing = "aujourd'hui"

                else:

                    timing = (
                        f"il y a {-days} jours"
                    )

                icon = importance_icon(
                    competition[
                        "Importance"
                    ]
                )

                st.write(
                    f"{icon} "
                    f"**{format_date(competition['Date'])}**"
                    f" — "
                    f"**{competition['Nom']}**"
                    f" · "
                    f"{timing}"
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

    st.title(
        "⚙️ Paramètres du club"
    )

    st.write(
        "Ces paramètres permettent de calculer "
        "les distances et les coûts de déplacement."
    )

    with st.form(
        "club_settings_form"
    ):

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
            "⛽ Véhicule"
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
        "💰 Paramètres actuels"
    )

    st.write(
        f"Club : **{settings['Nom']}**"
    )

    st.write(
        f"Adresse : **{settings['Adresse']}**"
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
    "🤼 Lutte Calendar V1.6"
)

st.sidebar.caption(
    "Calendrier sportif & planification"
)
