import streamlit as st
import time
import sys
import os
import base64

sys.path.append(os.path.dirname(__file__))

def render():
    def load_css():
        css_path = os.path.join(os.getcwd(), "style.css")
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
        st.session_state.page_was_inactive = False

    current_index = st.session_state.current_artwork_index
    from database.artwork_data import get_artwork_by_index, get_artwork_description
    artwork = get_artwork_by_index(current_index)

    if not artwork:
        st.error("Errore nel caricamento dell'opera.")
        st.stop()

    VIEWING_TIME = 30

    if st.session_state.artwork_start_time is None:
        st.session_state.artwork_start_time = time.time()

    elapsed_time = time.time() - st.session_state.artwork_start_time
    remaining_time = max(VIEWING_TIME - elapsed_time, 0)
    progress = elapsed_time / VIEWING_TIME

    st.progress(min(progress, 1.0), text=f"Opera {current_index + 1} di 3")

    countdown_ph = st.empty()
    
    st.markdown("""
    <div class="warning-box">
        <div style="font-size: 1.2rem; font-weight: bold; color: #856404; margin-bottom: 10px;">Istruzioni importanti</div>
        <ul>
            <li>Leggi attentamente la descrizione e osserva l'opera</li>
            <li><strong>Non prendere appunti</strong></li>
            <li><strong>Non aprire altre schede o finestre nel browser, altrimenti i tuoi dati NON veranno considerati</strong></li>
            <li>Il passaggio alla prossima opera avverrà automaticamente</li>
            <li>Cerca di comprendere e ricordare quanto più possibile</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">"{artwork["title"]}"</div>', unsafe_allow_html=True)

    col_img, col_desc = st.columns([1, 1])

    with col_img:
        try:
            image_filename = artwork['image_url']
            possible_paths = [
                os.path.join("images", image_filename),
                os.path.join(os.getcwd(), "images", image_filename),
                image_filename if os.path.isabs(image_filename) else None
            ]
            possible_paths = [p for p in possible_paths if p]
            image_found = False
            for image_path in possible_paths:
                if os.path.exists(image_path):
                    with open(image_path, "rb") as img_file:
                        img_bytes = img_file.read()
                        img_base64 = base64.b64encode(img_bytes).decode()
                    if image_path.lower().endswith('.png'):
                        mime_type = "image/png"
                    elif image_path.lower().endswith(('.jpg', '.jpeg')):
                        mime_type = "image/jpeg"
                    else:
                        mime_type = "image/jpeg"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
                        <img src="data:{mime_type};base64,{img_base64}" 
                             style="max-width: 500px; max-height: 500px; width: auto; height: auto; object-fit: contain;">
                    </div>
                    """, unsafe_allow_html=True)
                    image_found = True
                    break
            if not image_found:
                st.error(f"Immagine non trovata: {artwork['image_url']}")
        except Exception as e:
            st.error(f"⚠ Errore nel caricamento dell'immagine: {e}")

    with col_desc:
        st.markdown(f"**Artista:** {artwork['artist']} | **Anno:** {artwork['year']} | **Stile:** {artwork['style']}")
        description, selected_interest = get_artwork_description(
            artwork,
            st.session_state.experimental_group,
            st.session_state.top_3_interests
        )
        if 'artwork_interests' not in st.session_state:
            st.session_state.artwork_interests = {}
        st.session_state.artwork_interests[artwork['id']] = selected_interest
        
        st.markdown("### Descrizione dell'opera")
        st.markdown(f'<div class="description-box">{description}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if remaining_time <= 0:
        if not st.session_state.viewing_completed:
            if current_index < 2:
                st.session_state.current_artwork_index += 1
                st.session_state.artwork_start_time = None
                st.rerun()
            else:
                st.session_state.viewing_completed = True
                st.session_state.artwork_start_time = None
                st.success("✅ Visualizzazione opere completata! Procedendo al test...")
                time.sleep(2)
                st.session_state.app_state = "recall"
                st.rerun()
    else:
        while remaining_time > 0:
            mm = int(remaining_time // 60)
            ss = int(remaining_time % 60)
            countdown_ph.metric("Tempo rimanente", f"{mm:02d}:{ss:02d}")
            time.sleep(1)
            elapsed_time = time.time() - st.session_state.artwork_start_time
            remaining_time = max(VIEWING_TIME - elapsed_time, 0)
        
        st.rerun()
