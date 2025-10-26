import streamlit as st
import random
import time
from database.mongo_handler import save_user_data

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

    st.progress(33, text="Fase 2 di 3: Inventario interessi")

    st.markdown('<div class="main-title">I tuoi Interessi</div>', unsafe_allow_html=True)
    st.markdown("""
    - Questa sezione ci aiuterà a comprendere meglio i tuoi interessi personali.
    - Tempo stimato: 5-7 minuti
    - Per favore valuta quanto sei interessato a ciascuna delle seguenti categorie.
    - Usa le slider per dare un voto da 1 a 5 per ogni interesse.
    """)

    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
        st.session_state.timeout_reached = False
        st.session_state.auto_submit = False

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(300 - elapsed_time, 0)
    mm = int(remaining_time // 60)
    ss = int(remaining_time % 60)
    
    timer_placeholder = st.empty()
    timer_placeholder.metric("Tempo rimanente", f"{mm:02d}:{ss:02d}")

    if remaining_time <= 0 and not st.session_state.get('timeout_reached'):
        st.session_state.timeout_reached = True
        st.session_state.auto_submit = True
        st.rerun()

    interest_categories = [
        "Sport (calcio, basket, tennis, ecc.)",
        "Musica (rock, classica, jazz, pop, elettronica, ecc.)", 
        "Natura e Animali",
        "Tecnologia e Gaming",
        "Cibo e Cucina",
        "Viaggi e Geografia",
        "Film e TV",
        "Moda e Design",
        "Scienza (spazio, biologia, fisica, ecc.)",
        "Letteratura e Lettura",
        "Fotografia",
        "Social Media e Cultura Pop",
        "Storia",
        "Attività all'aperto (escursionismo, campeggio, ecc.)"
    ]

    if 'interest_ratings' not in st.session_state:
        st.session_state.interest_ratings = {category: 3 for category in interest_categories}

    st.markdown('<div class="section-header">Valuta i tuoi interessi</div>', unsafe_allow_html=True)
    st.caption("(1 = Per niente interessato, 5 = Molto interessato)")

    for category in interest_categories:
        st.slider(
            f"**{category}**",
            min_value=1, 
            max_value=5, 
            value=st.session_state.interest_ratings.get(category, 3),
            key=f"rate_{category}",
            on_change=lambda cat=category: st.session_state.interest_ratings.update({cat: st.session_state[f"rate_{cat}"]})
        )

    if not st.session_state.get('profile_completed'):
        submitted = st.button("✅ Profilo Completato", type="primary", use_container_width=True)

        if submitted or st.session_state.get('auto_submit'):
            ratings = st.session_state.interest_ratings
            sorted_interests = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
            top_3_interests = [interest[0] for interest in sorted_interests[:3]]
            st.session_state.top_3_interests = top_3_interests

            if 'experimental_group' not in st.session_state:
                st.session_state.experimental_group = random.choice(['A', 'B'])

            is_auto_submitted = st.session_state.get('auto_submit', False)

            user_complete_data = {
                'age': st.session_state.demographics['age'],
                'gender': st.session_state.demographics['gender'],
                'education': st.session_state.demographics['education'],
                'art_familiarity': st.session_state.demographics['art_familiarity'],
                'museum_visits': st.session_state.demographics['museum_visits'],
                'all_interest_ratings': st.session_state.interest_ratings,
                'top_3_interests': top_3_interests,
                'top_3_scores': [ratings[interest] for interest in top_3_interests],
                'experimental_group': st.session_state.experimental_group,
                'time_spent_on_interests': elapsed_time,
            }

            success, participant_id = save_user_data(user_complete_data)

            if success:
                st.session_state.participant_id = participant_id
                st.session_state.data_saved = True
                st.session_state.profile_completed = True
                st.rerun()
            else:
                st.error("❌ Errore nel salvataggio dei dati. Riprova.")

    if st.session_state.get('profile_completed') and st.session_state.get('participant_id'):
        st.markdown("---")
        st.markdown('<div class="section-header">Riepilogo del tuo profilo</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="user-data-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Dati Demografici:**")
            st.write(f"• **ID Partecipante:** {st.session_state.participant_id}")
            st.write(f"• Età: {st.session_state.demographics['age']}")
            st.write(f"• Genere: {st.session_state.demographics['gender']}")
            st.write(f"• Istruzione: {st.session_state.demographics['education']}")
        
        with col2:
            st.markdown("**I tuoi interessi principali:**")
            for i, interest in enumerate(st.session_state.top_3_interests, 1):
                score = st.session_state.interest_ratings[interest]
                st.write(f"{i}. {interest} - {score}/5")
            if st.session_state.get('auto_submitted'):
                st.write("**Nota:** Dati inviati automaticamente per timeout")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.success("✅ Profilo completato con successo!")
        
        if st.button("Procedi alla Visualizzazione delle Opere", type="primary", use_container_width=True):
            st.session_state.app_state = "art_warning"
            st.rerun()

    if remaining_time > 0 and not st.session_state.get('profile_completed'):
        time.sleep(1)
        st.rerun()