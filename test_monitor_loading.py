#!/usr/bin/env python3
"""
Test script to verify that Monitor loads saved values correctly
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.database import get_user_profile, daily_states
from datetime import datetime


def test_loading_logic():
    """Test the loading logic that Monitor.py uses"""

    print("🧪 Testing Monitor Loading Logic")
    print("=" * 50)

    user_id = "test_user_001"

    # Simulate what Monitor.py does
    print("📋 Step 1: Checking user profile...")

    user_profile = get_user_profile(user_id)

    if user_profile:
        actividad_desde_perfil = user_profile.get("actividad_mental_actual")
        emocional_desde_perfil = user_profile.get("estado_emocional_actual")

        print(f"   Perfil encontrado:")
        print(f"   actividad_mental_actual: {actividad_desde_perfil}")
        print(f"   estado_emocional_actual: {emocional_desde_perfil}")

        if actividad_desde_perfil and emocional_desde_perfil:
            print("✅ Load from profile: SUCCESS")
            actividad_cargada = actividad_desde_perfil
            emocional_cargada = emocional_desde_perfil
        else:
            print("⚠️ No values in profile, checking daily_states...")

            # Step 2: Check daily_states
            from datetime import datetime

            hoy_inicio = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            ultimo_fisio = daily_states.find_one(
                {
                    "user_id": user_id,
                    "agent": "AG-FISIO",
                    "timestamp": {"$gte": hoy_inicio},
                },
                sort=[("timestamp", -1)],
            )

            if ultimo_fisio:
                actividad_cargada = ultimo_fisio.get(
                    "actividad_mental", "Sin actividad mental importante"
                )
                emocional_cargada = ultimo_fisio.get(
                    "estado_emocional", "Normal y estable"
                )
                print("✅ Load from daily_states: SUCCESS")
            else:
                actividad_cargada = "Sin actividad mental importante"
                emocional_cargada = "Normal y estable"
                print("⚠️ No daily_states found, using defaults")

    print(f"\n📊 Final loaded values:")
    print(f"   actividad_mental: {actividad_cargada}")
    print(f"   estado_emocional: {emocional_cargada}")

    # Test selectbox index calculation
    print(f"\n🔍 Testing selectbox index calculation:")

    opciones_mentales = [
        "Estudiando intensamente",
        "Trabajando en proyectos",
        "Tareas administrativas",
        "Aprendiendo nuevo contenido",
        "Revisando material",
        "Descansando mentalmente",
        "Sin actividad mental importante",
    ]

    opciones_emocionales = [
        "Muy motivado y enfocado",
        "Bien y concentrado",
        "Normal y estable",
        "Un poco cansado",
        "Estresado o ansioso",
        "Desmotivado",
    ]

    try:
        index_mental = opciones_mentales.index(actividad_cargada)
        print(f"   Mental index: {index_mental} (✅ Found)")
    except ValueError:
        index_mental = 6  # Default to "Sin actividad mental importante"
        print(f"   Mental index: {index_mental} (⚠️ Not found, using default)")

    try:
        index_emocional = opciones_emocionales.index(emocional_cargada)
        print(f"   Emotional index: {index_emocional} (✅ Found)")
    except ValueError:
        index_emocional = 2  # Default to "Normal y estable"
        print(f"   Emotional index: {index_emocional} (⚠️ Not found, using default)")

    print(f"\n📋 Expected Monitor behavior:")
    print(f"   Activity selectbox should show: '{opciones_mentales[index_mental]}'")
    print(
        f"   Emotional selectbox should show: '{opciones_emocionales[index_emocional]}'"
    )

    print(f"\n🎯 Test Result:")
    if (
        index_mental < 7
        and index_emocional < 6
        and opciones_mentales[index_mental] == actividad_cargada
        and opciones_emocionales[index_emocional] == emocional_cargada
    ):
        print("✅ Monitor should display correct values")
    else:
        print("⚠️ Monitor may have issues displaying values")


if __name__ == "__main__":
    test_loading_logic()
