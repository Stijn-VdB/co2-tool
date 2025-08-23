import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="CO₂-uitstoot Berekening", page_icon="🚗", layout="wide")

# --- Load Data ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422056.png", width=80)
    st.title("⚙️ Instellingen")
    st.info("Upload je eigen Excel-bestand of gebruik de standaard data.")
    uploaded_file = st.file_uploader("Upload Excel bestand", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Blad1")
else:
    df = pd.read_excel("Tool.xlsx", sheet_name="Blad1")

df.columns = df.columns.str.strip()

# Store data in session state for editing
if "data" not in st.session_state:
    st.session_state["data"] = df.copy()

# --- Tabs ---
tab1, tab2 = st.tabs(["📐 Berekening", "📂 Data"])

with tab2:
    st.subheader("📂 Data uit Excel (Bewerkbaar)")
    edited_df = st.data_editor(st.session_state["data"], num_rows="dynamic", use_container_width=True)
    st.session_state["data"] = edited_df  # Save edits

with tab1:
    st.title("🌍 CO₂-Tracker")
    st.markdown("Bereken eenvoudig de CO₂-uitstoot van jouw ritten.")

    if "resultaten" not in st.session_state:
        st.session_state["resultaten"] = []

    # Use the edited data for calculations
    current_df = st.session_state["data"]

    # --- Input ---
    col1, col2, col3 = st.columns(3)
    with col1:
        naam = st.text_input("👤 Naam")
    with col2:
        wagen = st.selectbox("🚘 Wagentype", current_df["Type activiteit"].unique())
    with col3:
        km = st.number_input("📏 Aantal kilometers", min_value=0, step=1)

    if st.button("➕ Toevoegen"):
        if naam and km > 0:
            row = current_df[current_df["Type activiteit"] == wagen].iloc[0]
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

        # --- PIE CHART ---
        if not resultaten_df.empty:
            pie_data = resultaten_df.groupby("Wagen", as_index=False)["CO2 (kg)"].sum()
            pie_data = pie_data.rename(columns={"CO2 (kg)": "CO2_kg"})
            pie_data["Percentage"] = (pie_data["CO2_kg"] / pie_data["CO2_kg"].sum()) * 100

            pie_chart = alt.Chart(pie_data).mark_arc().encode(
                theta="CO2_kg:Q",
                color="Wagen:N",
                tooltip=[
                    "Wagen",
                    alt.Tooltip("CO2_kg:Q", format=".2f"),
                    alt.Tooltip("Percentage:Q", format=".1f")
                ]
            ).properties(title="CO₂-verdeling per Wagentype")

            st.subheader("🥧 CO₂-verdeling per wagentype")
            st.altair_chart(pie_chart, use_container_width=True)
    else:
        st.info("🚘 Voeg een rit toe om resultaten te zien.")

















