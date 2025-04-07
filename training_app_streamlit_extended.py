import streamlit as st
import pandas as pd
import itertools
from collections import Counter

MAX_FRISCHE = 100

# Standard-Trainingseinheiten, Auslaufen hat nun -13 Frischeverbrauch
default_einheiten = [
    {"name": "Langhanteln II", "dauer": 3, "frischeverbrauch": 60, "skillpunkte": 180, "kondition": 0, "kraft": 120, "schnelligkeit": 0, "passen": 0, "technik": 30},
    {"name": "Slalomdribbling II", "dauer": 3, "frischeverbrauch": 30, "skillpunkte": 102, "kondition": 30, "kraft": 0, "schnelligkeit": 15, "passen": 0, "technik": 40},
    {"name": "Medizinball II", "dauer": 3, "frischeverbrauch": 50, "skillpunkte": 126, "kondition": 40, "kraft": 65, "schnelligkeit": 0, "passen": 0, "technik": 0},
    {"name": "Joggen m. Ball", "dauer": 1, "frischeverbrauch": 20, "skillpunkte": 34, "kondition": 17, "kraft": 0, "schnelligkeit": 0, "passen": 12, "technik": 0},
    {"name": "Passen", "dauer": 1, "frischeverbrauch": 15, "skillpunkte": 36, "kondition": 0, "kraft": 0, "schnelligkeit": 0, "passen": 30, "technik": 0},
    {"name": "Jonglieren", "dauer": 1, "frischeverbrauch": 10, "skillpunkte": 24, "kondition": 0, "kraft": 0, "schnelligkeit": 0, "passen": 0, "technik": 20},
    {"name": "Torwand II", "dauer": 2, "frischeverbrauch": 25, "skillpunkte": 76, "kondition": 0, "kraft": 33, "schnelligkeit": 0, "passen": 0, "technik": 30},
    {"name": "Auslaufen", "dauer": 1, "frischeverbrauch": -13, "skillpunkte": 0, "kondition": 0, "kraft": 0, "schnelligkeit": 0, "passen": 0, "technik": 0}  # Auslaufen mit -13 Frischeverbrauch
]

# Speichern der Einheiten im Streamlit-Speicher
if "einheiten" not in st.session_state:
    st.session_state.einheiten = default_einheiten.copy()

def berechne_best_kombinationen(einheiten, max_frische, verfuegbare_zeit, top_n=10):
    best_combinations = []
    
    # Wir testen nun nur Kombinationen mit Wiederholungen, keine Permutationen
    for n in range(1, len(einheiten) + 1):  # Von 1 bis zu allen Einheiten
        for combo in itertools.combinations_with_replacement(einheiten, n):  # Kombinationen mit Wiederholungen
            dauer = sum(e["dauer"] for e in combo)
            frische = sum(e["frischeverbrauch"] for e in combo)
            punkte = sum(e["skillpunkte"] for e in combo)
            
            # Summiere die einzelnen Skills
            kondition = sum(e["kondition"] for e in combo)
            kraft = sum(e["kraft"] for e in combo)
            schnelligkeit = sum(e["schnelligkeit"] for e in combo)
            passen = sum(e["passen"] for e in combo)
            technik = sum(e["technik"] for e in combo)
            
            # Nur gültige Kombinationen, die in der verfügbaren Zeit und Frische liegen
            if dauer <= verfuegbare_zeit and frische <= max_frische:
                # Zähle die Einheiten
                combo_counter = Counter([e["name"] for e in combo])
                best_combinations.append((combo_counter, punkte, dauer, frische, kondition, kraft, schnelligkeit, passen, technik))
    
    # Sortieren nach den Skillpunkten
    best_combinations.sort(key=lambda x: x[1], reverse=True)
    
    # Nur die besten `top_n` Kombinationen zurückgeben
    return best_combinations[:top_n]

def main():
    st.title("⚽ Trainingsplan-Optimierer")

    st.subheader("🔢 Parameter wählen")
    restfrische = st.slider("Restfrische (0–100)", 0, 100, 80)
    verfuegbare_zeit = st.slider("Verfügbare Zeit (in Stunden)", 1, 24, 10)

    if st.button("🔍 Beste Kombinationen berechnen"):
        # Berechne Kombinationen mit Auslaufen, welches eine negative Frische verbraucht
        ergebnisse = berechne_best_kombinationen(st.session_state.einheiten, restfrische, verfuegbare_zeit, top_n=10)
        
        if not ergebnisse:
            st.warning("Keine gültigen Kombinationen gefunden.")
        else:
            st.subheader("🏆 Top 10 Kombinationen")
            for idx, (combo_counter, punkte, dauer, frische, kondition, kraft, schnelligkeit, passen, technik) in enumerate(ergebnisse):
                # Anzeige der Kombination ohne Reihenfolge, aber mit Zählung der Einheiten
                combo_str = ", ".join([f"{count}x {name}" for name, count in combo_counter.items()])
                st.markdown(f"**{idx+1}. {combo_str}**  \nSkillpunkte: {punkte} | Dauer: {dauer}h | Frischeverbrauch: {frische}")
                # Hier fügen wir die Anzeige der Einzelskills hinzu
                st.markdown(f"Kondition: {kondition} | Kraft: {kraft} | Schnelligkeit: {schnelligkeit} | Passen: {passen} | Technik: {technik}")

if __name__ == "__main__":
    main()
