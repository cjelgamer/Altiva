#!/usr/bin/env python3
"""
Test script to verify that actividad_mental and estado_emocional are saved in user_profiles
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.database import (
    get_user_profile,
    update_user_profile,
    user_profiles,
)
from datetime import datetime


def test_profile_update():
    """Test that we can update user profile with mental and emotional state"""

    print("🧪 Testing Profile Update with Mental and Emotional State")
    print("=" * 60)

    # Get test user profile
    user_id = "test_user_001"
    current_profile = get_user_profile(user_id)

    if not current_profile:
        print("❌ No se encontró el perfil del usuario test_user_001")
        return

    print("📋 Current profile fields:")
    print(f"   User ID: {current_profile.get('user_id')}")
    print(f"   Ciudad: {current_profile.get('ciudad')}")
    print(f"   Altitud: {current_profile.get('altitud')}")
    print(
        f"   Actividad mental actual: {current_profile.get('actividad_mental_actual', 'NO DEFINIDO')}"
    )
    print(
        f"   Estado emocional actual: {current_profile.get('estado_emocional_actual', 'NO DEFINIDO')}"
    )
    print(
        f"   Última actualización: {current_profile.get('ultima_actualizacion', 'NO DEFINIDO')}"
    )

    print("\n🔄 Testing profile update...")

    # Test update
    test_actividad = "Estudiando intensamente para examen"
    test_emocional = "Ansioso pero motivado"

    try:
        result = update_user_profile(
            user_id,
            {
                "actividad_mental_actual": test_actividad,
                "estado_emocional_actual": test_emocional,
                "ultima_actualizacion": datetime.now().isoformat(),
            },
        )

        if result:
            print("✅ Profile updated successfully")
        else:
            print("⚠️ Profile update may not have modified any documents")

    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return

    # Verify update
    print("\n🔍 Verifying update...")
    updated_profile = get_user_profile(user_id)

    if updated_profile:
        print("📋 Updated profile fields:")
        print(
            f"   Actividad mental actual: {updated_profile.get('actividad_mental_actual')}"
        )
        print(
            f"   Estado emocional actual: {updated_profile.get('estado_emocional_actual')}"
        )
        print(f"   Última actualización: {updated_profile.get('ultima_actualizacion')}")

        # Check if values match
        if (
            updated_profile.get("actividad_mental_actual") == test_actividad
            and updated_profile.get("estado_emocional_actual") == test_emocional
        ):
            print("✅ Update verified - fields saved correctly!")
        else:
            print("⚠️ Update failed - fields don't match expected values")
    else:
        print("❌ Could not retrieve updated profile")

    print("\n" + "=" * 60)
    print("📊 Current MongoDB Profile Structure:")
    print("=" * 60)

    # Show current profile structure
    all_profiles = list(user_profiles.find({"user_id": user_id}))

    if all_profiles:
        profile = all_profiles[0]
        print("Fields in user_profiles:")
        for key, value in sorted(profile.items()):
            if key != "_id":  # Skip ObjectId
                print(f"   {key}: {value}")
    else:
        print("❌ No profiles found")


if __name__ == "__main__":
    test_profile_update()
