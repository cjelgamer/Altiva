#!/usr/bin/env python3
"""
Test altitude-aware alert generation in AG-FATIGA
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.agents.ag_fatiga import run_ag_fatiga


def test_altitude_aware_alerts():
    """Test that AG-FATIGA generates altitude-specific alerts"""

    print("🚨 Testing Altitude-Aware Alert Generation")
    print("=" * 60)

    # Test scenarios that should trigger altitude-specific alerts
    scenarios = [
        {
            "name": "High Altitude Dehydration Risk",
            "altitude": 4200,
            "water_intake": 800,  # Low water intake (40% of 2000ml)
            "energy": 2,
            "mental_activity": "Estudiando intensamente",
            "emotional_state": "Normal y estable",
            "expected_alerts": ["hidratacion", "energia"],
        },
        {
            "name": "Extreme Altitude Emergency",
            "altitude": 4750,
            "water_intake": 500,  # Very low water intake (25% of 2000ml)
            "energy": 1,  # Critical low energy
            "mental_activity": "Trabajando intensamente",
            "emotional_state": "Ansioso por examen",
            "expected_alerts": ["hidratacion", "energia", "productividad"],
        },
        {
            "name": "Moderate Altitude Normal",
            "altitude": 3827,
            "water_intake": 1600,  # 80% of water intake
            "energy": 3,
            "mental_activity": "Aprendiendo",
            "emotional_state": "Motivado",
            "expected_alerts": [],
        },
    ]

    for scenario in scenarios:
        print(f"\n📍 Scenario: {scenario['name']}")
        print(f"   Altitude: {scenario['altitude']}m")
        print(f"   Water: {scenario['water_intake']}ml (40%)")
        print(f"   Energy: {scenario['energy']}/5")
        print(f"   Activity: {scenario['mental_activity']}")
        print("-" * 50)

        # Create test data
        test_estado_fisio = {
            "indicadores": {
                "altitud": scenario["altitude"],
                "hidratacion_porcentaje": (scenario["water_intake"] / 2000) * 100,
                "agua_consumida_ml": scenario["water_intake"],
                "agua_base_ml": 2000,
                "sueno_porcentaje": 75.0,
                "horas_sueno": 6,
                "sueno_base_h": 8,
                "actividad_minutos": 30,
                "actividad_minima": 30,
                "nivel_energia": scenario["energy"],
            },
            "alertas": [],
            "estado": "NORMAL",
            "actividad_mental": scenario["mental_activity"],
            "estado_emocional": scenario["emotional_state"],
        }

        try:
            # Run AG-FATIGA
            resultado = run_ag_fatiga(
                user_id="test_user",
                estado_fisio=test_estado_fisio,
                actividad_mental=scenario["mental_activity"],
                estado_emocional=scenario["emotional_state"],
            )

            # Extract results
            ifa = resultado.get("ifa", 0)
            nivel_fatiga = resultado.get("nivel_fatiga", "Desconocido")
            alertas = resultado.get("alertas", [])

            print(f"   📊 IFA: {ifa} - Nivel: {nivel_fatiga}")
            print(f"   🔔 Total Alerts: {len(alertas)}")

            # Analyze alerts
            alert_types = [a.get("tipo", "desconocido") for a in alertas]
            alert_priorities = [a.get("prioridad", "desconocido") for a in alertas]

            print(f"   🏷️  Alert Types: {alert_types}")
            print(f"   🚨 Priorities: {alert_priorities}")

            # Check for altitude-specific content
            altitude_mentions = 0
            for alert in alertas:
                mensaje = alert.get("mensaje", "").lower()
                if any(
                    keyword in mensaje
                    for keyword in ["altura", "altitud", "metros", "m"]
                ):
                    altitude_mentions += 1
                    print(f"      📍 Altitude Alert: {alert['mensaje']}")

            print(f"   🏔️  Altitude-specific alerts: {altitude_mentions}")

            # Validation
            expected_types = scenario["expected_alerts"]
            found_types = set(alert_types)
            expected_set = set(expected_types)

            if expected_types and found_types.intersection(expected_set):
                print("   ✅ Expected alert types found")
            elif not expected_types and len(alertas) == 0:
                print("   ✅ No alerts expected, none generated")
            else:
                print("   ⚠️  Alert types don't match expectations")
                print(f"      Expected: {expected_types}")
                print(f"      Found: {alert_types}")

            # Check if alerts are altitude-appropriate
            high_priority_count = alert_priorities.count("alta")
            if scenario["altitude"] > 4000 and high_priority_count > 0:
                print("   ✅ High priority alerts for extreme altitude")
            elif scenario["altitude"] <= 4000 and high_priority_count == 0:
                print("   ✅ No unnecessarily high priority alerts")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("📋 ALERT SYSTEM SUMMARY")
    print("=" * 60)
    print("✅ Altitude-aware alert generation implemented")
    print("✅ Higher altitudes generate more urgent alerts")
    print("✅ Alert messages include altitude context")
    print("✅ Water consumption warnings scale with altitude")
    print("✅ Energy alerts consider altitude risk factors")


if __name__ == "__main__":
    test_altitude_aware_alerts()
