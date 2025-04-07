import streamlit as st
import pandas as pd
import json
from collections import Counter
import itertools

# Konstanten
MAX_FRISCHE = 100
EINHEITEN_DATEI = "einheiten.json"  # JSON-Datei mit Einheiten

# Einheiten laden
def lade_einheiten():
    with open(EINHEITEN_DATEI, 'r', encoding='utf-8') as f:
        einheiten = json.load(f)
    
    # Wandelt flaches Skill-Format in geschachteltes um
    for einheit in einheiten:
        einheit["skills"] = {
            "Kondition": einheit.get("kondition", 0),
            "Kraft": einheit.get("kraft", 0),
            "Schnelligkeit": einheit.get("schnelligkeit", 0),
            "Passen": einheit.get("passen", 0),
            "Technik": einheit.get("technik", 0),
        }
    return einheiten

# Beste Kombinationen berechnen
def berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n=5):
    valid_combinations = []

    for n in range(1, len(einheiten) + 1):
        for combo in itertools.combinations_with_replacement(einheiten, n):
            gesamtfrische = sum(unit['frischeverbrauch'] for unit in combo)
            gesamtzeit = sum(unit['dauer'] for unit in combo)

            if gesamtfrische <= restfrische and gesamtzeit <= verfuegbare_zeit:
                gesamt_skills = Counter()
                for unit in combo:
                    gesamt_skills.update(unit['skills'])
                valid_combinations.append((gesamt_skills, gesamtfrische, gesamtzeit, combo))

    # Nach Gesamt-Skillpunkten sortieren (Summe aller Skills)
    valid_combinations.sort(key=lambda x: sum(x[0].values()), reverse=True)
    return valid_combinations[:top_n]

# Ausgabe der besten Kombinationen
def zeige_besten_auswahl(best_kombinationen):
    for index, (skills, frische, zeit, combo) in enumerate(best_kombinationen):
        # Einheiten zusammenfassen
        einheiten_counter = Counter([e['name'] for e in combo])
        einheiten_zeile = "; ".join([f"{anzahl}x {name}" for name, anzahl in einheiten_counter.items()])
        
        st.markdown(f"### 🥇 Kombination {index + 1}")
        st.markdown(f"**Einheiten:** {einheiten_zeile}")
        st.markdown(f"**Gesamte Skillpunkte:** {sum(skills.values())}")
        
        # Skills einzeln
        skills_text = ", ".join([f"{k}: {v}" for k, v in skills.items()])
        st.markdown(f"**Einzelskills:** {skills_text}")
        
        st.markdown(f"**Gesamtzeit:** {zeit} Stunden")
        st.markdown(f"**Gesamt Frischeverbrauch:** {frische}\n---")

# Streamlit-Hauptfunktion
def main():
    st.title("💪⚽ Trainingsplan-Optimierer")

    einheiten = lade_einheiten()

    st.subheader("📊 Parameter")
    restfrische = st.slider("Verbleibende Frische", 0, MAX_FRISCHE, 100)
    verfuegbare_zeit = st.number_input("Verfügbare Trainingszeit (Stunden)", min_value=1, value=6)
    top_n = st.number_input("Top N Kombinationen anzeigen", min_value=1, max_value=10, value=5)

    if st.button("🔍 Optimieren"):
        kombis = berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n)
        if not kombis:
            st.warning("Keine gültige Kombination gefunden.")
        else:
            zeige_besten_auswahl(kombis)

    # Tabelle mit allen Einheiten anzeigen
    st.subheader("📋 Aktuelle Einheiten")
    df = pd.DataFrame(einheiten)
    df['skillpunkte'] = df['skills'].apply(lambda s: sum(s.values()))
    st.dataframe(df)

    # Neue Einheit hinzufügen
    st.subheader("➕ Neue Einheit hinzufügen")
    name = st.text_input("Name")
    kosten = st.text_input("Kosten (optional)")
    dauer = st.number_input("Dauer [h]", min_value=1)
    frischeverbrauch = st.number_input("Frischeverbrauch", min_value=-MAX_FRISCHE, max_value=MAX_FRISCHE)
    kondition = st.number_input("Kondition", min_value=0)
    kraft = st.number_input("Kraft", min_value=0)
    schnelligkeit = st.number_input("Schnelligkeit", min_value=0)
    technik = st.number_input("Technik", min_value=0)

    if st.button("Einheit speichern"):
        neue_einheit = {
            "name": name,
            "kosten": kosten,
            "dauer": dauer,
            "frischeverbrauch": frischeverbrauch,
            "skills": {
                "Kondition": kondition,
                "Kraft": kraft,
                "Schnelligkeit": schnelligkeit,
                "Technik": technik
            }
        }
        einheiten.append(neue_einheit)
        with open(EINHEITEN_DATEI, 'w', encoding='utf-8') as f:
            json.dump(einheiten, f, ensure_ascii=False, indent=2)
        st.success(f"Einheit '{name}' wurde gespeichert.")
        st.experimental_rerun()

if __name__ == "__main__":
    main()
