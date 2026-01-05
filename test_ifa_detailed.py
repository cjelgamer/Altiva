#!/usr/bin/env python3
"""
Detailed test to verify IFA calculation differences based on altitude factors
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.agents.ag_fatiga import run_ag_fatiga


def test_ifa_calculation_details():
    """Test IFA calculations with specific scenarios to verify altitude impact"""

    print("🔬 Detailed IFA Calculation Analysis")
    print("=" * 50)

    # Test scenarios with identical physiological parameters
    base_scenario = {
        "user_id": "test_user",
        "estado_fisio": {
            "indicadores": {
                "altitud": 3827,  # Will be modified
                "hidratacion_porcentaje": 80.0,
                "agua_consumida_ml": 1600,
                "agua_base_ml": 2000,
                "sueno_porcentaje": 87.5,
                "horas_sueno": 7,
                "sueno_base_h": 8,
                "actividad_minutos": 30,
                "actividad_minima": 30,
                "nivel_energia": 3,
            },
            "alertas": [],
            "estado": "NORMAL",
            "actividad_mental": "Aprendiendo",
            "estado_emocional": "Normal y estable",
        },
        "actividad_mental": "Aprendiendo",
        "estado_emocional": "Normal y estable",
    }

    # Test key altitude thresholds
    altitude_tests = [
        {"name": "Below 2500m", "altitude": 2000, "expected_factor": 1.00},
        {"name": "2500-3000m", "altitude": 2750, "expected_factor": 1.05},
        {"name": "3000-3500m", "altitude": 3250, "expected_factor": 1.10},
        {"name": "3500-4000m", "altitude": 3750, "expected_factor": 1.15},
        {"name": "4000-4500m", "altitude": 4250, "expected_factor": 1.20},
        {"name": "Above 4500m", "altitude": 4750, "expected_factor": 1.25},
    ]

    results = []

    print(f"{'Scenario':<15} {'Altitude':<10} {'Factor':<8} {'IFA':<6} {'IFA/Base'}")
    print("-" * 65)

    base_ifa = None

    for test in altitude_tests:
        # Update altitude
        test_scenario = base_scenario.copy()
        test_scenario["estado_fisio"]["indicadores"]["altitud"] = test["altitude"]

        try:
            resultado = run_ag_fatiga(
                user_id=test_scenario["user_id"],
                estado_fisio=test_scenario["estado_fisio"],
                actividad_mental=test_scenario["actividad_mental"],
                estado_emocional=test_scenario["estado_emocional"],
            )

            ifa = resultado.get("ifa", 0)
            nivel_fatiga = resultado.get("nivel_fatiga", "Desconocido")

            # Calculate IFA relative to baseline (if set)
            if base_ifa is None:
                base_ifa = ifa
                relative_ifa = 1.0
            else:
                relative_ifa = ifa / base_ifa if base_ifa > 0 else 1.0

            results.append(
                {
                    "name": test["name"],
                    "altitude": test["altitude"],
                    "expected_factor": test["expected_factor"],
                    "ifa": ifa,
                    "relative_ifa": relative_ifa,
                    "nivel_fatiga": nivel_fatiga,
                }
            )

            print(
                f"{test['name']:<15} {test['altitude']:<10} {test['expected_factor']:<8.2f} {ifa:<6} {relative_ifa:.2f}"
            )

        except Exception as e:
            print(f"❌ Error in {test['name']}: {e}")

    # Analysis
    print("\n" + "=" * 50)
    print("📊 FACTOR CORRELATION ANALYSIS")
    print("=" * 50)

    if len(results) >= 3:
        print("Checking if IFA values correlate with expected altitude factors...")

        # Calculate actual IFA progression
        ifa_progression = [
            (r["altitude"], r["ifa"], r["expected_factor"]) for r in results
        ]
        ifa_progression.sort(key=lambda x: x[0])

        print(
            f"\n{'Altitude':<10} {'IFA':<8} {'Exp Factor':<12} {'IFA Diff':<10} {'Exp Diff'}"
        )
        print("-" * 65)

        prev_ifa = None
        prev_factor = None

        for altitude, ifa, exp_factor in ifa_progression:
            ifa_diff = f"+{ifa - prev_ifa}" if prev_ifa else "Base"
            exp_diff = f"+{exp_factor - prev_factor:.2f}" if prev_factor else "Base"

            print(
                f"{altitude:<10} {ifa:<8} {exp_factor:<12.2f} {ifa_diff:<10} {exp_diff}"
            )

            prev_ifa = ifa
            prev_factor = exp_factor

        # Verify progression
        print("\n🔍 Verification:")

        # Check monotonic progression
        ifa_values = [r["ifa"] for r in results]
        factors = [r["expected_factor"] for r in results]

        is_monotonic = all(
            ifa_values[i] >= ifa_values[i - 1] for i in range(1, len(ifa_values))
        )

        if is_monotonic:
            print("✅ IFA values increase monotonically with altitude")
        else:
            print("⚠️  IFA values don't follow perfect monotonic progression")

        # Check factor correlation
        lowest = results[0]
        highest = results[-1]

        ifa_increase = highest["ifa"] - lowest["ifa"]
        factor_increase = highest["expected_factor"] - lowest["expected_factor"]

        print(f"📈 From {lowest['name']} to {highest['name']}:")
        print(f"   Altitude: {lowest['altitude']}m → {highest['altitude']}m")
        print(f"   IFA: {lowest['ifa']} → {highest['ifa']} (+{ifa_increase})")
        print(
            f"   Factor: {lowest['expected_factor']:.2f} → {highest['expected_factor']:.2f} (+{factor_increase:.2f})"
        )

        # Calculate expected vs actual increase
        expected_ifa_increase = lowest["ifa"] * factor_increase
        actual_vs_expected = (
            ifa_increase / expected_ifa_increase if expected_ifa_increase > 0 else 0
        )

        print(f"   Expected IFA increase: ~{expected_ifa_increase:.1f}")
        print(f"   Actual vs Expected ratio: {actual_vs_expected:.2f}")

        if 0.7 <= actual_vs_expected <= 1.3:
            print("   ✅ IFA increase correlates well with altitude factors")
        else:
            print("   ⚠️  IFA increase may need adjustment")

    print("\n🎯 Altitude-Specific Test (Real Cities)")
    print("-" * 40)

    # Test with real cities to verify practical differences
    real_cities = [
        {"name": "Cuzco", "altitude": 3399},
        {"name": "Puno", "altitude": 3827},
        {"name": "Macusani", "altitude": 4315},
    ]

    for city in real_cities:
        test_scenario = base_scenario.copy()
        test_scenario["estado_fisio"]["indicadores"]["altitud"] = city["altitude"]

        try:
            resultado = run_ag_fatiga(
                user_id="test_user",
                estado_fisio=test_scenario["estado_fisio"],
                actividad_mental="Estudiando intensamente",
                estado_emocional="Ansioso por examen",
            )

            ifa = resultado.get("ifa", 0)
            nivel_fatiga = resultado.get("nivel_fatiga", "Desconocido")
            alertas = resultado.get("alertas", [])

            print(
                f"📍 {city['name']} ({city['altitude']}m): IFA {ifa} - {nivel_fatiga} - {len(alertas)} alertas"
            )

        except Exception as e:
            print(f"❌ Error testing {city['name']}: {e}")

    return results


if __name__ == "__main__":
    test_ifa_calculation_details()
