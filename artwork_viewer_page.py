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
    
    from database.artwork_data import get_artwork_by_index, get_artwork_description, initialize_artwork_order
    
    initialize_artwork_order()

    required_states = ['demographics', 'top_3_interests', 'experimental_group', 'participant_id']
    if not all(st.session_state.get(state) for state in required_states):
        st.error("Accesso non consentito.")
        st.session_state.app_state = "interests"
        st.rerun()

    if 'artwork_order' not in st.session_state:
        st.error("Errore ordine opere.")
        st.stop()

    if 'current_artwork' not in st.session_state:
        st.session_state.current_artwork = 0
        st.session_state.button_clicked = False

    current_idx = st.session_state.current_artwork
    
    if current_idx >= 3:
        st.session_state.viewing_completed = True
        st.session_state.app_state = "recall"
        st.rerun()

    artwork = get_artwork_by_index(current_idx)

    if not artwork:
        st.error("Errore nel caricamento dell'opera.")
        st.stop()

    if f"start_time_{current_idx}" not in st.session_state:
        st.session_state[f"start_time_{current_idx}"] = time.time()

    st.progress((current_idx + 1) / 3, text=f"Opera {current_idx + 1} di 3")
    
    st.markdown("""
    <div class="warning-box">
        <div style="font-size: 1.2rem; font-weight: bold; color: #856404; margin-bottom: 10px;">Istruzioni importanti</div>
        <ul>
            <li>Leggi attentamente la descrizione e osserva l'opera</li>
            <li><strong>Non prendere appunti</strong></li>
            <li><strong>Non aprire altre schede o finestre nel browser</strong></li>
            <li>Clicca sul pulsante quando sei pronto per proseguire</li>
            <li>Cerca di comprendere e ricordare quanto più possibile</li>
            <li><strong>Attendi un attimo</strong> - le descrizioni compariranno automaticamente</li>
            <li><strong>NON RICARICARE LA PAGINA!</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 30px;">
        {artwork["title"]}
    </div>
    """, unsafe_allow_html=True)


    col_img, col_desc = st.columns([1, 1])

    with col_img:
        try:
            image_filename = artwork['image_url']
            possible_paths = [
                os.path.join("images", image_filename),
                os.path.join(os.getcwd(), "images", image_filename),
            ]
            image_found = False
            for image_path in possible_paths:
                if os.path.exists(image_path):
                    with open(image_path, "rb") as img_file:
                        img_bytes = img_file.read()
                        img_base64 = base64.b64encode(img_bytes).decode()
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
                st.error(f"Immagine non trovata: {artwork['image_url']}")
        except Exception as e:
            st.error(f"Errore nel caricamento dell'immagine: {e}")

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

    button_text = "Procedi all'opera successiva" if current_idx < 2 else "Completa visualizzazione opere"
    
    if st.button(button_text, type="primary", use_container_width=True, key=f"btn_{current_idx}"):
        if st.session_state.get('button_clicked', False):
            return
            
        st.session_state.button_clicked = True
        
        viewing_time_seconds = time.time() - st.session_state[f"start_time_{current_idx}"]
        
        minutes = int(viewing_time_seconds // 60)
        seconds = int(viewing_time_seconds % 60)
        viewing_time_formatted = f"{minutes}:{seconds:02d}" 
        
        if 'artworks_viewed' not in st.session_state:
            st.session_state.artworks_viewed = []
        if 'artwork_viewing_times' not in st.session_state:
            st.session_state.artwork_viewing_times = {}
            
        st.session_state.artworks_viewed.append({
            'artwork_id': artwork['id'],
            'title': artwork['title'],
            'viewing_time': viewing_time_formatted,
            'interest_used': st.session_state.artwork_interests.get(artwork['id']),
            'timestamp': time.time()
        })
        st.session_state.artwork_viewing_times[artwork['id']] = viewing_time_formatted,
        
        st.session_state.current_artwork += 1
        st.session_state.button_clicked = False
        
        if st.session_state.current_artwork >= 3:
            st.session_state.viewing_completed = True
            st.session_state.app_state = "recall"
        st.rerun()