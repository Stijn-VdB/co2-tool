import streamlit as st
import pandas as pd
import altair as alt

# --- PAGE CONFIG ---
st.set_page_config(page_title="CO₂-uitstoot Berekening", page_icon="🚗", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stButton button {
        background-color: #2E86C1;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1em;
        font-size: 16px;
        border: none;
    }
    .stButton button:hover {
        background-color: #1F618D;
    }
    .stDataFrame, .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    .main {
        background-color: #F8F9FA;
    }
    h1, h2, h3 {
        color: #1C2833;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422056.png", width=80)
    st.title("⚙️ Instellingen")
    st.info("Upload je eigen Excel-bestand of gebruik de standaard data.")
    uploaded_file = st.file_uploader("Upload Excel bestand", type=["xlsx"])

# --- LOAD DATA ---
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Blad1")
else:
    df = pd.read_excel("Tool.xlsx", sheet_name="Blad1")

df.columns = df.columns.str.strip()

# --- HEADER ---
st.title("🌍 CO₂-Tracker")
st.markdown("Bereken eenvoudig de CO₂-uitstoot van jouw ritten. Vul de gegevens in en bekijk direct het resultaat.")

# --- SESSION STATE ---
if "resultaten" not in st.session_state:
    st.session_state["resultaten"] = []

# --- INPUT FORM ---
with st.container():
    st.subheader("✏️ Voer je gegevens in")
    col1, col2, col3 = st.columns(3)
    with col1:
        naam = st.text_input("👤 Naam")
    with col2:
        wagen = st.selectbox("🚘 Wagentype", df["Type activiteit"].unique())
    with col3:
        km = st.number_input("📏 Aantal kilometers", min_value=0, step=1)

    st.write("")  # space
    if st.button("➕ Toevoegen"):
        if naam and km > 0:
            row = df[df["Type activiteit"] == wagen].iloc[0]
            verbruik = row["Verbruik (liter of kWh / 100km)"]
            ef = row["EF (kg CO2/eenheid)"]
            co2 = ef * (verbruik / 100) * km

            st.session_state["resultaten"].append({
                "Naam": naam,
                "Wagen": wagen,
                "Kilometers": km,
                "CO2 (kg)": round(co2, 2)
            })
        else:
            st.warning("⚠️ Vul alle velden correct in.")

# --- RESULTS ---
if st.session_state["resultaten"]:
    resultaten_df = pd.DataFrame(st.session_state["resultaten"])

    st.subheader("📊 Resultaten")
    st.dataframe(resultaten_df, use_container_width=True)

    totaal = resultaten_df["CO2 (kg)"].sum()

    col4, col5 = st.columns(2)
    with col4:
        st.metric("Totale CO₂-uitstoot", f"{totaal:.2f} kg")
    with col5:
        gemiddelde = resultaten_df["CO2 (kg)"].mean()
        st.metric("Gemiddelde per rit", f"{gemiddelde:.2f} kg")

    # --- CHART ---
    if not resultaten_df.empty:
    # Aggregate CO₂ per wagen type
        pie_data = resultaten_df.groupby("Wagen", as_index=False)["CO2 (kg)"].sum()
        pie_data = pie_data.rename(columns={"CO2 (kg)": "CO2_kg"})
        pie_data["Percentage"] = (pie_data["CO2_kg"] / pie_data["CO2_kg"].sum()) * 100

    # Create pie chart
        pie_chart = alt.Chart(pie_data).mark_arc().encode(
            theta="CO2_kg:Q",
            color="Wagen:N",
            tooltip=["Wagen", alt.Tooltip("CO2_kg:Q", format=".2f"), alt.Tooltip("Percentage:Q", format=".1f")]
        ).properties(title="CO₂-verdeling per Wagentype")

        st.subheader("🥧 CO₂-verdeling per wagentype")
        st.altair_chart(pie_chart, use_container_width=True)

    else:
        st.info("🚘 Voeg een rit toe om resultaten te zien.")














