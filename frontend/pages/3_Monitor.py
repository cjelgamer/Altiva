import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from pytz import timezone

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.agents.ag_fisio import run_ag_fisio
from backend.agents.ag_fatiga import run_ag_fatiga
from backend.agents.ag_plan import run_ag_plan
from backend.services.database import get_user_profile, daily_states

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
        max-width: 1400px !important;
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
    
    /* Headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    
    /* Sección izquierda (Fatiga) */
    .analysis-section {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .analysis-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    .ifa-display {
        text-align: center;
        margin: 2rem 0;
    }
    
    .ifa-score {
        font-size: 4rem;
        font-weight: 800;
        margin: 1rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    
    .ifa-status {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .ifa-description {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 1rem;
    }
    
    /* Sección derecha (Plan) */
    .plan-section {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .plan-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--success-color), var(--warning-color));
    }
    
    .chat-container {
        height: 400px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 1rem 0;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        background: var(--bg-secondary);
        border-left: 3px solid var(--primary-color);
    }
    
    .chat-message.bot {
        background: var(--bg-tertiary);
        border-left-color: var(--success-color);
    }
    
    .chat-time {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    /* Progress bars oscuros */
    .progress-modern {
        background: var(--bg-tertiary) !important;
        height: 8px !important;
        border-radius: 4px !important;
        overflow: hidden !important;
        margin: 0.5rem 0 !important;
    }
    
    .progress-fill-modern {
        height: 100% !important;
        border-radius: 4px !important;
        transition: width 0.3s ease !important;
    }
    
    /* Ocultar elementos de código HTML */
    .stMarkdown > div > div > code,
    .stMarkdown pre {
        display: none !important;
    }
    
    /* Área de alertas en esquina superior derecha */
    .alertas-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .alertas-header {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        color: white;
        padding: 1rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .alertas-content {
        max-height: 300px;
        overflow-y: auto;
        padding: 0.5rem;
    }
    
    .alerta-item {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .alerta-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .alerta-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }
    
    .alerta-item.alta::before {
        background: var(--error-color);
        animation: pulseAlert 2s infinite;
    }
    
    @keyframes pulseAlert {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    
    .alerta-item.media::before {
        background: var(--warning-color);
    }
    
    .alerta-item.baja::before {
        background: var(--success-color);
    }
    
    .alerta-tipo {
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alerta-mensaje {
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.4;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .alerta-accion {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 0.5rem;
        padding: 0.6rem 0.75rem;
        font-size: 0.85rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--primary-color);
    }
    
    .alerta-tiempo {
        color: var(--accent-color);
        font-size: 0.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .contador-section {
        background: var(--bg-secondary);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .contador-titulo {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .contador-progress {
        background: var(--bg-tertiary);
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.25rem 0;
    }
    
    .contador-progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .contador-text {
        font-size: 0.75rem;
        color: var(--text-muted);
        display: flex;
        justify-content: space-between;
        margin-top: 0.25rem;
    }
    
    /* Botón cerrar alertas */
    .alertas-cerrar {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        border-radius: 0.25rem;
        padding: 0.25rem 0.5rem;
        font-size: 0.7rem;
        cursor: pointer;
        margin-left: auto;
    }
    
    .alertas-cerrar:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Ocultar alertas temporalmente */
    .alertas-container.hidden {
        display: none;
    }
    
    /* Botón flotante para mostrar/ocultar alertas */
    .alertas-toggle {
        position: fixed;
        top: 80px;
        right: 20px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
        transition: all 0.2s ease;
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .alertas-toggle:hover {
        background: var(--primary-dark);
        transform: scale(1.1);
    }
    
    .alertas-toggle.con-alertas {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
        }
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .analysis-section,
        .plan-section {
            padding: 1.5rem;
        }
        
        .chat-container {
            height: 300px;
        }
        
        .alertas-container {
            position: fixed;
            top: 70px;
            right: 10px;
            left: 10px;
            max-width: none;
        }
        
        .alertas-toggle {
            top: 70px;
            right: 10px;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="ALTIVA - Monitor",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)


def main():
    # Verificar autenticación
    user_data = st.session_state.get("user")
    user_id = str(user_data.get("_id")) if user_data else None

    if not user_id:
        st.error("❌ Por favor, inicia sesión para continuar")
        st.page_link("app.py", label="🔐 Ir a Login", icon="🔐")
        st.stop()

    profile = get_user_profile(user_id)
    if not profile:
        st.error("❌ Por favor, completa tu perfil primero")
        st.page_link("pages/2_Setup.py", label="⚙️ Ir a Configuración", icon="⚙️")
        st.stop()

    # Logo ALTIVA
    logo_path = Path(__file__).parent.parent / "images" / "logo-altiva.png"
    logo_html = ""
    if logo_path.exists():
        import base64

        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{encoded_string}" style="width: 60px; height: 60px; border-radius: 0.75rem; margin-bottom: 1rem;">'

    # Header moderno oscuro con logo y botón de perfil
    st.markdown(
        f"""
    <div style="text-align: center; margin-bottom: 2rem; position: relative;">
        <div style="position: absolute; top: 0; left: 0;">
            <button onclick="window.location.href='pages/2_Setup.py'" style="background: var(--primary-color); color: white; border: none; border-radius: 0.5rem; padding: 0.5rem 1rem; font-size: 0.9rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: all 0.2s ease;" onmouseover="this.style.background='var(--primary-dark)'" onmouseout="this.style.background='var(--primary-color)'">
                👤 Perfil
            </button>
        </div>
        {logo_html}
        <h1 style="color: var(--text-primary); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
            📊 Monitor Diario
        </h1>
        <p style="color: var(--text-secondary); font-size: 1rem; margin: 0;">
            AG-FISIO • AG-FATIGA • AG-PLAN
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Botón funcional de Perfil
    if st.button("👤 Perfil", key="perfil_btn", help="Ir a configuración de perfil"):
        st.switch_page("pages/2_Setup.py")

    # Información del usuario
    st.markdown(
        f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2rem;">👤</div>
            <div>
                <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
                    {user_data.get("username") if user_data else "Usuario"}
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    🏙️ {profile.get("ciudad", "N/A")} ({profile.get("altitud", 0)}m) • 🏔️ ALTIVA System
                </div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Cargar datos del día
    def cargar_datos_dia():
        hoy_inicio = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        estado_reciente = daily_states.find_one(
            {
                "user_id": user_id,
                "agent": "AG-FISIO",
                "timestamp": {"$gte": hoy_inicio},
            },
            sort=[("timestamp", -1)],
        )

        if estado_reciente:
            indicadores = estado_reciente.get("indicadores", {})
            return {
                "agua": indicadores.get("agua_consumida_ml", 0),
                "sueno": indicadores.get("horas_sueno", 0),
                "actividad": indicadores.get("actividad_minutos", 0),
                "energia": indicadores.get("nivel_energia", 3),
            }
        return {"agua": 0, "sueno": 0, "actividad": 0, "energia": 3}

    # Session state para guardar datos
    if "datos_dia" not in st.session_state:
        st.session_state.datos_dia = cargar_datos_dia()

    # Session state para resultados del análisis
    if "analisis_resultados" not in st.session_state:
        st.session_state.analisis_resultados = None

    # Session state para control de alertas
    if "alertas_visibles" not in st.session_state:
        st.session_state.alertas_visibles = True

    datos = st.session_state.datos_dia

    # Sección 1: Estado Actual y Datos
    st.markdown("### 📈 Estado Actual")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        agua_meta = profile.get("agua_base_ml", 2000)
        agua_pct = min((datos["agua"] / agua_meta) * 100, 100)
        agua_color = (
            "var(--success-color)"
            if agua_pct >= 80
            else "var(--warning-color)"
            if agua_pct >= 50
            else "var(--error-color)"
        )

        st.markdown(
            f"""
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; text-align: center; border-left: 4px solid {agua_color};">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💧</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">{datos["agua"]}ml</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Hidratación</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {agua_pct}%; background: {agua_color};"></div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">{agua_pct:.0f}% del objetivo</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        sueno_meta = profile.get("sueno_base_h", 8)
        sueno_pct = min((datos["sueno"] / sueno_meta) * 100, 100)
        sueno_color = (
            "var(--success-color)"
            if sueno_pct >= 90
            else "var(--warning-color)"
            if sueno_pct >= 70
            else "var(--error-color)"
        )

        st.markdown(
            f"""
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; text-align: center; border-left: 4px solid {sueno_color};">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">😴</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">{datos["sueno"]}h</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Sueño</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {sueno_pct}%; background: {sueno_color};"></div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">{sueno_pct:.0f}% del objetivo</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        actividad_meta = max(profile.get("actividad_minutos", 30), 30)
        actividad_pct = min((datos["actividad"] / actividad_meta) * 100, 100)
        actividad_color = (
            "var(--success-color)"
            if actividad_pct >= 100
            else "var(--warning-color)"
            if actividad_pct >= 50
            else "var(--error-color)"
        )

        st.markdown(
            f"""
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; text-align: center; border-left: 4px solid {actividad_color};">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏃</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">{datos["actividad"]}min</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Actividad</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {actividad_pct}%; background: {actividad_color};"></div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">{actividad_pct:.0f}% del objetivo</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        energia_pct = (datos["energia"] / 5) * 100
        energia_color = (
            "var(--success-color)"
            if datos["energia"] >= 4
            else "var(--warning-color)"
            if datos["energia"] >= 3
            else "var(--error-color)"
        )

        st.markdown(
            f"""
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; text-align: center; border-left: 4px solid {energia_color};">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">{datos["energia"]}/5</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Energía</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {energia_pct}%; background: {energia_color};"></div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">Nivel actual</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Formulario de actualización (sin botón de actualizar, solo análisis)
    st.markdown("### 📝 Actualizar Datos")

    st.markdown(
        """
    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2rem;">📊</div>
            <div>
                <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
                    Registro Diario
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    Los datos se guardan automáticamente al cambiar
                </div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Guardado automático de datos al cambiar
    col_a, col_b = st.columns(2)

    with col_a:
        nueva_agua = st.number_input(
            "💧 Agua consumida hoy (ml)",
            min_value=0,
            max_value=10000,
            value=int(datos["agua"]),
            step=100,
            help="Cantidad total de agua ingerida hoy",
        )
        nueva_sueno = st.number_input(
            "😴 Horas de sueño",
            min_value=0.0,
            max_value=24.0,
            value=float(datos["sueno"]),
            step=0.5,
            help="Horas de sueño la noche anterior",
        )

    with col_b:
        nueva_actividad = st.number_input(
            "🏃 Actividad física (minutos)",
            min_value=0,
            max_value=300,
            value=int(datos["actividad"]),
            step=5,
            help="Minutos de actividad física realizada hoy",
        )
        energia_labels = [
            "1 - Muy bajo",
            "2 - Bajo",
            "3 - Normal",
            "4 - Bueno",
            "5 - Excelente",
        ]
        nueva_energia_actual = st.select_slider(
            "⚡ Nivel de energía",
            options=energia_labels,
            value=energia_labels[datos["energia"] - 1],
            help="¿Cómo te sientes de energía hoy?",
        )

    # Guardar datos automáticamente si cambian y guardar en MongoDB
    if (
        nueva_agua != datos["agua"]
        or nueva_sueno != datos["sueno"]
        or nueva_actividad != datos["actividad"]
        or int(nueva_energia_actual.split(" - ")[0]) != datos["energia"]
    ):
        energia_valor = int(nueva_energia_actual.split(" - ")[0])

        # Actualizar session state
        st.session_state.datos_dia = {
            "agua": nueva_agua,
            "sueno": nueva_sueno,
            "actividad": nueva_actividad,
            "energia": energia_valor,
        }

        # Guardar en MongoDB usando AG-FISIO
        with st.spinner("💾 Guardando en MongoDB..."):
            try:
                run_ag_fisio(
                    user_id,
                    {
                        "agua_consumida_ml": nueva_agua,
                        "horas_sueno": nueva_sueno,
                        "actividad_minutos": nueva_actividad,
                        "nivel_energia": energia_valor,
                    },
                )
                st.success("✅ Datos guardados en MongoDB automáticamente")
            except Exception as e:
                st.error(f"❌ Error al guardar en MongoDB: {str(e)}")
        st.rerun()

    # Botón de análisis
    st.markdown("---")

    if st.button(
        "🔄 Analizar Estado",
        use_container_width=True,
        type="primary",
        key="analizar_btn",
    ):
        energia_valor = int(nueva_energia_actual.split(" - ")[0])

        with st.spinner("🤖 Analizando tu estado..."):
            # Actualizar estado fisiológico
            estado_fisio = run_ag_fisio(
                user_id,
                {
                    "agua_consumida_ml": nueva_agua,
                    "horas_sueno": nueva_sueno,
                    "actividad_minutos": nueva_actividad,
                    "nivel_energia": energia_valor,
                },
            )

            # Analizar fatiga
            resultado_fatiga = run_ag_fatiga(user_id, estado_fisio)

            # Generar plan
            historial_dia = list(
                daily_states.find(
                    {
                        "user_id": user_id,
                        "timestamp": {
                            "$gte": datetime.utcnow().replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                        },
                    }
                ).sort("timestamp", -1)
            )

            resultado_plan = (
                run_ag_plan(user_id, resultado_fatiga, historial_dia)
                if resultado_fatiga
                else {"plan": {}}
            )

            # Guardar resultados en session state
            st.session_state.analisis_resultados = {
                "fatiga": resultado_fatiga,
                "plan": resultado_plan,
            }

        st.success("✅ ¡Análisis completado!")

        # Mostrar alertas si hay
        alertas_activas = resultado_fatiga.get("alertas", [])
        if alertas_activas:
            st.session_state.alertas_visibles = True

        st.rerun()

    # Sección 2: Resultados del Análisis (solo AG-FATIGA)
    if st.session_state.analisis_resultados:
        st.markdown("---")
        st.markdown("### 🎯 Resultados del Análisis")

        resultados = st.session_state.analisis_resultados
        resultado_fatiga = resultados["fatiga"]

        # Mostrar solo análisis de fatiga en columna completa
        with st.container():
            # Sección izquierda: Análisis de Fatiga
            st.markdown(
                """
            <div class="analysis-section">
                <h3 style="color: var(--text-primary); margin-bottom: 1.5rem;">
                    🧠 Análisis de Fatiga
                </h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # IFA
            ifa = resultado_fatiga.get("ifa", 0) if resultado_fatiga else 0
            nivel = (
                resultado_fatiga.get("nivel_fatiga", "Medio")
                if resultado_fatiga
                else "Medio"
            )

            if ifa < 34:
                ifa_color = "var(--success-color)"
                emoji = "🟢"
                estado = "Óptimo"
            elif ifa < 67:
                ifa_color = "var(--warning-color)"
                emoji = "🟡"
                estado = "Moderado"
            else:
                ifa_color = "var(--error-color)"
                emoji = "🔴"
                estado = "Crítico"

            st.markdown(
                f"""
            <div class="analysis-section">
                <div class="ifa-display">
                    <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Índice de Fatiga en Altura</h4>
                    <div class="ifa-score" style="color: {ifa_color};">{ifa}/100</div>
                    <div class="ifa-status">{emoji} {estado}</div>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 1rem;">📈 Justificación del Análisis</h4>
                    <div class="ifa-description">
                        {resultado_fatiga.get("justificacion", "Sin justificación disponible") if resultado_fatiga else "Sin justificación disponible"}
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Mostrar alertas flotantes si hay análisis
    if st.session_state.analisis_resultados:
        resultado_fatiga = st.session_state.analisis_resultados.get("fatiga", {})
        alertas = resultado_fatiga.get("alertas", [])
        contadores = resultado_fatiga.get("contadores", {})

        if alertas and st.session_state.alertas_visibles:
            st.markdown(
                f"""
            <div class="alertas-container" id="alertasContainer">
                <div class="alertas-header">
                    <span>🔔 Alertas de Bienestar</span>
                    <button class="alertas-cerrar" onclick="document.getElementById('alertasContainer').style.display='none'">✕</button>
                </div>
                <div class="alertas-content">
            """,
                unsafe_allow_html=True,
            )

            # Mostrar resumen de alertas primero
            alertas_urgentes = [a for a in alertas if a.get("prioridad") == "alta"]
            alertas_medias = [a for a in alertas if a.get("prioridad") == "media"]
            alertas_bajas = [a for a in alertas if a.get("prioridad") == "baja"]

            # Resumen rápido al principio
            if alertas_urgentes:
                st.markdown(
                    f"""
                <div style="background: var(--error-color); color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem; text-align: center; font-weight: 600;">
                    ⚠️ {len(alertas_urgentes)} alerta(s) urgente(s) requiere(n) atención inmediata
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Mostrar cada alerta con información clara al inicio
            for i, alerta in enumerate(alertas):
                tipo_emoji = {
                    "hidratacion": "💧",
                    "descanso": "😴",
                    "actividad": "🏃",
                    "energia": "⚡",
                }.get(alerta.get("tipo", "info"), "ℹ️")

                # Extraer información clave del mensaje para mostrarla destacada
                mensaje_principal = (
                    alerta.get("mensaje", "Sin mensaje").split(".")[0] + "."
                )

                st.markdown(
                    f"""
                <div class="alerta-item {alerta.get("prioridad", "media")}" onclick="this.style.transform='scale(0.98)'; setTimeout(() => this.style.transform='scale(1)', 100)">
                    <div class="alerta-tipo">
                        {tipo_emoji} <span style="text-transform: uppercase; font-size: 0.8rem;">{alerta.get("tipo", "INFO")}</span>
                        <span style="margin-left: auto; padding: 0.2rem 0.5rem; background: {"var(--error-color)" if alerta.get("prioridad") == "alta" else "var(--warning-color)" if alerta.get("prioridad") == "media" else "var(--success-color)"}; color: white; border-radius: 0.25rem; font-size: 0.7rem;">
                            {alerta.get("prioridad", "media").upper()}
                        </span>
                    </div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 0.95rem; margin-bottom: 0.5rem; line-height: 1.3;">
                        {mensaje_principal}
                    </div>
                    <div class="alerta-accion">
                        💡 <strong>Acción:</strong> {alerta.get("accion_sugerida", "Sin acción sugerida")}
                    </div>
                    <div class="alerta-tiempo">
                        ⏰ <strong>Cuándo:</strong> {alerta.get("tiempo_recomendado", "Ahora")}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Mostrar contadores
            if contadores:
                # Contador de hidratación
                hidratacion = contadores.get("hidratacion", {})
                if hidratacion:
                    pct_hidratacion = (
                        hidratacion.get("consumido_ml", 0)
                        / hidratacion.get("objetivo_ml", 1)
                    ) * 100
                    color_h = (
                        "var(--success-color)"
                        if pct_hidratacion >= 80
                        else "var(--warning-color)"
                        if pct_hidratacion >= 50
                        else "var(--error-color)"
                    )

                    st.markdown(
                        f"""
                    <div class="contador-section">
                        <div class="contador-titulo">💧 Hidratación</div>
                        <div class="contador-progress">
                            <div class="contador-progress-fill" style="width: {pct_hidratacion}%; background: {color_h};"></div>
                        </div>
                        <div class="contador-text">
                            <span>{hidratacion.get("consumido_ml", 0)}ml</span>
                            <span>{hidratacion.get("objetivo_ml", 0)}ml objetivo</span>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Contador de actividad
                actividad = contadores.get("actividad", {})
                if actividad:
                    pct_actividad = (
                        actividad.get("realizado_min", 0)
                        / actividad.get("objetivo_min", 1)
                    ) * 100
                    color_a = (
                        "var(--success-color)"
                        if pct_actividad >= 100
                        else "var(--warning-color)"
                        if pct_actividad >= 50
                        else "var(--error-color)"
                    )

                    st.markdown(
                        f"""
                    <div class="contador-section">
                        <div class="contador-titulo">🏃 Actividad</div>
                        <div class="contador-progress">
                            <div class="contador-progress-fill" style="width: {pct_actividad}%; background: {color_a};"></div>
                        </div>
                        <div class="contador-text">
                            <span>{actividad.get("realizado_min", 0)}min</span>
                            <span>{actividad.get("objetivo_min", 0)}min objetivo</span>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Botón para ir al chat de AG-PLAN (solo si hay análisis)
        st.markdown(
            """
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "💬 Ir al Chat con AG-PLAN",
            type="primary",
            use_container_width=True,
            key="go_to_plan_chat_unique",
            help="Abre el chat interactivo con el asistente AG-PLAN",
        ):
            st.switch_page("pages/4_plan.py")

        st.markdown(
            """
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                💡 Conversa con el asistente AG-PLAN para obtener recomendaciones personalizadas
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Botón flotante para mostrar/ocultar alertas
        if alertas:
            alert_count = len(alertas)
            alta_priority = any(a.get("prioridad") == "alta" for a in alertas)
            toggle_class = "con-alertas" if alta_priority else ""

            st.markdown(
                f"""
            <button class="alertas-toggle {toggle_class}" onclick="toggleAlertas()">
                {"🔔" if st.session_state.alertas_visibles else "🔕"}
            </button>
            
            <script>
            function toggleAlertas() {{
                var container = document.getElementById('alertasContainer');
                var button = document.querySelector('.alertas-toggle');
                
                if (container && container.style.display === 'none') {{
                    container.style.display = 'block';
                    button.innerHTML = '🔔';
                }} else if (container) {{
                    container.style.display = 'none';
                    button.innerHTML = '🔕';
                }}
            }}
            </script>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
