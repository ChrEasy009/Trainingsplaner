import streamlit as st
import pandas as pd
import itertools
from collections import Counter

MAX_FRISCHE = 100

# Standard-Trainingseinheiten
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

    # Einheiten als Tabelle anzeigen und bearbeiten
    st.subheader("📝 Einheiten bearbeiten und hinzufügen")

    # Zeige die Einheiten als interaktive Tabelle
    df = pd.DataFrame(st.session_state.einheiten)

    # Einheiten anzeigen
    st.write("Aktuelle Einheiten:")
    st.dataframe(df)

    # Einheiten bearbeiten:
    st.subheader("🖋️ Einheit bearbeiten")
    edit_name = st.selectbox("Wähle eine Einheit zum Bearbeiten:", df["name"].tolist())

    # Details der gewählten Einheit anzeigen und ändern
    selected_unit = next(e for e in st.session_state.einheiten if e["name"] == edit_name)

    new_dauer = st.number_input(f"Neue Dauer (h) für {edit_name}", min_value=1, max_value=12, value=selected_unit["dauer"])
    new_frische = st.number_input(f"Neuer Frischeverbrauch für {edit_name}", min_value=1, max_value=100, value=selected_unit["frischeverbrauch"])
    new_skillpunkte = st.number_input(f"Neue Skillpunkte für {edit_name}", min_value=1, value=selected_unit["skillpunkte"])

    if st.button("Einheit bearbeiten"):
        # Einheit in der Liste aktualisieren
        selected_unit["dauer"] = new_dauer
        selected_unit["frischeverbrauch"] = new_frische
        selected_unit["skillpunkte"] = new_skillpunkte
        st.session_state.einheiten = [selected_unit if e["name"] == edit_name else e for e in st.session_state.einheiten]
        st.success(f"Einheit '{edit_name}' wurde erfolgreich geändert.")

    # Hinzufügen neuer Einheiten:
    st.subheader("➕ Neue Einheit hinzufügen")
    new_name = st.text_input("Name der neuen Einheit")
    new_dauer = st.number_input("Dauer (h)", min_value=1, max_value=12, value=1)
    new_frische = st.number_input("Frischeverbrauch", min_value=1, max_value=100, value=10)
    new_skillpunkte = st.number_input("Skillpunkte", min_value=1, value=10)

    if st.button("Neue Einheit hinzufügen"):
        if new_name:
            st.session_state.einheiten.append({
                "name": new_name,
                "dauer": new_dauer,
                "frischeverbrauch": new_frische,
                "skillpunkte": new_skillpunkte
            })
            st.success(f"Neue Einheit '{new_name}' hinzugefügt.")
    
    # Löschen von Einheiten:
    st.subheader("❌ Einheit löschen")
    delete_name = st.selectbox("Wähle eine Einheit zum Löschen:", df["name"].tolist())

    if st.button("Einheit löschen"):
        st.session_state.einheiten = [e for e in st.session_state.einheiten if e["name"] != delete_name]
        st.success(f"Einheit '{delete_name}' wurde gelöscht.")

    # Berechnungsoptionen
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
            for idx, (combo_counter, punkte, dauer, frische) in enumerate(ergebnisse):
                # Anzeige der Kombination ohne Reihenfolge, aber mit Zählung der Einheiten
                combo_str = ", ".join([f"{count}x {name}" for name, count in combo_counter.items()])
                st.markdown(f"**{idx+1}. {combo_str}**  \nSkillpunkte: {punkte} | Dauer: {dauer}h | Frischeverbrauch: {frische}")

if __name__ == "__main__":
    main()
