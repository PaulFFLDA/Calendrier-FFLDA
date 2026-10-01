import streamlit as st
import pandas as pd
import calendar
import math
from datetime import date, datetime

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

    /* ========================================================
       CALENDRIER
       ======================================================== */

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        margin-top: 10px;
    }

    .calendar-header {
        background: #111827;
        color: white;
        padding: 10px 5px;
        text-align: center;
        font-weight: 700;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .calendar-day {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        min-height: 135px;
        padding: 7px;
        overflow: hidden;
    }

    .calendar-day.empty {
        background: #f3f4f6;
        opacity: 0.5;
    }

    .calendar-day.today {
        border: 2px solid #2563eb;
    }

    .day-number {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }

    .event {
        border-radius: 7px;
        padding: 5px;
        margin-bottom: 5px;
        font-size: 0.72rem;
        color: #111827;
        cursor: default;
    }

    .event-preparation {
        background: #dcfce7;
        border-left: 4px solid #16a34a;
    }

    .event-secondary {
        background: #dbeafe;
        border-left: 4px solid #2563eb;
    }

    .event-intermediate {
        background: #ffedd5;
        border-left: 4px solid #ea580c;
    }

    .event-main {
        background: #fee2e2;
        border-left: 4px solid #dc2626;
    }

    .event-name {
        font-weight: 700;
        line-height: 1.15;
    }

    .event-info {
        color: #4b5563;
        margin-top: 2px;
        line-height: 1.15;
    }

    .legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 12px 0 18px 0;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.85rem;
    }

    .legend-color {
        width: 14px;
        height: 14px;
        border-radius: 4px;
    }

    /* ========================================================
       COMPETITION
       ======================================================== */

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

    /* ========================================================
       DEPLACEMENT
       ======================================================== */

    .cost-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        margin-top: 10px;
    }

    .cost-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 5px;
    }

    .cost-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111827;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PARAMÈTRES CLUB
# ============================================================

DEFAULT_CLUB = {
    "Nom": "Mon club de lutte",
    "Adresse": "Caen, France",
    "Prix carburant": 1.80,
    "Consommation": 7.0,
    "Péage par km": 0.00,
}

if "club" not in st.session_state:
    st.session_state.club = DEFAULT_CLUB.copy()

# ============================================================
# COMPÉTITIONS
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
        "Organisateur": "Comité régional",
        "Inscription": "",
        "Description": "Tournoi de rentrée.",
    },

    # OCTOBRE
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

    # NOVEMBRE
    {
        "Nom": "Tournoi National Ranking #1",
        "Date": date(2026, 11, 7),
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
    },

    {
        "Nom": "Championnat de Normandie",
        "Date": date(2026, 11, 22),
        "Ville": "Rouen",
        "Département": "Seine-Maritime",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U17",
        "Latitude": 49.4432,
        "Longitude": 1.0993,
        "Importance": "Objectif intermédiaire",
        "Organisateur": "Ligue Normandie",
        "Inscription": "",
        "Description": "Championnat régional de Normandie.",
    },

    # DÉCEMBRE
    {
        "Nom": "Tournoi National Ranking #2",
        "Date": date(2026, 12, 12),
        "Ville": "Dijon",
        "Département": "Côte-d'Or",
        "Région": "Bourgogne-Franche-Comté",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 47.3220,
        "Longitude": 5.0415,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Deuxième étape du ranking national.",
    },

    # JANVIER
    {
        "Nom": "TNR Janvier",
        "Date": date(2027, 1, 16),
        "Ville": "Saint-Brieuc",
        "Département": "Côtes-d'Armor",
        "Région": "Bretagne",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 48.5142,
        "Longitude": -2.7658,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi National Ranking.",
    },

    {
        "Nom": "Tournoi de préparation France",
        "Date": date(2027, 1, 30),
        "Ville": "Caen",
        "Département": "Calvados",
        "Région": "Normandie",
        "Style": "Lutte gréco-romaine",
        "Niveau": "Régional",
        "Categorie": "U20",
        "Latitude": 49.1829,
        "Longitude": -0.3707,
        "Importance": "Préparation",
        "Organisateur": "Club",
        "Inscription": "",
        "Description": "Compétition de préparation.",
    },

    # FÉVRIER
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
    },

    # MARS
    {
        "Nom": "TNR Mars",
        "Date": date(2027, 3, 13),
        "Ville": "Lyon",
        "Département": "Rhône",
        "Région": "Auvergne-Rhône-Alpes",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 45.7640,
        "Longitude": 4.8357,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi National Ranking.",
    },

    # AVRIL
    {
        "Nom": "Championnat de Normandie jeunes",
        "Date": date(2027, 4, 10),
        "Ville": "Évreux",
        "Département": "Eure",
        "Région": "Normandie",
        "Style": "Lutte libre",
        "Niveau": "Régional",
        "Categorie": "U15",
        "Latitude": 49.0270,
        "Longitude": 1.1514,
        "Importance": "Objectif intermédiaire",
        "Organisateur": "Ligue Normandie",
        "Inscription": "",
        "Description": "Championnat régional jeunes.",
    },

    # MAI
    {
        "Nom": "TNR Mai",
        "Date": date(2027, 5, 8),
        "Ville": "Besançon",
        "Département": "Doubs",
        "Région": "Bourgogne-Franche-Comté",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 47.2378,
        "Longitude": 6.0241,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi National Ranking.",
    },

    # JUIN
    {
        "Nom": "Tournoi National de fin de saison",
        "Date": date(2027, 6, 5),
        "Ville": "Toulouse",
        "Département": "Haute-Garonne",
        "Région": "Occitanie",
        "Style": "Lutte libre",
        "Niveau": "National",
        "Categorie": "Senior",
        "Latitude": 43.6047,
        "Longitude": 1.4442,
        "Importance": "Compétition secondaire",
        "Organisateur": "Fédération",
        "Inscription": "",
        "Description": "Tournoi national de fin de saison.",
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


def event_class(importance):

    if importance == "Objectif principal":
        return "event-main"

    if importance == "Objectif intermédiaire":
        return "event-intermediate"

    if importance == "Préparation":
        return "event-preparation"

    return "event-secondary"


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


def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return R * 2 * math.asin(math.sqrt(a))


def calculate_trip(comp):

    club_lat = 49.1829
    club_lon = -0.3707

    distance = haversine(
        club_lat,
        club_lon,
        float(comp["Latitude"]),
        float(comp["Longitude"]),
    )

    round_trip = distance * 2

    consumption = st.session_state.club[
        "Consommation"
    ]

    fuel_price = st.session_state.club[
        "Prix carburant"
    ]

    toll_price = st.session_state.club[
        "Péage par km"
    ]

    liters = (
        round_trip * consumption / 100
    )

    fuel_cost = liters * fuel_price

    toll_cost = round_trip * toll_price

    total = fuel_cost + toll_cost

    return {
        "distance": round(distance),
        "round_trip": round(round_trip),
        "liters": round(liters, 1),
        "fuel_cost": round(fuel_cost, 2),
        "toll_cost": round(toll_cost, 2),
        "total": round(total, 2),
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
        "💰 Club & finances",
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

# ============================================================
# CALENDRIER MENSUEL
# ============================================================

elif page == "📅 Calendrier":

    st.title("📅 Calendrier de la saison")

    # --------------------------------------------------------
    # Initialisation du mois affiché
    # --------------------------------------------------------

    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = 2026

    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = 9

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    nav1, nav2, nav3 = st.columns(
        [1, 4, 1]
    )

    with nav1:

        if st.button(
            "◀️ Mois précédent",
            use_container_width=True,
        ):

            if st.session_state.calendar_month == 1:

                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1

            else:

                st.session_state.calendar_month -= 1

            st.rerun()

    with nav2:

        month_name = calendar.month_name[
            st.session_state.calendar_month
        ]

        month_name_fr = {
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
        }[
            st.session_state.calendar_month
        ]

        st.markdown(
            f"""
            <h2 style="text-align:center;">
                📅 {month_name_fr}
                {st.session_state.calendar_year}
            </h2>
            """,
            unsafe_allow_html=True,
        )

    with nav3:

        if st.button(
            "Mois suivant ▶️",
            use_container_width=True,
        ):

            if st.session_state.calendar_month == 12:

                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1

            else:

                st.session_state.calendar_month += 1

            st.rerun()

    # --------------------------------------------------------
    # Légende
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="legend">

            <div class="legend-item">
                <span
                    class="legend-color"
                    style="background:#dcfce7;"
                ></span>
                Préparation
            </div>

            <div class="legend-item">
                <span
                    class="legend-color"
                    style="background:#dbeafe;"
                ></span>
                Compétition secondaire
            </div>

            <div class="legend-item">
                <span
                    class="legend-color"
                    style="background:#ffedd5;"
                ></span>
                Objectif intermédiaire
            </div>

            <div class="legend-item">
                <span
                    class="legend-color"
                    style="background:#fee2e2;"
                ></span>
                Objectif principal
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Filtres
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_style = st.selectbox(
            "🥋 Style",
            ["Tous"] + sorted(
                df["Style"].dropna().unique().tolist()
            ),
        )

    with col2:

        selected_level = st.selectbox(
            "🏆 Niveau",
            ["Tous"] + sorted(
                df["Niveau"].dropna().unique().tolist()
            ),
        )

    with col3:

        selected_category = st.selectbox(
            "👤 Catégorie",
            ["Toutes"] + sorted(
                df["Categorie"].dropna().unique().tolist()
            ),
        )

    calendar_df = df.copy()

    if selected_style != "Tous":

        calendar_df = calendar_df[
            calendar_df["Style"] == selected_style
        ]

    if selected_level != "Tous":

        calendar_df = calendar_df[
            calendar_df["Niveau"] == selected_level
        ]

    if selected_category != "Toutes":

        calendar_df = calendar_df[
            calendar_df["Categorie"] == selected_category
        ]

    # --------------------------------------------------------
    # Calendrier
    # --------------------------------------------------------

    year = st.session_state.calendar_year
    month = st.session_state.calendar_month

    cal = calendar.Calendar(
        firstweekday=0
    )

    weeks = cal.monthdayscalendar(
        year,
        month,
    )

    # En-tête
    days_names = [
        "Lun",
        "Mar",
        "Mer",
        "Jeu",
        "Ven",
        "Sam",
        "Dim",
    ]

    header_html = '<div class="calendar-grid">'

    for day_name in days_names:

        header_html += f"""
            <div class="calendar-header">
                {day_name}
            </div>
        """

    header_html += "</div>"

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Cases du calendrier
    # --------------------------------------------------------

    for week in weeks:

        html = '<div class="calendar-grid">'

        for day_number in week:

            if day_number == 0:

                html += """
                    <div class="calendar-day empty"></div>
                """

                continue

            current_date = date(
                year,
                month,
                day_number,
            )

            is_today = (
                current_date == date.today()
            )

            today_class = (
                "today"
                if is_today
                else ""
            )

            html += f"""
                <div class="calendar-day {today_class}">
                    <div class="day-number">
                        {day_number}
                    </div>
            """

            day_events = calendar_df[
                calendar_df["Date"] == current_date
            ]

            for _, event in day_events.iterrows():

                css_class = event_class(
                    event["Importance"]
                )

                html += f"""
                    <div class="event {css_class}">

                        <div class="event-name">
                            {event["Nom"]}
                        </div>

                        <div class="event-info">
                            📍 {event["Ville"]}
                        </div>

                        <div class="event-info">
                            🥋 {event["Categorie"]}
                        </div>

                        <div class="event-info">
                            🎯 {event["Importance"]}
                        </div>

                    </div>
                """

            html += "</div>"

        html += "</div>"

        st.markdown(
            html,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Détails du mois
    # --------------------------------------------------------

    st.divider()

    month_events = calendar_df[
        (calendar_df["Date"].dt.year == year)
        & (calendar_df["Date"].dt.month == month)
    ].sort_values("Date")

    st.subheader(
        f"📋 Compétitions de {month_name_fr}"
    )

    if month_events.empty:

        st.info(
            "Aucune compétition ce mois-ci."
        )

    else:

        for _, competition in month_events.iterrows():

            with st.container(border=True):

                c1, c2, c3 = st.columns(
                    [2.5, 2, 1.5]
                )

                with c1:

                    st.subheader(
                        competition["Nom"]
                    )

                    st.write(
                        f"📅 {format_date(competition['Date'])}"
                    )

                    st.write(
                        f"📍 {competition['Ville']}"
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

                    trip = calculate_trip(
                        competition
                    )

                    st.write(
                        f"🚗 {trip['round_trip']} km A/R"
                    )

                    st.write(
                        f"💰 {trip['total']:.2f} €"
                    )

# ============================================================
# CARTE INTERACTIVE
# ============================================================

elif page == "🗺️ Carte":

    st.title("🗺️ Carte des compétitions")

    st.info(
        "La carte affiche les compétitions. "
        "Les couleurs correspondent à leur importance."
    )

    map_df = df.copy()

    map_df["Importance"] = map_df[
        "Importance"
    ].fillna("Compétition secondaire")

    # couleurs
    color_map = {
        "Préparation": "#16a34a",
        "Compétition secondaire": "#2563eb",
        "Objectif intermédiaire": "#ea580c",
        "Objectif principal": "#dc2626",
    }

    map_df["color"] = map_df[
        "Importance"
    ].map(color_map)

    map_df["size"] = map_df[
        "Importance"
    ].apply(
        lambda x:
        20
        if x == "Objectif principal"
        else 14
    )

    map_df["label"] = map_df.apply(
        lambda row:
        f"{row['Nom']} | "
        f"{row['Ville']} | "
        f"{format_date(row['Date'])} | "
        f"{row['Importance']}",
        axis=1,
    )

    map_df = map_df.dropna(
        subset=[
            "Latitude",
            "Longitude",
        ]
    )

    if not map_df.empty:

        st.map(
            map_df,
            latitude="Latitude",
            longitude="Longitude",
            color="color",
            size="size",
            tooltip="label",
            zoom=5,
        )

        st.markdown(
            """
            ### 🎨 Légende

            🟢 Préparation  
            🔵 Compétition secondaire  
            🟠 Objectif intermédiaire  
            🔴 Objectif principal
            """
        )

        st.divider()

        st.subheader(
            "📍 Compétitions"
        )

        for _, competition in map_df.sort_values(
            "Date"
        ).iterrows():

            st.write(
                f"📍 **{competition['Nom']}** — "
                f"{competition['Ville']} — "
                f"{format_date(competition['Date'])}"
            )

    else:

        st.warning(
            "Aucune compétition géolocalisée."
        )

# ============================================================
# AJOUT COMPÉTITION
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
# CLUB & FINANCES
# ============================================================

elif page == "💰 Club & finances":

    st.title("💰 Club & finances")

    st.subheader(
        "⚙️ Paramètres de déplacement"
    )

    col1, col2 = st.columns(2)

    with col1:

        club_name = st.text_input(
            "Nom du club",
            value=st.session_state.club["Nom"],
        )

        club_address = st.text_input(
            "Adresse du club",
            value=st.session_state.club["Adresse"],
        )

        fuel_price = st.number_input(
            "⛽ Prix du carburant €/L",
            min_value=0.0,
            value=float(
                st.session_state.club[
                    "Prix carburant"
                ]
            ),
            step=0.01,
        )

    with col2:

        consumption = st.number_input(
            "🚗 Consommation L/100 km",
            min_value=0.0,
            value=float(
                st.session_state.club[
                    "Consommation"
                ]
            ),
            step=0.1,
        )

        toll_per_km = st.number_input(
            "🛣️ Péage €/km",
            min_value=0.0,
            value=float(
                st.session_state.club[
                    "Péage par km"
                ]
            ),
            step=0.01,
        )

    if st.button(
        "💾 Enregistrer les paramètres",
        use_container_width=True,
    ):

        st.session_state.club = {
            "Nom": club_name,
            "Adresse": club_address,
            "Prix carburant": fuel_price,
            "Consommation": consumption,
            "Péage par km": toll_per_km,
        }

        st.success(
            "Paramètres enregistrés."
        )

    st.divider()

    st.subheader(
        "📊 Budget déplacements"
    )

    total_km = 0
    total_fuel = 0
    total_tolls = 0
    total_cost = 0

    rows = []

    for _, competition in df.iterrows():

        trip = calculate_trip(
            competition
        )

        total_km += trip["round_trip"]
        total_fuel += trip["fuel_cost"]
        total_tolls += trip["toll_cost"]
        total_cost += trip["total"]

        rows.append(
            {
                "Compétition": competition["Nom"],
                "Ville": competition["Ville"],
                "Date": competition["Date"],
                "Distance A/R (km)": trip["round_trip"],
                "Carburant (€)": trip["fuel_cost"],
                "Péages (€)": trip["toll_cost"],
                "Total (€)": trip["total"],
            }
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🚗 Distance totale",
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
            f"{total_cost:,.2f} €",
        )

    st.divider()

    st.subheader(
        "📋 Détail des déplacements"
    )

    finance_df = pd.DataFrame(rows)

    st.dataframe(
        finance_df,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤼 Lutte Calendar V1.7"
)

st.sidebar.caption(
    "Calendrier · Carte · Déplacements · Planification"
)
