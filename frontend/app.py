import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.services.auth import login_user, register_user
from backend.services.database import get_user_profile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="ALTIVA",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🏔️",
)

# --- ESTILO OSCURO MODERNO CON AJUSTES ---
st.markdown(
    """
<style>
    /* Reset y variables oscuras */
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
    
    /* Ocultar completamente elementos de Streamlit */
    .stSidebar,
    .stMainMenu,
    .stDeployButton,
    .stDebugButton,
    [data-testid="stPageLink-NavLink"] {
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
        max-width: 800px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Fondo oscuro */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: var(--text-primary) !important;
        min-height: 100vh;
    }
    
    /* Contenedor principal centrado */
    .main-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - 6rem);
        padding: 2rem;
    }
    
    /* Login card compacto */
    .login-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2.5rem;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .login-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    /* Logo y título */
    .logo-section {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .logo-img {
        width: 80px;
        height: 80px;
        margin-bottom: 1rem;
        border-radius: 1rem;
    }
    
    .logo {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .subtitle {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Tabs de auth */
    .auth-tabs {
        display: flex;
        background: var(--bg-tertiary);
        border-radius: 0.75rem;
        padding: 0.25rem;
        margin-bottom: 2rem;
    }
    
    .auth-tab {
        flex: 1;
        padding: 0.75rem;
        text-align: center;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        background: transparent;
        color: var(--text-secondary);
    }
    
    .auth-tab:hover {
        background: var(--bg-secondary);
    }
    
    .auth-tab.active {
        background: var(--primary-color);
        color: white;
    }
    
    /* Form inputs oscuros */
    .stTextInput > div > div > input,
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
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        outline: none !important;
    }
    
    .stTextInput > label,
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
        font-size: 0.95rem !important;
        width: 100% !important;
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
        margin-bottom: 1.5rem !important;
        font-size: 0.9rem !important;
    }
    
    .stAlert[data-baseweb="toast"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stAlert p {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Dashboard compacto */
    .dashboard-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        max-width: 500px;
        margin: 0 auto;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .welcome-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }
    
    /* Navigation buttons */
    .nav-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .nav-button {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
        text-decoration: none;
        color: var(--text-primary);
        display: block;
    }
    
    .nav-button:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-color);
        transform: translateY(-2px);
    }
    
    .nav-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .nav-title {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    
    .nav-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    /* Ocultar elementos de código HTML */
    .stMarkdown > div > div > code,
    .stMarkdown pre {
        display: none !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .nav-buttons {
            grid-template-columns: 1fr;
        }
        
        .login-card {
            padding: 2rem 1.5rem;
            margin: 1rem;
        }
        
        .dashboard-card {
            padding: 1.5rem;
            margin: 1rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- FUNCIÓN PARA CAMBIAR DE PÁGINA ---
def navigate_to(page_path):
    """Función personalizada para navegar entre páginas"""
    st.switch_page(page_path)


# --- VERIFICAR SESIÓN ACTIVA ---
def show_dashboard():
    """Mostrar el dashboard principal si el usuario está logueado"""
    user_data = st.session_state.get("user")
    if not user_data:
        st.error("❌ Error en la sesión. Por favor, inicia sesión nuevamente.")
        if st.button("🔄 Volver al Login", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return

    username = user_data.get("username", "Usuario")

    # Logo ALTIVA
    logo_path = Path(__file__).parent / "images" / "logo-altiva.png"
    logo_html = ""
    if logo_path.exists():
        import base64

        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            logo_html = (
                f'<img src="data:image/png;base64,{encoded_string}" class="logo-img">'
            )

    st.markdown(
        f"""
    <div class="main-container">
        <div class="dashboard-card">
            <div class="logo-section">
                {logo_html}
                <h2 class="welcome-title">¡Bienvenido, {username}!</h2>
                <p class="welcome-subtitle">¿Qué te gustaría hacer hoy?</p>
            </div>
            
            <div class="nav-buttons">
                <a href="#" onclick="window.location.href='pages/2_Setup.py'" class="nav-button">
                    <span class="nav-icon">⚙️</span>
                    <div class="nav-title">Configurar Perfil</div>
                    <div class="nav-desc">Ajusta tu información</div>
                </a>
                <a href="#" onclick="window.location.href='pages/3_Monitor.py'" class="nav-button">
                    <span class="nav-icon">📊</span>
                    <div class="nav-title">Monitor Diario</div>
                    <div class="nav-desc">Registra tu estado</div>
                </a>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Botones funcionales
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⚙️ Configurar Perfil", use_container_width=True, key="setup_btn"):
            navigate_to("pages/2_Setup.py")

    with col2:
        if st.button("📊 Monitor Diario", use_container_width=True, key="monitor_btn"):
            navigate_to("pages/3_Monitor.py")

    # Botón de logout
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()


def show_auth():
    """Mostrar pantalla de autenticación"""
    # Sistema de tabs
    col1, col2 = st.columns(2)

    with col1:
        login_selected = st.button(
            "🔐 Iniciar Sesión", use_container_width=True, key="login_tab"
        )

    with col2:
        register_selected = st.button(
            "✏️ Registrarse", use_container_width=True, key="register_tab"
        )

    # Determinar qué tab mostrar
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if login_selected:
        st.session_state.auth_mode = "login"
    elif register_selected:
        st.session_state.auth_mode = "register"

    # Logo ALTIVA
    logo_path = Path(__file__).parent / "images" / "logo-altiva.png"
    logo_html = ""
    if logo_path.exists():
        import base64

        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            logo_html = (
                f'<img src="data:image/png;base64,{encoded_string}" class="logo-img">'
            )

    st.markdown(
        f"""
    <div class="main-container">
        <div class="login-card">
            <div class="logo-section">
                {logo_html}
                <div class="logo">ALTIVA</div>
                <p class="subtitle">Sistema de Monitoreo en Altura</p>
            </div>
            
            <div class="auth-tabs">
                <button class="auth-tab {"active" if st.session_state.auth_mode == "login" else ""}">
                    Iniciar Sesión
                </button>
                <button class="auth-tab {"active" if st.session_state.auth_mode == "register" else ""}">
                    Registrarse
                </button>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Mostrar el formulario correspondiente
    if st.session_state.auth_mode == "login":
        show_login_form()
    else:
        show_register_form()


def show_login_form():
    """Mostrar formulario de login"""
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("👤 Usuario", placeholder="Tu nombre de usuario")
        password = st.text_input(
            "🔒 Contraseña", type="password", placeholder="Tu contraseña"
        )

        submitted = st.form_submit_button(
            "🚀 Iniciar Sesión", use_container_width=True, type="primary"
        )

        if submitted:
            if not username or not password:
                st.error("⚠️ Por favor, completa todos los campos")
                return

            with st.spinner("🔐 Verificando..."):
                result = login_user(username, password)

                if result.get("success"):
                    st.session_state.user = result.get("user")
                    st.success(f"✅ ¡Bienvenido {username}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('message', 'Error en el login')}")


def show_register_form():
    """Mostrar formulario de registro"""
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("👤 Usuario", placeholder="Elige un nombre de usuario")
        password = st.text_input(
            "🔒 Contraseña", type="password", placeholder="Crea una contraseña"
        )
        confirm_password = st.text_input(
            "🔁 Confirmar", type="password", placeholder="Repite tu contraseña"
        )

        submitted = st.form_submit_button(
            "🌟 Crear Cuenta", use_container_width=True, type="primary"
        )

        if submitted:
            if not username or not password or not confirm_password:
                st.error("⚠️ Completa todos los campos")
                return

            if password != confirm_password:
                st.error("⚠️ Las contraseñas no coinciden")
                return

            if len(password) < 6:
                st.error("⚠️ Mínimo 6 caracteres")
                return

            with st.spinner("🌟 Creando cuenta..."):
                result = register_user(username, password)

                if result.get("success"):
                    st.success(f"✅ ¡Cuenta creada! Ahora inicia sesión.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('message', 'Error al crear cuenta')}")


# --- LÓGICA PRINCIPAL ---
def main():
    """Función principal de la aplicación"""
    # Verificar si el usuario ya está logueado
    if "user" in st.session_state and st.session_state.user is not None:
        show_dashboard()
    else:
        show_auth()


if __name__ == "__main__":
    main()
