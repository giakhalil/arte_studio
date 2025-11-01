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
1. Identifica i fatti storico-artistici essenziali. Includi informazioni su:
    - L'artista e quando è stata creata
    - La tecnica artistica e lo stile utilizzato
    - Gli elementi visivi chiave e la composizione
    - Il contesto storico e i significati/temi
2. Organizza le informazioni in una struttura chiara e logica
3. Mantieni il rigore accademico restando coinvolgente

CONTROLLI CRITICI:
- Assicurati che tutte le informazioni fattuali siano accurate e ben contestualizzate
- Evita interpretazioni soggettive o opinioni personali

OUTPUT FINALE:
- 150-200 parole
- Fatti storico-artistici completi
- Descrizione educativa chiara e strutturata
- Tono coinvolgente e accessibile.

Informazioni opera:
- Titolo: {artwork_data['title']}
- Artista: {artwork_data['artist']}
- Anno: {artwork_data['year']}
- Stile: {artwork_data['style']}

Informazioni di base sull'opera:
{artwork_data['standard_description']}
"""
            description = self._call_openrouter_api(prompt)
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']
    
    def get_personalized_description(self, artwork_data, top_interests):
        if self.use_real_api:
            interests_text = ", ".join(top_interests[:3])
            
            prompt = f"""
CONTESTO: Stai conducendo una visita educativa, collegando i concetti artistici dell'opera ai mondi esperienziali dei visitatori in modo totalmente naturale e celato.

IL TUO PROCESSO:
1. Identifica i fatti storico-artistici essenziali. Includi informazioni su:
    - L'artista e quando è stata creata
    - La tecnica artistica e lo stile utilizzato
    - Gli elementi visivi chiave e la composizione
    - Il contesto storico e i significati/temi

2. Trova connessioni genuine tra l'opera e questi interessi: {interests_text}. 
Le analogie devono:
- Essere celate nel flusso narrativo, senza formule fisse.
- Essere almeno una per ogni interesse dato
- Rivelare un aspetto significativo dell'opera

CONTROLLI CRITICI:
- Assicurati che tutte le informazioni fattuali siano accurate e ben contestualizzate
- Analogie significative e non forzate
- Integrazione totale delle analogie nel racconto

OUTPUT FINALE:
- 150-200 parole
- Fatti storico-artistici completi
- Un unico flusso narrativo coinvolgente
- Fatti artistici e analogie fuse organicamente
- Linguaggio accessibile ma profondo

Informazioni opera:
- Titolo: {artwork_data['title']}
- Artista: {artwork_data['artist']}
- Anno: {artwork_data['year']}
- Stile: {artwork_data['style']}

Informazioni di base sull'opera:
{artwork_data['standard_description']}
"""
            description = self._call_openrouter_api(prompt)
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']