import streamlit as st
import requests
import json

class DescriptionGenerator:
    def __init__(self, use_real_api=True):
        self.use_real_api = use_real_api
        if self.use_real_api:
            self.api_key = st.secrets["openrouter"]["api_key"]
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _call_openrouter_api(self, prompt):
        try:
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://artestudio.streamlit.app/",
                    "X-Title": "Arte studio",
                },
                data=json.dumps({
                    "model": "openai/gpt-4o-mini-2024-07-18",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7
                }),
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            return None
    
    def get_standard_description(self, artwork_data):
        if self.use_real_api:
            prompt = f"""
CONTESTO: Stai conducendo una visita educativa per visitatori.

IL TUO PROCESSO:
1. Presenta con rigore i dati fondamentali: 
    - L'artista e quando è stata creata
    - La tecnica artistica e lo stile utilizzato
    - Gli elementi visivi chiave e la composizione
    - Il contesto storico e i significati/temi
2. Organizza le informazioni in un flusso narrativo logico, con tono coinvolgente e narrativo.
3. Evita commenti personali o interpretazioni soggettive.

CONTROLLI CRITICI:
- Tutte le informazioni devono essere corrette e contestualizzate.
- Linguaggio chiaro e naturale. 

OUTPUT FINALE:
- 150-200 parole
- Narrazione unica e coerente
- Tono accessibile ma denso di significato


Informazioni opera:
- Titolo: {artwork_data['title']}
- Artista: {artwork_data['artist']}
- Anno: {artwork_data['year']}
- Stile: {artwork_data['style']}

Informazioni di base sull'opera:
{artwork_data['standard_description']}
"""
            description = self._call_openrouter_api(prompt)
            if description:
                description = description.replace('**', '')
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']
    
    def get_personalized_description(self, artwork_data, top_interests):
        if self.use_real_api:
            interests_text = ", ".join(top_interests[:3])
            
            prompt = f"""
CONTESTO: Stai conducendo una visita educativa per visitatori, 
dove l'obiettivo è rendere l'opera più comprensibile intrecciando i concetti 
artistici con gli interessi personali dei visitatori. 

IL TUO PROCESSO:
1. Presenta con rigore i dati fondamentali: 
    - L'artista e quando è stata creata
    - La tecnica artistica e lo stile utilizzato
    - Gli elementi visivi chiave e la composizione
    - Il contesto storico e i significati/temi

2. Analizza questi interessi: {interests_text}. 
- Identifica uno solo tra essi che si collega in modo più naturale e significativo alla storia o ai temi dell'opera.
- Integra tutte le analogie esclusivamente a partire da questo interesse, in modo fluido e coerente, senza mai nominarlo direttamente come “interesse scelto”.
- Le analogie devono aiutare i visitatori a capire meglio l'opera attraverso ciò che già conoscono, usando esempi concreti, accessibili e naturali (mai astratti o troppo allegorici).

CONTROLLI CRITICI:
- Tutte le informazioni devono essere corrette e contestualizzate.
- Linguaggio chiaro e naturale. 
- Almeno tre analogie presenti nel output finale. 

OUTPUT FINALE:
- 150-200 parole
- Narrazione unica e coerente
- Fatti artistici e analogie integrati organicamente
- Tono accessibile ma denso di significato

Informazioni opera:
- Titolo: {artwork_data['title']}
- Artista: {artwork_data['artist']}
- Anno: {artwork_data['year']}
- Stile: {artwork_data['style']}

Informazioni di base sull'opera:
{artwork_data['standard_description']}
"""
            description = self._call_openrouter_api(prompt)
            if description:
                description = description.replace('**', '')
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']