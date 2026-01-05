"""
Componente de reloj con hora peruana para Streamlit - Versión funcional
"""

from datetime import datetime
import streamlit as st
from pytz import timezone


def peru_clock_component():
    """
    Muestra un reloj con la hora actual de Perú (GMT-5) en la esquina superior izquierda
    """

    # Obtener hora peruana
    peru_tz = timezone("America/Lima")
    peru_time = datetime.now(peru_tz)

    # Formatear la hora
    time_str = peru_time.strftime("%H:%M:%S")
    date_str = peru_time.strftime("%d/%m/%Y")
    day_str = peru_time.strftime("%A")

    # Mapeo de días a español
    dias_espanol = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    day_es = dias_espanol.get(day_str, day_str)

    # HTML del reloj con botón de refresh integrado
    clock_html = f"""
    <div style="
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
        background: rgba(59, 130, 246, 0.95);
        color: white;
        padding: 12px 18px;
        border-radius: 12px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        cursor: default;
        user-select: none;
        min-width: 220px;
        animation: pulse 2s infinite;
    "
    onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 20px rgba(0, 0, 0, 0.4)';"
    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 16px rgba(0, 0, 0, 0.3)';"
    >
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        ">
            <div style="
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            ">
                <div style="
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 2px;
                ">
                    🇵🇪 PERÚ
                </div>
                <div style="
                    font-size: 18px;
                    font-weight: 700;
                    letter-spacing: 1px;
                ">
                    {time_str}
                </div>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                text-align: right;
                font-size: 11px;
                opacity: 0.9;
            ">
                <div style="margin-bottom: 1px;">
                    {day_es}
                </div>
                <div>
                    {date_str}
                </div>
            </div>
        </div>
        <div style="
            position: absolute;
            top: -8px;
            right: -8px;
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 12px;
            color: #3b82f6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        "
        onclick="location.reload()"
        title="Actualizar hora"
        onmouseover="this.style.background='white'; this.style.transform='scale(1.1)';"
        onmouseout="this.style.background='rgba(255,255,255,0.9)'; this.style.transform='scale(1)';"
        >
            🔄
        </div>
    </div>
    
    <style>
    @keyframes pulse {{
        0% {{
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
        }}
        50% {{
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5);
        }}
        100% {{
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
        }}
    }}
    </style>
    """

    st.markdown(clock_html, unsafe_allow_html=True)

    # Mostrar información de actualización
    st.caption("🕐 **Hora Perú:** Presiona 🔄 o F5 para actualizar el reloj")


def get_peru_datetime():
    """
    Retorna el datetime actual en zona horaria de Perú
    """
    peru_tz = timezone("America/Lima")
    return datetime.now(peru_tz)


def get_peru_midnight():
    """
    Retorna el datetime de medianoche (inicio del día) en zona horaria de Perú
    """
    peru_time = get_peru_datetime()
    return peru_time.replace(hour=0, minute=0, second=0, microsecond=0)


def get_utc_equivalent(peru_dt):
    """
    Convierte un datetime de Perú a su equivalente UTC para MongoDB
    """
    peru_tz = timezone("America/Lima")
    peru_time = peru_dt if peru_dt.tzinfo else peru_tz.localize(peru_dt)
    return peru_time.astimezone(timezone("UTC"))


def format_peru_time(dt):
    """
    Formatea un datetime para mostrarlo en formato peruano
    """
    if dt.tzinfo is None:
        peru_tz = timezone("America/Lima")
        dt = peru_tz.localize(dt)
    else:
        dt = dt.astimezone(timezone("America/Lima"))

    return dt.strftime("%d/%m/%Y %H:%M:%S")


def is_new_day_in_peru(last_timestamp):
    """
    Verifica si es un nuevo día en Perú comparado con el último timestamp
    """
    if not last_timestamp:
        return True

    # Convertir el último timestamp a hora peruana
    if hasattr(last_timestamp, "astimezone"):
        last_peru_time = last_timestamp.astimezone(timezone("America/Lima"))
    else:
        peru_tz = timezone("America/Lima")
        last_peru_time = peru_tz.localize(last_timestamp)

    # Obtener medianoche de hoy en Perú
    today_midnight_peru = get_peru_midnight()

    # Si el último timestamp es antes de la medianoche de hoy, es nuevo día
    return last_peru_time < today_midnight_peru
