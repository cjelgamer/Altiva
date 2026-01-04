import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.agents.ag_fisio import run_ag_fisio
from backend.services.database import get_user_profile, daily_states

st.set_page_config(
    page_title="ALTIVA - Monitor",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

# --- DISEÑO MINIMALISTA CLARO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo sepia claro */
    .stApp {
        background: #faf7f2 !important;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }
    
    .block-container {
        padding-top: 2rem;
        max-width: 100%;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        color: #2c3e50 !important;
        font-weight: 300 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #34495e !important;
        font-weight: 400 !important;
        font-size: 1.5rem !important;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #5a6c7d !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    
    .stNumberInput > div > div > input {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        background: white !important;
        color: #2c3e50 !important;
        font-size: 1rem;
        font-weight: 400;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .stNumberInput > label,
    .stSlider > label {
        color: #5a6c7d !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    .stSlider > div > div > div > div {
        background: #3498db !important;
    }
    
    .stButton > button {
        background: white;
        color: #3498db !important;
        border: 1px solid #3498db;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        background: #3498db;
        color: white !important;
    }
    
    .progress-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .progress-circle {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: conic-gradient(
            #3498db 0deg,
            #3498db var(--progress),
            #ecf0f1 var(--progress),
            #ecf0f1 360deg
        );
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 0 auto 0.75rem;
    }
    
    .progress-circle::before {
        content: '';
        position: absolute;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: white;
    }
    
    .progress-value {
        position: relative;
        z-index: 1;
        font-size: 2rem;
        font-weight: 300;
        color: #2c3e50;
    }
    
    .progress-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #5a6c7d;
    }
    
    .progress-detail {
        font-size: 0.85rem;
        color: #95a5a6;
    }
    
    /* Estado con rojo y celeste */
    .estado-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 1rem;
        margin: 1rem 0;
        border: 1px solid;
    }
    
    .estado-normal {
        background: #d6eaf8;
        color: #3498db;
        border-color: #3498db;
    }
    
    .estado-bajo {
        background: #fadbd8;
        color: #e74c3c;
        border-color: #e74c3c;
    }
    
    .estado-alerta {
        background: #fadbd8;
        color: #e74c3c;
        border-color: #e74c3c;
    }
    
    .estado-critico {
        background: #fadbd8;
        color: #e74c3c;
        border-color: #e74c3c;
    }
    
    /* Alertas con texto NEGRO visible */
    .stAlert {
        border-radius: 8px;
        border-left: 3px solid;
        padding: 1rem;
        font-size: 0.9rem;
        background: white !important;
    }
    
    /* FORZAR TEXTO NEGRO EN TODAS LAS ALERTAS */
    .stAlert p, .stAlert div, .stAlert span {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    hr {
        border: none;
        border-top: 1px solid #ecf0f1;
        margin: 2rem 0;
    }
    
    /* Page links con color visible */
    a[data-testid="stPageLink-NavLink"] {
        background: #3498db !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        display: inline-block !important;
        margin-top: 0.5rem !important;
    }
    
    a[data-testid="stPageLink-NavLink"]:hover {
        background: #2980b9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Verificar login
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Debes iniciar sesión primero")
    st.page_link("app.py", label="🔐 Ir a Login")
    st.stop()

user_id = str(st.session_state["user"]["_id"])

# Verificar perfil
profile = get_user_profile(user_id)
if not profile:
    st.warning("⚠️ Primero completa tu perfil inicial")
    st.page_link("pages/2_Setup.py", label="⚙️ Ir a Configuración")
    st.stop()

# INICIALIZAR SESSION STATE
if "agua_acumulada" not in st.session_state:
    today = date.today()
    ultimo_registro = daily_states.find_one(
        {"user_id": user_id},
        sort=[("fecha", -1)]
    )
    
    if ultimo_registro and ultimo_registro.get("fecha").date() == today:
        st.session_state.agua_acumulada = ultimo_registro["indicadores"]["agua_consumida_ml"]
        st.session_state.sueno_total = ultimo_registro["indicadores"]["horas_sueno"]
        st.session_state.actividad_total = ultimo_registro["indicadores"]["actividad_minutos"]
        st.session_state.energia_actual = ultimo_registro["indicadores"]["nivel_energia"]
    else:
        st.session_state.agua_acumulada = 0
        st.session_state.sueno_total = 0
        st.session_state.actividad_total = 0
        st.session_state.energia_actual = 3

# Función para guardar automáticamente
def auto_guardar():
    try:
        run_ag_fisio(
            user_id,
            {
                "agua_consumida_ml": st.session_state.agua_acumulada,
                "horas_sueno": st.session_state.sueno_total,
                "actividad_minutos": st.session_state.actividad_total,
                "nivel_energia": st.session_state.energia_actual
            }
        )
    except:
        pass

# --- HEADER ---
st.title("Monitor Diario")

# --- LAYOUT DE 2 COLUMNAS ---
col_left, col_right = st.columns([1, 1], gap="large")

# === COLUMNA IZQUIERDA: INPUTS CON VALORES ACTUALES ===
with col_left:
    st.markdown("## Actualizar Progreso")
    
    # Agua - MUESTRA VALOR ACTUAL
    agua_total = st.number_input(
        "💧 Agua consumida hoy (ml)", 
        min_value=0, 
        max_value=10000, 
        value=st.session_state.agua_acumulada,
        step=100,
        key="agua_input",
        help="Total de agua que has tomado hoy"
    )
    
    if agua_total != st.session_state.agua_acumulada:
        st.session_state.agua_acumulada = agua_total
        auto_guardar()
        st.rerun()
    
    # Sueño - MUESTRA VALOR ACTUAL
    sueno_hoy = st.number_input(
        "😴 Horas de sueño", 
        min_value=0.0, 
        max_value=24.0, 
        value=float(st.session_state.sueno_total), 
        step=0.5,
        key="sueno_input",
        help="Horas que dormiste anoche"
    )
    
    if sueno_hoy != st.session_state.sueno_total:
        st.session_state.sueno_total = sueno_hoy
        auto_guardar()
        st.rerun()
    
    # Actividad - MUESTRA VALOR ACTUAL
    actividad_total = st.number_input(
        "🏃 Actividad física hoy (min)", 
        min_value=0, 
        max_value=500, 
        value=st.session_state.actividad_total, 
        step=5,
        key="actividad_input",
        help="Total de minutos de ejercicio hoy"
    )
    
    if actividad_total != st.session_state.actividad_total:
        st.session_state.actividad_total = actividad_total
        auto_guardar()
        st.rerun()
    
    # Energía - MUESTRA VALOR ACTUAL
    energia_nueva = st.slider(
        "⚡ Nivel de energía actual", 
        min_value=1, 
        max_value=5, 
        value=st.session_state.energia_actual,
        key="energia_input",
        help="1 = Muy cansado | 5 = Muy energético"
    )
    
    if energia_nueva != st.session_state.energia_actual:
        st.session_state.energia_actual = energia_nueva
        auto_guardar()
        st.rerun()
    
    st.markdown("---")
    
    # Botones de navegación
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Inicio", use_container_width=True):
            st.switch_page("app.py")
    with col2:
        if st.button("🔄 Reiniciar Día", use_container_width=True):
            st.session_state.agua_acumulada = 0
            st.session_state.sueno_total = 0
            st.session_state.actividad_total = 0
            st.session_state.energia_actual = 3
            st.rerun()

# === COLUMNA DERECHA: PROGRESO CIRCULAR ===
with col_right:
    st.markdown("## Progreso del Día")
    
    # Calcular porcentajes
    agua_porcentaje = min((st.session_state.agua_acumulada / profile['agua_base_ml']) * 100, 100)
    sueno_porcentaje = min((st.session_state.sueno_total / profile['sueno_base_h']) * 100, 100)
    actividad_minima = 30 if profile['altitud'] <= 3500 else 20
    actividad_porcentaje = min((st.session_state.actividad_total / actividad_minima) * 100, 100)
    
    # 4 círculos en 2 filas
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-circle" style="--progress: {agua_porcentaje * 3.6}deg;">
                <div class="progress-value">{agua_porcentaje:.0f}%</div>
            </div>
            <div class="progress-label">💧 Hidratación</div>
            <div class="progress-detail">{st.session_state.agua_acumulada} / {profile['agua_base_ml']} ml</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-circle" style="--progress: {sueno_porcentaje * 3.6}deg;">
                <div class="progress-value">{sueno_porcentaje:.0f}%</div>
            </div>
            <div class="progress-label">😴 Sueño</div>
            <div class="progress-detail">{st.session_state.sueno_total} / {profile['sueno_base_h']} h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col1:
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-circle" style="--progress: {actividad_porcentaje * 3.6}deg;">
                <div class="progress-value">{actividad_porcentaje:.0f}%</div>
            </div>
            <div class="progress-label">🏃 Actividad</div>
            <div class="progress-detail">{st.session_state.actividad_total} / {actividad_minima} min</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        energia_color = "#27ae60" if st.session_state.energia_actual >= 4 else "#f39c12" if st.session_state.energia_actual >= 3 else "#e74c3c"
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-circle" style="background: conic-gradient({energia_color} 0deg, {energia_color} {st.session_state.energia_actual * 72}deg, #ecf0f1 {st.session_state.energia_actual * 72}deg, #ecf0f1 360deg);">
                <div class="progress-value">{st.session_state.energia_actual}</div>
            </div>
            <div class="progress-label">⚡ Energía</div>
            <div class="progress-detail">de 5</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Estado y alertas
    st.markdown("### Estado Actual")
    
    deshidratado = agua_porcentaje < 70
    falta_sueno = sueno_porcentaje < 80
    
    if deshidratado and falta_sueno:
        estado = "CRÍTICO"
    elif deshidratado or falta_sueno:
        estado = "ALERTA"
    elif st.session_state.energia_actual <= 2:
        estado = "BAJO"
    else:
        estado = "NORMAL"
    
    estado_icons = {"NORMAL": "🟢", "BAJO": "🟡", "ALERTA": "🟠", "CRÍTICO": "🔴"}
    estado_classes = {"NORMAL": "estado-normal", "BAJO": "estado-bajo", "ALERTA": "estado-alerta", "CRÍTICO": "estado-critico"}
    
    st.markdown(
        f'<div class="estado-badge {estado_classes[estado]}">'
        f'{estado_icons[estado]} {estado}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Alertas compactas
    if deshidratado:
        st.warning(f"💧 Hidratación baja ({agua_porcentaje:.0f}%)")
    if falta_sueno:
        st.warning(f"😴 Sueño insuficiente ({sueno_porcentaje:.0f}%)")
    if st.session_state.actividad_total < actividad_minima:
        st.info(f"🏃 Faltan {actividad_minima - st.session_state.actividad_total} min")
    if not (deshidratado or falta_sueno) and st.session_state.actividad_total >= actividad_minima:
        st.success("✓ Cumpliendo objetivos")
