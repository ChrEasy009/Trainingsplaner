import streamlit as st
import pandas as pd
import json
from collections import Counter
import itertools

# Konstanten
MAX_FRISCHE = 100
EINHEITEN_DATEI = "einheiten.json"  # Die JSON-Datei mit den Einheiten

# Einheiten aus der JSON-Datei laden
def lade_einheiten():
    with open(EINHEITEN_DATEI, 'r') as f:
        einheiten = json.load(f)
    return einheiten

# Berechnung der besten Kombinationen
def berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n=10):
    valid_combinations = []
    
    # Alle Kombinationen erstellen
    for n in range(1, len(einheiten) + 1):
        for combo in itertools.combinations_with_replacement(einheiten, n):  # Kombinationen mit Wiederholungen
            gesamtfrische = sum(unit['frischeverbrauch'] for unit in combo)
            gesamtzeit = sum(unit['dauer'] for unit in combo)  # Die Dauer jeder Einheit wird nun berücksichtigt

            # Überprüfen, ob der Gesamtfrischeverbrauch und die Gesamtzeit innerhalb der erlaubten Grenzen liegen
            if gesamtfrische <= restfrische and gesamtzeit <= verfuegbare_zeit:
                gesamt_skills = Counter()
                for unit in combo:
                    gesamt_skills.update(unit['skills'])
                valid_combinations.append((gesamt_skills, gesamtfrische, gesamtzeit, combo))

    # Top-N besten Kombinationen nach Gesamt-Skills (Sortierung nach höchster Skill-Punkte-Summe)
    valid_combinations.sort(key=lambda x: sum(x[0].values()), reverse=True)

    return valid_combinations[:top_n]

# Funktion zur Ausgabe der besten Kombinationen
def zeige_besten_auswahl(best_kombinationen):
    for index, (skills, frische, zeit, combo) in enumerate(best_kombinationen):
        st.write(f"Kombination {index + 1}:")
        st.write("Einheiten:")
        for unit in combo:
            st.write(f"- {unit['name']}")
        st.write("Skills:")
        for skill, value in skills.items():
            st.write(f"  {skill}: {value}")
        st.write(f"Gesamt Frischeverbrauch: {frische}")
        st.write(f"Gesamt Zeitaufwand: {zeit} Stunden")
        st.write("")

# Streamlit-App
def main():
    # Lade die Einheiten
    einheiten = lade_einheiten()
    
    # Benutzeroberfläche für die Eingabe
    st.title("Trainingsplaner")

    restfrische = st.slider("Verbleibende Frische", 0, MAX_FRISCHE, 100)
    verfuegbare_zeit = st.number_input("Verfügbare Stunden für Training", min_value=1, value=6)
    top_n = st.number_input("Top N besten Kombinationen anzeigen", min_value=1, max_value=10, value=5)

    # Auswahl der verfügbaren Einheiten (Checkboxes oder Dropdown)
    st.subheader("Wähle deine verfügbaren Einheiten aus:")
    einheiten_names = [unit['name'] for unit in einheiten]
    ausgewaehlte_einheiten_namen = st.multiselect(
        "Verfügbare Einheiten", einheiten_names, default=einheiten_names[:3]  # Optional: Standardmäßig die ersten 3 Einheiten
    )
    
    # Filtere die ausgewählten Einheiten
    ausgewaehlte_einheiten = [unit for unit in einheiten if unit['name'] in ausgewaehlte_einheiten_namen]

    # Berechnung der besten Kombinationen
    if st.button("Berechne beste Kombinationen"):
        best_kombinationen = berechne_best_kombinationen(ausgewaehlte_einheiten, restfrische, verfuegbare_zeit, top_n)
        zeige_besten_auswahl(best_kombinationen)

    # Tabelle mit den verfügbaren Einheiten anzeigen
    df = pd.DataFrame(einheiten)
    st.write("Verfügbare Einheiten:", df)

# Main-App ausführen
if __name__ == "__main__":
    main()
