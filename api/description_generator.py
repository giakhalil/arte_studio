import streamlit as st
import requests
import json
import random


class DescriptionGenerator:
    def __init__(self, use_real_api=True):
        self.use_real_api = use_real_api
        if self.use_real_api:
            self.api_key = st.secrets["openrouter"]["api_key"]
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _get_artwork_specific_facts(self, artwork_id):
        
        facts_map = {
            "10661-17csont.jpg": """
- L'artista è Tivadar Csontváry Kosztka
- Dipinto nel 1907 (circa)
- Tecnica: Olio su tela
- L'albero di cedro simboleggia la persona dell'artista stesso
- L'albero centrale ha un doppio tronco
- Attorno all'albero si svolge una celebrazione che ricorda antichi rituali
- Ci sono figure di uomini e animali
- I colori sono irreali e simbolici
- Scritti di Csontváry menzionano l'albero come simbolo della sua persona
""",
            "24610-moneylen.jpg": """
- L'artista è Quentin Massys
- Dipinto nel 1514
- Tecnica: Olio su tavola
- Lo specchio convesso riflette l'autoritratto dell'artista
- La moglie sta sfogliando un libro
- L'artista cita Jan van Eyck attraverso lo specchio
- Genere: pittura di genere
- Espressioni dei personaggi: indifferenti e distaccate
- Segna un passo importante verso la natura morta pura
""",
            "02502-5season.jpg": """
- L'artista è Giuseppe Arcimboldo
- Dipinto circa nel 1590
- Tecnica: Olio su legno di pioppo
- Realizzato per Don Gregorio Comanini, un letterato mantovano
- La barba è fatta di ciuffi di muschio
- Dall'orecchio pendono ciliegie
- Il tronco spoglio simbolizza l'inverno che non produce nulla
- Il piccolo fiore sul petto simboleggia la primavera
- Il dipinto rappresenta le quattro stagioni in una sola testa
"""
        }
        
        return facts_map.get(artwork_id)
    
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
            artwork_specific_facts = self._get_artwork_specific_facts(artwork_data['id'])
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
- Informazioni obbligatorie da includere: {artwork_specific_facts}

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
            artwork_specific_facts = self._get_artwork_specific_facts(artwork_data['id'])
            selected_interest = random.choice(top_interests[:3])
            
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

2. Trova connessioni genuine tra l'opera e questo interesse: {selected_interest}

CONTROLLI CRITICI:
- Tutte le informazioni devono essere corrette e contestualizzate.
- Integra almeno 3 analogie ESPLICATIVE basate sull'interesse selezionato
- Ogni analogia deve chiarire un aspetto specifico dell'opera
- Usa linguaggio naturale, mai nominare direttamente l'interesse scelto

OUTPUT FINALE:
- circa 200 parole
- Narrazione unica e coerente
- Fatti artistici e analogie integrati organicamente
- Tono accessibile ma informativo
- Informazioni obbligatorie da includere: {artwork_specific_facts}

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