import streamlit as st
import time
import sys
import os
import base64
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

def render():
    if "app_state" not in st.session_state:
        st.session_state.app_state = "welcome"
        st.warning("⚠ Sessione riavviata. Torna alla schermata iniziale.")
        st.rerun()

    def load_css():
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    load_css()

    required_states = ['demographics', 'top_3_interests', 'experimental_group', 'participant_id']
    if not all(st.session_state.get(state) for state in required_states):
        st.error("⚠ Accesso non consentito. Completa prima il profilo.")
        st.session_state.app_state = "interests"
        st.rerun()

    if 'current_artwork_index' not in st.session_state:
        st.session_state.current_artwork_index = 0
        st.session_state.artwork_start_time = None
        st.session_state.viewing_completed = False

    from database.artwork_data import get_artwork_by_index, get_artwork_description
    current_index = st.session_state.current_artwork_index
    artwork = get_artwork_by_index(current_index)

    if not artwork:
        st.error("Errore nel caricamento dell'opera.")
        st.stop()

    VIEWING_TIME = 60

    if st.session_state.artwork_start_time is None:
        st.session_state.artwork_start_time = time.time()

    elapsed_time = time.time() - st.session_state.artwork_start_time
    remaining_time = max(VIEWING_TIME - elapsed_time, 0)
    progress = elapsed_time / VIEWING_TIME

    st.progress(min(progress, 1.0), text=f"Opera {current_index + 1} di 3")

    countdown_ph = st.empty()
    mm, ss = int(remaining_time // 60), int(remaining_time % 60)
    countdown_ph.metric("Tempo rimanente", f"{mm:02d}:{ss:02d}")

    st.experimental_set_query_params(ts=datetime.now().timestamp())

    st.markdown("""
    <div class="warning-box">
        <h4>Istruzioni importanti</h4>
        <ul>
            <li>Leggi attentamente la descrizione e osserva l'opera</li>
            <li><strong>Non prendere appunti</strong></li>
            <li><strong>Non aprire altre schede o finestre nel browser</strong></li>
            <li>Il passaggio alla prossima opera avverrà automaticamente</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">"{artwork["title"]}"</div>', unsafe_allow_html=True)

    col_img, col_desc = st.columns([1, 1])

    with col_img:
        try:
            image_filename = artwork['image_url']
            image_path = os.path.join(os.path.dirname(__file__), "images", image_filename)
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    img_bytes = img_file.read()
                    img_base64 = base64.b64encode(img_bytes).decode()
                mime_type = "image/png" if image_path.endswith(".png") else "image/jpeg"
                st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
                    <img src="data:{mime_type};base64,{img_base64}" 
                         style="max-width: 500px; max-height: 500px; object-fit: contain;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Immagine non trovata: {artwork['image_url']}")
        except Exception as e:
            st.error(f"⚠ Errore nel caricamento dell'immagine: {e}")

    with col_desc:
        st.markdown(f"**Artista:** {artwork['artist']} | **Anno:** {artwork['year']} | **Stile:** {artwork['style']}")
        description = get_artwork_description(
            artwork,
            st.session_state.experimental_group,
            st.session_state.top_3_interests
        )
        st.markdown("### Descrizione dell'opera")
        st.markdown(f'<div class="description-box">{description}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if remaining_time <= 0:
        if not st.session_state.viewing_completed:
            if current_index < 2:
                st.session_state.current_artwork_index += 1
                st.session_state.artwork_start_time = None
                st.toast(f"➡ Passaggio automatico all'opera {current_index + 2}...", icon="🖼️")
                st.experimental_rerun()
            else:
                st.session_state.viewing_completed = True
                st.session_state.artwork_start_time = None
                st.success("✅ Visualizzazione opere completata! Procedendo al test...")
                st.session_state.app_state = "recall"
                st.experimental_rerun()
