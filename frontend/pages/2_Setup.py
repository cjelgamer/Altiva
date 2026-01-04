import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.crew.crew import run_initial_crew
from backend.services.database import has_user_profile, get_user_profile, user_profiles

st.set_page_config(
    page_title="ALTIVA - Configuración de Perfil",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚙️"
)

# --- DISEÑO MINIMALISTA CLARO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #faf7f2 !important;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }
    
    .block-container {
        padding-top: 2.5rem;
        max-width: 900px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        color: #2c3e50 !important;
        font-weight: 300 !important;
        font-size: 2rem !important;
    }
    
    h2 {
        color: #34495e !important;
        font-weight: 400 !important;
        font-size: 1.3rem !important;
    }
    
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 1px solid #e8dfd5;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        background: white !important;
        color: #2c3e50 !important;
        font-size: 1rem;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .stNumberInput > label,
    .stSelectbox > label {
        color: #5a6c7d !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    .stButton > button {
        background: #3498db;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.875rem 2rem;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: #2980b9;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #3498db;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5a6c7d;
        font-weight: 500;
        font-size: 0.85rem;
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

st.markdown('<div class="setup-container">', unsafe_allow_html=True)

st.title("⚙️ Configuración de Perfil")
st.markdown('<p class="subtitle">AG-INICIAL: Perfil Fisiológico Base</p>', unsafe_allow_html=True)

# Verificar login
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Debes iniciar sesión primero")
    st.page_link("app.py", label="🔐 Ir a Login")
    st.stop()

user_id = str(st.session_state["user"]["_id"])

# Obtener perfil existente (si existe)
existing_profile = get_user_profile(user_id)
is_editing = existing_profile is not None

# Modo edición o creación
if is_editing:
    st.info("✏️ **Modo Edición** - Modifica los datos que necesites actualizar")
else:
    st.info("✨ **Primer Uso** - Completa tu perfil inicial")

st.markdown("---")

# Formulario con valores pre-cargados si existe perfil
with st.form("setup_form"):
    st.markdown("### 📝 Datos Personales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        edad = st.number_input(
            "Edad", 
            min_value=10, 
            max_value=100, 
            value=int(existing_profile.get("edad", 20)) if existing_profile else 20,
            help="Tu edad actual en años"
        )
        sexo = st.selectbox(
            "Sexo", 
            ["M", "F"],
            index=0 if not existing_profile else (0 if existing_profile.get("sexo") == "M" else 1),
            help="Masculino o Femenino"
        )
        peso = st.number_input(
            "Peso (kg)", 
            min_value=30.0, 
            max_value=150.0, 
            value=float(existing_profile.get("peso", 70.0)) if existing_profile else 70.0,
            step=0.5,
            help="Tu peso corporal en kilogramos"
        )
    
    with col2:
        altura = st.number_input(
            "Altura (m)", 
            min_value=1.0, 
            max_value=2.2, 
            value=float(existing_profile.get("altura", 1.70)) if existing_profile else 1.70,
            step=0.01,
            help="Tu estatura en metros"
        )
        ciudad = st.selectbox(
            "Ciudad", 
            ["Puno", "Juliaca", "Ilave", "Ayaviri", "Azangaro"],
            index=["Puno", "Juliaca", "Ilave", "Ayaviri", "Azangaro"].index(existing_profile.get("ciudad", "Puno")) if existing_profile else 0,
            help="Ciudad donde vives o estudias"
        )
        nivel = st.selectbox(
            "Nivel de actividad", 
            ["bajo", "medio", "alto"],
            index=["bajo", "medio", "alto"].index(existing_profile.get("nivel_actividad", "medio")) if existing_profile else 1,
            help="Tu nivel de actividad física habitual"
        )

    st.markdown("---")
    
    button_text = "💾 Guardar Cambios" if is_editing else "✨ Crear Perfil"
    submitted = st.form_submit_button(button_text, use_container_width=True, type="primary")
    
    if submitted:
        with st.spinner("🤖 AG-INICIAL procesando..."):
            try:
                # Si está editando, eliminar el perfil anterior
                if is_editing:
                    user_profiles.delete_one({"user_id": user_id})
                
                # Crear/actualizar perfil
                profile = run_initial_crew(
                    user_id,
                    {
                        "edad": edad,
                        "sexo": sexo,
                        "peso": peso,
                        "altura": altura,
                        "ciudad": ciudad,
                        "nivel_actividad": nivel
                    }
                )
                
                # Actualizar session state
                st.session_state.user["has_profile"] = True
                
                if is_editing:
                    st.success("✅ Perfil actualizado exitosamente!")
                else:
                    st.success("✅ Perfil creado exitosamente!")
                    st.balloons()
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Mostrar perfil actual si existe
if existing_profile:
    st.markdown("---")
    st.markdown("### 📊 Tu Perfil Actual")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Edad", f"{existing_profile['edad']} años")
        st.metric("⚖️ Peso", f"{existing_profile['peso']} kg")
    with col2:
        st.metric("🧬 Sexo", existing_profile['sexo'])
        st.metric("📏 Altura", f"{existing_profile['altura']} m")
    with col3:
        st.metric("🏙️ Ciudad", existing_profile['ciudad'])
        st.metric("🏔️ Altitud", f"{existing_profile['altitud']} msnm")
    
    st.markdown("### 💧 Valores Base Calculados")
    st.markdown("*Estos valores son calculados automáticamente por AG-INICIAL según tu perfil y altitud*")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(
            "💧 Agua Diaria", 
            f"{existing_profile['agua_base_ml']} ml",
            help="Agua recomendada ajustada por altitud"
        )
    with col5:
        st.metric(
            "😴 Sueño Diario", 
            f"{existing_profile['sueno_base_h']} h",
            help="Horas de sueño recomendadas"
        )
    with col6:
        st.metric(
            "🏃 Actividad", 
            existing_profile.get('nivel_actividad', 'medio').title(),
            help="Nivel de actividad física"
        )
    
    st.markdown("---")
    st.info("📊 Ahora puedes ir al **Monitor** para registrar tu día")
    st.page_link("pages/3_Monitor.py", label="📊 Ir al Monitor", icon="📊")

st.markdown('</div>', unsafe_allow_html=True)
