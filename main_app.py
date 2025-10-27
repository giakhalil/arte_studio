import streamlit as st
st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="Studio Artistico", page_icon="🎨", layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = "welcome"

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