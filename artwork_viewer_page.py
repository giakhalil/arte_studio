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
    if not all(state in st.session_state for state in required_states):
        st.session_state.app_state = "interests"
        st.rerun()

    from database.artwork_data import get_all_artworks
    artworks = get_all_artworks()

    if "artwork_viewing_times" not in st.session_state:
        st.session_state.artwork_viewing_times = {}

    viewed = list(st.session_state.artwork_viewing_times.keys())

    if len(viewed) >= len(artworks):
        st.session_state.total_viewing_time = sum(st.session_state.artwork_viewing_times.values())
        st.session_state.viewing_completed = True
        st.session_state.app_state = "recall"
        st.rerun()

    current_artwork = artworks[len(viewed)]
    art_id = current_artwork["id"]

    if "artwork_start_time" not in st.session_state:
        st.session_state.artwork_start_time = time.time()

    st.progress((len(viewed) + 1) / len(artworks), text=f"Opera {len(viewed) + 1} di {len(artworks)}")

    st.markdown("""
    <div class="warning-box">
        <div style="font-size: 1.2rem; font-weight: bold; color: #856404; margin-bottom: 10px;">Istruzioni importanti</div>
        <ul>
            <li>Leggi attentamente la descrizione e osserva l'opera</li>
            <li><strong>Non prendere appunti</strong></li>
            <li><strong>Prenditi tutto il tempo che ti serve</strong></li>
            <li>Non aprire altre schede o finestre nel browser</li>
            <li>Quando hai finito, clicca il pulsante per procedere</li>
            <li><strong>NON RICARICARE LA PAGINA!</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">"{current_artwork["title"]}"</div>', unsafe_allow_html=True)

    col_img, col_desc = st.columns([1, 1])

    with col_img:
        try:
            image_filename = current_artwork['image_url']
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
                             style="max-width: 700px; max-height: 600px; width: auto; height: auto; object-fit: contain;">
                    </div>
                    """, unsafe_allow_html=True)
                    image_found = True
                    break
            if not image_found:
                st.error(f"Immagine non trovata: {current_artwork['image_url']}")
        except Exception as e:
            st.error(f"⚠ Errore nel caricamento dell'immagine: {e}")

    with col_desc:
        st.markdown(f"**Artista:** {current_artwork['artist']} | **Anno:** {current_artwork['year']} | **Stile:** {current_artwork['style']}")
        from database.artwork_data import get_artwork_description
        description, selected_interest = get_artwork_description(
            current_artwork,
            st.session_state.experimental_group,
            st.session_state.top_3_interests
        )
        if 'artwork_interests' not in st.session_state:
            st.session_state.artwork_interests = {}
        st.session_state.artwork_interests[current_artwork['id']] = selected_interest
        
        st.markdown("### Descrizione dell'opera")
        st.markdown(f'<div class="description-box">{description}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("Procedi all'opera successiva", type="primary", use_container_width=True):
        elapsed = time.time() - st.session_state.artwork_start_time
        st.session_state.artwork_viewing_times[art_id] = elapsed / 60 
        st.session_state.artwork_start_time = time.time()
        st.rerun()

