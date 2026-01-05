#!/usr/bin/env python3
"""
Test script to verify altitude-based fatigue calculations in AG-FATIGA
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.agents.ag_fatiga import run_ag_fatiga


def test_altitude_impact():
    """Test AG-FATIGA with different altitudes to verify proper altitude impact"""

    # Test scenarios with same physiological data but different altitudes
    base_estado_fisio = {
        "indicadores": {
            "altitud": 3827,  # Will be modified per test
            "hidratacion_porcentaje": 75.0,
            "agua_consumida_ml": 1500,
            "agua_base_ml": 2000,
            "sueno_porcentaje": 80.0,
            "horas_sueno": 6.4,
            "sueno_base_h": 8,
            "actividad_minutos": 45,
            "actividad_minima": 30,
            "nivel_energia": 3,
        },
        "alertas": [],
        "estado": "NORMAL",
        "actividad_mental": "Estudiando intensamente",
        "estado_emocional": "Normal y estable",
    }

    test_cases = [
        {"city": "Puno", "altitude": 3827, "expected_factor": 1.15},
        {"city": "Macusani", "altitude": 4315, "expected_factor": 1.20},
        {"city": "Juliaca", "altitude": 3825, "expected_factor": 1.15},
        {"city": "Azuaycocha", "altitude": 4200, "expected_factor": 1.20},
        {"city": "Cuzco", "altitude": 3399, "expected_factor": 1.10},
    ]

    print("🧪 Testing AG-FATIGA Altitude Impact\n")
    print("=" * 60)

    results = []

    for test in test_cases:
        print(f"\n📍 Testing {test['city']} at {test['altitude']}m")
        print("-" * 40)

        # Update altitude in the test data
        test_estado = base_estado_fisio.copy()
        test_estado["indicadores"]["altitud"] = test["altitude"]

        try:
            # Run AG-FATIGA
            resultado = run_ag_fatiga(
                user_id="test_user",
                estado_fisio=test_estado,
                actividad_mental="Estudiando intensamente",
                estado_emocional="Normal y estable",
            )

            # Extract key metrics
            ifa = resultado.get("ifa", 0)
            nivel_fatiga = resultado.get("nivel_fatiga", "Desconocido")

            results.append(
                {
                    "city": test["city"],
                    "altitude": test["altitude"],
                    "ifa": ifa,
                    "nivel_fatiga": nivel_fatiga,
                    "expected_factor": test["expected_factor"],
                }
            )

            print(f"IFA: {ifa}")
            print(f"Nivel Fatiga: {nivel_fatiga}")
            print(f"Expected Altitude Factor: {test['expected_factor']}")

        except Exception as e:
            print(f"❌ Error testing {test['city']}: {e}")
            results.append(
                {
                    "city": test["city"],
                    "altitude": test["altitude"],
                    "ifa": -1,
                    "error": str(e),
                }
            )

    # Analysis
    print("\n" + "=" * 60)
    print("📊 ALTITUDE IMPACT ANALYSIS")
    print("=" * 60)

    valid_results = [r for r in results if r.get("ifa", -1) >= 0]

    if len(valid_results) >= 2:
        # Sort by altitude
        valid_results.sort(key=lambda x: x["altitude"])

        print(f"{'City':<15} {'Altitude':<10} {'IFA':<8} {'Level':<12} {'Factor'}")
        print("-" * 65)

        for result in valid_results:
            print(
                f"{result['city']:<15} {result['altitude']:<10} {result['ifa']:<8} {result['nivel_fatiga']:<12} {result['expected_factor']}"
            )

        # Check if higher altitudes have higher IFA
        ifa_values = [(r["altitude"], r["ifa"]) for r in valid_results]

        print("\n🔍 Altitude-IFA Correlation:")
        for altitude, ifa in ifa_values:
            print(f"  {altitude}m → IFA: {ifa}")

        # Verify altitude progression
        if len(ifa_values) >= 3:
            sorted_ifa = sorted(ifa_values, key=lambda x: x[1], reverse=True)
            highest_altitude = max(ifa_values, key=lambda x: x[0])
            lowest_altitude = min(ifa_values, key=lambda x: x[0])

            print(f"\n📈 Expected Pattern: Higher altitude → Higher IFA")
            print(
                f"Highest altitude ({highest_altitude[0]}m): IFA {highest_altitude[1]}"
            )
            print(f"Lowest altitude ({lowest_altitude[0]}m): IFA {lowest_altitude[1]}")

            if highest_altitude[1] > lowest_altitude[1]:
                print("✅ Altitude impact working correctly!")
            else:
                print("❌ Altitude impact may need adjustment")

    return results


if __name__ == "__main__":
    test_altitude_impact()
