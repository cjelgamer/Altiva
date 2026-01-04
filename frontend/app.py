import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.services.auth import login_user, register_user
from backend.services.database import get_user_profile


# --- CARGAR ESTILOS MODERNOS DE ALTIVA ---
def load_modern_css():
    """Carga el CSS moderno con animaciones y diseño mobile-first"""
    css_file = ROOT_DIR / "frontend" / "styles" / "altiva.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_modern_css()

# --- CONFIGURACIÓN DE PÁGINA SIN NAVEGACIÓN ---
st.set_page_config(
    page_title="ALTIVA",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🏔️",
)

# --- OCULTAR ELEMENTOS DE STREAMLIT ---
st.markdown(
    """
<style>
    /* Ocultar completamente la navegación de Streamlit */
    .stSidebar {
        display: none !important;
    }
    
    /* Ocultar el menú de hamburguesa */
    .stMainMenu {
        visibility: hidden;
    }
    
    /* Ocultar el footer */
    footer {
        visibility: hidden;
    }
    
    /* Ocultar el deploy menu y otros controles */
    .stDeployButton {
        visibility: hidden;
    }
    
    /* Ocultar report bug */
    .stDebugButton {
        visibility: hidden;
    }
    
    /* Ocultar page links por defecto */
    [data-testid="stPageLink-NavLink"] {
        display: none !important;
    }
    
    /* Ocultar el header por defecto */
    .stApp > header {
        display: none !important;
    }
    
    /* Header personalizado ALTIVA */
    .altiva-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        text-align: center;
        border-radius: 0 0 2rem 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
        margin-bottom: 3rem;
    }
    
    .altiva-header::before {
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
    
    .altiva-logo {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(45deg, white, rgba(255,255,255,0.8));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 1rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); }
        50% { text-shadow: 0 0 30px rgba(255, 255, 255, 0.8); }
    }
    
    .altiva-tagline {
        font-size: 1.2rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
    }
    
    /* Cards de autenticación */
    .auth-card {
        background: white;
        border-radius: 1.5rem;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(226, 232, 240, 0.5);
        max-width: 450px;
        margin: 0 auto;
        position: relative;
        overflow: hidden;
    }
    
    .auth-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .auth-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .auth-subtitle {
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    /* Botones de navegación personalizados */
    .nav-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        max-width: 500px;
        margin: 2rem auto;
    }
    
    .nav-button {
        background: white;
        border: 2px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        color: var(--text-primary);
        display: block;
        position: relative;
        overflow: hidden;
    }
    
    .nav-button:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border-color: var(--primary-color);
    }
    
    .nav-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .nav-button:hover::before {
        transform: translateX(0);
    }
    
    .nav-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .nav-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .nav-description {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    /* Ocultar inputs por defecto y personalizar */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 1rem !important;
        border: 2px solid var(--border-color) !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Etiquetas de formularios */
    .stTextInput > label,
    .stSelectbox > label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Botones de acción */
    .stButton > button {
        border-radius: 1rem !important;
        font-weight: 600 !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
        border: none !important;
        width: 100% !important;
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
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Tabs personalizados */
    .auth-tabs {
        display: flex;
        background: var(--bg-tertiary);
        border-radius: 1rem;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .auth-tab {
        flex: 1;
        padding: 1rem;
        text-align: center;
        border-radius: 0.75rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        color: var(--text-secondary);
    }
    
    .auth-tab.active {
        background: var(--primary-gradient);
        color: white;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 1rem !important;
        border-left: 4px solid !important;
        font-size: 0.95rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    .stAlert p {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .nav-container {
            grid-template-columns: 1fr;
            gap: 1rem;
            max-width: 100%;
            padding: 0 1rem;
        }
        
        .auth-card {
            padding: 2rem;
            margin: 0 1rem;
        }
        
        .altiva-header {
            padding: 2rem 1rem;
        }
        
        .altiva-logo {
            font-size: 3rem;
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

    user_id = str(user_data.get("_id"))

    # Header personalizado
    st.markdown(
        f"""
    <div class="altiva-header">
        <div class="altiva-logo">🏔️ ALTIVA</div>
        <div class="altiva-tagline">Sistema Inteligente de Monitoreo en Altura</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Mensaje de bienvenida
    username = user_data.get("username", "Usuario") if user_data else "Usuario"
    st.markdown(
        f"""
    <div class="auth-card animate-fade-in">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                ¡Bienvenido de nuevo, {username}!
            </div>
            <div style="color: var(--text-secondary); margin-bottom: 2rem;">
                ¿Qué te gustaría hacer hoy?
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Botones de navegación principales
    st.markdown(
        """
    <div class="nav-container">
        <a href="#" onclick="window.location.href='pages/2_Setup.py'" class="nav-button">
            <span class="nav-icon">⚙️</span>
            <div class="nav-title">Configurar Perfil</div>
            <div class="nav-description">Ajusta tu información personal</div>
        </a>
        <a href="#" onclick="window.location.href='pages/3_Monitor.py'" class="nav-button">
            <span class="nav-icon">📊</span>
            <div class="nav-title">Monitor Diario</div>
            <div class="nav-description">Registra tu estado actual</div>
        </a>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Botones funcionales (los que realmente funcionan en Streamlit)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⚙️ Configurar Perfil", use_container_width=True, key="setup_btn"):
            navigate_to("pages/2_Setup.py")

    with col2:
        if st.button("📊 Monitor Diario", use_container_width=True, key="monitor_btn"):
            navigate_to("pages/3_Monitor.py")

    # Verificar si tiene perfil
    if user_id:
        try:
            profile = get_user_profile(user_id)
            if profile:
                st.markdown("---")
                st.markdown("### 📋 Tu Resumen Rápido")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏙️ Ciudad", profile.get("ciudad", "N/A"))
                    st.metric("🏔️ Altitud", f"{profile.get('altitud', 0)}m")
                with col2:
                    st.metric("💧 Agua Meta", f"{profile.get('agua_base_ml', 0)}ml")
                    st.metric("😴 Sueño Meta", f"{profile.get('sueno_base_h', 0)}h")
                with col3:
                    st.metric("⚖️ Peso", f"{profile.get('peso', 0)}kg")
                    st.metric("📏 Altura", f"{profile.get('altura', 0)}m")
        except Exception as e:
            st.error(f"❌ Error al cargar el perfil: {str(e)}")

        # Botón de logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def show_auth():
    """Mostrar pantalla de autenticación"""
    # Header personalizado
    st.markdown(
        """
    <div class="altiva-header">
        <div class="altiva-logo">🏔️ ALTIVA</div>
        <div class="altiva-tagline">Sistema Inteligente de Monitoreo en Altura</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sistema de tabs personalizado
    tab1, tab2 = st.columns(2)

    with tab1:
        login_selected = st.button(
            "🔐 Iniciar Sesión", use_container_width=True, key="login_tab"
        )

    with tab2:
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

    # Mostrar el modo actual
    if st.session_state.auth_mode == "login":
        show_login_form()
    else:
        show_register_form()


def show_login_form():
    """Mostrar formulario de login"""
    st.markdown(
        """
    <div class="auth-card animate-fade-in">
        <div class="auth-title">🔐 Iniciar Sesión</div>
        <div class="auth-subtitle">Accede a tu cuenta ALTIVA</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
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

            with st.spinner("🔐 Verificando credenciales..."):
                result = login_user(username, password)

                if result["success"]:
                    st.session_state.user = result["user"]
                    st.success(f"✅ ¡Bienvenido {username}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")


def show_register_form():
    """Mostrar formulario de registro"""
    st.markdown(
        """
    <div class="auth-card animate-fade-in">
        <div class="auth-title">✏️ Crear Cuenta</div>
        <div class="auth-subtitle">Únete a ALTIVA hoy mismo</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("register_form"):
        username = st.text_input("👤 Usuario", placeholder="Elige un nombre de usuario")
        password = st.text_input(
            "🔒 Contraseña", type="password", placeholder="Crea una contraseña segura"
        )
        confirm_password = st.text_input(
            "🔁 Confirmar Contraseña",
            type="password",
            placeholder="Repite tu contraseña",
        )

        submitted = st.form_submit_button(
            "🌟 Crear Cuenta", use_container_width=True, type="primary"
        )

        if submitted:
            if not username or not password or not confirm_password:
                st.error("⚠️ Por favor, completa todos los campos")
                return

            if password != confirm_password:
                st.error("⚠️ Las contraseñas no coinciden")
                return

            if len(password) < 6:
                st.error("⚠️ La contraseña debe tener al menos 6 caracteres")
                return

            with st.spinner("🌟 Creando tu cuenta..."):
                result = register_user(username, password)

                if result["success"]:
                    st.success(
                        f"✅ ¡Cuenta creada para {username}! Ahora puedes iniciar sesión."
                    )
                    st.session_state.auth_mode = "login"  # Cambiar a login
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")


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
