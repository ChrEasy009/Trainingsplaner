import streamlit as st
import pandas as pd
import itertools
from collections import Counter
import json

MAX_FRISCHE = 100

# Standard-Trainingseinheiten, Auslaufen hat nun -13 Frischeverbrauch
default_einheiten = [
    {"name": "Langhanteln", "dauer": 3, "frischeverbrauch": 60, "skillpunkte": 180},
    {"name": "Slalomdribbling", "dauer": 3, "frischeverbrauch": 30, "skillpunkte": 102},
    {"name": "Medizinball", "dauer": 3, "frischeverbrauch": 50, "skillpunkte": 126},
    {"name": "Joggen mit Ball", "dauer": 1, "frischeverbrauch": 20, "skillpunkte": 34},
    {"name": "Passen", "dauer": 1, "frischeverbrauch": 15, "skillpunkte": 36},
    {"name": "Jonglieren", "dauer": 1, "frischeverbrauch": 10, "skillpunkte": 24},
    {"name": "Torwand", "dauer": 2, "frischeverbrauch": 25, "skillpunkte": 76},
    {"name": "Auslaufen", "dauer": 1, "frischeverbrauch": -13, "skillpunkte": 0}  # Auslaufen mit -13 Frischeverbrauch
]

# Funktion zum Laden der Einheiten aus einer JSON-Datei
def lade_einheiten_von_datei(dateiname="einheiten.json"):
    try:
        with open(dateiname, "r", encoding="utf-8") as f:
            einheiten = json.load(f)
        return einheiten
    except FileNotFoundError:
        st.error(f"Die Datei {dateiname} wurde nicht gefunden.")
        return []
    except json.JSONDecodeError:
        st.error(f"Die Datei {dateiname} ist nicht korrekt formatiert.")
        return []

# Wenn die Einheiten noch nicht im session_state sind, lade sie aus der JSON-Datei oder verwende die Standard-Einheiten
if "einheiten" not in st.session_state:
    st.session_state.einheiten = lade_einheiten_von_datei() or default_einheiten

# Standardmäßig ausgewählte Einheiten (basierend auf den zuletzt erwähnten)
default_selected_einheiten = ["Joggen mit Ball", "Langhanteln", "Slalomdribbling", "Passen", "Medizinball"]

def berechne_best_kombinationen(einheiten, max_frische, verfuegbare_zeit, top_n=10):
    best_combinations = []
    
    # Wir testen nun nur Kombinationen mit Wiederholungen, keine Permutationen
    for n in range(1, len(einheiten) + 1):  # Von 1 bis zu allen Einheiten
        for combo in itertools.combinations_with_replacement(einheiten, n):  # Kombinationen mit Wiederholungen
            dauer = sum(e["dauer"] for e in combo)
            frische = sum(e["frischeverbrauch"] for e in combo)
            punkte = sum(e["skillpunkte"] for e in combo)
            
            # Nur gültige Kombinationen, die in der verfügbaren Zeit und Frische liegen
            if dauer <= verfuegbare_zeit and frische <= max_frische:
                # Zähle die Einheiten
                combo_counter = Counter([e["name"] for e in combo])
                best_combinations.append((combo_counter, punkte, dauer, frische))
    
    # Sortieren nach den Skillpunkten
    best_combinations.sort(key=lambda x: x[1], reverse=True)
    
    # Nur die besten `top_n` Kombinationen zurückgeben
    return best_combinations[:top_n]

def main():
    st.title("⚽ Trainingsplan-Optimierer")

    # Zeige die Einheiten als Tabelle
    df = pd.DataFrame(st.session_state.einheiten)
    
    # Einheiten Tabelle im Dropdown/Expander anzeigen
    st.subheader("📝 Verfügbare Einheiten")
    with st.expander("Einheiten anzeigen"):
        st.dataframe(df)

    # Einheiten-Auswahl für das Training
    st.subheader("🔢 Wähle Einheiten für das Training aus")
    available_unit_names = [unit["name"] for unit in st.session_state.einheiten]
    
    # Auswahl mit Standardauswahl der zuletzt genannten Einheiten
    selected_units = st.multiselect(
        "Wähle die Einheiten, die für die Optimierung berücksichtigt werden sollen:",
        available_unit_names,
        default=default_selected_einheiten  # Standardmäßig ausgewählte Einheiten
    )

    # Filtere die ausgewählten Einheiten aus
    selected_einheiten = [unit for unit in st.session_state.einheiten if unit["name"] in selected_units]

    st.subheader("🔢 Parameter wählen")
    restfrische = st.slider("Restfrische (0–100)", 0, 100, 80)
    verfuegbare_zeit = st.slider("Verfügbare Zeit (in Stunden)", 1, 24, 10)

    if st.button("🔍 Beste Kombinationen berechnen"):
        # Berechne Kombinationen mit den ausgewählten Einheiten
        ergebnisse = berechne_best_kombinationen(selected_einheiten, restfrische, verfuegbare_zeit, top_n=5)
        
        if not ergebnisse:
            st.warning("Keine gültigen Kombinationen gefunden.")
        else:
            st.subheader("🏆 Top 5 Kombinationen")
            for idx, (combo_counter, punkte, dauer, frische) in enumerate(ergebnisse):
                # Anzeige der Kombination ohne Reihenfolge, aber mit Zählung der Einheiten
                combo_str = ", ".join([f"{count}x {name}" for name, count in combo_counter.items()])
                st.markdown(f"**{idx+1}. {combo_str}**  \nSkillpunkte: {punkte} | Dauer: {dauer}h | Frischeverbrauch: {frische}")

if __name__ == "__main__":
    main()
