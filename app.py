import streamlit as st
import pandas as pd
import requests
import math
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
# PARAMÈTRES DU CLUB
# ============================================================

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
else:
    current = st.session_state.competitions

    if not isinstance(current, pd.DataFrame):
        st.session_state.competitions = create_default_dataframe()

    elif not all(
        column in current.columns
        for column in REQUIRED_COLUMNS
    ):
        st.session_state.competitions = create_default_dataframe()


if "club" not in st.session_state:
    st.session_state.club = DEFAULT_CLUB.copy()


df = st.session_state.competitions.copy()
club = st.session_state.club

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

    if pd.isna(d):
        return ""

    return d.strftime("%d/%m/%Y")


# ============================================================
# GÉOCODAGE DU CLUB
# ============================================================

def geocode_address(address):

    try:

        url = "https://nominatim.openstreetmap.org/search"

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

        latitude = float(results[0]["lat"])
        longitude = float(results[0]["lon"])

        return latitude, longitude

    except Exception:
        return None, None


# ============================================================
# DISTANCE À VOL D'OISEAU
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2,
):

    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return R * c


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

        distance_km = (
            data["routes"][0]["distance"] / 1000
        )

        duration_minutes = (
            data["routes"][0]["duration"] / 60
        )

        return distance_km, duration_minutes

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

    distance_round_trip = distance_one_way * 2

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
        "🏠 Mon club",
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

    st.subheader(
        "📅 Prochaines compétitions"
    )

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

    st.subheader(
        "🎯 Objectifs principaux"
    )

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

    st.title(
        "📅 Calendrier des compétitions"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        styles = [
            "Tous"
        ] + sorted(
            df["Style"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_style = st.selectbox(
            "🥋 Style",
            styles,
        )

    with col2:

        levels = [
            "Tous"
        ] + sorted(
            df["Niveau"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_level = st.selectbox(
            "🏆 Niveau",
            levels,
        )

    with col3:

        categories = [
            "Toutes"
        ] + sorted(
            df["Categorie"]
            .dropna()
            .unique()
            .tolist()
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
            df["Région"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_region = st.selectbox(
            "📍 Région",
            regions,
        )

    with col5:

        importances = [
            "Toutes"
        ] + sorted(
            df["Importance"]
            .dropna()
            .unique()
            .tolist()
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
                competition["Date"]
                - date.today()
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

                # ========================================
                # DÉPLACEMENT
                # ========================================

                if (
                    club["Latitude"] is not None
                    and club["Longitude"] is not None
                ):

                    trip = calculate_trip(
                        competition["Latitude"],
                        competition["Longitude"],
                    )

                    if trip:

                        st.info(
                            f"""
🚗 **Déplacement**

📏 **{trip['distance_aller']:.0f} km** aller
· **{trip['distance_AR']:.0f} km** aller-retour

⛽ **{trip['litres']:.1f} L**
· **{trip['carburant']:.2f} €** de carburant

🛣️ **{trip['peages']:.2f} €** de péages

💰 **Coût total estimé : {trip['total']:.2f} €**
"""
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

    st.title(
        "🗺️ Carte des compétitions"
    )

    col1, col2 = st.columns(2)

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


# ============================================================
# PLANIFICATION
# ============================================================

elif page == "🎯 Planification":

    st.title(
        "🎯 Planification sportive"
    )

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
                    competition["Latitude"],
                    competition["Longitude"],
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

            planning["Distance A/R"] = distances
            planning["Coût trajet"] = costs

            planning = planning.sort_values(
                "Date"
            )

            total_distance = (
                planning["Distance A/R"].sum()
            )

            total_cost = (
                planning["Coût trajet"].sum()
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

        else:

            st.info(
                "Sélectionne les compétitions de la saison."
            )

    else:

        st.info(
            "Entre le nom d'un lutteur."
        )


# ============================================================
# MON CLUB
# ============================================================

elif page == "🏠 Mon club":

    st.title(
        "🏠 Mon club"
    )

    st.write(
        "Ces paramètres servent à calculer "
        "les distances et les coûts de déplacement."
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
                "❌ Impossible de trouver cette adresse. "
                "Vérifie l'adresse, le code postal et la ville."
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

            club = st.session_state.club

            st.success(
                "✅ Paramètres du club enregistrés."
            )

            st.info(
                f"📍 Position trouvée : "
                f"{latitude:.5f}, "
                f"{longitude:.5f}"
            )

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
            f"Latitude : `{club['Latitude']:.5f}`"
        )

        st.write(
            f"Longitude : `{club['Longitude']:.5f}`"
        )

        club_map = pd.DataFrame(
            [
                {
                    "latitude": club["Latitude"],
                    "longitude": club["Longitude"],
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
                f"{club['Consommation']:.1f} L/100",
            )

        with c3:

            st.metric(
                "🛣️ Péages",
                f"{club['Peages']:.2f} €",
            )


# ============================================================
# FOOTER
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
    "🤼 Lutte Calendar V1.2"
)
