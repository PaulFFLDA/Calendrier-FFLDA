import streamlit as st
import pandas as pd
import requests
import math
import pydeck as pdk
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


DEFAULT_CLUB = {
    "Nom": "",
    "Adresse": "",
    "Code postal": "",
    "Ville": "",
    "Latitude": None,
    "Longitude": None,
    "Prix carburant": 1.70,
    "Consommation": 7.0,
    "Peages": 0.0,
}


# ============================================================
# INITIALISATION
# ============================================================

def create_default_dataframe():
    return pd.DataFrame(DEFAULT_COMPETITIONS)


if "competitions" not in st.session_state:
    st.session_state.competitions = create_default_dataframe()


if "club" not in st.session_state:
    st.session_state.club = DEFAULT_CLUB.copy()


current = st.session_state.competitions

if not isinstance(current, pd.DataFrame):
    st.session_state.competitions = create_default_dataframe()

elif not all(
    column in current.columns
    for column in REQUIRED_COLUMNS
):
    st.session_state.competitions = create_default_dataframe()


df = st.session_state.competitions.copy()
club = st.session_state.club


# ============================================================
# FONCTIONS
# ============================================================

def format_date(value):
    if pd.isna(value):
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")

    return str(value)


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


# ============================================================
# GÉOCODAGE
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def geocode_address(address):

    try:

        url = (
            "https://nominatim.openstreetmap.org/search"
        )

        params = {
            "q": address,
            "format": "json",
            "limit": 1,
        }

        headers = {
            "User-Agent": "LutteCalendar/1.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            return None, None

        results = response.json()

        if not results:
            return None, None

        latitude = float(
            results[0]["lat"]
        )

        longitude = float(
            results[0]["lon"]
        )

        return latitude, longitude

    except Exception:
        return None, None


# ============================================================
# DISTANCE GÉOGRAPHIQUE
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2,
):

    radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius * c


# ============================================================
# DISTANCE ROUTIÈRE
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def road_distance(
    start_lat,
    start_lon,
    end_lat,
    end_lon,
):

    try:

        url = (
            "https://router.project-osrm.org/"
            "route/v1/driving/"
            f"{start_lon},{start_lat};"
            f"{end_lon},{end_lat}"
        )

        params = {
            "overview": "false"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("code") != "Ok":
            return None

        route = data["routes"][0]

        distance_km = (
            route["distance"] / 1000
        )

        duration_minutes = (
            route["duration"] / 60
        )

        return (
            distance_km,
            duration_minutes,
        )

    except Exception:
        return None


# ============================================================
# CALCUL DU TRAJET
# ============================================================

def calculate_trip(
    competition_lat,
    competition_lon,
):

    if club["Latitude"] is None:
        return None

    if club["Longitude"] is None:
        return None

    if pd.isna(competition_lat):
        return None

    if pd.isna(competition_lon):
        return None

    route = road_distance(
        club["Latitude"],
        club["Longitude"],
        float(competition_lat),
        float(competition_lon),
    )

    if route is not None:

        distance_one_way = route[0]
        duration_one_way = route[1]

    else:

        distance_one_way = haversine_distance(
            club["Latitude"],
            club["Longitude"],
            float(competition_lat),
            float(competition_lon),
        )

        duration_one_way = None

    distance_round_trip = (
        distance_one_way * 2
    )

    fuel_liters = (
        distance_round_trip
        * club["Consommation"]
        / 100
    )

    fuel_cost = (
        fuel_liters
        * club["Prix carburant"]
    )

    total_cost = (
        fuel_cost
        + club["Peages"]
    )

    return {
        "distance_aller": distance_one_way,
        "distance_AR": distance_round_trip,
        "duree_aller": duration_one_way,
        "litres": fuel_liters,
        "carburant": fuel_cost,
        "peages": club["Peages"],
        "total": total_cost,
    }


# ============================================================
# COULEURS CARTE
# ============================================================

def importance_color(importance):

    colors = {
        "Objectif principal": [
            220,
            38,
            38,
        ],
        "Objectif intermédiaire": [
            249,
            115,
            22,
        ],
        "Compétition secondaire": [
            37,
            99,
            235,
        ],
        "Préparation": [
            22,
            163,
            74,
        ],
    }

    return colors.get(
        importance,
        [107, 114, 128],
    )


# ============================================================
# PRÉPARATION DES DONNÉES CARTE
# ============================================================

def create_map_dataframe(source_df):

    map_rows = []

    for _, competition in source_df.iterrows():

        if pd.isna(
            competition["Latitude"]
        ):

            continue

        if pd.isna(
            competition["Longitude"]
        ):

            continue

        trip = calculate_trip(
            competition["Latitude"],
            competition["Longitude"],
        )

        if trip:

            distance_ar = (
                trip["distance_AR"]
            )

            total_cost = (
                trip["total"]
            )

        else:

            distance_ar = 0
            total_cost = 0

        color = importance_color(
            competition["Importance"]
        )

        map_rows.append(
            {
                "Nom": competition["Nom"],
                "Date": format_date(
                    competition["Date"]
                ),
                "Ville": competition["Ville"],
                "Région": competition["Région"],
                "Style": competition["Style"],
                "Categorie": competition["Categorie"],
                "Niveau": competition["Niveau"],
                "Importance": competition["Importance"],
                "Organisateur": competition["Organisateur"],
                "Latitude": float(
                    competition["Latitude"]
                ),
                "Longitude": float(
                    competition["Longitude"]
                ),
                "Distance_AR": round(
                    distance_ar
                ),
                "Cout": round(
                    total_cost,
                    2,
                ),
                "color_r": color[0],
                "color_g": color[1],
                "color_b": color[2],
            }
        )

    return pd.DataFrame(map_rows)


# ============================================================
# TITRE
# ============================================================

st.title("🤼 Lutte Calendar")

st.caption(
    "Calendrier des compétitions de lutte "
    "et planification sportive"
)


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
        "📅 Calendrier",
        "🗺️ Carte",
        "➕ Ajouter une compétition",
        "🎯 Planification",
        "🏠 Mon club",
    ],
)


# ============================================================
# TABLEAU DE BORD
# ============================================================

if page == "🏠 Tableau de bord":

    st.header(
        "🏠 Tableau de bord"
    )

    today = date.today()

    upcoming = df[
        df["Date"] >= today
    ].sort_values("Date")

    total = len(df)

    upcoming_count = len(
        upcoming
    )

    regions = df[
        "Région"
    ].nunique()

    cities = df[
        "Ville"
    ].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🏆 Compétitions",
            total,
        )

    with c2:

        st.metric(
            "📅 À venir",
            upcoming_count,
        )

    with c3:

        st.metric(
            "📍 Régions",
            regions,
        )

    with c4:

        st.metric(
            "🏙️ Villes",
            cities,
        )

    st.divider()

    st.subheader(
        "📅 Prochaines compétitions"
    )

    if upcoming.empty:

        st.info(
            "Aucune compétition à venir."
        )

    else:

        for _, competition in upcoming.head(
            5
        ).iterrows():

            days = (
                competition["Date"]
                - today
            ).days

            if days == 0:

                countdown = (
                    "Aujourd'hui"
                )

            else:

                countdown = (
                    f"dans {days} jours"
                )

            with st.container(
                border=True
            ):

                st.subheader(
                    f"🏆 {competition['Nom']}"
                )

                st.write(
                    f"📅 **{format_date(competition['Date'])}** "
                    f"— {countdown}"
                )

                st.write(
                    f"📍 **{competition['Ville']}** "
                    f"({competition['Région']})"
                )

                st.write(
                    f"🥋 {competition['Style']} "
                    f"· 👤 {competition['Categorie']} "
                    f"· 🏆 {competition['Niveau']}"
                )

                st.write(
                    f"🎯 **{competition['Importance']}**"
                )

    st.divider()

    st.subheader(
        "🎯 Objectifs principaux"
    )

    objectives = df[
        df["Importance"]
        == "Objectif principal"
    ].sort_values("Date")

    if objectives.empty:

        st.info(
            "Aucun objectif principal enregistré."
        )

    else:

        for _, competition in objectives.iterrows():

            days = (
                competition["Date"]
                - today
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

    st.header(
        "📅 Calendrier des compétitions"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        styles = (
            ["Tous"]
            + sorted(
                df["Style"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        selected_style = st.selectbox(
            "🥋 Style",
            styles,
        )

    with col2:

        levels = (
            ["Tous"]
            + sorted(
                df["Niveau"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        selected_level = st.selectbox(
            "🏆 Niveau",
            levels,
        )

    with col3:

        categories = (
            ["Toutes"]
            + sorted(
                df["Categorie"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        selected_category = st.selectbox(
            "👤 Catégorie",
            categories,
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        regions = (
            ["Toutes"]
            + sorted(
                df["Région"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        selected_region = st.selectbox(
            "📍 Région",
            regions,
        )

    with col5:

        importances = (
            ["Toutes"]
            + sorted(
                df["Importance"]
                .dropna()
                .unique()
                .tolist()
            )
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
            filtered["Style"]
            == selected_style
        ]

    if selected_level != "Tous":

        filtered = filtered[
            filtered["Niveau"]
            == selected_level
        ]

    if selected_category != "Toutes":

        filtered = filtered[
            filtered["Categorie"]
            == selected_category
        ]

    if selected_region != "Toutes":

        filtered = filtered[
            filtered["Région"]
            == selected_region
        ]

    if selected_importance != "Toutes":

        filtered = filtered[
            filtered["Importance"]
            == selected_importance
        ]

    if only_future:

        filtered = filtered[
            filtered["Date"]
            >= date.today()
        ]

    filtered = filtered.sort_values(
        "Date"
    )

    st.divider()

    st.subheader(
        f"{len(filtered)} compétition(s)"
    )

    if filtered.empty:

        st.info(
            "Aucune compétition ne correspond "
            "aux filtres."
        )

    else:

        for _, competition in filtered.iterrows():

            days = (
                competition["Date"]
                - date.today()
            ).days

            if days > 0:

                countdown = (
                    f"dans {days} jours"
                )

            elif days == 0:

                countdown = "Aujourd'hui"

            else:

                countdown = (
                    f"il y a {-days} jours"
                )

            with st.container(
                border=True
            ):

                st.subheader(
                    f"🏆 {competition['Nom']}"
                )

                st.write(
                    f"📅 **{format_date(competition['Date'])}** "
                    f"— {countdown}"
                )

                st.write(
                    f"📍 **{competition['Ville']}** "
                    f"({competition['Région']})"
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.write(
                        f"🥋 **Style**\n\n"
                        f"{competition['Style']}"
                    )

                with c2:

                    st.write(
                        f"👤 **Catégorie**\n\n"
                        f"{competition['Categorie']}"
                    )

                with c3:

                    st.write(
                        f"🏆 **Niveau**\n\n"
                        f"{competition['Niveau']}"
                    )

                st.write(
                    f"🎯 **Importance :** "
                    f"{competition['Importance']}"
                )

                if competition[
                    "Organisateur"
                ]:

                    st.caption(
                        "Organisateur : "
                        f"{competition['Organisateur']}"
                    )

                # ----------------------------------------
                # DÉPLACEMENT
                # ----------------------------------------

                if (
                    club["Latitude"]
                    is not None
                    and club["Longitude"]
                    is not None
                ):

                    trip = calculate_trip(
                        competition[
                            "Latitude"
                        ],
                        competition[
                            "Longitude"
                        ],
                    )

                    if trip:

                        st.divider()

                        st.subheader(
                            "🚗 Déplacement"
                        )

                        c1, c2, c3, c4 = (
                            st.columns(4)
                        )

                        with c1:

                            st.metric(
                                "📏 Distance aller",
                                f"{trip['distance_aller']:.0f} km",
                            )

                        with c2:

                            st.metric(
                                "🔄 Distance A/R",
                                f"{trip['distance_AR']:.0f} km",
                            )

                        with c3:

                            st.metric(
                                "⛽ Carburant",
                                f"{trip['carburant']:.2f} €",
                            )

                        with c4:

                            st.metric(
                                "💰 Coût total",
                                f"{trip['total']:.2f} €",
                            )

                        if trip[
                            "duree_aller"
                        ]:

                            duration = (
                                trip[
                                    "duree_aller"
                                ]
                            )

                            hours = int(
                                duration // 60
                            )

                            minutes = int(
                                duration % 60
                            )

                            if hours > 0:

                                duration_text = (
                                    f"{hours} h "
                                    f"{minutes:02d}"
                                )

                            else:

                                duration_text = (
                                    f"{minutes} min"
                                )

                            st.caption(
                                "⏱️ Temps de trajet "
                                f"aller : {duration_text}"
                            )

                    else:

                        st.warning(
                            "Impossible de calculer "
                            "le trajet."
                        )

                else:

                    st.info(
                        "🏠 Configure ton club dans "
                        "« Mon club » pour calculer "
                        "les déplacements."
                    )

                if competition[
                    "Description"
                ]:

                    st.write(
                        competition[
                            "Description"
                        ]
                    )

                if competition[
                    "Inscription"
                ]:

                    st.link_button(
                        "🔗 Ouvrir l'inscription",
                        competition[
                            "Inscription"
                        ],
                    )


# ============================================================
# CARTE INTERACTIVE
# ============================================================

elif page == "🗺️ Carte":

    st.header(
        "🗺️ Carte interactive"
    )

    st.write(
        "Survole un marqueur pour afficher "
        "les informations de la compétition. "
        "Clique dessus pour la sélectionner."
    )

    # --------------------------------------------------------
    # FILTRES
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        map_level = st.selectbox(
            "🏆 Niveau",
            ["Tous"]
            + sorted(
                df["Niveau"]
                .dropna()
                .unique()
                .tolist()
            ),
            key="map_level",
        )

    with col2:

        map_style = st.selectbox(
            "🥋 Style",
            ["Tous"]
            + sorted(
                df["Style"]
                .dropna()
                .unique()
                .tolist()
            ),
            key="map_style",
        )

    with col3:

        map_importance = st.selectbox(
            "🎯 Importance",
            ["Toutes"]
            + sorted(
                df["Importance"]
                .dropna()
                .unique()
                .tolist()
            ),
            key="map_importance",
        )

    map_df_source = df.copy()

    if map_level != "Tous":

        map_df_source = map_df_source[
            map_df_source["Niveau"]
            == map_level
        ]

    if map_style != "Tous":

        map_df_source = map_df_source[
            map_df_source["Style"]
            == map_style
        ]

    if map_importance != "Toutes":

        map_df_source = map_df_source[
            map_df_source["Importance"]
            == map_importance
        ]

    map_df = create_map_dataframe(
        map_df_source
    )

    st.divider()

    # --------------------------------------------------------
    # LÉGENDE
    # --------------------------------------------------------

    st.subheader(
        "🎨 Légende"
    )

    legend_cols = st.columns(4)

    legend = [
        (
            "🟢",
            "Préparation",
        ),
        (
            "🟠",
            "Objectif intermédiaire",
        ),
        (
            "🔴",
            "Objectif principal",
        ),
        (
            "🔵",
            "Compétition secondaire",
        ),
    ]

    for column, item in zip(
        legend_cols,
        legend,
    ):

        with column:

            st.write(
                f"{item[0]} {item[1]}"
            )

    st.divider()

    # --------------------------------------------------------
    # CARTE
    # --------------------------------------------------------

    if map_df.empty:

        st.info(
            "Aucune compétition géolocalisée "
            "ne correspond aux filtres."
        )

    else:

        # Centre de la carte
        if (
            club["Latitude"] is not None
            and club["Longitude"] is not None
        ):

            center_lat = club[
                "Latitude"
            ]

            center_lon = club[
                "Longitude"
            ]

            initial_zoom = 6

        else:

            center_lat = map_df[
                "Latitude"
            ].mean()

            center_lon = map_df[
                "Longitude"
            ].mean()

            initial_zoom = 5

        # --------------------------------------------
        # COUCHE DES COMPÉTITIONS
        # --------------------------------------------

        competition_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=[
                "Longitude",
                "Latitude",
            ],
            get_fill_color=[
                "color_r",
                "color_g",
                "color_b",
                210,
            ],
            get_line_color=[
                255,
                255,
                255,
                255,
            ],
            get_radius=7000,
            radius_min_pixels=7,
            radius_max_pixels=18,
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        )

        layers = [
            competition_layer
        ]

        # --------------------------------------------
        # COUCHE DU CLUB
        # --------------------------------------------

        if (
            club["Latitude"] is not None
            and club["Longitude"] is not None
        ):

            club_df = pd.DataFrame(
                [
                    {
                        "Nom": club["Nom"]
                        or "Mon club",
                        "Latitude": club[
                            "Latitude"
                        ],
                        "Longitude": club[
                            "Longitude"
                        ],
                    }
                ]
            )

            club_layer = pdk.Layer(
                "ScatterplotLayer",
                data=club_df,
                get_position=[
                    "Longitude",
                    "Latitude",
                ],
                get_fill_color=[
                    17,
                    24,
                    39,
                    255,
                ],
                get_line_color=[
                    255,
                    255,
                    255,
                    255,
                ],
                get_radius=10000,
                radius_min_pixels=10,
                radius_max_pixels=22,
                line_width_min_pixels=3,
                pickable=True,
            )

            layers.append(
                club_layer
            )

        # --------------------------------------------
        # TOOLTIP
        # --------------------------------------------

        tooltip = {
            "html": """
                <div style="
                    padding: 8px;
                    font-family: Arial;
                    color: #111827;
                    background: white;
                ">

                    <div style="
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 8px;
                    ">
                        🏆 {Nom}
                    </div>

                    <div>
                        📅 {Date}
                    </div>

                    <div>
                        📍 {Ville} — {Région}
                    </div>

                    <div>
                        🥋 {Style}
                    </div>

                    <div>
                        👤 {Categorie}
                    </div>

                    <div>
                        🏆 {Niveau}
                    </div>

                    <div>
                        🎯 {Importance}
                    </div>

                    <div style="
                        margin-top: 8px;
                        border-top: 1px solid #ddd;
                        padding-top: 8px;
                    ">
                        🚗 {Distance_AR} km A/R
                    </div>

                    <div>
                        💰 {Cout} €
                    </div>

                </div>
            """,
            "style": {
                "backgroundColor": "white",
                "color": "#111827",
                "fontSize": "13px",
            },
        }

        # --------------------------------------------
        # VUE
        # --------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=initial_zoom,
            pitch=0,
            bearing=0,
        )

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light",
        )

        st.pydeck_chart(
            deck,
            use_container_width=True,
        )

        st.caption(
            "💡 Survole un point pour afficher "
            "les détails de la compétition."
        )

        # ----------------------------------------------------
        # LISTE SOUS LA CARTE
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            f"📍 {len(map_df)} compétition(s) "
            "sur la carte"
        )

        for _, competition in map_df.sort_values(
            "Date"
        ).iterrows():

            with st.container(
                border=True
            ):

                c1, c2, c3 = st.columns(
                    [3, 2, 1]
                )

                with c1:

                    st.write(
                        f"🏆 **{competition['Nom']}**"
                    )

                    st.caption(
                        f"📍 {competition['Ville']} "
                        f"· 📅 {competition['Date']}"
                    )

                with c2:

                    st.write(
                        f"🎯 {competition['Importance']}"
                    )

                    st.write(
                        f"🥋 {competition['Style']}"
                    )

                with c3:

                    st.metric(
                        "🚗 A/R",
                        f"{competition['Distance_AR']} km",
                    )

                    st.caption(
                        f"💰 {competition['Cout']:.2f} €"
                    )


# ============================================================
# AJOUT COMPÉTITION
# ============================================================

elif page == "➕ Ajouter une compétition":

    st.header(
        "➕ Ajouter une compétition"
    )

    with st.form(
        "competition_form"
    ):

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

                st.rerun()


# ============================================================
# PLANIFICATION
# ============================================================

elif page == "🎯 Planification":

    st.header(
        "🎯 Planification sportive"
    )

    athlete = st.text_input(
        "Nom du lutteur",
        placeholder="Ex : Jean Dupont",
    )

    if not athlete:

        st.info(
            "Entre le nom d'un lutteur."
        )

    else:

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

        if not selected:

            st.info(
                "Sélectionne les compétitions "
                "de la saison."
            )

        else:

            planning = df[
                df["Nom"].isin(selected)
            ].copy()

            planning["Jours avant"] = (
                planning["Date"].apply(
                    lambda x:
                    (x - date.today()).days
                )
            )

            planning["Phase"] = (
                planning["Jours avant"].apply(
                    phase_planification
                )
            )

            distances = []
            costs = []

            for _, competition in planning.iterrows():

                trip = calculate_trip(
                    competition[
                        "Latitude"
                    ],
                    competition[
                        "Longitude"
                    ],
                )

                if trip:

                    distances.append(
                        trip["distance_AR"]
                    )

                    costs.append(
                        trip["total"]
                    )

                else:

                    distances.append(0)

                    costs.append(0)

            planning[
                "Distance A/R"
            ] = distances

            planning[
                "Coût trajet"
            ] = costs

            planning = planning.sort_values(
                "Date"
            )

            total_distance = (
                planning[
                    "Distance A/R"
                ].sum()
            )

            total_cost = (
                planning[
                    "Coût trajet"
                ].sum()
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "🏆 Compétitions",
                    len(planning),
                )

            with c2:

                st.metric(
                    "🚗 Distance totale",
                    f"{total_distance:.0f} km",
                )

            with c3:

                st.metric(
                    "💰 Transport estimé",
                    f"{total_cost:.2f} €",
                )

            st.divider()

            display_planning = planning[
                [
                    "Nom",
                    "Date",
                    "Ville",
                    "Importance",
                    "Distance A/R",
                    "Coût trajet",
                    "Jours avant",
                    "Phase",
                ]
            ].copy()

            display_planning[
                "Date"
            ] = display_planning[
                "Date"
            ].apply(format_date)

            display_planning[
                "Distance A/R"
            ] = display_planning[
                "Distance A/R"
            ].round(0).astype(int)

            display_planning[
                "Coût trajet"
            ] = display_planning[
                "Coût trajet"
            ].round(2)

            st.dataframe(
                display_planning,
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
                    f"→ {competition['Phase']} "
                    f"· 🚗 "
                    f"{competition['Distance A/R']:.0f} km "
                    f"· 💰 "
                    f"{competition['Coût trajet']:.2f} €"
                )


# ============================================================
# MON CLUB
# ============================================================

elif page == "🏠 Mon club":

    st.header(
        "🏠 Mon club"
    )

    st.write(
        "Configure ici l'adresse de ton club "
        "et les paramètres utilisés pour calculer "
        "les déplacements."
    )

    st.divider()

    st.subheader(
        "🏠 Informations du club"
    )

    club_name = st.text_input(
        "Nom du club",
        value=club["Nom"],
        placeholder="Ex : Caen Lutte",
    )

    address = st.text_input(
        "Adresse",
        value=club["Adresse"],
        placeholder="Ex : 10 rue du Sport",
    )

    col1, col2 = st.columns(2)

    with col1:

        postal_code = st.text_input(
            "Code postal",
            value=club["Code postal"],
        )

    with col2:

        city = st.text_input(
            "Ville",
            value=club["Ville"],
        )

    st.divider()

    st.subheader(
        "🚗 Paramètres du véhicule"
    )

    col1, col2 = st.columns(2)

    with col1:

        fuel_price = st.number_input(
            "⛽ Prix du carburant (€/L)",
            min_value=0.0,
            max_value=10.0,
            value=float(
                club["Prix carburant"]
            ),
            step=0.01,
        )

    with col2:

        consumption = st.number_input(
            "🚗 Consommation (L/100 km)",
            min_value=1.0,
            max_value=50.0,
            value=float(
                club["Consommation"]
            ),
            step=0.1,
        )

    tolls = st.number_input(
        "🛣️ Péages aller-retour (€)",
        min_value=0.0,
        max_value=500.0,
        value=float(
            club["Peages"]
        ),
        step=1.0,
    )

    st.divider()

    save = st.button(
        "💾 Enregistrer les paramètres",
        type="primary",
        use_container_width=True,
    )

    if save:

        full_address = (
            f"{address}, "
            f"{postal_code} "
            f"{city}, France"
        )

        with st.spinner(
            "📍 Recherche de l'adresse..."
        ):

            latitude, longitude = (
                geocode_address(
                    full_address
                )
            )

        if latitude is None:

            st.error(
                "❌ Adresse introuvable. "
                "Vérifie l'adresse, le code postal "
                "et la ville."
            )

        else:

            st.session_state.club = {
                "Nom": club_name,
                "Adresse": address,
                "Code postal": postal_code,
                "Ville": city,
                "Latitude": latitude,
                "Longitude": longitude,
                "Prix carburant": fuel_price,
                "Consommation": consumption,
                "Peages": tolls,
            }

            st.success(
                "✅ Paramètres du club enregistrés."
            )

            st.info(
                f"📍 Position trouvée : "
                f"{latitude:.5f}, "
                f"{longitude:.5f}"
            )

            st.rerun()

    if club["Latitude"] is not None:

        st.divider()

        st.subheader(
            "📍 Position enregistrée"
        )

        st.write(
            f"**{club['Nom']}**"
        )

        st.write(
            f"{club['Adresse']}, "
            f"{club['Code postal']} "
            f"{club['Ville']}"
        )

        st.write(
            f"Latitude : "
            f"`{club['Latitude']:.5f}`"
        )

        st.write(
            f"Longitude : "
            f"`{club['Longitude']:.5f}`"
        )

        club_map = pd.DataFrame(
            [
                {
                    "latitude": club[
                        "Latitude"
                    ],
                    "longitude": club[
                        "Longitude"
                    ],
                }
            ]
        )

        st.map(
            club_map,
            latitude="latitude",
            longitude="longitude",
            zoom=12,
        )

        st.divider()

        st.subheader(
            "⚙️ Paramètres actuels"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "⛽ Carburant",
                f"{club['Prix carburant']:.2f} €/L",
            )

        with c2:

            st.metric(
                "🚗 Consommation",
                f"{club['Consommation']:.1f} L/100 km",
            )

        with c3:

            st.metric(
                "🛣️ Péages",
                f"{club['Peages']:.2f} €",
            )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.divider()

if club["Nom"]:

    st.sidebar.success(
        f"🏠 {club['Nom']}"
    )

else:

    st.sidebar.warning(
        "🏠 Club non configuré"
    )

st.sidebar.caption(
    "🤼 Lutte Calendar V1.4"
)
