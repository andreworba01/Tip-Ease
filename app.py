import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta

st.set_page_config(page_title="TipEase Resort Dashboard", layout="wide")

# ---------------------------
# Language toggle
# ---------------------------
LANG = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])

def T(en, es):
    return es if LANG == "Español" else en

st.title("💸 TipEase Resort Dashboard")

# ---------------------------
# Data input
# ---------------------------
st.sidebar.markdown("### " + T("Data Source", "Fuente de Datos"))
csv_file = st.sidebar.file_uploader(
    T("Upload CSV (your bilingual file)",
      "Sube el CSV (tu archivo bilingüe)"),
    type=["csv"]
)

# Fallback: path on disk (optional)
default_csv = "Simulated_15-Day_Guest_Tipping_Data__Bilingual_.csv"

def load_df(file_like):
    # Read CSV and normalize headers
    df = pd.read_csv(file_like, encoding="utf-8")
    # Map verbose bilingual headers -> safe internal names
    col_map = {
        "Day / Día": "day",
        "Guest ID / Huésped": "guest",
        "Tip (USD) / Propina (USD)": "tip",
        "Department / Departamento": "dept",
        "Time of Day / Hora del Día": "tod"
    }
    # Handle possible mojibake (DÃ­a, HuÃ©sped, etc.)
    for c in list(df.columns):
        key = (c.encode("latin1", "ignore").decode("latin1")
               if "Ã" in c else c)
        if key in col_map and c != col_map[key]:
            df.rename(columns={c: col_map[key]}, inplace=True)
    # Also try direct rename in case headers are already fine
    df.rename(columns=col_map, inplace=True)
    return df

if csv_file is not None:
    df = load_df(csv_file)
elif Path(default_csv).exists():
    df = load_df(default_csv)
else:
    st.warning(T(
        "Please upload your CSV to proceed.",
        "Por favor sube tu archivo CSV para continuar."
    ))
    st.stop()

# Coerce types
df["day"] = pd.to_numeric(df["day"], errors="coerce").astype(int)
df["tip"] = pd.to_numeric(df["tip"], errors="coerce").fillna(0.0)

# Create a synthetic timestamp (for recent log) from Day + Time of Day bucket
# Create a simple timestamp using an arbitrary start date
bucket_map = {"Morning": 10, "Afternoon": 14, "Evening": 19,
              "Mañana": 10, "Tarde": 14, "Noche": 19}
hour = df["tod"].map(bucket_map).fillna(12).astype(int)

# Force day column to plain Python ints, fallback to 0 if NaN
days_list = [int(x) if pd.notna(x) else 0 for x in df["day"]]

# Pick a fixed base date ~15 days ago
base_date = datetime.today() - timedelta(days=15)

df["timestamp"] = [
    base_date + timedelta(days=d) + timedelta(hours=int(h))
    for d, h in zip(days_list, hour)
]


# ---------------------------
# KPI cards
# ---------------------------
c1, c2, c3 = st.columns(3)
c1.metric(T("Total Tips", "Propinas Totales"), f"${df['tip'].sum():,.2f}")
c2.metric(T("Unique Guests", "Huéspedes Únicos"), df["guest"].nunique())
c3.metric(T("Departments", "Departamentos"), df["dept"].nunique())

st.divider()

# ---------------------------
# Charts row
# ---------------------------
lc, rc = st.columns([1,1])

with lc:
    st.subheader(T("Tips by Department", "Propinas por Departamento"))
    dep_sum = df.groupby("dept")["tip"].sum().reset_index().sort_values("tip", ascending=False)
    fig_dep = px.bar(
        dep_sum, x="dept", y="tip", color="dept",
        labels={"dept": T("Department", "Departamento"), "tip": T("Total Tips ($)", "Total Propinas ($)")},
        title=T("Tip Distribution by Department", "Distribución de Propinas por Departamento")
    )
    st.plotly_chart(fig_dep, use_container_width=True)

with rc:
    st.subheader(T("Daily Tip Activity (15 Days)", "Actividad Diaria de Propinas (15 Días)"))
    daily = df.groupby("day")["tip"].sum().reset_index()
    fig_day = px.line(
        daily, x="day", y="tip", markers=True,
        labels={"day": T("Day", "Día"), "tip": T("Total Tips ($)", "Total Propinas ($)")},
        title=T("Daily Tipping Trend", "Tendencia Diaria de Propinas")
    )
    st.plotly_chart(fig_day, use_container_width=True)

st.divider()

# ---------------------------
# Top tippers + Recent log
# ---------------------------
l2, r2 = st.columns([1,1])

with l2:
    st.subheader(T("Top Tippers (Guests)", "Quienes Más Dan Propina (Huéspedes)"))
    top_guests = df.groupby("guest")["tip"].sum().reset_index().sort_values("tip", ascending=False).head(5)
    st.dataframe(top_guests.rename(columns={
        "guest": T("Guest", "Huésped"),
        "tip": T("Total Tipped ($)", "Total Propinado ($)")
    }), use_container_width=True)

with r2:
    st.subheader(T("Recent Tip Log", "Registro Reciente de Propinas"))
    recent = df.sort_values("timestamp", ascending=False)[["timestamp", "guest", "dept", "tod", "tip"]].head(15)
    st.dataframe(recent.rename(columns={
        "timestamp": T("Time", "Hora"),
        "guest": T("Guest", "Huésped"),
        "dept": T("Department", "Departamento"),
        "tod": T("Time of Day", "Momento del Día"),
        "tip": T("Tip ($)", "Propina ($)")
    }), use_container_width=True)

st.divider()

# ---------------------------
# Resort heatmap
# ---------------------------
st.subheader(T("Resort Heatmap", "Mapa de Calor del Resort"))

st.caption(T(
    "Tip intensity by department overlaid on a resort map (mock).",
    "Intensidad de propinas por departamento sobre un mapa del resort (simulado)."
))

# Upload or load resort map
map_file = st.file_uploader(T("Upload resort map image (PNG/JPG)", "Sube imagen del mapa del resort (PNG/JPG)"),
                            type=["png","jpg","jpeg"])
if map_file:
    resort_img = Image.open(map_file)
elif Path("resort_map.png").exists():
    resort_img = Image.open("resort_map.png")
else:
    resort_img = None

# Assign department anchor points (x,y) in an abstract 1000x700 canvas
# Tweak these to match your map layout
anchor = {
    "Dining": (750, 420),
    "Valet": (900, 200),
    "Spa": (500, 120),
    "Housekeeping": (300, 380),
    "Pool": (420, 480),
    "Beachfront": (520, 650),
    "Concierge": (820, 320),
    "Room Service": (250, 520),
}

# Map Spanish dept names back to English anchors if needed
# (If your CSV uses only EN/only ES, it still works.)
synonyms = {
    "Comedor": "Dining",
    "Valet": "Valet",
    "Spa": "Spa",
    "Limpieza": "Housekeeping",
    "Piscina": "Pool",
    "Playa": "Beachfront",
    "Conserjería": "Concierge",
    "Servicio a la Habitación": "Room Service"
}

dep_points = []
for d, total in dep_sum.values:
    key = synonyms.get(d, d)  # normalize
    if key in anchor:
        x, y = anchor[key]
        dep_points.append({"dept": d, "x": x, "y": y, "tip": float(total)})

heat_df = pd.DataFrame(dep_points)

if heat_df.empty:
    st.info(T("No departments matched the heatmap anchors. Adjust names or anchors.",
              "No hubo coincidencias entre departamentos y anclas del mapa. Ajusta nombres o anclas."))
else:
    # If there is a background image, we’ll scale axes to match
    if resort_img:
        w, h = resort_img.size
        sizex, sizey = w, h
        bg = resort_img
    else:
        # Fallback virtual canvas
        sizex, sizey = 1000, 700
        bg = None

    fig_map = px.scatter(
        heat_df,
        x="x", y="y",
        size="tip",
        color="dept",
        size_max=80,
        hover_data={"tip": ":.2f", "x": False, "y": False},
        labels={"dept": T("Department", "Departamento"), "tip": T("Total Tips ($)", "Total Propinas ($)")},
        title=T("Tip Intensity by Location", "Intensidad de Propinas por Ubicación")
    )
    fig_map.update_yaxes(autorange="reversed")  # image coords
    fig_map.update_layout(
        xaxis=dict(visible=False, range=[0, sizex]),
        yaxis=dict(visible=False, range=[0, sizey]),
        margin=dict(l=0, r=0, t=40, b=0),
        height=int(sizey * 0.75),
    )
    if bg:
        fig_map.add_layout_image(
            dict(source=bg, x=0, y=0, xref="x", yref="y",
                 sizex=sizex, sizey=sizey, sizing="stretch", layer="below", opacity=1.0)
        )
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ---------------------------
# AI-like Insights
# ---------------------------
st.subheader(T("Smart Insights", "Recomendaciones Basadas en Datos"))

most_active_day = daily.loc[daily["tip"].idxmax(), "day"]
avg_tip = df["tip"].mean()
top_dept = dep_sum.iloc[0]["dept"] if not dep_sum.empty else None

ins = [
    T(f"📈 Highest tipping day: **Day {int(most_active_day)}**.",
      f"📈 Día con más propinas: **Día {int(most_active_day)}**."),
    T(f"💵 Average tip: **${avg_tip:.2f}**.",
      f"💵 Propina promedio: **${avg_tip:.2f}**."),
    T(f"🏝️ Strongest area: **{top_dept}** — consider placing high-performing staff here.",
      f"🏝️ Zona más fuerte: **{top_dept}** — considera ubicar a tu mejor personal aquí.") if top_dept else "",
    T("🗓️ Tip peaks tend to cluster around weekends — plan staffing accordingly.",
      "🗓️ Los picos de propinas suelen darse en fines de semana — planifica la dotación de personal."),
    T("🎁 Consider loyalty perks for top tippers to encourage repeat stays.",
      "🎁 Considera beneficios de fidelidad para los huéspedes que más propinan."),
]
for s in ins:
    if s:
        st.markdown(f"- {s}")
