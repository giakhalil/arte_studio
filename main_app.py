import streamlit as st

def initialize_session_state():
    INTEREST_CATEGORIES = [
        "Sport", "Musica", "Natura e Animali", "Tecnologia e Gaming", 
        "Cibo e Cucina", "Viaggi", "Film e TV", "Moda e Design",
        "Scienza", "Letteratura", "Fotografia", "Social Media", 
        "Storia", "Attività all'aperto"
    ]
    navigation_keys = {
        "app_state": "welcome",
        "consent_given": False,
        "profile_completed": False,
        "viewing_completed": False,
        "recall_test_started": False,
        "test_submitted": False,
        "data_saved": False,
        "feedback_given": False
    }
    
    artwork_keys = {
        "current_artwork_index": 0,
        "artwork_start_time": None,
        "current_recall_artwork_index": 0,
        "page_was_inactive": False
    }
    
    user_data_keys = {
        "demographics": None,
        "interest_ratings": {category: 1 for category in INTEREST_CATEGORIES},
        "interest_categories": INTEREST_CATEGORIES,
        "top_3_interests": [],
        "experimental_group": None,
        "participant_id": None,
        "interests_time_spent": 0,
        "user_feedback": ""
    }
    
    cache_keys = {
        "artwork_order": [],
        "artwork_interest_map": {},
        "generated_descriptions": {},
        "artwork_interests": {},
        "recall_answers": {},
        "artwork_start_time": None 
    }
    
    all_keys = {**navigation_keys, **artwork_keys, **user_data_keys, **cache_keys}
    for key, default_value in all_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def safe_render():
    """Wrapper sicuro per il rendering che gestisce errori di sessione"""
    try:
        initialize_session_state()
        
        current_state = st.session_state.app_state
        
        if current_state == "welcome":
            from welcome_page import welcome_page
            welcome_page()
        elif current_state == "interests":
            from interessi_page import interessi_page
            interessi_page()
        elif current_state == "art_warning":
            from art_warning_page import render
            render()
        elif current_state == "art_viewing":
            from artwork_viewer_page import render
            render()
        elif current_state == "recall":
            from recall_page import render
            render()
            
    except Exception as e:
        error_msg = str(e)
        if "Bad session" in error_msg or "SessionInfo" in error_msg:
            st.warning("""
            ⚠️ **Problema di sessione rilevato**
            
            Si è verificato un problema temporaneo. La pagina verrà ricaricata automaticamente.
            """)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        else:
            raise e

st.set_page_config(page_title="Studio Artistico", page_icon="🎨", layout="wide")

safe_render()