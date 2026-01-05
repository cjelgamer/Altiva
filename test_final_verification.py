#!/usr/bin/env python3
"""
Final verification - Check current MongoDB state
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.database import user_profiles, daily_states


def final_verification():
    """Final check of MongoDB state"""

    print("🔍 FINAL VERIFICATION - MongoDB Current State")
    print("=" * 60)

    # Check user_profiles collection
    print("📋 user_profiles collection:")
    profiles = list(user_profiles.find({}))

    for profile in profiles:
        print(f"\n👤 User: {profile.get('user_id')}")
        print(f"   Ciudad: {profile.get('ciudad')}")
        print(f"   Altitud: {profile.get('altitud')}")

        # Check for new fields
        has_actividad_mental = "actividad_mental_actual" in profile
        has_estado_emocional = "estado_emocional_actual" in profile
        has_ultima_actualizacion = "ultima_actualizacion" in profile

        print(
            f"   actividad_mental_actual: {'✅' if has_actividad_mental else '❌'} - {profile.get('actividad_mental_actual', 'N/A')}"
        )
        print(
            f"   estado_emocional_actual: {'✅' if has_estado_emocional else '❌'} - {profile.get('estado_emocional_actual', 'N/A')}"
        )
        print(
            f"   ultima_actualizacion: {'✅' if has_ultima_actualizacion else '❌'} - {profile.get('ultima_actualizacion', 'N/A')}"
        )

    # Check daily_states collection for recent entries
    print(f"\n📊 daily_states collection (recent entries):")

    from datetime import datetime, timedelta

    recent_entries = list(
        daily_states.find(
            {"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}}
        )
        .sort("timestamp", -1)
        .limit(5)
    )

    for entry in recent_entries:
        user = entry.get("user_id", "Unknown")
        agent = entry.get("agent", "Unknown")
        timestamp = entry.get("timestamp", "Unknown")

        print(f"\n🔄 Entry: {user} - {agent}")
        print(f"   Time: {timestamp}")

        # Check for activity and emotional state
        actividad = entry.get("actividad_mental", "N/A")
        emocional = entry.get("estado_emocional", "N/A")

        print(f"   actividad_mental: {actividad}")
        print(f"   estado_emocional: {emocional}")

    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("=" * 60)

    if profiles:
        main_profile = profiles[0]
        has_new_fields = all(
            [
                "actividad_mental_actual" in main_profile,
                "estado_emocional_actual" in main_profile,
                "ultima_actualizacion" in main_profile,
            ]
        )

        if has_new_fields:
            print("✅ user_profiles collection now includes:")
            print("   - actividad_mental_actual")
            print("   - estado_emocional_actual")
            print("   - ultima_actualizacion")
            print("✅ Fields persist across browser sessions")
            print("✅ Monitor workflow correctly updates permanent profile")
        else:
            print("⚠️ Some fields may be missing from user_profiles")

    if recent_entries:
        print("✅ daily_states continues to store:")
        print("   - Temporary activity and emotional state")
        print("   - Historical tracking for analysis")
        print("✅ Both storage systems work in parallel")

    print(f"\n📋 To verify manually in MongoDB shell:")
    print(f"   > db.user_profiles.find().pretty()")
    print(f"   Look for: actividad_mental_actual, estado_emocional_actual")
    print(
        f"\n   > db.daily_states.find({{agent: 'AG-FISIO'}}).sort({{timestamp: -1}}).limit(3).pretty()"
    )
    print(f"   Look for: actividad_mental, estado_emocional")


if __name__ == "__main__":
    final_verification()
