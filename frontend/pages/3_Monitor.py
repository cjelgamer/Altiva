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

st.set_page_config(
    page_title="ALTIVA - Monitor",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)

# Cargar CSS básico
st.markdown(
    """
<style>
.metric-container {
    background-color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}
.metric-label {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f77b4;
}
</style>
""",
    unsafe_allow_html=True,
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

    st.title("📊 Monitor Diario")
    st.markdown(
        f"**Usuario:** {user_data.get('username')} | **Ciudad:** {profile['ciudad']} ({profile['altitud']}m)"
    )

    # Estado actual
    st.markdown("### 📈 Estado Actual")

    # Métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="metric-container">
            <div class="metric-label">💧 Hidratación</div>
            <div class="metric-value">{datos["agua"]}ml</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-container">
            <div class="metric-label">😴 Sueño</div>
            <div class="metric-value">{datos["sueno"]}h</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-container">
            <div class="metric-label">🏃 Actividad</div>
            <div class="metric-value">{datos["actividad"]}min</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="metric-container">
            <div class="metric-label">⚡ Energía</div>
            <div class="metric-value">{datos["energia"]}/5</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Inputs
    st.markdown("### 📝 Actualizar Datos")

    col_a, col_b = st.columns(2)

    with col_a:
        agua_total = st.number_input(
            "💧 Agua consumida hoy (ml)",
            min_value=0,
            max_value=10000,
            value=int(datos["agua"]),
            step=100,
        )
        sueno_hoy = st.number_input(
            "😴 Horas de sueño",
            min_value=0.0,
            max_value=24.0,
            value=float(datos["sueno"]),
            step=0.5,
        )

    with col_b:
        actividad_hoy = st.number_input(
            "🏃 Actividad física (minutos)",
            min_value=0,
            max_value=300,
            value=int(datos["actividad"]),
            step=5,
        )
        energia_actual = st.select_slider(
            "⚡ Nivel de energía",
            options=[
                "1 - Muy bajo",
                "2 - Bajo",
                "3 - Normal",
                "4 - Bueno",
                "5 - Excelente",
            ],
            value=f"{datos['energia']} - {['Muy bajo', 'Bajo', 'Normal', 'Bueno', 'Excelente'][datos['energia'] - 1]}",
        )

    # Botón para actualizar
    if st.button("🔄 Actualizar y Analizar", use_container_width=True, type="primary"):
        # Actualizar estado fisiológico
        estado_fisio = run_ag_fisio(
            user_id,
            {
                "agua_consumida_ml": agua_total,
                "horas_sueno": sueno_hoy,
                "actividad_minutos": actividad_hoy,
                "nivel_energia": datos["energia"],
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

        # Mostrar resultados
        st.markdown("---")
        st.markdown("### 🎯 Resultados del Análisis")

        # IFA
        ifa = resultado_fatiga.get("ifa", 0)
        nivel = resultado_fatiga.get("nivel_fatiga", "Medio")

        if ifa < 34:
            color = "green"
            emoji = "🟢"
        elif ifa < 67:
            color = "orange"
            emoji = "🟡"
        else:
            color = "red"
            emoji = "🔴"

        st.markdown(
            f"""
        <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; margin: 1rem 0;">
            <h3>🎯 Índice de Fatiga en Altura (IFA)</h3>
            <div style="font-size: 2.5rem; font-weight: bold;">{emoji} {ifa}/100</div>
            <p><strong>Nivel de Fatiga:</strong> {nivel}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Justificación
        st.markdown("### 📊 Justificación")
        st.info(resultado_fatiga.get("justificacion", "Sin justificación disponible"))

        # Plan de recuperación
        plan_data = resultado_plan.get("plan", {})
        st.markdown("### 🎯 Plan de Recuperación")

        if plan_data.get("recomendaciones_inmediatas"):
            st.markdown("**🚀 Recomendaciones Inmediatas:**")
            for rec in plan_data.get("recomendaciones_inmediatas", []):
                st.write(f"• {rec}")

        if plan_data.get("horarios_optimos"):
            st.markdown("**⏰ Horarios Óptimos:**")
            for tipo, horario in plan_data.get("horarios_optimos", {}).items():
                st.write(f"• **{tipo.title()}:** {horario}")

        if plan_data.get("pausas_activas"):
            st.markdown("**🤸 Pausas Activas:**")
            for pausa in plan_data.get("pausas_activas", []):
                st.write(f"• {pausa}")

        if plan_data.get("consejos_altitud"):
            st.markdown("**🏔️ Consejos para Altitud:**")
            for consejo in plan_data.get("consejos_altitud", []):
                st.write(f"• {consejo}")


if __name__ == "__main__":
    main()
