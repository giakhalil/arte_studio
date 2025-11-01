import streamlit as st
import random
import time
from database.mongo_handler import generate_participant_id

def interessi_page():
    def load_css():
        try:
            with open("style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass

    load_css()

    if not st.session_state.get('demographics'):
        st.error("❌ Accesso non consentito. Completa prima la pagina iniziale.")
        time.sleep(1)
        st.session_state.app_state = "welcome"
        st.rerun()

    if 'interests_start_time' not in st.session_state:
        st.session_state.interests_start_time = time.time()

    st.progress(75, text="Fase 3 di 4: Inventario interessi")

    st.markdown('<div class="main-title">I tuoi Interessi</div>', unsafe_allow_html=True)
    st.markdown("""
    - Questa sezione ci aiuterà a comprendere meglio i tuoi interessi personali.
    - Per favore valuta quanto sei interessato a ciascuna delle seguenti categorie.
    - Usa le slider per dare un voto da 1 a 5 per ogni interesse.
    """)

    interest_categories = [
        "Sport",
        "Musica", 
        "Natura e Animali",
        "Tecnologia e Gaming",
        "Cibo e Cucina",
        "Viaggi",
        "Film e TV",
        "Moda e Design",
        "Scienza",
        "Letteratura",
        "Fotografia",
        "Social Media",
        "Storia",
        "Attività all'aperto"
    ]

    if 'interest_ratings' not in st.session_state:
        st.session_state.interest_ratings = {category: 1 for category in interest_categories}

    st.markdown('<div class="section-header">Valuta i tuoi interessi</div>', unsafe_allow_html=True)
    st.caption("(1 = Per niente interessato, 5 = Molto interessato)")

    col1, col2 = st.columns(2)
    interests_per_col = len(interest_categories) // 2

    with col1:
        for category in interest_categories[:interests_per_col]:
            st.slider(
                category,
                min_value=1, 
                max_value=5, 
                value=st.session_state.interest_ratings.get(category, 1),
                key=f"rate_{category}",
                on_change=lambda cat=category: st.session_state.interest_ratings.update({cat: st.session_state[f"rate_{cat}"]})
            )

    with col2:
        for category in interest_categories[interests_per_col:]:
            st.slider(
                category,
                min_value=1, 
                max_value=5, 
                value=st.session_state.interest_ratings.get(category, 1),
                key=f"rate_{category}",
                on_change=lambda cat=category: st.session_state.interest_ratings.update({cat: st.session_state[f"rate_{cat}"]})
            )

    if not st.session_state.get('profile_completed'):
        submitted = st.button("Profilo Completato", type="primary", use_container_width=True)

        if submitted:
            interests_time_spent = time.time() - st.session_state.interests_start_time
            st.session_state.interests_time_spent = interests_time_spent
            ratings = st.session_state.interest_ratings
            sorted_interests = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
            top_3_interests = [interest[0] for interest in sorted_interests[:3]]
            st.session_state.top_3_interests = top_3_interests

            if 'experimental_group' not in st.session_state:
                st.session_state.experimental_group = random.choice(['A', 'B'])

            st.session_state.participant_id = generate_participant_id()
            st.session_state.data_saved = True 
            st.session_state.profile_completed = True
            st.rerun()
            
    if st.session_state.get('profile_completed'):
        st.success("✅ Profilo completato con successo!")
        
        if st.button("Procedi alla Visualizzazione delle Opere", type="primary", use_container_width=True):
            st.session_state.app_state = "art_warning"
            st.rerun()