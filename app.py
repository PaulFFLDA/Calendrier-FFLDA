import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="Calendrier Lutte",
    page_icon="🤼",
    layout="wide"
)

# ---------------------------------------------------------
# DONNÉES
# ---------------------------------------------------------

if "competitions" not in st.session_state:
    st.session_state.competitions = pd.DataFrame([
        {
            "Nom": "Tournoi de rentrée",
            "Date": date(2026, 9, 20),
            "Ville": "Caen",
            "Département": "Calvados",
            "Style": "Lutte libre",
            "Niveau": "Régional",
            "Categorie": "U17",
            "Latitude": 49.1829,
            "Longitude": -0.3707,
            "Importance": "Préparation"
        },
        {
            "Nom": "Championnat régional",
            "Date": date(2026, 10, 18),
            "Ville": "Rennes",
            "Département": "Ille-et-Vilaine",
            "Style": "Lutte gréco-romaine",
            "Niveau": "Régional",
            "Categorie": "U20",
            "Latitude": 48.1173,
            "Longitude": -1.6778,
            "Importance": "Objectif intermédiaire"
        },
        {
            "Nom": "Championnat de France",
            "Date": date(2027, 2, 20),
            "Ville": "Paris",
            "Département": "Paris",
            "Style": "Lutte libre",
            "Niveau": "National",
            "Categorie": "Senior",
            "Latitude": 48.8566,
            "Longitude": 2.3522,
            "Importance": "Objectif principal"
        }
    ])

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🤼 Calendrier Lutte")
st.sidebar.caption("Mutualisation du calendrier et planification sportive")

page = st.sidebar.radio(
    "Navigation",
    [
        "📅 Calendrier",
        "🗺️ Carte",
        "➕ Ajouter une compétition",
        "🎯 Planification"
    ]
)

df = st.session_state.competitions.copy()

# ---------------------------------------------------------
# CALENDRIER
# ---------------------------------------------------------

if page == "📅 Calendrier":

    st.title("📅 Calendrier des compétitions")

    col1, col2, col3 = st.columns(3)

    with col1:
        styles = ["Tous"] + sorted(df["Style"].unique().tolist())
        style = st.selectbox("Style", styles)

    with col2:
        levels = ["Tous"] + sorted(df["Niveau"].unique().tolist())
        level = st.selectbox("Niveau", levels)

    with col3:
        categories = ["Toutes"] + sorted(df["Categorie"].unique().tolist())
        category = st.selectbox("Catégorie", categories)

    filtered = df.copy()

    if style != "Tous":
        filtered = filtered[filtered["Style"] == style]

    if level != "Tous":
        filtered = filtered[filtered["Niveau"] == level]

    if category != "Toutes":
        filtered = filtered[filtered["Categorie"] == category]

    filtered = filtered.sort_values("Date")

    st.subheader(f"{len(filtered)} compétition(s)")

    if len(filtered) == 0:
        st.info("Aucune compétition ne correspond aux filtres.")
    else:
        for _, competition in filtered.iterrows():

            days = (competition["Date"] - date.today()).days

            if days > 0:
                countdown = f"dans {days} jours"
            elif days == 0:
                countdown = "Aujourd'hui"
            else:
                countdown = f"il y a {-days} jours"

            with st.container(border=True):

                c1, c2, c3 = st.columns([2, 1, 2])

                with c1:
                    st.subheader(competition["Nom"])
                    st.write(
                        f"📅 **{competition['Date'].strftime('%d/%m/%Y')}** "
                        f"({countdown})"
                    )

                with c2:
                    st.write(f"📍 {competition['Ville']}")
                    st.write(f"🥋 {competition['Style']}")

                with c3:
                    st.write(f"🏆 {competition['Niveau']}")
                    st.write(f"👤 {competition['Categorie']}")
                    st.write(
                        f"🎯 **{competition['Importance']}**"
                    )

# ---------------------------------------------------------
# CARTE
# ---------------------------------------------------------

elif page == "🗺️ Carte":

    st.title("🗺️ Carte des compétitions")

    st.write(
        "Visualisation géographique des compétitions enregistrées."
    )

    map_data = df[
        ["Latitude", "Longitude"]
    ].dropna()

    st.map(
        map_data,
        latitude="Latitude",
        longitude="Longitude",
        zoom=5
    )

    st.divider()

    st.subheader("Compétitions")

    for _, competition in df.sort_values("Date").iterrows():

        st.write(
            f"**{competition['Nom']}** — "
            f"{competition['Ville']} — "
            f"{competition['Date'].strftime('%d/%m/%Y')}"
        )

# ---------------------------------------------------------
# AJOUT COMPÉTITION
# ---------------------------------------------------------

elif page == "➕ Ajouter une compétition":

    st.title("➕ Ajouter une compétition")

    st.write(
        "Ajoute une compétition au calendrier partagé."
    )

    with st.form("competition_form"):

        name = st.text_input(
            "Nom de la compétition *"
        )

        col1, col2 = st.columns(2)

        with col1:
            competition_date = st.date_input(
                "Date *",
                value=date.today()
            )

            city = st.text_input(
                "Ville *"
            )

            department = st.text_input(
                "Département / région"
            )

        with col2:
            style = st.selectbox(
                "Style",
                [
                    "Lutte libre",
                    "Lutte gréco-romaine",
                    "Lutte féminine"
                ]
            )

            level = st.selectbox(
                "Niveau",
                [
                    "Départemental",
                    "Régional",
                    "National",
                    "International"
                ]
            )

            category = st.text_input(
                "Catégorie",
                placeholder="Ex : U15, U17, U20, Senior"
            )

        importance = st.selectbox(
            "Importance dans la saison",
            [
                "Préparation",
                "Compétition secondaire",
                "Objectif intermédiaire",
                "Objectif principal"
            ]
        )

        st.subheader("📍 Géolocalisation")

        col3, col4 = st.columns(2)

        with col3:
            latitude = st.number_input(
                "Latitude",
                value=49.1829,
                format="%.6f"
            )

        with col4:
            longitude = st.number_input(
                "Longitude",
                value=-0.3707,
                format="%.6f"
            )

        submitted = st.form_submit_button(
            "Ajouter au calendrier"
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
                    "Style": style,
                    "Niveau": level,
                    "Categorie": category,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Importance": importance
                }

                st.session_state.competitions = pd.concat(
                    [
                        st.session_state.competitions,
                        pd.DataFrame([new_competition])
                    ],
                    ignore_index=True
                )

                st.success(
                    f"✅ {name} a été ajouté au calendrier."
                )

# ---------------------------------------------------------
# PLANIFICATION
# ---------------------------------------------------------

elif page == "🎯 Planification":

    st.title("🎯 Planification sportive")

    st.write(
        "Première version de l'outil de planification "
        "autour des compétitions."
    )

    athlete = st.text_input(
        "Nom du lutteur",
        placeholder="Ex : Jean Dupont"
    )

    if athlete:

        st.subheader(
            f"Planification de {athlete}"
        )

        objective = st.selectbox(
            "Objectif principal de la saison",
            [
                "Développement / apprentissage",
                "Championnat régional",
                "Championnat de France",
                "Compétition internationale",
                "Autre"
            ]
        )

        st.write(
            f"🎯 Objectif sélectionné : **{objective}**"
        )

        st.divider()

        st.subheader("📅 Compétitions de préparation")

        available = df.sort_values("Date")

        selected = st.multiselect(
            "Sélectionner les compétitions",
            options=available["Nom"].tolist()
        )

        if selected:

            planning = available[
                available["Nom"].isin(selected)
            ].copy()

            planning["Jours avant"] = (
                planning["Date"]
                .apply(lambda x: (x - date.today()).days)
            )

            st.dataframe(
                planning[
                    [
                        "Nom",
                        "Date",
                        "Ville",
                        "Importance",
                        "Jours avant"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("📈 Lecture de la saison")

            for _, competition in planning.iterrows():

                days = competition["Jours avant"]

                if days > 42:
                    phase = "🟢 Préparation générale"
                elif days > 21:
                    phase = "🟡 Préparation spécifique"
                elif days > 7:
                    phase = "🟠 Pré-compétition"
                elif days >= 0:
                    phase = "🔴 Compétition / affûtage"
                else:
                    phase = "🔵 Récupération"

                st.write(
                    f"**{competition['Date'].strftime('%d/%m/%Y')}** — "
                    f"{competition['Nom']} → {phase}"
                )

        else:
            st.info(
                "Sélectionne les compétitions qui font partie "
                "de la planification du lutteur."
            )

    else:
        st.info(
            "Entre le nom d'un lutteur pour commencer "
            "sa planification."
        )

# ---------------------------------------------------------
# PIED DE PAGE
# ---------------------------------------------------------

st.sidebar.divider()

st.sidebar.caption(
    "V1 — Calendrier mutualisé de la lutte"
)
