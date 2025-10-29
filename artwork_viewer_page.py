import streamlit as st
import time
import sys
import os
import base64

sys.path.append(os.path.dirname(__file__))
from database.artwork_data import get_artwork_by_index, get_artwork_description

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

    if 'artwork_start_time' not in st.session_state:
        st.session_state.artwork_start_time = None

    if 'viewing_completed' not in st.session_state:
        st.session_state.viewing_completed = False

    if 'page_was_inactive' not in st.session_state:
        st.session_state.page_was_inactive = False

    if 'artwork_elapsed_time' not in st.session_state:
        st.session_state.artwork_elapsed_time = 0.0

    
    if 'page_visibility_changed' not in st.session_state:
        st.session_state.page_visibility_changed = False
    if 'focus_lost_count' not in st.session_state:
        st.session_state.focus_lost_count = 0
    if 'inactive_periods' not in st.session_state:
        st.session_state.inactive_periods = []

    current_index = st.session_state.current_artwork_index
    artwork = get_artwork_by_index(current_index)
    if not artwork:
        st.error("Errore nel caricamento dell'opera.")
        st.stop()

    VIEWING_TIME = 30 

    if st.session_state.artwork_start_time is None:
        st.session_state.artwork_start_time = time.time()

   
    visibility_js = """
    <script>
    let lastFocusTime = Date.now();
    let currentInactiveStart = null;

    function handleVisibilityChange() {
        const now = Date.now();
        
        if (document.hidden) {
            // Pagina non visibile - utente ha cambiato scheda
            currentInactiveStart = now;
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'focus_lost_' + now
            }, '*');
        } else {
            // Pagina di nuovo visibile
            if (currentInactiveStart) {
                const inactiveDuration = (now - currentInactiveStart) / 1000;
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 'focus_regained_' + inactiveDuration.toFixed(1)
                }, '*');
                currentInactiveStart = null;
            }
            lastFocusTime = now;
        }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Monitora anche gli eventi di focus/blur della finestra
    window.addEventListener('blur', function() {
        currentInactiveStart = Date.now();
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'window_blurred'
        }, '*');
    });
    
    window.addEventListener('focus', function() {
        if (currentInactiveStart) {
            const inactiveDuration = (Date.now() - currentInactiveStart) / 1000;
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'window_focused_' + inactiveDuration.toFixed(1)
            }, '*');
            currentInactiveStart = null;
        }
    });
    </script>
    """

    
    st.components.v1.html(visibility_js, height=0)

  
    query_params = st.experimental_get_query_params()
    for key, value in query_params.items():
        if 'focus_lost' in key or 'window_blurred' in key:
            st.session_state.page_visibility_changed = True
            st.session_state.focus_lost_count += 1
            st.session_state.page_was_inactive = True
            st.experimental_set_query_params()
            break
        elif 'focus_regained' in key or 'window_focused' in key:
            if value and len(value) > 0:
                try:
                    duration = float(value[0].split('_')[-1])
                    st.session_state.inactive_periods.append({
                        'artwork_index': current_index,
                        'duration': duration,
                        'timestamp': time.time()
                    })
                except:
                    pass
            st.experimental_set_query_params()
            break

    elapsed_time = time.time() - st.session_state.artwork_start_time + st.session_state.artwork_elapsed_time
    remaining_time = max(VIEWING_TIME - elapsed_time, 0)
    progress = elapsed_time / VIEWING_TIME

    st.progress(min(progress, 1.0), text=f"Opera {current_index + 1} di 3")
    countdown_ph = st.empty()

  
    if st.session_state.page_visibility_changed:
        st.error("""
        ⚠ **ATTENZIONE: Hai cambiato scheda o finestra!** 
        Questo è stato registrato nel sistema. 
        Per favore, mantieni la concentrazione sullo studio.
        """)

    st.markdown("""
    <div class="warning-box">
        <h4>Istruzioni importanti</h4>
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
                    mime_type = "image/png" if image_path.lower().endswith('.png') else "image/jpeg"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
                        <img src="data:{mime_type};base64,{img_base64}"
                             style="max-width: 500px; max-height: 500px; object-fit: contain;">
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
        description = get_artwork_description(
            artwork,
            st.session_state.experimental_group,
            st.session_state.top_3_interests
        )
        st.markdown("### Descrizione dell'opera")
        st.markdown(f'<div class="description-box">{description}</div>', unsafe_allow_html=True)

    st.markdown("---")

    
    with st.expander("📊 Monitoraggio Attività (Solo per ricerca)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cambi scheda rilevati", st.session_state.focus_lost_count)
        with col2:
            status = "⚠️ ATTENZIONE PERSA" if st.session_state.page_visibility_changed else "✅ IN STUDIO"
            st.metric("Stato attuale", status)
        
        if st.session_state.inactive_periods:
            current_artwork_periods = [p for p in st.session_state.inactive_periods 
                                     if p['artwork_index'] == current_index]
            if current_artwork_periods:
                st.write("Periodi di inattività per questa opera:")
                for i, period in enumerate(current_artwork_periods[-3:]):  # Ultimi 3 periodi
                    st.write(f"- {period['duration']:.1f} secondi")

    while remaining_time > 0:
        mm = int(remaining_time // 60)
        ss = int(remaining_time % 60)
        countdown_ph.metric("Tempo rimanente", f"{mm:02d}:{ss:02d}")
        time.sleep(1)
        elapsed_time = time.time() - st.session_state.artwork_start_time + st.session_state.artwork_elapsed_time
        remaining_time = max(VIEWING_TIME - elapsed_time, 0)
        st.session_state.artwork_elapsed_time = elapsed_time

    if elapsed_time < VIEWING_TIME:
        st.session_state.page_was_inactive = True 
    st.session_state.artwork_start_time = None
    st.session_state.artwork_elapsed_time = 0.0


    if st.session_state.page_visibility_changed:
       
        print(f"PARTICIPANT {st.session_state.participant_id}: Focus perso {st.session_state.focus_lost_count} volte durante l'opera {current_index + 1}")

    if current_index < 2:
        st.session_state.current_artwork_index += 1
        st.rerun()
    else:
        st.session_state.viewing_completed = True
        
        if st.session_state.focus_lost_count > 0:
            st.warning(f"""
            **Nota per il ricercatore:** 
            Il partecipante ha cambiato scheda/finestra {st.session_state.focus_lost_count} volte durante lo studio.
            Totale periodi di inattività: {len(st.session_state.inactive_periods)}
            """)
        
        st.success("✅ Visualizzazione opere completata! Procedendo al test...")
        time.sleep(0.5)
        st.session_state.app_state = "recall"
        st.rerun()