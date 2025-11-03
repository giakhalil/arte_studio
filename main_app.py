import streamlit as st
import time

if 'app_state' not in st.session_state:
    st.session_state.app_state = "welcome"

required_states = [
    'consent_given', 'demographics', 'top_3_interests', 'experimental_group',
    'participant_id', 'interest_ratings', 'profile_completed', 'viewing_completed',
    'recall_test_started', 'current_recall_artwork_index', 'recall_answers',
    'test_submitted', 'data_saved', 'feedback_given', 'current_artwork_index',
    'artwork_start_time', 'page_was_inactive', 'interests_start_time',
    'generated_descriptions', 'artwork_order'
]

for state in required_states:
    if state not in st.session_state:
        if state in ['recall_answers', 'generated_descriptions', 'interest_ratings']:
            st.session_state[state] = {}
        elif state in ['current_recall_artwork_index', 'current_artwork_index']:
            st.session_state[state] = 0
        elif state in ['recall_test_started', 'test_submitted', 'data_saved', 
                      'feedback_given', 'viewing_completed', 'profile_completed',
                      'page_was_inactive', 'consent_given']:
            st.session_state[state] = False
        else:
            st.session_state[state] = None
            
st.set_page_config(page_title="Studio Artistico", page_icon="🎨", layout="wide")
time.sleep(0.1)
main_container = st.container()

with main_container:
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