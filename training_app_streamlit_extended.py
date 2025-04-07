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
    # Sicherstellen, dass jede Einheit den Schlüssel 'skills' hat
    for unit in einheiten:
        if 'skills' not in unit:
            unit['skills'] = {}  # Leeres Dictionary, falls 'skills' nicht vorhanden ist
    return einheiten

# Berechnung der besten Kombinationen
def berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n=10):
    valid_combinations = []
    
    # Alle Kombinationen erstellen
    for n in range(1, len(einheiten) + 1):
        for combo in itertools.combinations_with_replacement(einheiten, n):  # Kombinationen mit Wiederholungen
            gesamtfrische = sum(unit['frischeverbrauch'] for unit in combo)
            gesamtzeit = len(combo)  # Annahme: Jede Einheit dauert 1 Stunde
            
            # Überprüfen, ob der Gesamtfrischeverbrauch innerhalb der erlaubten Grenze liegt
            if gesamtfrische <= restfrische and gesamtzeit <= verfuegbare_zeit:
                gesamt_skills = Counter()
                for unit in combo:
                    gesamt_skills.update(unit['skills'])
                valid_combinations.append((gesamt_skills, gesamtfrische, gesamtzeit, combo))

    # Wenn keine gültige Kombination gefunden wurde, eine Standardkombination (z.B. Jonglieren) zurückgeben
    if not valid_combinations:
        st.warning("Keine gültige Kombination gefunden! Es wird 'Jonglieren' empfohlen.")
        valid_combinations = [(
            Counter({"Technik": 20}),
            10,  # Frischeverbrauch von Jonglieren
            1,  # Zeit für Jonglieren
            [{"name": "Jonglieren", "dauer": 1, "frischeverbrauch": 10, "skillpunkte": 24, "kondition": 0, "kraft": 0, "schnelligkeit": 0, "passen": 0, "technik": 20}]
        )]

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

    restfrische = st.slider("Verbleibende Frische", 0, MAX_FRISCHE, 10)
    verfuegbare_zeit = st.number_input("Verfügbare Stunden für Training", min_value=1, value=1)
    top_n = st.number_input("Top N besten Kombinationen anzeigen", min_value=1, max_value=10, value=5)

    # Multi-Select für Einheiten
    available_units = [unit['name'] for unit in einheiten]
    selected_units = st.multiselect("Wähle Einheiten für die Optimierung", available_units, default=[
        "Langhanteln II", "Auslaufen", "Slalomdribbling II", "Joggen m. Ball", "Passen", "Medizinball II", "Jonglieren"
    ])

    # Filtere die Einheiten basierend auf den ausgewählten Einheiten
    filtered_einheiten = [unit for unit in einheiten if unit['name'] in selected_units]

    # Berechnung der besten Kombinationen
    if st.button("Berechne beste Kombinationen"):
        best_kombinationen = berechne_best_kombinationen(filtered_einheiten, restfrische, verfuegbare_zeit, top_n)
        zeige_besten_auswahl(best_kombinationen)

    # Tabelle mit den verfügbaren Einheiten anzeigen
    with st.expander("Verfügbare Einheiten"):
        df = pd.DataFrame(einheiten)
        st.write(df)

# Main-App ausführen
if __name__ == "__main__":
    main()
