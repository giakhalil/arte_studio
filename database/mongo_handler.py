import streamlit as st
from pymongo import MongoClient
import datetime
import random
import string

@st.cache_resource(show_spinner=False)
def get_mongo_connection():
    try:
        connection_string = st.secrets["mongodb"]["connection_string"]
        client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        
        client.admin.command('ping')
        return client
        
    except Exception as e:
        st.error(f"❌ Errore connessione MongoDB: {e}")
        return None

def generate_participant_id():
    random_part = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"P_{random.randint(100, 999)}_{random_part}"

def save_user_data(user_data):
    try:
        client = get_mongo_connection()
        if not client:
            return False, None
            
        db = client[st.secrets["mongodb"]["database_name"]]
        collection = db["participants"]
        
        user_data["created_at"] = datetime.datetime.now()
        
        if "participant_id" not in user_data:
            user_data["participant_id"] = generate_participant_id()
        
        result = collection.insert_one(user_data)
        return True, user_data["participant_id"]
        
    except Exception as e:
        st.error(f"❌ Errore salvataggio MongoDB: {e}")
        return False, None