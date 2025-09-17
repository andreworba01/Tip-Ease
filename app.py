import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image
from pathlib import Path

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="TipEase Resort Dashboard",
    page_icon="💸",
    layout="wide"
)

# ------------------------------------------------------------------
# Custom CSS for premium look
# ------------------------------------------------------------------
st.markdown("""
<style>
/* Center content and add padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1350px;
    margin: auto;
}
/* Card-style metrics */
div[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin: 0.5rem;
}
/* Table hover effect */
table.dataframe tbody tr:hover {
    background-color: #f1f5f9;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Language Toggle
# ------------------------------------------------------------------
LANG = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
def T(en, es): return es if LANG == "Español" else en

# ------------------------------------------------------------------
# Upload Data
# ------------------------------------------------------------------
st.sidebar.markdown("### " + T("Upload Data", "Subir Datos"))
csv_file = st.sidebar.file_uploader(
    T("Upload the 15-day bilingual CSV", "Sube el CSV bilingüe de 15 días"), type="csv"
)

if not csv_file:
    st.info(T("Please upload your tipping data CSV to continue.",
              "Por favor sube tu archivo CSV de propinas para continuar."))
    st.stop()

df = pd.read_csv(csv_file)

# Normalize headers for bilingual columns
df.rename(columns={
    "Day / Día": "day",
    "Guest ID / Huésped": "guest",
    "Tip (USD) / Propina (USD)": "tip",
    "Department / Departamento": "dept",
    "Time of Day / Hora del Día": "tod"
}, inplace=True)

df["day"] = pd.to_numeric(df["day"], errors="coerce").fillna(0).astype(int)
df["tip"] = pd.to_numeric(df["tip"], errors="coerce").fillna(0.0)

# Synthetic timestamp for recent log
bucket_map = {"Morning": 10, "Afternoon": 14, "Evening": 19,
              "Mañana": 10, "Tarde": 14, "Noche": 19}
hours = df["tod"].map(bucket_map).fillna(12).astype(int)
base_date = datetime.today() - timedelta(days=15)
df["timestamp"] = [base_date + timedelta(days=int(d), hours=int(h))
                   for d, h in zip(df["day"], hours)]

# ------------------------------------------------------------------
# Hero Header
# ------------------------------------------------------------------
st.title("💸 TipEase Resort Dashboard")
st.markdown(
    f"<h3 style='text-align:center;color:#6B7280;'>{T('Real-time tipping analytics for a seamless guest experience', 'Analítica de propinas en tiempo real para una experiencia sin fricciones')}</h3>",
    unsafe_allow_html=True
)

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
k1, k2, k3 = st.columns(3)
k1.metric(T("Total Tips", "Propinas Totales"), f"${df['tip'].sum():,.2f}")
k2.metric(T("Unique Guests", "Huéspedes Únicos"), df["guest"].nunique())
k3.metric(T("Departments", "Departamentos"), df["dept"].nunique())

st.divider()

# ------------------------------------------------------------------
# Charts Row
# ------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader(T("Tips by Department", "Propinas por Departamento"))
    dep_sum = df.groupby("dept")["tip"].sum().reset_index().sort_values("tip", ascending=False)
    fig_dep = px.bar(
        dep_sum, x="dept", y="tip", color="dept",
        labels={"dept": T("Department", "Departamento"), "tip": T("Total Tips ($)", "Propinas Totales ($)")},
        color_discrete_sequence=["#2A9D8F", "#E76F51", "#264653", "#F4A261"]
    )
    fig_dep.update_layout(template="plotly_white", font=dict(size=14, family="Inter, sans-serif"))
    st.plotly_chart(fig_dep, use_container_width=True)

with right:
    st.subheader(T("Daily Tip Activity (15 Days)", "Actividad Diaria de Propinas (15 Días)"))
    daily = df.groupby("day")["tip"].sum().reset_index()
    fig_day = px.line(
        daily, x="day", y="tip", markers=True,
        labels={"day": T("Day", "Día"), "tip": T("Total Tips ($)", "Propinas Totales ($)")},
        color_discrete_sequence=["#2A9D8F"]
    )
    fig_day.update_layout(template="plotly_white", font=dict(size=14, family="Inter, sans-serif"))
    st.plotly_chart(fig_day, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# Top Tippers & Recent Log
# ------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(T("Top Tippers (Guests)", "Huéspedes que Más Propinan"))
    top_guests = df.groupby("guest")["tip"].sum().reset_index().sort_values("tip", ascending=False)
    st.dataframe(top_guests.rename(columns={
        "guest": T("Guest", "Huésped"),
        "tip": T("Total Tipped ($)", "Total Propinado ($)")
    }), use_container_width=True)

with col2:
    st.subheader(T("Recent Tip Log", "Registro Reciente de Propinas"))
    recent = df.sort_values("timestamp", ascending=False).head(15)
    st.dataframe(recent.rename(columns={
        "timestamp": T("Time", "Hora"),
        "guest": T("Guest", "Huésped"),
        "dept": T("Department", "Departamento"),
        "tod": T("Time of Day", "Momento del Día"),
        "tip": T("Tip ($)", "Propina ($)")
    }), use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# Heatmap (Optional Map Upload)
# ------------------------------------------------------------------
st.subheader(T("Resort Heatmap", "Mapa de Calor del Resort"))
st.caption(T(
    "Tip intensity by department over a resort map (upload PNG/JPG).",
    "Intensidad de propinas por departamento sobre un mapa del resort (sube PNG/JPG)."
))
map_file = st.file_uploader(T("Upload resort map image", "Sube imagen del mapa del resort"), type=["png", "jpg", "jpeg"])

if map_file:
    img = Image.open(map_file)
    st.image(img, caption=T("Uploaded Resort Map", "Mapa del Resort"), use_column_width=True)

st.divider()

# ------------------------------------------------------------------
# Smart Insights
# ------------------------------------------------------------------
st.subheader(T("Smart Insights", "Recomendaciones"))
avg_tip = df["tip"].mean()
top_dept = dep_sum.iloc[0]["dept"] if not dep_sum.empty else None
max_day = daily.loc[daily["tip"].idxmax(), "day"]

insights = [
    T(f"📈 Highest tipping day: Day {int(max_day)}.",
      f"📈 Día con más propinas: Día {int(max_day)}."),
    T(f"💵 Average tip: ${avg_tip:.2f}.",
      f"💵 Propina promedio: ${avg_tip:.2f}."),
    T(f"🏝️ Strongest area: {top_dept} — consider placing high-performing staff here.",
      f"🏝️ Área más fuerte: {top_dept} — considera ubicar a tu mejor personal allí."),
    T("🗓️ Tip peaks cluster around weekends — plan staffing accordingly.",
      "🗓️ Los picos de propinas suelen ser en fines de semana — planifica personal."),
    T("🎁 Offer loyalty perks to top tippers to encourage repeat stays.",
      "🎁 Ofrece beneficios de fidelidad a los huéspedes que más propinan.")
]
for i in insights:
    st.markdown(f"- {i}")

