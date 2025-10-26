import streamlit as st

class DescriptionGenerator:
    def __init__(self, use_real_api=False):
        self.use_real_api = use_real_api
    
    def get_standard_description(self, artwork_data):
        if self.use_real_api:
            return self.real_api(artwork_data, "standard")
        else:
            prompt = f"""
Agisci come una guida turistica museale. Descrivi la seguente opera d'arte in modo chiaro e coinvolgente.

CONTESTO: Stai conducendo una visita educativa per visitatori .

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
{artwork_data['standard_description'][:500]}...
"""
            return artwork_data['standard_description']
    
    def get_personalized_description(self, artwork_data, top_interests):
        if self.use_real_api:
            return self.real_api(artwork_data, "personalized", top_interests)
        else:
            interests_text = ", ".join(top_interests[:3])
            
            prompt = f"""
Agisci come una guida turistica museale che crea connessioni personalizzate per i visitatori. Descrivi la seguente opera d'arte in modo chiaro e coinvolgente.

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
{artwork_data['standard_description'][:500]}...
"""
            return artwork_data['standard_description']