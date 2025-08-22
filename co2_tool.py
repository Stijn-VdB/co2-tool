import streamlit as st
import pandas as pd

# Excel inladen
df = pd.read_excel("Tool.xlsx", sheet_name="Blad1")

st.title("🚗 CO₂-uitstoot berekening")

# Resultaten bewaren in session_state
if "resultaten" not in st.session_state:
    st.session_state["resultaten"] = []

# Invoer
naam = st.text_input("Naam")
wagen = st.selectbox("Wagentype", df["Type activiteit"].unique())
km = st.number_input("Aantal kilometers", min_value=0, step=1)

# ✅ Gewone knop (geen st.form)
if st.button("Toevoegen"):
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

# Resultaten tonen
if st.session_state["resultaten"]:
    resultaten_df = pd.DataFrame(st.session_state["resultaten"])
    st.subheader("Resultaten")
    st.table(resultaten_df)

    totaal = resultaten_df["CO2 (kg)"].sum()
    st.success(f"🌍 Totale CO₂-uitstoot: {totaal:.2f} kg")
import streamlit as st
import pandas as pd

# Excel inladen
df = pd.read_excel("Tool.xlsx", sheet_name="Blad1")

st.title("🚗 CO₂-uitstoot berekening")

# Resultaten bewaren in session_state
if "resultaten" not in st.session_state:
    st.session_state["resultaten"] = []

# Invoer
naam = st.text_input("Naam")
wagen = st.selectbox("Wagentype", df["Type activiteit"].unique())
km = st.number_input("Aantal kilometers", min_value=0, step=1)

# ✅ Gewone knop (geen st.form)
if st.button("Toevoegen"):
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

# Resultaten tonen
if st.session_state["resultaten"]:
    resultaten_df = pd.DataFrame(st.session_state["resultaten"])
    st.subheader("Resultaten")
    st.table(resultaten_df)

    totaal = resultaten_df["CO2 (kg)"].sum()
    st.success(f"🌍 Totale CO₂-uitstoot: {totaal:.2f} kg")




