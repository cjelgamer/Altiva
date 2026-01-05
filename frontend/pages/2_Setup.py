import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.crew.crew import run_initial_crew
from backend.services.database import has_user_profile, get_user_profile, user_profiles
from backend.services.altitude_loader import get_all_cities

# --- ESTILO OSCURO MODERNO CON AJUSTES ---
st.markdown(
    """
<style>
    /* Variables oscuras */
    :root {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --primary-color: #3b82f6;
        --primary-dark: #2563eb;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --border-color: #334155;
        --border-light: #475569;
    }
    
    /* Ocultar elementos de Streamlit */
    .stSidebar,
    .stMainMenu,
    .stDeployButton,
    .stDebugButton {
        display: none !important;
    }
    
    /* Ocultar header por defecto pero dejar espacio */
    .stApp > header {
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }
    
    /* Aumentar padding superior para contenido */
    .block-container {
        padding-top: 3rem !important;
        max-width: 900px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: var(--text-primary) !important;
    }
    
    /* Form inputs oscuros */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        outline: none !important;
    }
    
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Botones oscuros */
    .stButton > button {
        background: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Alertas oscuras */
    .stAlert {
        border-radius: 0.5rem !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        margin-bottom: 1.5rem !important;
        font-size: 0.9rem !important;
    }
    
    .stAlert p, .stAlert div, .stAlert span {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Métricas oscuras */
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
    
    /* Page links oscuros */
    a[data-testid="stPageLink-NavLink"] {
        background: var(--primary-color) !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.5rem !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        display: inline-block !important;
        margin-top: 0.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    a[data-testid="stPageLink-NavLink"]:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Cards oscuras */
    .metric-card {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0.75rem !important;
        padding: 1.5rem !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    
    .metric-card:hover {
        border-color: var(--primary-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    .metric-icon {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    
    .metric-value {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.25rem !important;
    }
    
    .metric-label {
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    /* Headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    
    /* Ocultar elementos de código HTML */
    .stMarkdown > div > div > code,
    .stMarkdown pre {
        display: none !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .metric-card {
            padding: 1rem !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="ALTIVA - Configuración",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚙️",
)

# Logo ALTIVA
logo_path = Path(__file__).parent.parent / "images" / "logo-altiva.png"
logo_html = ""
if logo_path.exists():
    import base64

    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{encoded_string}" style="width: 60px; height: 60px; border-radius: 0.75rem; margin-bottom: 1rem;">'

# Header moderno oscuro con logo
st.markdown(
    f"""
<div style="text-align: center; margin-bottom: 2rem;">
    {logo_html}
    <h1 style="color: var(--text-primary); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
        ⚙️ Configuración de Perfil
    </h1>
    <p style="color: var(--text-secondary); font-size: 1rem; margin: 0;">
        AG-INICIAL: Perfil Fisiológico Base
    </p>
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

# Obtener perfil existente
existing_profile = get_user_profile(user_id)
is_editing = existing_profile is not None

# Modo edición o creación
if is_editing:
    st.markdown(
        """
    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✏️</div>
            <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
                Modo Edición
            </div>
            <div style="color: var(--text-muted); font-size: 0.9rem;">
                Modifica los datos que necesites actualizar
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✨</div>
            <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
                Primer Uso
            </div>
            <div style="color: var(--text-muted); font-size: 0.9rem;">
                Completa tu perfil inicial
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Formulario
with st.form("setup_form"):
    st.markdown("### 📝 Datos Personales")

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
        # Cargar ciudades dinámicamente desde el JSON
        todas_las_ciudades = get_all_cities()

        # Mostrar información de depuración
        if todas_las_ciudades:
            st.markdown(f"🔍 **Debug**: {len(todas_las_ciudades)} ciudades disponibles")
        else:
            st.error("⚠️ No se pudieron cargar las ciudades del JSON")

        # Encontrar el índice de la ciudad guardada
        indice_ciudad = 0
        ciudad_guardada = (
            existing_profile.get("ciudad", "Puno") if existing_profile else "Puno"
        )

        if ciudad_guardada in todas_las_ciudades:
            indice_ciudad = todas_las_ciudades.index(ciudad_guardada)
        else:
            # Si la ciudad guardada no está en la lista, usar la primera
            st.warning(
                f"⚠️ Ciudad '{ciudad_guardada}' no encontrada, usando Puno por defecto"
            )
            indice_ciudad = 0

        ciudad = st.selectbox(
            "Ciudad",
            todas_las_ciudades,
            index=indice_ciudad,
            help="Ciudad donde vives o estudias",
        )

        nivel_guardado = (
            existing_profile.get("nivel_actividad", "medio")
            if existing_profile
            else "medio"
        )

        nivel_map = {"bajo": 0, "medio": 1, "alto": 2}
        index_valor = nivel_map.get(nivel_guardado, 1) if existing_profile else 1

        nivel = st.selectbox(
            "Nivel de actividad",
            ["bajo", "medio", "alto"],
            index=index_valor,
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

    # Grid de métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-icon">👤</div>
            <div class="metric-value">{existing_profile["edad"]}</div>
            <div class="metric-label">Edad (años)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card">
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
        <div class="metric-card">
            <div class="metric-icon">🧬</div>
            <div class="metric-value">{existing_profile["sexo"]}</div>
            <div class="metric-label">Sexo</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card">
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
        <div class="metric-card">
            <div class="metric-icon">🏙️</div>
            <div class="metric-value">{existing_profile["ciudad"]}</div>
            <div class="metric-label">Ciudad</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="metric-card">
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
        <div class="metric-card">
            <div class="metric-icon">💧</div>
            <div class="metric-value">{existing_profile["agua_base_ml"]}</div>
            <div class="metric-label">Agua Diaria (ml)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-icon">😴</div>
            <div class="metric-value">{existing_profile["sueno_base_h"]}</div>
            <div class="metric-label">Sueño Diario (h)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-icon">🏃</div>
            <div class="metric-value">{existing_profile.get("nivel_actividad", "medio").title()}</div>
            <div class="metric-label">Nivel de Actividad</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🚀 ¡Listo para monitorear!")
    st.markdown(
        "Tu perfil está completo. Ahora puedes registrar tu estado diario en el Monitor."
    )
    st.page_link("pages/3_Monitor.py", label="📊 Ir al Monitor", icon="📊")
