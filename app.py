import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------
# LANGUAGE TOGGLE
# ------------------------
language = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])

# ------------------------
# LOAD DATA (Replace this with real or uploaded CSV later)
# ------------------------
df = pd.read_csv("Simulated_TipEase_Resort_Data__Bilingual_.csv")  # Replace with your CSV file

# Parse dates
df["Fecha"] = pd.to_datetime(df["Fecha"])

# ------------------------
# UI HEADERS
# ------------------------
if language == "English":
    st.title("TipEase Resort Dashboard")
    st.subheader("15-Day Resort Tipping Summary")
else:
    st.title("Panel de Control de TipEase para Resorts")
    st.subheader("Resumen de Propinas de 15 Días")

# ------------------------
# KPI METRICS
# ------------------------
total_tips = df["Propina ($)"].sum()
total_guests = df["Huésped"].nunique()
total_staff = df["Colaborador"].nunique()

if language == "English":
    st.metric("Total Tips", f"${total_tips:,.2f}")
    st.metric("Unique Guests Tipped", total_guests)
    st.metric("Staff Tipped", total_staff)
else:
    st.metric("Propinas Totales", f"${total_tips:,.2f}")
    st.metric("Huéspedes que Dieron Propina", total_guests)
    st.metric("Colaboradores que Recibieron Propina", total_staff)

# ------------------------
# TIPS BY LOCATION
# ------------------------
if language == "English":
    st.subheader("Tips by Location")
else:
    st.subheader("Propinas por Ubicación")

loc_chart = px.bar(
    df.groupby("Ubicación")["Propina ($)"].sum().reset_index(),
    x="Ubicación",
    y="Propina ($)",
    color="Ubicación",
    labels={"Ubicación": "Location", "Propina ($)": "Total Tips ($)"} if language == "English" else {"Ubicación": "Ubicación", "Propina ($)": "Total de Propinas ($)"},
    title="Tip Distribution by Resort Area" if language == "English" else "Distribución de Propinas por Área"
)
st.plotly_chart(loc_chart, use_container_width=True)

# ------------------------
# TOP STAFF
# ------------------------
if language == "English":
    st.subheader("Top Staff by Tip Value")
else:
    st.subheader("Colaboradores Destacados por Propinas")

staff_table = df.groupby("Colaborador")["Propina ($)"].sum().sort_values(ascending=False).reset_index()
st.dataframe(staff_table)

# ------------------------
# DAILY TIPS CHART
# ------------------------
if language == "English":
    st.subheader("Daily Tip Activity")
else:
    st.subheader("Actividad Diaria de Propinas")

daily_tips = df.groupby("Fecha")["Propina ($)"].sum().reset_index()
fig_daily = px.line(daily_tips, x="Fecha", y="Propina ($)", markers=True)
st.plotly_chart(fig_daily, use_container_width=True)

# ------------------------
# RECENT ACTIVITY FEED
# ------------------------
if language == "English":
    st.subheader("Recent Tip Activity")
else:
    st.subheader("Actividad Reciente de Propinas")

recent_tips = df.sort_values(by="Fecha", ascending=False).head(15)
st.table(recent_tips[["Fecha", "Hora", "Huésped", "Colaborador", "Ubicación", "Propina ($)"]])

# ------------------------
# AI-Driven Insight
# ------------------------
if language == "English":
    st.markdown("### 🤖 Insights & Recommendations")
    st.markdown("- Guests tip **more frequently at the Spa and Beach**, suggesting these are key service points. Consider positioning top-performing staff here.")
    st.markdown("- **Saturday and Sunday** show the highest tip volume. Reinforce staffing or upsell services on weekends.")
    st.markdown("- One guest tipped **over $100** in the last 15 days. Consider sending a personalized thank-you or loyalty perk.")
else:
    st.markdown("### 🤖 Recomendaciones Basadas en Datos")
    st.markdown("- Los huéspedes dan **más propinas en el Spa y la Playa**, indicando que son puntos clave de servicio. Considere asignar a sus mejores colaboradores aquí.")
    st.markdown("- **Sábados y domingos** tienen el mayor volumen de propinas. Refuerce la dotación o promociones durante estos días.")
    st.markdown("- Un huésped dio **más de $100** en propinas en 15 días. Considere enviarle un agradecimiento personalizado o recompensa de fidelidad.")
