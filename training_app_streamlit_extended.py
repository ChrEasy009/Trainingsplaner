import streamlit as st
import pandas as pd
import json
from collections import Counter
import itertools

# Konstanten
MAX_FRISCHE = 100
EINHEITEN_DATEI = "einheiten.json"  # JSON-Datei mit den Einheiten

# Einheiten laden und Skill-Daten strukturieren
def lade_einheiten():
    with open(EINHEITEN_DATEI, 'r', encoding='utf-8') as f:
        einheiten = json.load(f)

    # Skills korrekt zusammenfassen
    for einheit in einheiten:
        einheit["skills"] = {
            "Kondition": einheit.get("kondition", 0),
            "Kraft": einheit.get("kraft", 0),
            "Schnelligkeit": einheit.get("schnelligkeit", 0),
            "Passen": einheit.get("passen", 0),
            "Technik": einheit.get("technik", 0)
        }
    return einheiten

# Beste Kombinationen berechnen
def berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n=10):
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

    valid_combinations.sort(key=lambda x: sum(x[0].values()), reverse=True)
    return valid_combinations[:top_n]

# Ergebnisse anzeigen
def zeige_besten_auswahl(best_kombinationen):
    for index, (skills, frische, zeit, combo) in enumerate(best_kombinationen):
        st.markdown(f"### Kombination {index + 1}")
        with st.expander("Einheiten anzeigen"):
            for unit in combo:
                st.write(f"- {unit['name']}")

        st.write("**Skillpunkte gesamt:**")
        for skill, value in skills.items():
            st.write(f"- {skill}: {value}")

        st.write(f"**Frischeverbrauch:** {frische}")
        st.write(f"**Zeitaufwand:** {zeit} Stunden")
        st.markdown("---")

# Haupt-App
def main():
    st.title("⚽ Trainingsplaner")

    einheiten = lade_einheiten()

    # Eingaben
    restfrische = st.slider("Verbleibende Frische", 0, MAX_FRISCHE, 100)
    verfuegbare_zeit = st.number_input("Verfügbare Stunden", min_value=1, value=5)
    top_n = st.number_input("Top N Kombinationen", min_value=1, max_value=10, value=5)

    if st.button("Beste Kombinationen berechnen"):
        kombis = berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n)
        zeige_besten_auswahl(kombis)

    # Tabelle in Expander anzeigen
    with st.expander("📋 Verfügbare Einheiten anzeigen"):
        df = pd.DataFrame(einheiten)
        st.dataframe(df)

# Start
if __name__ == "__main__":
    main()
