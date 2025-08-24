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





















