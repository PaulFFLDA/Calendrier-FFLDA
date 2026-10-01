import math
from datetime import date

import pandas as pd
import pydeck as pdk
import streamlit as st


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

    .cost-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .cost-title {
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
    }

    .cost-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #166534;
        margin-top: 0.5rem;
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

    .month-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .calendar-event {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #2563eb;
        border-radius: 10px;
        padding: 0.9rem;
        margin-bottom: 0.6rem;
    }

    .calendar-event-title {
        font-weight: 700;
        color: #111827;
    }

    .calendar-event-date {
        color: #6b7280;
        font-size: 0.9rem;
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
        "Description": "Tournoi de rentrée et reprise de compétition.",
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Septembre",
        "Date": date(2026, 9, 27),
        "Ville": "Rouen",
        "Département": "Seine-Maritime",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U15",
        "Latitude": 49.4432,
        "Longitude": 1.0993,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
        "Peage": 0.0,
    },
    {
        "Nom": "Championnat régional Normandie",
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
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Octobre",
        "Date": date(2026, 10, 31),
        "Ville": "Dijon",
        "Département": "Côte-d'Or",
        "Région": "Bourgogne-Franche-Comté",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 47.3220,
        "Longitude": 5.0415,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Novembre",
        "Date": date(2026, 11, 15),
        "Ville": "Paris",
        "Département": "Paris",
        "Région": "Île-de-France",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 48.8566,
        "Longitude": 2.3522,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
        "Peage": 0.0,
    },
    {
        "Nom": "Championnat de Normandie",
        "Date": date(2026, 12, 6),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U20",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Objectif intermédiaire",
        "Organisateur": "Ligue de Normandie",
        "Inscription": "",
        "Description": "Championnat régional de Normandie.",
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Janvier",
        "Date": date(2027, 1, 17),
        "Ville": "Nantes",
        "Département": "Loire-Atlantique",
        "Région": "Pays de la Loire",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 47.2184,
        "Longitude": -1.5536,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking de janvier.",
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Février",
        "Date": date(2027, 2, 7),
        "Ville": "Lyon",
        "Département": "Rhône",
        "Région": "Auvergne-Rhône-Alpes",
        "Style": "Lutte gréco-romaine",
        "Niveau": "National",
        "Categorie": "U20",
        "Latitude": 45.7640,
        "Longitude": 4.8357,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
        "Peage": 0.0,
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
        "Description": "Championnat de France.",
        "Peage": 0.0,
    },
    {
        "Nom": "TNR Mars",
        "Date": date(2027, 3, 14),
        "Ville": "Strasbourg",
        "Département": "Bas-Rhin",
        "Région": "Grand Est",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "U17",
        "Latitude": 48.5734,
        "Longitude": 7.7521,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national ranking.",
        "Peage": 0.0,
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
    "Peage",
]


# ============================================================
# PARAMÈTRES CLUB PAR DÉFAUT
# ============================================================

DEFAULT_CLUB = {
    "nom": "Mon club de lutte",
    "adresse": "Caen, France",
    "latitude": 49.1829,
    "longitude": -0.3707,
    "prix_essence": 1.80,
    "consommation": 7.0,
    "cout_km": 0.0,
}


# ============================================================
# INITIALISATION
# ============================================================

def create_default_dataframe():
    return pd.DataFrame(DEFAULT_COMPETITIONS)


if "competitions" not in st.session_state:
    st.session_state.competitions = create_default_dataframe()

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

if "wrestlers" not in st.session_state:
    st.session_state.wrestlers = pd.DataFrame(
        columns=[
            "Nom", "Prenom", "Categorie", "Poids", "Objectif",
            "Competitions", "Roles", "Priorites"
        ]
    )


df = st.session_state.competitions.copy()


# ============================================================
# NORMALISATION DES DONNÉES
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
).dt.date

for column in [
    "Nom",
    "Ville",
    "Département",
    "Région",
    "Style",
    "Niveau",
    "Categorie",
    "Importance",
    "Organisateur",
    "Inscription",
    "Description",
]:
    df[column] = df[column].fillna("").astype(str)

df["Latitude"] = pd.to_numeric(
    df["Latitude"],
    errors="coerce",
)

df["Longitude"] = pd.to_numeric(
    df["Longitude"],
    errors="coerce",
)

df["Peage"] = pd.to_numeric(
    df["Peage"],
    errors="coerce",
).fillna(0.0)


# ============================================================
# FONCTIONS
# ============================================================

def format_date(value):
    if pd.isna(value):
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")

    return str(value)


def importance_badge(importance):

    if importance == "Objectif principal":
        return "badge-red"

    if importance == "Objectif intermédiaire":
        return "badge-orange"

    if importance == "Préparation":
        return "badge-green"

    return "badge-blue"


def importance_color(importance):

    colors = {
        "Préparation": [22, 163, 74],
        "Compétition secondaire": [37, 99, 235],
        "Objectif intermédiaire": [234, 88, 12],
        "Objectif principal": [220, 38, 38],
    }

    return colors.get(
        importance,
        [100, 116, 139],
    )


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


def haversine(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """
    Distance approximative à vol d'oiseau.
    """

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

    c = 2 * math.asin(
        math.sqrt(a)
    )

    return radius * c


def calculate_trip(competition):

    club = st.session_state.club

    distance = haversine(
        club["latitude"],
        club["longitude"],
        competition["Latitude"],
        competition["Longitude"],
    )

    if distance is None:
        return {
            "one_way": 0,
            "round_trip": 0,
            "liters": 0,
            "fuel": 0,
            "toll": float(
                competition.get(
                    "Peage",
                    0,
                )
            ),
            "total": 0,
        }

    # On applique une marge de 10 %
    # car la distance routière est généralement
    # supérieure à la distance à vol d'oiseau.
    one_way = distance * 1.10

    round_trip = one_way * 2

    consumption = max(
        float(
            club["consommation"]
        ),
        0.1,
    )

    liters = (
        round_trip
        * consumption
        / 100
    )

    fuel_cost = (
        liters
        * float(
            club["prix_essence"]
        )
    )

    toll = float(
        competition.get(
            "Peage",
            0,
        )
    )

    total = fuel_cost + toll

    return {
        "one_way": one_way,
        "round_trip": round_trip,
        "liters": liters,
        "fuel": fuel_cost,
        "toll": toll,
        "total": total,
    }


def month_name(month):

    months = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    return months[month]


def render_trip_cost(competition):

    trip = calculate_trip(
        competition
    )

    st.markdown(
        f"""
        <div class="cost-box">

            <div class="cost-title">
                🚗 Déplacement
            </div>

            <div>
                📏 {trip["one_way"]:.0f} km aller
                · {trip["round_trip"]:.0f} km A/R
            </div>

            <div>
                ⛽ {trip["liters"]:.1f} L
                · {trip["fuel"]:.2f} € de carburant
            </div>

            <div>
                🛣️ {trip["toll"]:.2f} € de péages
            </div>

            <div class="cost-value">
                💰 {trip["total"]:.2f} €
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


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
        "📅 Calendrier",
        "🗺️ Carte",
        "➕ Ajouter une compétition",
        "🎯 Planification",
        "💰 Finances club",
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

    total_transport = sum(
        calculate_trip(row)["total"]
        for _, row in upcoming.iterrows()
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (total, "Compétitions"),
        (upcoming_count, "À venir"),
        (regions, "Régions"),
        (
            f"{total_transport:.0f} €",
            "Déplacements à venir",
        ),
    ]

    for col, (
        number,
        label,
    ) in zip(
        [c1, c2, c3, c4],
        metrics,
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
                competition["Date"]
                - today
            ).days

            if days == 0:
                countdown = "Aujourd'hui"

            else:
                countdown = (
                    f"dans {days} jours"
                )

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

                    <strong>
                        {countdown}
                    </strong>

                </div>
                """,
                unsafe_allow_html=True,
            )

            render_trip_cost(
                competition
            )


# ============================================================
# CALENDRIER
# ============================================================

elif page == "📅 Calendrier":

    st.title(
        "📅 Calendrier des compétitions"
    )

    st.caption(
        "Vue mensuelle de la saison sportive."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_year = st.selectbox(
            "Année",
            sorted(
                df["Date"]
                .dropna()
                .apply(
                    lambda x: x.year
                )
                .unique()
                .tolist()
            ),
        )

    with col2:

        selected_style = st.selectbox(
            "🥋 Style",
            ["Tous"]
            + sorted(
                df["Style"]
                .unique()
                .tolist()
            ),
        )

    with col3:

        selected_importance = st.selectbox(
            "🎯 Importance",
            ["Toutes"]
            + sorted(
                df["Importance"]
                .unique()
                .tolist()
            ),
        )

    calendar_df = df[
        df["Date"].apply(
            lambda x: x.year
            == selected_year
        )
    ].copy()

    if selected_style != "Tous":

        calendar_df = calendar_df[
            calendar_df["Style"]
            == selected_style
        ]

    if (
        selected_importance
        != "Toutes"
    ):

        calendar_df = calendar_df[
            calendar_df["Importance"]
            == selected_importance
        ]

    st.divider()

    for month in range(1, 13):

        month_df = calendar_df[
            calendar_df["Date"].apply(
                lambda x: x.month
                == month
            )
        ].sort_values("Date")

        if month_df.empty:
            continue

        st.markdown(
            f"""
            <div class="month-title">
                📅 {month_name(month)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        for _, competition in month_df.iterrows():

            color = (
                importance_color(
                    competition[
                        "Importance"
                    ]
                )
            )

            color_hex = "#{:02x}{:02x}{:02x}".format(
                *color
            )

            st.markdown(
                f"""
                <div
                    class="calendar-event"
                    style="border-left-color:
                    {color_hex};"
                >

                    <div class="calendar-event-title">
                        {competition["Nom"]}
                    </div>

                    <div class="calendar-event-date">
                        📅 {format_date(competition["Date"])}
                        · 📍 {competition["Ville"]}
                        · 🥋 {competition["Style"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(
                [3, 1]
            )

            with c1:

                st.caption(
                    f"🏆 {competition['Niveau']} "
                    f"· 👤 {competition['Categorie']} "
                    f"· 🎯 {competition['Importance']}"
                )

            with c2:

                if competition[
                    "Inscription"
                ]:

                    st.link_button(
                        "🔗 Inscription",
                        competition[
                            "Inscription"
                        ],
                    )

    if calendar_df.empty:

        st.info(
            "Aucune compétition pour cette année "
            "avec les filtres sélectionnés."
        )


# ============================================================
# CARTE INTERACTIVE
# ============================================================

elif page == "🗺️ Carte":

    st.title(
        "🗺️ Carte des compétitions"
    )

    st.caption(
        "Survole les points pour afficher les détails."
    )

    map_df = df.copy()

    map_df = map_df.dropna(
        subset=[
            "Latitude",
            "Longitude",
        ]
    ).copy()

    col1, col2, col3 = st.columns(3)

    with col1:

        map_level = st.selectbox(
            "🏆 Niveau",
            ["Tous"]
            + sorted(
                map_df["Niveau"]
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
                map_df["Style"]
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
                map_df["Importance"]
                .unique()
                .tolist()
            ),
            key="map_importance",
        )

    if map_level != "Tous":

        map_df = map_df[
            map_df["Niveau"]
            == map_level
        ]

    if map_style != "Tous":

        map_df = map_df[
            map_df["Style"]
            == map_style
        ]

    if map_importance != "Toutes":

        map_df = map_df[
            map_df["Importance"]
            == map_importance
        ]

    map_df["color"] = map_df[
        "Importance"
    ].apply(
        importance_color
    )

    map_df["Date_affichee"] = map_df[
        "Date"
    ].apply(
        format_date
    )

    map_df["tooltip"] = map_df.apply(
        lambda row: (
            f"<b>{row['Nom']}</b><br/>"
            f"📅 {row['Date_affichee']}<br/>"
            f"📍 {row['Ville']}<br/>"
            f"🥋 {row['Style']}<br/>"
            f"👤 {row['Categorie']}<br/>"
            f"🏆 {row['Niveau']}<br/>"
            f"🎯 {row['Importance']}"
        ),
        axis=1,
    )

    st.subheader(
        f"📍 {len(map_df)} compétition(s)"
    )

    if not map_df.empty:

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=[
                "Longitude",
                "Latitude",
            ],
            get_fill_color="color",
            get_radius=10000,
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=float(
                map_df[
                    "Latitude"
                ].mean()
            ),
            longitude=float(
                map_df[
                    "Longitude"
                ].mean()
            ),
            zoom=5,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "{tooltip}",
                "style": {
                    "backgroundColor": "#111827",
                    "color": "white",
                    "fontSize": "14px",
                    "padding": "10px",
                },
            },
        )

        st.pydeck_chart(
            deck,
            use_container_width=True,
        )

        st.markdown(
            """
            ### 🎨 Légende

            🟢 **Préparation**

            🔵 **Compétition secondaire**

            🟠 **Objectif intermédiaire**

            🔴 **Objectif principal**
            """
        )

        st.divider()

        st.subheader(
            "📋 Compétitions"
        )

        for _, competition in map_df.sort_values(
            "Date"
        ).iterrows():

            badge = importance_badge(
                competition[
                    "Importance"
                ]
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

                </div>
                """,
                unsafe_allow_html=True,
            )

            render_trip_cost(
                competition
            )

    else:

        st.info(
            "Aucune compétition ne correspond "
            "aux filtres."
        )


# ============================================================
# AJOUT COMPÉTITION
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

        col5, col6 = st.columns(2)

        with col5:

            organizer = st.text_input(
                "Organisateur"
            )

        with col6:

            registration = st.text_input(
                "Lien d'inscription"
            )

        toll = st.number_input(
            "🛣️ Péage aller/retour (€)",
            min_value=0.0,
            value=0.0,
            step=1.0,
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
                    "Organisateur": organizer,
                    "Inscription": registration,
                    "Description": description,
                    "Peage": toll,
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
# =========================
# 6) PLANIFICATION DES LUTTEURS
# =========================
elif page == "🎯 Planification":

    st.title("🎯 Planification de la saison")
    st.caption("Construis la saison de chaque lutteur compétition par compétition.")

    def wrestler_display_name(row):
        return f"{row['Prenom']} {row['Nom']}".strip()

    def save_wrestler(
        nom, prenom, categorie, poids, objectif,
        competitions, roles, priorites, index=None
    ):
        new_row = {
            "Nom": nom,
            "Prenom": prenom,
            "Categorie": categorie,
            "Poids": poids,
            "Objectif": objectif,
            "Competitions": competitions,
            "Roles": roles,
            "Priorites": priorites,
        }

        if index is None:
            st.session_state.wrestlers.loc[len(st.session_state.wrestlers)] = new_row
        else:
            st.session_state.wrestlers.loc[index] = new_row

    st.subheader("🥋 Mes lutteurs")

    with st.expander("➕ Ajouter un lutteur", expanded=st.session_state.wrestlers.empty):
        with st.form("add_wrestler"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prénom")

            c3, c4 = st.columns(2)
            categorie = c3.text_input(
                "Catégorie d'âge",
                placeholder="U15, U17, U20, Senior…"
            )
            poids = c4.text_input(
                "Poids / catégorie",
                placeholder="-57 kg"
            )

            objectif = st.text_input(
                "🎯 Objectif principal de la saison",
                placeholder="Championnat de France, qualification régionale…"
            )

            if st.form_submit_button("Ajouter le lutteur", type="primary"):
                if not nom.strip() or not prenom.strip():
                    st.error("Indique au minimum le nom et le prénom.")
                else:
                    save_wrestler(
                        nom.strip(),
                        prenom.strip(),
                        categorie.strip(),
                        poids.strip(),
                        objectif.strip(),
                        [],
                        {},
                        {}
                    )
                    st.success("Lutteur ajouté.")
                    st.rerun()

    if st.session_state.wrestlers.empty:
        st.info("Aucun lutteur pour le moment. Ajoute ton premier lutteur ci-dessus.")
    else:
        names = [
            wrestler_display_name(row)
            for _, row in st.session_state.wrestlers.iterrows()
        ]

        selected_name = st.selectbox("👤 Lutteur à planifier", names)
        selected_index = names.index(selected_name)
        wrestler = st.session_state.wrestlers.iloc[selected_index]

        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lutteur", selected_name)
        c2.metric("Catégorie", wrestler["Categorie"] or "—")
        c3.metric("Poids", wrestler["Poids"] or "—")
        c4.metric("Compétitions", len(wrestler["Competitions"]))

        if wrestler["Objectif"]:
            st.info(f"🎯 **Objectif principal :** {wrestler['Objectif']}")

        with st.expander("✏️ Modifier la fiche du lutteur"):
            with st.form(f"edit_wrestler_{selected_index}"):
                e1, e2 = st.columns(2)
                edit_nom = e1.text_input("Nom", value=wrestler["Nom"])
                edit_prenom = e2.text_input("Prénom", value=wrestler["Prenom"])

                e3, e4 = st.columns(2)
                edit_categorie = e3.text_input(
                    "Catégorie d'âge",
                    value=wrestler["Categorie"]
                )
                edit_poids = e4.text_input(
                    "Poids / catégorie",
                    value=wrestler["Poids"]
                )

                edit_objectif = st.text_input(
                    "Objectif principal",
                    value=wrestler["Objectif"]
                )

                if st.form_submit_button("Enregistrer"):
                    save_wrestler(
                        edit_nom.strip(),
                        edit_prenom.strip(),
                        edit_categorie.strip(),
                        edit_poids.strip(),
                        edit_objectif.strip(),
                        wrestler["Competitions"],
                        wrestler["Roles"],
                        wrestler["Priorites"],
                        selected_index
                    )
                    st.success("Fiche mise à jour.")
                    st.rerun()

        st.subheader("📅 Programmer les compétitions")

        competitions_df = st.session_state.competitions.copy()
        competitions_df = competitions_df.sort_values("Date")

        if competitions_df.empty:
            st.warning("Aucune compétition disponible.")
        else:
            selected_ids = set(wrestler["Competitions"])
            current_roles = dict(wrestler["Roles"])
            current_priorities = dict(wrestler["Priorites"])

            role_options = [
                "Préparation",
                "Compétition",
                "Qualification",
                "Objectif principal",
                "Expérience"
            ]
            priority_options = ["Faible", "Normale", "Haute"]

            for _, comp in competitions_df.iterrows():
                comp_id = str(comp["ID"])
                selected = comp_id in selected_ids

                with st.container(border=True):
                    a, b, c, d = st.columns([0.8, 2.8, 1.5, 1.5])

                    checked = a.checkbox(
                        "Participer",
                        value=selected,
                        key=f"participate_{selected_index}_{comp_id}"
                    )

                    b.markdown(
                        f"**{comp['Nom']}**  \n"
                        f"📅 {format_date(comp['Date'])} · "
                        f"📍 {comp['Ville']} · "
                        f"{comp['Style']} · {comp['Niveau']}"
                    )

                    previous_role = current_roles.get(comp_id, "Compétition")
                    previous_priority = current_priorities.get(comp_id, "Normale")

                    role = c.selectbox(
                        "Rôle",
                        role_options,
                        index=(
                            role_options.index(previous_role)
                            if previous_role in role_options else 1
                        ),
                        key=f"role_{selected_index}_{comp_id}",
                        disabled=not checked
                    )

                    priority = d.selectbox(
                        "Priorité",
                        priority_options,
                        index=(
                            priority_options.index(previous_priority)
                            if previous_priority in priority_options else 1
                        ),
                        key=f"priority_{selected_index}_{comp_id}",
                        disabled=not checked
                    )

                    if checked:
                        selected_ids.add(comp_id)
                        current_roles[comp_id] = role
                        current_priorities[comp_id] = priority
                    else:
                        selected_ids.discard(comp_id)
                        current_roles.pop(comp_id, None)
                        current_priorities.pop(comp_id, None)

            if st.button("💾 Enregistrer la saison", type="primary"):
                st.session_state.wrestlers.at[selected_index, "Competitions"] = sorted(
                    selected_ids
                )
                st.session_state.wrestlers.at[selected_index, "Roles"] = current_roles
                st.session_state.wrestlers.at[selected_index, "Priorites"] = current_priorities
                st.success("Saison enregistrée.")
                st.rerun()

        st.divider()
        st.subheader("📆 Calendrier annuel du lutteur")

        selected_ids = set(wrestler["Competitions"])
        selected_comps = competitions_df[
            competitions_df["ID"].astype(str).isin(selected_ids)
        ].copy()

        if selected_comps.empty:
            st.info("Aucune compétition n'est encore programmée pour ce lutteur.")
        else:
            selected_comps["Date_dt"] = pd.to_datetime(
                selected_comps["Date"],
                errors="coerce"
            )
            selected_comps = selected_comps.dropna(subset=["Date_dt"])
            selected_comps["Mois"] = selected_comps["Date_dt"].dt.month
            selected_comps["Annee"] = selected_comps["Date_dt"].dt.year

            min_date = selected_comps["Date_dt"].min()
            max_date = selected_comps["Date_dt"].max()

            for year in range(min_date.year, max_date.year + 1):
                st.markdown(f"### Saison {year}")

                month_cols = st.columns(3)

                for month in range(1, 13):
                    month_data = selected_comps[
                        (selected_comps["Annee"] == year) &
                        (selected_comps["Mois"] == month)
                    ].sort_values("Date_dt")

                    col = month_cols[(month - 1) % 3]

                    with col:
                        st.markdown(f"**{month_name(month).capitalize()}**")

                        if month_data.empty:
                            st.caption("Aucune compétition")
                        else:
                            for _, comp in month_data.iterrows():
                                comp_id = str(comp["ID"])
                                role = current_roles.get(
                                    comp_id,
                                    wrestler["Roles"].get(comp_id, "Compétition")
                                )
                                priority = current_priorities.get(
                                    comp_id,
                                    wrestler["Priorites"].get(comp_id, "Normale")
                                )

                                badge = {
                                    "Haute": "🔴",
                                    "Normale": "🟠",
                                    "Faible": "🟢"
                                }.get(priority, "🟠")

                                role_icon = {
                                    "Objectif principal": "🏆",
                                    "Qualification": "🎯",
                                    "Compétition": "🤼",
                                    "Préparation": "🏋️",
                                    "Expérience": "🌱"
                                }.get(role, "🤼")

                                st.markdown(
                                    f"""
                                    <div style="
                                        border:1px solid #d9d9d9;
                                        border-radius:8px;
                                        padding:9px;
                                        margin-bottom:8px;
                                        background:#fafafa;">
                                        <b>{format_date(comp['Date'])}</b><br>
                                        <b>{comp['Nom']}</b><br>
                                        📍 {comp['Ville']}<br>
                                        {role_icon} {role}<br>
                                        {badge} Priorité {priority}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

        st.divider()
        st.subheader("📊 Synthèse de saison")

        selected_ids = set(wrestler["Competitions"])
        season_comps = competitions_df[
            competitions_df["ID"].astype(str).isin(selected_ids)
        ].copy()

        if not season_comps.empty:
            roles = wrestler["Roles"]
            priorities = wrestler["Priorites"]

            total = len(season_comps)
            objectives = sum(
                roles.get(str(cid), "") == "Objectif principal"
                for cid in season_comps["ID"]
            )
            qualifications = sum(
                roles.get(str(cid), "") == "Qualification"
                for cid in season_comps["ID"]
            )
            high_priority = sum(
                priorities.get(str(cid), "") == "Haute"
                for cid in season_comps["ID"]
            )

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Compétitions", total)
            s2.metric("Objectifs principaux", objectives)
            s3.metric("Qualifications", qualifications)
            s4.metric("Priorités hautes", high_priority)

            summary_rows = []
            for _, comp in season_comps.sort_values("Date").iterrows():
                cid = str(comp["ID"])
                summary_rows.append({
                    "Date": format_date(comp["Date"]),
                    "Compétition": comp["Nom"],
                    "Ville": comp["Ville"],
                    "Rôle": roles.get(cid, "Compétition"),
                    "Priorité": priorities.get(cid, "Normale")
                })

            st.dataframe(
                pd.DataFrame(summary_rows),
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        with st.expander("⚠️ Gestion du lutteur"):
            if st.button("🗑️ Supprimer ce lutteur", type="secondary"):
                st.session_state.wrestlers = (
                    st.session_state.wrestlers.drop(index=selected_index)
                    .reset_index(drop=True)
                )
                st.success("Lutteur supprimé.")
                st.rerun()


elif page == "💰 Finances club":

    st.title(
        "💰 Budget déplacements"
    )

    st.caption(
        "Estimation des coûts de déplacement "
        "pour les compétitions."
    )

    today = date.today()

    future_df = df[
        df["Date"] >= today
    ].sort_values("Date")

    if future_df.empty:

        st.info(
            "Aucune compétition à venir."
        )

    else:

        financial_rows = []

        for _, competition in future_df.iterrows():

            trip = calculate_trip(
                competition
            )

            financial_rows.append(
                {
                    "Date": competition[
                        "Date"
                    ],
                    "Compétition": competition[
                        "Nom"
                    ],
                    "Ville": competition[
                        "Ville"
                    ],
                    "Distance A/R (km)": round(
                        trip[
                            "round_trip"
                        ]
                    ),
                    "Carburant (€)": round(
                        trip[
                            "fuel"
                        ],
                        2,
                    ),
                    "Péages (€)": round(
                        trip[
                            "toll"
                        ],
                        2,
                    ),
                    "Total (€)": round(
                        trip[
                            "total"
                        ],
                        2,
                    ),
                }
            )

        finance_df = pd.DataFrame(
            financial_rows
        )

        total_km = finance_df[
            "Distance A/R (km)"
        ].sum()

        total_fuel = finance_df[
            "Carburant (€)"
        ].sum()

        total_tolls = finance_df[
            "Péages (€)"
        ].sum()

        total_budget = finance_df[
            "Total (€)"
        ].sum()

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "🚗 Kilomètres",
                f"{total_km:,.0f} km",
            )

        with c2:
            st.metric(
                "⛽ Carburant",
                f"{total_fuel:,.2f} €",
            )

        with c3:
            st.metric(
                "🛣️ Péages",
                f"{total_tolls:,.2f} €",
            )

        with c4:
            st.metric(
                "💰 Total",
                f"{total_budget:,.2f} €",
            )

        st.divider()

        st.subheader(
            "📊 Budget par compétition"
        )

        st.dataframe(
            finance_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(
            "📅 Budget par mois"
        )

        finance_df[
            "Mois"
        ] = finance_df[
            "Date"
        ].apply(
            lambda x:
            f"{month_name(x.month)} {x.year}"
        )

        monthly = (
            finance_df
            .groupby("Mois")[
                "Total (€)"
            ]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            monthly.set_index(
                "Mois"
            )
        )


# ============================================================
# PARAMÈTRES CLUB
# ============================================================

elif page == "⚙️ Paramètres club":

    st.title(
        "⚙️ Paramètres du club"
    )

    st.info(
        "Ces informations servent à calculer "
        "automatiquement les coûts de déplacement."
    )

    club = st.session_state.club

    with st.form(
        "club_settings"
    ):

        club_name = st.text_input(
            "Nom du club",
            value=club["nom"],
        )

        club_address = st.text_input(
            "Adresse du club",
            value=club["adresse"],
        )

        st.subheader(
            "📍 Position du club"
        )

        col1, col2 = st.columns(2)

        with col1:

            club_latitude = st.number_input(
                "Latitude",
                value=float(
                    club["latitude"]
                ),
                format="%.6f",
            )

        with col2:

            club_longitude = st.number_input(
                "Longitude",
                value=float(
                    club["longitude"]
                ),
                format="%.6f",
            )

        st.subheader(
            "⛽ Paramètres véhicule"
        )

        col3, col4 = st.columns(2)

        with col3:

            fuel_price = st.number_input(
                "Prix de l'essence (€ / L)",
                min_value=0.0,
                value=float(
                    club["prix_essence"]
                ),
                step=0.01,
            )

        with col4:

            consumption = st.number_input(
                "Consommation (L / 100 km)",
                min_value=0.1,
                value=float(
                    club["consommation"]
                ),
                step=0.1,
            )

        save = st.form_submit_button(
            "💾 Enregistrer",
            use_container_width=True,
        )

        if save:

            st.session_state.club = {
                "nom": club_name,
                "adresse": club_address,
                "latitude": club_latitude,
                "longitude": club_longitude,
                "prix_essence": fuel_price,
                "consommation": consumption,
                "cout_km": 0.0,
            }

            st.success(
                "✅ Paramètres du club enregistrés."
            )

    st.divider()

    st.subheader(
        "📋 Paramètres actuels"
    )

    current_club = st.session_state.club

    st.write(
        f"**Club :** {current_club['nom']}"
    )

    st.write(
        f"**Adresse :** {current_club['adresse']}"
    )

    st.write(
        f"**Prix essence :** "
        f"{current_club['prix_essence']:.2f} €/L"
    )

    st.write(
        f"**Consommation :** "
        f"{current_club['consommation']:.1f} L/100 km"
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤼 Lutte Calendar V2.0"
)

st.sidebar.caption(
    "Calendrier · Carte · Budget · Planification"
)
