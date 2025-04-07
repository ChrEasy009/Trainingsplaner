import streamlit as st
import itertools

MAX_FRISCHE = 100

default_einheiten = [
    {"name": "Langhanteln", "dauer": 3, "frischeverbrauch": 60, "skillpunkte": 180},
    {"name": "Slalomdribbling", "dauer": 3, "frischeverbrauch": 30, "skillpunkte": 102},
    {"name": "Medizinball", "dauer": 3, "frischeverbrauch": 50, "skillpunkte": 126},
    {"name": "Joggen mit Ball", "dauer": 1, "frischeverbrauch": 20, "skillpunkte": 34},
    {"name": "Passen", "dauer": 1, "frischeverbrauch": 15, "skillpunkte": 36},
    {"name": "Jonglieren", "dauer": 1, "frischeverbrauch": 10, "skillpunkte": 24},
    {"name": "Torwand", "dauer": 2, "frischeverbrauch": 25, "skillpunkte": 76},
    {"name": "Auslaufen", "dauer": 1, "frischeverbrauch": 0, "skillpunkte": 0}  # Auslaufen als separate Einheit
]

if "einheiten" not in st.session_state:
    st.session_state.einheiten = default_einheiten.copy()

def berechne_best_kombinationen(einheiten, max_frische, verfuegbare_zeit, top_n=10):
    best_combinations = []
    for n in range(1, len(einheiten) + 1):
        for combo in itertools.product(einheiten, repeat=n):  # Erlaubt mehrfache Verwendung
            dauer = sum(e["dauer"] for e in combo)
            frische = sum(e["frischeverbrauch"] for e in combo)
            punkte = sum(e["skillpunkte"] for e in combo)
            if dauer <= verfuegbare_zeit and frische <= max_frische:
                best_combinations.append((combo, punkte, dauer, frische))
    best_combinations.sort(key=lambda x: x[1], reverse=True)
    return best_combinations[:top_n]

def auslaufen(frische, max_frische, auslauf_zeit):
    # Auslaufen Einheiten hinzufügen, um die Frische zu regenerieren
    while frische < max_frische and auslauf_zeit > 0:
        frische += 13
        if frische > max_frische:
            frische = max_frische
        auslauf_zeit -= 1
    return frische, auslauf_zeit

def main():
    st.title("⚽ Trainingsplan-Optimierer")
    
    with st.expander("➕ Einheit hinzufügen"):
        name = st.text_input("Name der Einheit")
        dauer = st.number_input("Dauer (h)", min_value=1, max_value=12, value=1)
        frische = st.number_input("Frischeverbrauch", min_value=1, max_value=100, value=10)
        punkte = st.number_input("Skillpunkte", min_value=1, value=10)
        if st.button("Hinzufügen"):
            if name:
                st.session_state.einheiten.append({
                    "name": name,
                    "dauer": dauer,
                    "frischeverbrauch": frische,
                    "skillpunkte": punkte
                })
                st.success(f"Einheit '{name}' hinzugefügt.")

    with st.expander("🗑️ Einheiten löschen"):
        to_delete = st.multiselect("Wähle Einheiten zum Löschen", [e["name"] for e in st.session_state.einheiten])
        if st.button("Ausgewählte Einheiten löschen"):
            st.session_state.einheiten = [e for e in st.session_state.einheiten if e["name"] not in to_delete]
            st.success("Ausgewählte Einheiten wurden gelöscht.")

    st.subheader("🔢 Parameter wählen")
    restfrische = st.slider("Restfrische (0–100)", 0, 100, 80)
    verfuegbare_zeit = st.slider("Verfügbare Zeit (in Stunden)", 1, 24, 10)
    auslauf_zeit = st.number_input("Stunden für Auslaufen (1h = +13 Frische)", min_value=0, max_value=verfuegbare_zeit, value=0)

    # Berechne die Frische nach Auslaufen
    if auslauf_zeit > 0:
        restfrische, _ = auslaufen(restfrische, MAX_FRISCHE, auslauf_zeit)

    if st.button("🔍 Beste Kombinationen berechnen"):
        ergebnisse = berechne_best_kombinationen(st.session_state.einheiten, restfrische, verfuegbare_zeit - auslauf_zeit, top_n=10)
        if not ergebnisse:
            st.warning("Keine gültigen Kombinationen gefunden.")
        else:
            st.subheader("🏆 Top 10 Kombinationen")
            for idx, (combo, punkte, dauer, frische) in enumerate(ergebnisse):
                namen = ", ".join(e["name"] for e in combo)
                st.markdown(f"**{idx+1}. {namen}**  \nSkillpunkte: {punkte} | Dauer: {dauer}h | Frischeverbrauch: {frische}")

if __name__ == "__main__":
    main()
