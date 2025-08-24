import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

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

# Initialize session state for werven and resultaten
if "werven" not in st.session_state:
    st.session_state["werven"] = []
if "resultaten" not in st.session_state:
    st.session_state["resultaten"] = []

# --- Tabs ---
tab_data, tab_werven = st.tabs(["📂 Data", "🏗️ Werven"])

# =============================
# 📂 TAB DATA
# =============================
with tab_data:
    st.subheader("📂 Data uit Excel (Bewerkbaar)")
    edited_df = st.data_editor(st.session_state["data"], num_rows="dynamic", use_container_width=True)
    st.session_state["data"] = edited_df  # Save edits

# =============================
# 🏗️ TAB WERVEN
# =============================
with tab_werven:
    st.title("🏗️ Werven Beheer")

    # --- Nieuwe werf toevoegen ---
    st.subheader("➕ Nieuwe Werf")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        werf_naam = st.text_input("Naam werf")
    with col2:
        start_datum = st.date_input("Begin datum")
    with col3:
        eind_datum = st.date_input("Eind datum")
    with col4:
        if st.button("✅ Werf toevoegen"):
            if werf_naam and start_datum <= eind_datum:
                st.session_state["werven"].append({
                    "Naam": werf_naam,
                    "Begin": start_datum,
                    "Einde": eind_datum
                })
            else:
                st.warning("⚠️ Vul een geldige naam en datumbereik in.")

    # --- Werven bewerken ---
    st.subheader("📋 Huidige Werven")
    if st.session_state["werven"]:
        werven_df = pd.DataFrame(st.session_state["werven"])
        edited_werven = st.data_editor(werven_df, num_rows="dynamic", use_container_width=True)
        st.session_state["werven"] = edited_werven.to_dict("records")
    else:
        st.info("Nog geen werven toegevoegd.")

    # --- Selecteer werf om berekeningen te doen ---
    if st.session_state["werven"]:
        st.markdown("---")
        st.subheader("📅 Selecteer Werf & Dag")
        werf_namen = [w["Naam"] for w in st.session_state["werven"]]
        selected_werf = st.selectbox("Kies een werf", werf_namen)

        werf_info = next(w for w in st.session_state["werven"] if w["Naam"] == selected_werf)
        start = werf_info["Begin"]
        einde = werf_info["Einde"]

        # Genereer datums
        dagen = pd.date_range(start=start, end=einde).strftime("%Y-%m-%d").tolist()
        selected_dag = st.selectbox("Kies een dag", dagen)

        # --- Input voor berekening (zoals origineel tab1) ---
        st.markdown("### 🌍 Berekening voor geselecteerde dag")
        current_df = st.session_state["data"]

        col1, col2, col3 = st.columns(3)
        with col1:
            naam = st.text_input("👤 Naam")
        with col2:
            wagen = st.selectbox("🚘 Wagentype", current_df["Type activiteit"].unique())
        with col3:
            km = st.number_input("📏 Aantal kilometers", min_value=0, step=1)

        if st.button("➕ Toevoegen voor deze dag"):
            if naam and km > 0:
                row = current_df[current_df["Type activiteit"] == wagen].iloc[0]
                verbruik = row["Verbruik (liter of kWh / 100km)"]
                ef = row["EF (kg CO2/eenheid)"]
                co2 = ef * (verbruik / 100) * km

                st.session_state["resultaten"].append({
                    "Werf": selected_werf,
                    "Datum": selected_dag,
                    "Naam": naam,
                    "Wagen": wagen,
                    "Kilometers": km,
                    "CO2 (kg)": round(co2, 2)
                })
            else:
                st.warning("⚠️ Vul alle velden correct in.")

        # --- Resultaten voor deze dag ---
dag_df = pd.DataFrame([r for r in st.session_state["resultaten"] if r["Werf"] == selected_werf and r["Datum"] == selected_dag])

if not dag_df.empty:
    st.subheader(f"📊 Resultaten voor {selected_dag}")
    st.dataframe(dag_df, use_container_width=True)

    totaal_dag = dag_df["CO2 (kg)"].sum()
    gemiddelde_dag = dag_df["CO2 (kg)"].mean()

    col4, col5 = st.columns(2)
    with col4:
        st.metric("Totale CO₂ (dag)", f"{totaal_dag:.2f} kg")
    with col5:
        st.metric("Gemiddelde per rit (dag)", f"{gemiddelde_dag:.2f} kg")

    # Pie chart voor geselecteerde dag
    pie_dag = dag_df.groupby("Wagen", as_index=False)["CO2 (kg)"].sum()
    pie_dag = pie_dag.rename(columns={"CO2 (kg)": "CO2_kg"})
    pie_dag["Percentage"] = (pie_dag["CO2_kg"] / pie_dag["CO2_kg"].sum()) * 100

    pie_chart_dag = alt.Chart(pie_dag).mark_arc().encode(
        theta="CO2_kg:Q",
        color="Wagen:N",
        tooltip=[
            "Wagen",
            alt.Tooltip("CO2_kg:Q", format=".2f"),
            alt.Tooltip("Percentage:Q", format=".1f")
        ]
    ).properties(title=f"🥧 CO₂-verdeling per wagentype ({selected_dag})")

    st.altair_chart(pie_chart_dag, use_container_width=True)

else:
    st.info("Geen data voor deze dag.")

# --- Totaal voor hele werf ---
werf_df = pd.DataFrame([r for r in st.session_state["resultaten"] if r["Werf"] == selected_werf])
if not werf_df.empty:
    st.subheader(f"📦 Totaal voor werf '{selected_werf}'")
    totaal_werf = werf_df["CO2 (kg)"].sum()
    gemiddelde_werf = werf_df["CO2 (kg)"].mean()

    col6, col7 = st.columns(2)
    with col6:
        st.metric("Totale CO₂ (werf)", f"{totaal_werf:.2f} kg")
    with col7:
        st.metric("Gemiddelde per rit (werf)", f"{gemiddelde_werf:.2f} kg")

    # Staafgrafiek per dag (Datum als text, niet per uur)
    grafiek_df = werf_df.groupby("Datum", as_index=False)["CO2 (kg)"].sum()
    grafiek_df["Datum"] = pd.to_datetime(grafiek_df["Datum"])  # sorteerbaar
    grafiek_df = grafiek_df.sort_values("Datum")
    grafiek_df["Datum"] = grafiek_df["Datum"].dt.strftime("%Y-%m-%d")

    chart = alt.Chart(grafiek_df).mark_bar().encode(
        x=alt.X("Datum:N", sort=None),
        y="CO2 (kg):Q",
        tooltip=["Datum", "CO2 (kg)"]
    ).properties(title="CO₂ per dag")
    st.altair_chart(chart, use_container_width=True)

    # Pie chart voor de hele werf
    pie_werf = werf_df.groupby("Wagen", as_index=False)["CO2 (kg)"].sum()
    pie_werf = pie_werf.rename(columns={"CO2 (kg)": "CO2_kg"})
    pie_werf["Percentage"] = (pie_werf["CO2_kg"] / pie_werf["CO2_kg"].sum()) * 100

    pie_chart_werf = alt.Chart(pie_werf).mark_arc().encode(
        theta="CO2_kg:Q",
        color="Wagen:N",
        tooltip=[
            "Wagen",
            alt.Tooltip("CO2_kg:Q", format=".2f"),
            alt.Tooltip("Percentage:Q", format=".1f")
        ]
    ).properties(title="🥧 CO₂-verdeling per wagentype (gehele werf)")

    st.altair_chart(pie_chart_werf, use_container_width=True)


            # Optioneel: grafiek over dagen
            grafiek_df = werf_df.groupby("Datum", as_index=False)["CO2 (kg)"].sum()
            chart = alt.Chart(grafiek_df).mark_bar().encode(
                x="Datum:T",
                y="CO2 (kg):Q",
                tooltip=["Datum", "CO2 (kg)"]
            ).properties(title="CO₂ per dag")
            st.altair_chart(chart, use_container_width=True)






















