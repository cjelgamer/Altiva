import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from pytz import timezone

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.agents.ag_plan import run_ag_plan
from backend.services.database import get_user_profile, daily_states
from frontend.components.peru_clock import (
    peru_clock_component,
    get_peru_midnight,
    get_utc_equivalent,
)

# --- ESTILO OSCURO MODERNO ---
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
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: var(--text-primary) !important;
    }
    
    /* Chat container */
    .chat-container {
        height: 500px;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: var(--text-primary);
        scrollbar-width: thin;
        scrollbar-color: var(--border-light) var(--bg-primary);
    }
    
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: var(--border-light);
        border-radius: 4px;
    }
    
    .chat-message {
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-radius: 0.5rem;
        background: var(--bg-secondary);
        border-left: 3px solid var(--primary-color);
        animation: slideIn 0.3s ease-out;
    }
    
    .chat-message.bot {
        background: var(--bg-tertiary);
        border-left-color: var(--success-color);
    }
    
    .chat-message.user {
        background: var(--bg-card);
        border-left-color: var(--accent-color);
        margin-left: 2rem;
    }
    
    .chat-time {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .chat-content {
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    /* Input area */
    .input-area {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .stTextInput > div > div > input {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        outline: none !important;
    }
    
    /* Botones */
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
    
    /* Estado卡片 */
    .status-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .ifa-score {
        font-size: 3rem;
        font-weight: 800;
        margin: 1rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    
    .ifa-status {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    /* Animación */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .chat-container {
            height: 400px;
            padding: 1rem;
        }
        
        .chat-message.user {
            margin-left: 1rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="ALTIVA - Plan Chat",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="💬",
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

    # Header con botones de navegación
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_left:
        if st.button("⬅️ Volver", key="volver_btn", help="Volver al Monitor"):
            st.switch_page("pages/3_Monitor.py")

    with col_center:
        st.markdown(
            f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            {logo_html}
            <h1 style="color: var(--text-primary); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                💬 AG-PLAN Chat
            </h1>
            <p style="color: var(--text-secondary); font-size: 1rem; margin: 0;">
                Asistente Personal de Recuperación
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Añadir reloj de hora peruana
    peru_clock_component()

    with col_right:
        if st.button(
            "👤 Perfil", key="perfil_btn", help="Ir a configuración de perfil"
        ):
            st.switch_page("pages/2_Setup.py")

    # Estado actual del usuario
    st.markdown("### 📊 Estado Actual")

    # Obtener análisis reciente (usar hora peruana)
    hoy_inicio_peru = get_peru_midnight()
    hoy_inicio_utc = get_utc_equivalent(hoy_inicio_peru)

    estado_fatiga_reciente = daily_states.find_one(
        {
            "user_id": user_id,
            "agent": "AG-FATIGA",
            "timestamp": {"$gte": hoy_inicio_utc},
        },
        sort=[("timestamp", -1)],
    )

    # Valores por defecto
    ifa = 50
    nivel_fatiga = "Medio"
    ifa_color = "var(--warning-color)"
    emoji = "🟡"
    estado = "Moderado"

    if estado_fatiga_reciente:
        ifa = estado_fatiga_reciente.get("ifa", 50)
        nivel_fatiga = estado_fatiga_reciente.get("nivel_fatiga", "Medio")

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
    <div class="status-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏔️</div>
        <div style="font-size: 1.1rem; color: var(--text-primary); font-weight: 600; margin-bottom: 1rem;">
            Índice de Fatiga en Altura
        </div>
        <div class="ifa-score" style="color: {ifa_color};">{ifa}/100</div>
        <div class="ifa-status">{emoji} {estado}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;">
            👤 {user_data.get("username", "Usuario")} • 🏙️ {profile.get("ciudad", "N/A")} ({profile.get("altitud", 0)}m)
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Session state para el chat y plan
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "plan_generado" not in st.session_state:
        st.session_state.plan_generado = None

        # Generar plan inicial automáticamente
        if estado_fatiga_reciente:
            with st.spinner("🤖 Generando tu plan inicial de recuperación..."):
                try:
                    # Obtener historial reciente para contexto
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
                        )
                        .sort("timestamp", -1)
                        .limit(10)
                    )

                    # Ejecutar AG-PLAN sin consulta específica
                    resultado = run_ag_plan(
                        user_id,
                        estado_fatiga_reciente,
                        historial_dia,
                        "Generar plan completo de recuperación y productividad para hoy",
                    )

                    plan_data = resultado.get("plan", {}) if resultado else {}

                    if plan_data:
                        st.session_state.plan_generado = plan_data

                        # Construir mensaje con el plan generado
                        plan_content = f"""¡Hola! Soy AG-PLAN, tu asistente personal de recuperación en altura.

🏔️ Tu IFA actual es: {ifa}/100 ({estado})
📍 Basado en tu perfil: {profile.get("ciudad", "N/A")} ({profile.get("altitud", 0)}m)

📋 **TU PLAN DE RECUPERACIÓN PARA HOY:**
"""

                        if plan_data.get("recomendaciones_inmediatas"):
                            plan_content += "🚀 **Recomendaciones Inmediatas:**\n"
                            for rec in plan_data["recomendaciones_inmediatas"][:3]:
                                plan_content += f"• {rec}\n"
                            plan_content += "\n"

                        if plan_data.get("horarios_optimos"):
                            plan_content += "⏰ **Horarios Óptimos:**\n"
                            for tipo, horario in list(
                                plan_data["horarios_optimos"].items()
                            )[:3]:
                                plan_content += f"• {tipo.title()}: {horario}\n"
                            plan_content += "\n"

                        if plan_data.get("pausas_activas"):
                            plan_content += "🤸 **Pausas Activas Recomendadas:**\n"
                            for pausa in plan_data["pausas_activas"][:3]:
                                plan_content += f"• {pausa}\n"
                            plan_content += "\n"

                        if plan_data.get("consejos_altitud"):
                            plan_content += "🏔️ **Consejos para Altitud:**\n"
                            for consejo in plan_data["consejos_altitud"][:2]:
                                plan_content += f"• {consejo}\n"
                            plan_content += "\n"

                        plan_content += """💡 **Puedes preguntarme detalles como:**
• "¿Qué ejercicios específicos me recomiendas?"
• "¿A qué hora debo estudiar hoy?"
• "¿Cuántas pausas debo tomar?"
• "¿Cómo puedo mejorar mi energía?"

¿Sobre qué aspecto de tu plan te gustaría saber más?"""

                        st.session_state.chat_messages.append(
                            {
                                "role": "bot",
                                "content": plan_content,
                                "timestamp": datetime.now(),
                            }
                        )
                    else:
                        # Mensaje de bienvenida si no hay plan
                        st.session_state.chat_messages.append(
                            {
                                "role": "bot",
                                "content": f"""¡Hola! Soy AG-PLAN, tu asistente personal de recuperación en altura.

🏔️ Tu IFA actual es: {ifa}/100 ({estado})
📍 Basado en tu perfil: {profile.get("ciudad", "N/A")} ({profile.get("altitud", 0)}m)

Puedo ayudarte con:
• 📅 Planificación de actividades y descansos
• ⏰ Recomendaciones de horarios óptimos
• 🤸 Ejercicios de pausas activas
• 🧘 Técnicas de recuperación
• 📈 Seguimiento de tu progreso

¿En qué puedo ayudarte hoy?""",
                                "timestamp": datetime.now(),
                            }
                        )

                except Exception as e:
                    st.session_state.chat_messages.append(
                        {
                            "role": "bot",
                            "content": f"❌ Error al generar plan inicial. Por favor, intenta de nuevo.\n\nError: {str(e)}",
                            "timestamp": datetime.now(),
                        }
                    )

    # Mostrar mensajes del chat
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_messages:
            time_str = message["timestamp"].strftime("%H:%M:%S")
            css_class = (
                "chat-message bot" if message["role"] == "bot" else "chat-message user"
            )

            st.markdown(
                f"""
            <div class="{css_class}">
                <div class="chat-time">{time_str} - {"AG-PLAN" if message["role"] == "bot" else "Tú"}</div>
                <div class="chat-content">{message["content"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Input del usuario
    st.markdown('<div class="input-area">', unsafe_allow_html=True)

    col_input, col_send = st.columns([4, 1])

    with col_input:
        user_message = st.text_input(
            "💬 Escribe tu mensaje...",
            placeholder="Pregunta sobre tu plan de recuperación...",
            key="user_input",
            label_visibility="collapsed",
        )

    with col_send:
        send_button = st.button(
            "📤 Enviar", type="primary", use_container_width=True, key="send_btn"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Procesar mensaje del usuario
    if (send_button and user_message.strip()) or (
        user_message.strip() and st.session_state.get("submit_on_enter", False)
    ):
        # Guardar el mensaje para procesar
        mensaje_procesar = user_message.strip()

        # Agregar mensaje del usuario al chat
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": mensaje_procesar,
                "timestamp": datetime.now(),
            }
        )

        # Procesar con AG-PLAN
        with st.spinner("🤖 AG-PLAN está pensando..."):
            try:
                # Obtener historial reciente para contexto
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
                    )
                    .sort("timestamp", -1)
                    .limit(10)
                )

                # Crear contexto del fatiga actual
                contexto_fatiga = (
                    estado_fatiga_reciente
                    if estado_fatiga_reciente
                    else {"ifa": ifa, "nivel_fatiga": nivel_fatiga}
                )

                # Ejecutar AG-PLAN con el mensaje del usuario
                resultado = run_ag_plan(
                    user_id, contexto_fatiga, historial_dia, mensaje_procesar
                )

                # Extraer respuesta del plan
                plan_data = resultado.get("plan", {}) if resultado else {}

                # Construir respuesta del bot más directa usando el plan
                if plan_data and (
                    plan_data.get("recomendaciones_inmediatas")
                    or plan_data.get("horarios_optimos")
                    or plan_data.get("pausas_activas")
                ):
                    # Hay un plan específico, mostrarlo directamente
                    bot_response = f"""✅ **Plan personalizado generado para tu consulta:** "{mensaje_procesar}"

"""

                    if plan_data.get("recomendaciones_inmediatas"):
                        bot_response += "🚀 **Recomendaciones Inmediatas:**\n"
                        for rec in plan_data["recomendaciones_inmediatas"][:3]:
                            bot_response += f"• {rec}\n"
                        bot_response += "\n"

                    if plan_data.get("horarios_optimos"):
                        bot_response += "⏰ **Horarios Óptimos:**\n"
                        for tipo, horario in list(
                            plan_data["horarios_optimos"].items()
                        )[:3]:
                            bot_response += f"• {tipo.title()}: {horario}\n"
                        bot_response += "\n"

                    if plan_data.get("pausas_activas"):
                        bot_response += "🤸 **Pausas Activas Recomendadas:**\n"
                        for pausa in plan_data["pausas_activas"][:2]:
                            bot_response += f"• {pausa}\n"
                        bot_response += "\n"

                    if plan_data.get("consejos_altitud"):
                        bot_response += "🏔️ **Consejos para Altitud:**\n"
                        for consejo in plan_data["consejos_altitud"][:2]:
                            bot_response += f"• {consejo}\n"

                    bot_response += """
💡 **Puedes preguntarme:**
• "¿Qué ejercicio específico me recomiendas?"
• "¿A qué hora debo estudiar hoy?"
• "¿Cuándo debo tomar mi próxima pausa?"
• "¿Cómo puedo mejorar mi nivel de energía?"
"""

                else:
                    # No hay plan específico o respuesta vacía
                    bot_response = f"""🤔 **Basado en tu estado actual (IFA: {ifa}/100 - {nivel_fatiga}):**

💡 **Recomendaciones generales:**
• 💤 Asegúrate de dormir las horas recomendadas
• 💧 Mantente hidratado durante todo el día
• 🚶 Realiza pausas activas cada 2 horas
• 📈 Continúa con el monitoreo diario

🎯 **Para obtener un plan más específico, pregúntame:**
• "¿Qué actividades físicas me recomiendas?"
• "¿Cuál es el mejor horario para estudiar hoy?"
• "¿Cómo puedo mejorar mi productividad?"
• "¿Qué ejercicios de relajación me sugieres?"

¿Sobre qué aspecto te gustaría obtener recomendaciones específicas?"""

                # Agregar respuesta del bot
                st.session_state.chat_messages.append(
                    {
                        "role": "bot",
                        "content": bot_response,
                        "timestamp": datetime.now(),
                    }
                )

            except Exception as e:
                st.session_state.chat_messages.append(
                    {
                        "role": "bot",
                        "content": f"❌ Lo siento, tuve un problema al procesar tu solicitud. Por favor, intenta de nuevo.\n\nError: {str(e)}",
                        "timestamp": datetime.now(),
                    }
                )

        # Forzar rerun para limpiar el input (sin modificar session_state.user_input)
        st.rerun()


if __name__ == "__main__":
    main()
