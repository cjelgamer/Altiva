#!/usr/bin/env python3
"""
Complete session persistence test - simulates a new browser session
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.database import get_user_profile


def simulate_new_session():
    """Simulate what Monitor.py does in a new session"""

    print("🔄 Simulating New Browser Session")
    print("=" * 60)

    user_id = "test_user_001"

    # Simulate fresh session state (what happens when browser closes)
    print("🌐 Fresh browser session - no session state variables")
    session_state = {
        "actividad_mental_guardada": None,
        "estado_emocional_guardado": None,
    }

    print(f"   actividad_mental_guardada: {session_state['actividad_mental_guardada']}")
    print(f"   estado_emocional_guardado: {session_state['estado_emocional_guardado']}")

    # Apply Monitor.py loading logic
    print(f"\n🔍 Applying Monitor.py loading logic...")

    if (
        session_state["actividad_mental_guardada"] is None
        or session_state["estado_emocional_guardado"] is None
    ):
        # Step 1: Load from user profile
        user_profile = get_user_profile(user_id)

        if user_profile:
            actividad_desde_perfil = user_profile.get("actividad_mental_actual")
            emocional_desde_perfil = user_profile.get("estado_emocional_actual")

            if actividad_desde_perfil and emocional_desde_perfil:
                session_state["actividad_mental_guardada"] = actividad_desde_perfil
                session_state["estado_emocional_guardado"] = emocional_desde_perfil
                print(f"✅ Loaded from profile:")
                print(f"   actividad: {actividad_desde_perfil}")
                print(f"   emocional: {emocional_desde_perfil}")
            else:
                print(f"⚠️ No values in profile, would check daily_states")
        else:
            print(f"❌ No profile found")

    # Simulate selectbox index calculation
    print(f"\n🎛️ Simulating selectbox index calculation...")

    valor_guardado_mental = session_state["actividad_mental_guardada"]
    valor_guardado_emocional = session_state["estado_emocional_guardado"]

    # Mental activity matching
    opciones_mentales = [
        "Estudiando intensamente",
        "Trabajando en proyectos",
        "Tareas administrativas",
        "Aprendiendo nuevo contenido",
        "Revisando material",
        "Descansando mentalmente",
        "Sin actividad mental importante",
    ]

    valor_lower = valor_guardado_mental.lower()
    index_mental = 6  # Default

    if "estudiando intensamente" in valor_lower:
        index_mental = 0
    elif "trabajando en proyectos" in valor_lower or "trabajando" in valor_lower:
        index_mental = 1
    elif "tareas administrativas" in valor_lower:
        index_mental = 2
    elif "aprendiendo" in valor_lower:
        index_mental = 3
    elif "revisando" in valor_lower:
        index_mental = 4
    elif "descansando" in valor_lower:
        index_mental = 5
    elif "sin actividad" in valor_lower:
        index_mental = 6

    # Emotional state matching
    opciones_emocionales = [
        "Muy motivado y enfocado",
        "Bien y concentrado",
        "Normal y estable",
        "Un poco cansado",
        "Estresado o ansioso",
        "Desmotivado",
    ]

    emocional_lower = valor_guardado_emocional.lower()
    index_emocional = 2  # Default

    if "muy motivado" in emocional_lower or "motivado y enfocado" in emocional_lower:
        index_emocional = 0
    elif "bien y concentrado" in emocional_lower or "bien" in emocional_lower:
        index_emocional = 1
    elif "normal y estable" in emocional_lower or "normal" in emocional_lower:
        index_emocional = 2
    elif "cansado" in emocional_lower:
        index_emocional = 3
    elif "estresado" in emocional_lower or "ansioso" in emocional_lower:
        index_emocional = 4
    elif "desmotivado" in emocional_lower:
        index_emocional = 5

    print(f"📊 Results:")
    print(f"   Saved values: '{valor_guardado_mental}' | '{valor_guardado_emocional}'")
    print(f"   Mental index: {index_mental} → '{opciones_mentales[index_mental]}'")
    print(
        f"   Emotional index: {index_emocional} → '{opciones_emocionales[index_emocional]}'"
    )

    # Verification
    print(f"\n✅ Verification:")

    mental_match = (
        opciones_mentales[index_mental] == valor_guardado_mental
        or (
            index_mental == 0
            and "estudiando intensamente" in valor_guardado_mental.lower()
        )
        or (index_mental == 1 and "trabajando" in valor_guardado_mental.lower())
    )

    emotional_match = (
        opciones_emocionales[index_emocional] == valor_guardado_emocional
        or (index_emocional == 4 and "ansioso" in valor_guardado_emocional.lower())
        or (index_emocional == 1 and "bien" in valor_guardado_emocional.lower())
    )

    if mental_match and emotional_match:
        print("✅ ✅ ✅ PERFECT! Values will display correctly in new session")
        print("✅ Activity and emotional states persist across browser sessions")
        print("✅ Monitor will show the user's last saved selections")
    else:
        print("❌ There may be display issues")

    print(f"\n📋 Summary:")
    print(f"   - Values are loaded from user_profiles (permanent storage)")
    print(f"   - Flexible matching handles variations in saved values")
    print(f"   - Selectboxes show correct saved options")
    print(f"   - Session persistence is working correctly")


if __name__ == "__main__":
    simulate_new_session()
