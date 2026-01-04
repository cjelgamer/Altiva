import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.services.auth import login_user, register_user

st.set_page_config(
    page_title="ALTIVA",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🏔️"
)

# --- DISEÑO SEPIA CLARO CON ROJO Y CELESTE ---
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
        padding-top: 4rem;
        max-width: 450px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        color: #2c3e50 !important;
        font-weight: 300 !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #8b7355;
        font-size: 1rem;
        margin-bottom: 2.5rem;
    }
    
    /* Tabs con celeste */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #e8dfd5;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 0 2rem;
        background: transparent;
        border: none;
        color: #8b7355;
        font-weight: 500;
        border-radius: 6px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3498db;
        color: white;
    }
    
    .stTextInput > div > div > input {
        border: 1px solid #e8dfd5;
        border-radius: 8px;
        padding: 0.875rem 1rem;
        background: white !important;
        color: #2c3e50 !important;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #c4b5a0 !important;
    }
    
    .stTextInput > label {
        color: #5a6c7d !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Botón celeste */
    .stButton > button {
        background: #3498db;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.875rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        background: #2980b9;
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
    
    div[data-baseweb="notification"][kind="error"] {
        border-left-color: #e74c3c;
    }
    
    div[data-baseweb="notification"][kind="success"] {
        border-left-color: #3498db;
    }
    
    div[data-baseweb="notification"][kind="warning"] {
        border-left-color: #e74c3c;
    }
    
    div[data-baseweb="notification"][kind="info"] {
        border-left-color: #3498db;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 2rem;
    }
    
    /* Form submit con Enter */
    .stForm {
        border: none !important;
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

# --- SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN ---
if st.session_state.user is None:
    
    st.title("ALTIVA")
    st.markdown('<p class="subtitle">Sistema de Fatiga en Altura</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta"])

    with tab1:
        # FORMULARIO CON ENTER
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="Tu usuario")
            pwd = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                if user and pwd:
                    result = login_user(user, pwd)
                    if result:
                        st.session_state.user = result
                        st.success("✓ Bienvenido")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.warning("Completa todos los campos")

    with tab2:
        # FORMULARIO CON ENTER
        with st.form("register_form"):
            new_user = st.text_input("Usuario", placeholder="Elige un usuario")
            new_pwd = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            submitted = st.form_submit_button("Registrar", use_container_width=True)
            
            if submitted:
                if new_user and new_pwd:
                    if len(new_pwd) < 6:
                        st.warning("La contraseña debe tener al menos 6 caracteres")
                    else:
                        ok = register_user(new_user, new_pwd)
                        if ok:
                            st.success("✓ Cuenta creada. Ahora inicia sesión")
                        else:
                            st.error("Este usuario ya existe")
                else:
                    st.warning("Completa todos los campos")
    
    st.stop()

# --- USUARIO LOGUEADO ---
st.title(f"Hola, {st.session_state.user['username']}")

if not st.session_state.user.get("has_profile", False):
    st.info("Necesitas completar tu perfil inicial")
    st.page_link("pages/2_Setup.py", label="⚙️ Configurar Perfil")
else:
    st.success("Tu perfil está configurado")
    st.page_link("pages/3_Monitor.py", label="📊 Ir al Monitor")

st.markdown("---")

if st.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()
