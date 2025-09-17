import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image

# ----------------------------------------------------
# Simulated 30-Day Data
# ----------------------------------------------------
def generate_data():
    np.random.seed(42)
    guests = [f"Guest {i}" for i in range(1, 6)]
    depts = ["Spa", "Valet", "Housekeeping", "Dining", "Pool"]
    tod_opts = ["Morning", "Afternoon", "Evening"]

    rows = []
    for day in range(1, 31):
        for g in guests:
            if np.random.rand() < 0.85:
                rows.append({
                    "day": day,
                    "guest": g,
                    "tip": round(np.random.uniform(3, 20), 2),
                    "dept": np.random.choice(depts),
                    "tod": np.random.choice(tod_opts)
                })
    return pd.DataFrame(rows)

# ----------------------------------------------------
# App Wide Theme + Config
# ----------------------------------------------------
st.set_page_config(
    page_title="TipEase Resort",
    page_icon="",
    layout="wide"
)

# ----------------------------------------------------
# Custom CSS for polished look
# ----------------------------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# Language Toggle
# ----------------------------------------------------
LANG = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
def T(en, es): return es if LANG == "Español" else en

# ----------------------------------------------------
# Pages
# ----------------------------------------------------
page = st.sidebar.radio(
    T("Navigate", "Navegar"),
    [T("Landing Page", "Inicio"),
     T("Dashboard", "Panel"),
     T("Resort Heatmap", "Mapa de Calor"),
     T("Smart Insights", "Recomendaciones")]
)

# ----------------------------------------------------
# Load Data (simulate or allow upload)
# ----------------------------------------------------
st.sidebar.markdown("### " + T("Data Source", "Fuente de Datos"))
uploaded = st.sidebar.file_uploader(T("Upload 30-day CSV", "Sube CSV de 30 días"), type="csv")
df = pd.read_csv(uploaded) if uploaded else generate_data()

# Create timestamp for sorting
bucket_map = {"Morning":10,"Afternoon":14,"Evening":19}
hours = df["tod"].map(bucket_map).fillna(12).astype(int)
base = datetime.today() - timedelta(days=30)
df["timestamp"] = [base + timedelta(days=int(d), hours=int(h))
                   for d,h in zip(df["day"], hours)]

# ----------------------------------------------------
# Landing Page
# ----------------------------------------------------
logo = Image.open("assets/tipease_logo_.png")

if page == T("Landing Page", "Inicio"):
    st.title("TipEase")
    st.subheader(T("Seamless Resort Tipping Platform",
                   "Plataforma de Propinas sin Fricciones"))
    st.markdown(
        T("""
        Welcome to TipEase!  
        Guests tip digitally, staff are rewarded instantly,
        and resorts gain actionable insights.
        """,
        """
        ¡Bienvenido a TipEase!  
        Los huéspedes dejan propina digital,
        el personal recibe al instante,
        y el resort obtiene información valiosa.
        """)
    )
    st.image(logo, width=280)  # adjust width as needed
    st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{st.image(logo, output_format="png", use_container_width=False)}" width="240">
    </div>
    """,
    unsafe_allow_html=True)
    st.markdown("### Seamless Resort Tipping Platform")
    st.write("Welcome to **TipEase** – Guests tip digitally, staff are rewarded instantly, and resorts gain actionable insights.")

# ----------------------------------------------------
# Dashboard
# ----------------------------------------------------
elif page == T("Dashboard", "Panel"):
    st.title("TipEase Resort Dashboard")
    k1,k2,k3 = st.columns(3)
    k1.metric(T("Total Tips","Propinas Totales"), f"${df['tip'].sum():,.2f}")
    k2.metric(T("Unique Guests","Huéspedes Únicos"), df["guest"].nunique())
    k3.metric(T("Departments","Departamentos"), df["dept"].nunique())

    st.divider()
    left,right = st.columns(2)
    with left:
        st.subheader(T("Tips by Department","Propinas por Departamento"))
        dep = df.groupby("dept")["tip"].sum().reset_index()
        fig = px.bar(dep, x="dept", y="tip",
                     color="dept",
                     color_discrete_sequence=["#2A9D8F","#E76F51","#264653","#F4A261","#8AB17D"],
                     labels={"dept":T("Department","Departamento"),"tip":T("Total Tips ($)","Propinas ($)")})
        fig.update_layout(template="plotly_white", font=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader(T("Daily Tip Activity (30 Days)","Actividad Diaria (30 Días)"))
        daily = df.groupby("day")["tip"].sum().reset_index()
        fig2 = px.line(daily, x="day", y="tip", markers=True,
                       color_discrete_sequence=["#2A9D8F"],
                       labels={"day":T("Day","Día"),"tip":T("Total Tips ($)","Propinas ($)")})
        fig2.update_layout(template="plotly_white", font=dict(size=14))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        st.subheader(T("Top Tippers","Huéspedes Destacados"))
        topg = df.groupby("guest")["tip"].sum().reset_index().sort_values("tip",ascending=False)
        st.dataframe(topg)
    with c2:
        st.subheader(T("Recent Tip Log","Registro Reciente"))
        st.dataframe(df.sort_values("timestamp", ascending=False).head(15))

# ----------------------------------------------------
# Heatmap Page
# ----------------------------------------------------
elif page == T("Resort Heatmap", "Mapa de Calor"):
    st.title(T("Resort Heatmap","Mapa de Calor del Resort"))
    st.caption(T("Upload a resort map PNG/JPG to overlay tip intensity.",
                 "Sube un mapa PNG/JPG para ver la intensidad de propinas."))
    map_file = st.file_uploader(T("Upload resort map","Subir mapa del resort"), type=["png","jpg","jpeg"])
    if map_file:
        img = Image.open(map_file)
        st.image(img, caption=T("Uploaded Resort Map","Mapa del Resort"), use_column_width=True)
    # Simple heat bubbles (mock coordinates)
    coords = {
        "Spa": (0.3,0.7), "Valet": (0.8,0.5),
        "Housekeeping": (0.5,0.4), "Dining": (0.2,0.3), "Pool": (0.6,0.2)
    }
    hdata = df.groupby("dept")["tip"].sum().reset_index()
    hdata["x"] = hdata["dept"].apply(lambda d: coords[d][0])
    hdata["y"] = hdata["dept"].apply(lambda d: coords[d][1])
    fig_h = px.scatter(
        hdata, x="x", y="y", size="tip", color="dept",
        size_max=80, template="plotly_white",
        labels={"x":"", "y":""}
    )
    fig_h.update_xaxes(showgrid=False, visible=False)
    fig_h.update_yaxes(showgrid=False, visible=False)
    st.plotly_chart(fig_h, use_container_width=True)

# ----------------------------------------------------
# Smart Insights Page
# ----------------------------------------------------
else:
    st.title(T("Smart Insights","Recomendaciones"))
    avg_tip = df["tip"].mean()
    top_dept = df.groupby("dept")["tip"].sum().idxmax()
    max_day = df.groupby("day")["tip"].sum().idxmax()
    st.markdown(f"- {T('Highest tipping day:',' Día con más propinas:')} {int(max_day)}")
    st.markdown(f"- {T('Average tip:',' Propina promedio:')} ${avg_tip:.2f}")
    st.markdown(f"- {T(' Strongest area:',' Área más fuerte:')} {top_dept}")
    st.markdown(T("-  Tip peaks around weekends — plan staffing accordingly.",
                  "- Los picos de propinas suelen ser en fines de semana."))
    st.markdown(T("-  Consider loyalty perks for top tippers.",
                  "- Considere beneficios de fidelidad para los mejores huéspedes."))


