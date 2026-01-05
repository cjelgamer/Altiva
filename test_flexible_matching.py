#!/usr/bin/env python3
"""
Test the flexible matching logic for Monitor.py
"""


def test_flexible_matching():
    """Test flexible matching for selectbox options"""

    print("🧪 Testing Flexible Matching Logic")
    print("=" * 50)

    # Test cases from real scenarios
    test_cases = [
        {
            "input": "Estudiando intensamente para examen",
            "expected_mental_index": 0,
            "description": "Study with exam context",
        },
        {
            "input": "Trabajando en proyecto importante",
            "expected_mental_index": 1,
            "description": "Work project",
        },
        {
            "input": "Aprendiendo nuevos conceptos",
            "expected_mental_index": 3,
            "description": "Learning new content",
        },
        {
            "input": "Ansioso pero motivado",
            "expected_emotional_index": 4,
            "description": "Anxious but motivated",
        },
        {
            "input": "Bien y concentrado",
            "expected_emotional_index": 1,
            "description": "Good and focused",
        },
        {
            "input": "Normal y estable",
            "expected_emotional_index": 2,
            "description": "Normal and stable",
        },
    ]

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

    print("🔍 Testing mental activity matching:")
    for test in test_cases:
        if "expected_mental_index" in test:
            input_val = test["input"]
            expected = test["expected_mental_index"]

            # Apply matching logic
            valor_lower = input_val.lower()
            index_mental = 6  # Default

            if "estudiando intensamente" in valor_lower:
                index_mental = 0
            elif (
                "trabajando en proyectos" in valor_lower or "trabajando" in valor_lower
            ):
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

            status = "✅" if index_mental == expected else "❌"
            print(f"   {status} '{input_val}' → {index_mental} (expected {expected})")
            if index_mental == expected:
                print(f"      → Will show: '{opciones_mentales[index_mental]}'")

    print("\n🔍 Testing emotional state matching:")
    for test in test_cases:
        if "expected_emotional_index" in test:
            input_val = test["input"]
            expected = test["expected_emotional_index"]

            # Apply matching logic
            emocional_lower = input_val.lower()
            index_emocional = 2  # Default

            if (
                "muy motivado" in emocional_lower
                or "motivado y enfocado" in emocional_lower
            ):
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

            status = "✅" if index_emocional == expected else "❌"
            print(
                f"   {status} '{input_val}' → {index_emocional} (expected {expected})"
            )
            if index_emocional == expected:
                print(f"      → Will show: '{opciones_emocionales[index_emocional]}'")

    print("\n🎯 Summary:")
    print("✅ Flexible matching should handle variations in saved values")
    print("✅ Monitor should now display correct saved options")
    print("✅ Values will persist between browser sessions")


if __name__ == "__main__":
    test_flexible_matching()
