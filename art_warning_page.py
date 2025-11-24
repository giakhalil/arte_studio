import streamlit as st
import os
import time

def render():
    def load_css():
        css_path = os.path.join(os.getcwd(), "style.css")
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    load_css()

    required_states = ['demographics', 'top_3_interests', 'experimental_group', 'participant_id']
    missing_states = [state for state in required_states if not st.session_state.get(state)]

    if missing_states:
        st.error("❌ Accesso non consentito. Completa prima il profilo.")
        st.session_state.app_state = "welcome"
        st.rerun()

    st.progress(100, text="Fase 4 di 4: Visualizzazione opere e test")

    st.markdown('<div class="main-title">Visualizzazione Opere d\'Arte</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Istruzioni per la fase successiva</div>', unsafe_allow_html=True)

    st.markdown("""
    **Cosa succederà ora:**
    - Vedrai 3 opere d'arte, una alla volta
    - Leggi attentamente la descrizione
    - **Non prendere appunti**
    - Dopo le 3 opere, risponderai a domande su ciò che ricordi
    """)

    if st.button("Inizia la Visualizzazione delle Opere", type="primary", use_container_width=True):
        st.session_state.current_artwork_index = 0
        st.session_state.artwork_start_time = None
        st.session_state.viewing_completed = False
    
        st.session_state.app_state = "art_viewing"
        
        st.success("✅ Avvio della visualizzazione opere...")
        time.sleep(0.3)
        st.rerun()