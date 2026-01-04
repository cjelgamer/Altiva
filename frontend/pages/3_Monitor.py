import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from backend.agents.ag_fisio import run_ag_fisio
from backend.agents.ag_fatiga import run_ag_fatiga
from backend.agents.ag_plan import run_ag_plan
from backend.services.database import get_user_profile, daily_states


# --- CARGAR ESTILOS MODERNOS DE ALTIVA ---
def load_modern_css():
    """Carga el CSS moderno con animaciones y diseño mobile-first"""
    css_file = ROOT_DIR / "frontend" / "styles" / "altiva.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_modern_css()

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
        st.stop()

    profile = get_user_profile(user_id)
    if not profile:
        st.error("❌ Por favor, completa tu perfil primero")
        st.stop()

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

    datos = cargar_datos_dia()

    # Header moderno con gradiente
    st.markdown(
        """
    <div class="header-gradient">
        <h1>📊 Monitor Diario</h1>
        <p>AG-FISIO • AG-FATIGA • AG-PLAN</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Información del usuario
    st.markdown(
        f"""
    <div class="card-modern animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">👤</span>
            <div>
                <div class="font-semibold">{user_data.get("username")}</div>
                <div class="text-sm text-muted">🏙️ {profile["ciudad"]} ({profile["altitud"]}m) • 🏔️ ALTIVA System</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Estado actual con métricas modernas
    st.markdown("### 📈 Estado Actual")

    # Grid responsivo de métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Calcular porcentaje de agua vs meta
        agua_meta = profile.get("agua_base_ml", 2000)
        agua_pct = min((datos["agua"] / agua_meta) * 100, 100)
        agua_color = (
            "success" if agua_pct >= 80 else "warning" if agua_pct >= 50 else "error"
        )

        st.markdown(
            f"""
        <div class="metric-card {agua_color} animate-fade-in">
            <div class="metric-icon">💧</div>
            <div class="metric-value">{datos["agua"]}ml</div>
            <div class="metric-label">Hidratación</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {agua_pct}%; background: var(--success-gradient) if agua_pct >= 80 else var(--warning-gradient) if agua_pct >= 50 else var(--error-gradient);"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Calcular porcentaje de sueño vs meta
        sueno_meta = profile.get("sueno_base_h", 8)
        sueno_pct = min((datos["sueno"] / sueno_meta) * 100, 100)
        sueno_color = (
            "success" if sueno_pct >= 90 else "warning" if sueno_pct >= 70 else "error"
        )

        st.markdown(
            f"""
        <div class="metric-card {sueno_color} animate-fade-in" style="animation-delay: 0.1s;">
            <div class="metric-icon">😴</div>
            <div class="metric-value">{datos["sueno"]}h</div>
            <div class="metric-label">Sueño</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {sueno_pct}%; background: var(--success-gradient) if sueno_pct >= 90 else var(--warning-gradient) if sueno_pct >= 70 else var(--error-gradient);"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        # Calcular porcentaje de actividad vs meta (30 min mínimo)
        actividad_meta = max(profile.get("actividad_minutos", 30), 30)
        actividad_pct = min((datos["actividad"] / actividad_meta) * 100, 100)
        actividad_color = (
            "success"
            if actividad_pct >= 100
            else "warning"
            if actividad_pct >= 50
            else "error"
        )

        st.markdown(
            f"""
        <div class="metric-card {actividad_color} animate-fade-in" style="animation-delay: 0.2s;">
            <div class="metric-icon">🏃</div>
            <div class="metric-value">{datos["actividad"]}min</div>
            <div class="metric-label">Actividad</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {actividad_pct}%; background: var(--success-gradient) if actividad_pct >= 100 else var(--warning-gradient) if actividad_pct >= 50 else var(--error-gradient);"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        # Calcular color para energía
        energia_color = (
            "success"
            if datos["energia"] >= 4
            else "warning"
            if datos["energia"] >= 3
            else "error"
        )
        energia_pct = (datos["energia"] / 5) * 100

        st.markdown(
            f"""
        <div class="metric-card {energia_color} animate-fade-in" style="animation-delay: 0.3s;">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{datos["energia"]}/5</div>
            <div class="metric-label">Energía</div>
            <div class="progress-modern">
                <div class="progress-fill-modern" style="width: {energia_pct}%; background: var(--success-gradient) if datos['energia'] >= 4 else var(--warning-gradient) if datos['energia'] >= 3 else var(--error-gradient);"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Sección de actualización de datos
    st.markdown("### 📝 Actualizar Datos")

    st.markdown(
        """
    <div class="section-highlight animate-fade-in">
        <div class="card-title">
            <span class="icon-xl">📊</span>
            <div>
                <div class="font-semibold">Registro Diario</div>
                <div class="text-sm text-muted">Ingresa tus datos para análisis inteligente</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Formulario con diseño moderno
    with st.form("monitor_form", clear_on_submit=False):
        col_a, col_b = st.columns(2)

        with col_a:
            agua_total = st.number_input(
                "💧 Agua consumida hoy (ml)",
                min_value=0,
                max_value=10000,
                value=int(datos["agua"]),
                step=100,
                help="Cantidad total de agua ingerida hoy",
            )
            sueno_hoy = st.number_input(
                "😴 Horas de sueño",
                min_value=0.0,
                max_value=24.0,
                value=float(datos["sueno"]),
                step=0.5,
                help="Horas de sueño la noche anterior",
            )

        with col_b:
            actividad_hoy = st.number_input(
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
            energia_actual = st.select_slider(
                "⚡ Nivel de energía",
                options=energia_labels,
                value=energia_labels[datos["energia"] - 1],
                help="¿Cómo te sientes de energía hoy?",
            )

        # Botón moderno
        submitted = st.form_submit_button(
            "🔄 Actualizar y Analizar", use_container_width=True, type="primary"
        )

    if submitted:
        # Parsear nivel de energía
        energia_valor = int(energia_actual.split(" - ")[0])

        with st.spinner("🤖 Analizando tu estado..."):
            # Actualizar estado fisiológico
            estado_fisio = run_ag_fisio(
                user_id,
                {
                    "agua_consumida_ml": agua_total,
                    "horas_sueno": sueno_hoy,
                    "actividad_minutos": actividad_hoy,
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

            resultado_plan = run_ag_plan(user_id, resultado_fatiga, historial_dia)

        st.success("✅ ¡Análisis completado!")

        # Mostrar resultados con diseño moderno
        st.markdown("---")
        st.markdown("### 🎯 Resultados del Análisis")

        # IFA con diseño moderno
        ifa = resultado_fatiga.get("ifa", 0)
        nivel = resultado_fatiga.get("nivel_fatiga", "Medio")

        # Determinar estilo del IFA
        if ifa < 34:
            bg_gradient = "var(--success-gradient)"
            emoji = "🟢"
            estado = "Óptimo"
        elif ifa < 67:
            bg_gradient = "var(--warning-gradient)"
            emoji = "🟡"
            estado = "Moderado"
        else:
            bg_gradient = "var(--error-gradient)"
            emoji = "🔴"
            estado = "Crítico"

        st.markdown(
            f"""
        <div class="card-modern animate-slide-in" style="background: {bg_gradient}; color: white; border: none;">
            <div style="text-align: center;">
                <h3 style="color: white; margin: 0 0 1rem 0;">🎯 Índice de Fatiga en Altura (IFA)</h3>
                <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">{emoji} {ifa}/100</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: white;">Estado: {estado}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem; color: rgba(255,255,255,0.9);">{nivel}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Justificación
        st.markdown("### 📊 Análisis Detallado")
        justificacion = resultado_fatiga.get(
            "justificacion", "Sin justificación disponible"
        )
        st.markdown(
            f"""
        <div class="card-modern animate-fade-in">
            <div class="card-header">
                <h4><span class="icon-lg">📈</span> Justificación del IFA</h4>
            </div>
            <div class="card-content">
                <p class="text-secondary">{justificacion}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Plan de recuperación
        plan_data = resultado_plan.get("plan", {})
        if plan_data:
            st.markdown("### 🎯 Plan de Recuperación Inteligente")

            st.markdown(
                """
            <div class="plan-header animate-slide-in">
                <h4>🤖 AG-PLAN: Recomendaciones Personalizadas</h4>
                <p>Plan generado automáticamente según tu estado actual y perfil</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Grid de secciones del plan
            sections = []
            if plan_data.get("recomendaciones_inmediatas"):
                sections.append(
                    (
                        "🚀",
                        "Recomendaciones Inmediatas",
                        plan_data.get("recomendaciones_inmediatas", []),
                    )
                )

            if plan_data.get("horarios_optimos"):
                horarios_text = [
                    f"**{tipo.title()}:** {horario}"
                    for tipo, horario in plan_data.get("horarios_optimos", {}).items()
                ]
                sections.append(("⏰", "Horarios Óptimos", horarios_text))

            if plan_data.get("pausas_activas"):
                sections.append(
                    ("🤸", "Pausas Activas", plan_data.get("pausas_activas", []))
                )

            if plan_data.get("consejos_altitud"):
                sections.append(
                    (
                        "🏔️",
                        "Consejos para Altitud",
                        plan_data.get("consejos_altitud", []),
                    )
                )

            if sections:
                cols = st.columns(len(sections) if len(sections) <= 2 else 2)
                for i, (icon, title, items) in enumerate(sections):
                    with cols[i % 2]:
                        st.markdown(
                            f"""
                        <div class="plan-section animate-fade-in" style="animation-delay: {i * 0.1}s;">
                            <h5><span class="icon-lg">{icon}</span> {title}</h5>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        for item in items:
                            st.markdown(
                                f"""
                            <div class="plan-item">
                                {item}
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
            else:
                st.info("ℹ️ No hay recomendaciones específicas para tu estado actual")


if __name__ == "__main__":
    main()
