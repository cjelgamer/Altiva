import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.crew.crew import run_initial_crew
from backend.services.database import has_user_profile, get_user_profile, user_profiles


# --- CARGAR ESTILOS MODERNOS DE ALTIVA ---
def load_modern_css():
    """Carga el CSS moderno con animaciones y diseño mobile-first"""
    css_file = ROOT_DIR / "frontend" / "styles" / "altiva.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_modern_css()

st.set_page_config(
    page_title="ALTIVA - Configuración de Perfil",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚙️",
)

# --- DISEÑO MODERNO CON ICONOS GRANDES Y BORDES REDONDEADOS ---
st.markdown(
    """
<style>
    /* Asegurar que el CSS moderno se aplique correctamente */
    .stApp {
        background: var(--bg-secondary) !important;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(124, 58, 237, 0.03) 0%, transparent 50%);
    }
    
    .stApp > header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 2rem !important;
        text-align: center !important;
        border-radius: 0 0 1rem 1rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        overflow: hidden !important;
        margin-bottom: 2rem !important;
    }
    
    .stApp > header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1));
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .stApp h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        animation: glow 2s ease-in-out infinite alternate !important;
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 8px rgba(255, 255, 255, 0.4); }
        50% { text-shadow: 0 0 20px rgba(255, 255, 255, 0.6); }
    }
    
    .block-container {
        padding-top: 0 !important;
        max-width: 900px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Forzar colores de texto */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: var(--border-radius-lg) !important;
        border: 2px solid var(--border-color) !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
        outline: none !important;
    }
    
    .stButton > button {
        border-radius: var(--border-radius-lg) !important;
        font-weight: 600 !important;
        padding: 0.875rem 2rem !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
        border: none !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%);
        transition: all 0.5s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Alertas con texto visible */
    .stAlert {
        border-radius: var(--border-radius-lg) !important;
        border-left: 4px solid !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    .stAlert p, .stAlert div, .stAlert span {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Métricas modernas */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: var(--primary-color) !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    
    /* Page links con color visible */
    a[data-testid="stPageLink-NavLink"] {
        background: var(--primary-gradient) !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--border-radius) !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        display: inline-block !important;
        margin-top: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    a[data-testid="stPageLink-NavLink"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Mobile adjustments */
    @media (max-width: 768px) {
        .stApp > header {
            padding: 1.5rem !important;
        }
        
        .stApp h1 {
            font-size: 2rem !important;
        }
        
        .stButton > button {
            padding: 0.75rem 1.5rem !important;
            font-size: 0.875rem !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header moderno
st.markdown(
    """
<div class="header-gradient">
    <h1>⚙️ Configuración de Perfil</h1>
    <p>AG-INICIAL: Perfil Fisiológico Base</p>
</div>
""",
    unsafe_allow_html=True,
)

# Verificar login
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Debes iniciar sesión primero")
    st.page_link("app.py", label="🔐 Ir a Login", icon="🔐")
    st.stop()

user_id = str(st.session_state["user"]["_id"])

# Obtener perfil existente (si existe)
existing_profile = get_user_profile(user_id)
is_editing = existing_profile is not None

# Modo edición o creación
if is_editing:
    st.markdown(
        """
    <div class="card-modern animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">✏️</span>
            <div>
                <div class="font-semibold">Modo Edición</div>
                <div class="text-sm text-muted">Modifica los datos que necesites actualizar</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div class="card-modern animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">✨</span>
            <div>
                <div class="font-semibold">Primer Uso</div>
                <div class="text-sm text-muted">Completa tu perfil inicial</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Formulario con valores pre-cargados si existe perfil
with st.form("setup_form"):
    st.markdown(
        """
    <div class="section-highlight animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">📝</span>
            <div>
                <div class="font-semibold">Datos Personales</div>
                <div class="text-sm text-muted">Información básica para personalizar tu experiencia</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        edad = st.number_input(
            "Edad",
            min_value=10,
            max_value=100,
            value=int(existing_profile.get("edad", 20)) if existing_profile else 20,
            help="Tu edad actual en años",
        )
        sexo = st.selectbox(
            "Sexo",
            ["M", "F"],
            index=0
            if not existing_profile
            else (0 if existing_profile.get("sexo") == "M" else 1),
            help="Masculino o Femenino",
        )
        peso = st.number_input(
            "Peso (kg)",
            min_value=30.0,
            max_value=150.0,
            value=float(existing_profile.get("peso", 70.0))
            if existing_profile
            else 70.0,
            step=0.5,
            help="Tu peso corporal en kilogramos",
        )

    with col2:
        altura = st.number_input(
            "Altura (m)",
            min_value=1.0,
            max_value=2.2,
            value=float(existing_profile.get("altura", 1.70))
            if existing_profile
            else 1.70,
            step=0.01,
            help="Tu estatura en metros",
        )
        ciudad = st.selectbox(
            "Ciudad",
            ["Puno", "Juliaca", "Ilave", "Ayaviri", "Azangaro"],
            index=["Puno", "Juliaca", "Ilave", "Ayaviri", "Azangaro"].index(
                existing_profile.get("ciudad", "Puno")
            )
            if existing_profile
            else 0,
            help="Ciudad donde vives o estudias",
        )
        nivel = st.selectbox(
            "Nivel de actividad",
            ["bajo", "medio", "alto"],
            index=["bajo", "medio", "alto"].index(
                existing_profile.get("nivel_actividad", "medio")
            )
            if existing_profile
            else 1,
            help="Tu nivel de actividad física habitual",
        )

    st.markdown("---")

    button_text = "💾 Guardar Cambios" if is_editing else "✨ Crear Perfil"
    submitted = st.form_submit_button(
        button_text, use_container_width=True, type="primary"
    )

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
                        "nivel_actividad": nivel,
                    },
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

    # Grid de métricas moderno
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon">👤</div>
            <div class="metric-value">{existing_profile["edad"]}</div>
            <div class="metric-label">Edad (años)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.1s;">
            <div class="metric-icon">⚖️</div>
            <div class="metric-value">{existing_profile["peso"]}</div>
            <div class="metric-label">Peso (kg)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.2s;">
            <div class="metric-icon">🧬</div>
            <div class="metric-value">{existing_profile["sexo"]}</div>
            <div class="metric-label">Sexo</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.3s;">
            <div class="metric-icon">📏</div>
            <div class="metric-value">{existing_profile["altura"]}</div>
            <div class="metric-label">Altura (m)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.4s;">
            <div class="metric-icon">🏙️</div>
            <div class="metric-value">{existing_profile["ciudad"]}</div>
            <div class="metric-label">Ciudad</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.5s;">
            <div class="metric-icon">🏔️</div>
            <div class="metric-value">{existing_profile["altitud"]}</div>
            <div class="metric-label">Altitud (msnm)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Valores base calculados
    st.markdown("### 💧 Valores Base Calculados")
    st.markdown(
        "*Estos valores son calculados automáticamente por AG-INICIAL según tu perfil y altitud*"
    )

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(
            f"""
        <div class="metric-card success animate-fade-in">
            <div class="metric-icon">💧</div>
            <div class="metric-value">{existing_profile["agua_base_ml"]}</div>
            <div class="metric-label">Agua Diaria (ml)</div>
            <div class="text-sm text-muted">Ajustada por altitud</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
        <div class="metric-card success animate-fade-in" style="animation-delay: 0.1s;">
            <div class="metric-icon">😴</div>
            <div class="metric-value">{existing_profile["sueno_base_h"]}</div>
            <div class="metric-label">Sueño Diario (h)</div>
            <div class="text-sm text-muted">Horas recomendadas</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.2s;">
            <div class="metric-icon">🏃</div>
            <div class="metric-value">{existing_profile.get("nivel_actividad", "medio").title()}</div>
            <div class="metric-label">Nivel de Actividad</div>
            <div class="text-sm text-muted">Actividad física habitual</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
    <div class="section-highlight animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">📊</span>
            <div>
                <div class="font-semibold">¡Listo para monitorear!</div>
                <div class="text-sm text-muted">Tu perfil está completo. Ahora puedes registrar tu estado diario en el Monitor</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Monitor.py", label="📊 Ir al Monitor", icon="📊")
