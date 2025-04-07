import streamlit as st
import pandas as pd
import json
from collections import Counter
from itertools import product

# Konstante
MAX_FRISCHE = 100
MAX_MENGE_PRO_EINHEIT = 10
EINHEITEN_DATEI = "einheiten.json"

# Einheiten laden & Skills vereinheitlichen
def lade_einheiten():
    with open(EINHEITEN_DATEI, 'r') as f:
        daten = json.load(f)
    for einheit in daten:
        einheit["skills"] = {
            "Kondition": einheit.get("kondition", 0),
            "Kraft": einheit.get("kraft", 0),
            "Schnelligkeit": einheit.get("schnelligkeit", 0),
            "Passen": einheit.get("passen", 0),
            "Technik": einheit.get("technik", 0)
        }
    return daten

# Berechnung der besten Kombinationen mit Mengenbegrenzung
def berechne_best_kombinationen(einheiten, restfrische, verfuegbare_zeit, top_n):
    valid_combinations = []

    # Erzeuge alle möglichen Mengen (0 bis MAX) für jede Einheit
    menge_optionen = [range(0, MAX_MENGE_PRO_EINHEIT + 1) for _ in einheiten]
    for mengen_kombi in product(*menge_optionen):
        if sum(mengen_kombi) == 0:
            continue

        total_frische = 0
        total_zeit = 0
        total_skills = Counter()
        kombi = []

        for einheit, anzahl in zip(einheiten, mengen_kombi):
            if anzahl > 0:
                total_frische += einheit["frischeverbrauch"] * anzahl
                total_zeit += einheit["dauer"] * anzahl

                for skill, val in einheit["skills"].items():
                    total_skills[skill] += val * anzahl

                kombi.extend([einheit] * anzahl)

        if total_frische <= restfrische and total_zeit <= verfuegbare_zeit:
            valid_combinations.append((total_skills, total_frische, total_zeit, kombi))

    # Nach Summe der Skills sortieren
    valid_combinations.sort(key=lambda x: sum(x[0].values()), reverse=True)
    return valid_combinations[:top_n]

# Darstellung der besten Kombinationen
def zeige_besten_auswahl(best_kombinationen):
    for index, (skills, frische, zeit, combo) in enumerate(best_kombinationen):
        st.markdown(f"### Kombination {index + 1}")
        einheits_counter = Counter([e["name"] for e in combo])
        st.write("Einheiten:")
        for name, count in einheits_counter.items():
            st.write(f"- {name} × {count}")
        st.write("Skills:")
        for skill, value in skills.items():
            st.write(f"  - {skill}: {value}")
        st.write(f"**Frischeverbrauch:** {frische}")
        st.write(f"**Zeitaufwand:** {zeit} Stunden")
        st.markdown("---")

# Hauptanwendung
def main():
    einheiten = lade_einheiten()

    st.title("⚽ Trainingsplan Optimierer")

    st.sidebar.header("🔧 Parameter")
    restfrische = st.sidebar.slider("Verfügbare Frische", 0, MAX_FRISCHE, 100)
    verfuegbare_zeit = st.sidebar.number_input("Verfügbare Trainingszeit [Stunden]", min_value=1, value=5)
    top_n = st.sidebar.slider("Top Kombinationen anzeigen", 1, 10, 5)

    # Standardmäßig vorab ausgewählte Einheiten
    standard_auswahl = [
        "Langhanteln II", "Auslaufen", "Slalomdribbling II", 
        "Joggen m. Ball", "Passen", "Medizinball II", "Jonglieren"
    ]
    
    st.subheader("Einheitenauswahl")
    ausgewaehlt_namen = st.multiselect(
        "Welche Einheiten sollen berücksichtigt werden?",
        options=[e["name"] for e in einheiten],
        default=standard_auswahl
    )
    gefilterte_einheiten = [e for e in einheiten if e["name"] in ausgewaehlt_namen]

    if st.button("💡 Beste Kombination berechnen"):
        if not gefilterte_einheiten:
            st.warning("Bitte mindestens eine Einheit auswählen.")
        else:
            with st.spinner("Berechne optimale Kombinationen..."):
                beste = berechne_best_kombinationen(gefilterte_einheiten, restfrische, verfuegbare_zeit, top_n)
            if beste:
                zeige_besten_auswahl(beste)
            else:
                st.info("Keine gültige Kombination gefunden.")

    with st.expander("📋 Alle verfügbaren Einheiten anzeigen"):
        df = pd.DataFrame(einheiten).drop(columns=["skills"])
        st.dataframe(df)

# Run
if __name__ == "__main__":
    main()
