import streamlit as st
import itertools
from collections import Counter
import json
import os

MAX_FRISCHE = 100

# Einheiten laden aus einheiten.json
@st.cache_data
def lade_einheiten():
    with open("einheiten.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Beste Kombinationen berechnen
def berechne_best_kombinationen(einheiten, max_frische, verfuegbare_zeit, top_n=10):
    best_combinations = []

    for n in range(1, len(einheiten) + 1):
        for combo in itertools.combinations_with_replacement(einheiten, n):
            dauer = sum(e["dauer"] for e in combo)
            frische = sum(e["frischeverbrauch"] for e in combo)
            punkte = sum(e["skillpunkte"] for e in combo)

            if dauer <= verfuegbare_zeit and frische <= max_frische:
                counter = Counter([e["name"] for e in combo])
                best_combinations.append((counter, punkte, dauer, frische))

    best_combinations.sort(key=lambda x: x[1], reverse=True)
    return best_combinations[:top_n]

# UI & Hauptlogik
def main():
    st.title("⚽ Trainingsplan-Optimierer")

    einheiten = lade_einheiten()

    st.subheader("🔢 Parameter wählen")
    restfrische = st.slider("Restfrische (0–100)", 0, 100, 80)
    verfuegbare_zeit = st.slider("Verfügbare Zeit (in Stunden)", 1, 24, 10)

    if st.button("🔍 Beste Kombinationen berechnen"):
        ergebnisse = berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit)

        if not ergebnisse:
            st.warning("Keine gültigen Kombinationen gefunden.")
        else:
            st.subheader("🏆 Top 10 Kombinationen")
            for idx, (combo_counter, punkte, dauer, frische) in enumerate(ergebnisse):
                combo_str = ", ".join([f"{count}x {name}" for name, count in combo_counter.items()])
                st.markdown(f"**{idx+1}. {combo_str}**  \nSkillpunkte: {punkte} | Dauer: {dauer}h | Frischeverbrauch: {frische}")

if __name__ == "__main__":
    main()
