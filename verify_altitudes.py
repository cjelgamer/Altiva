#!/usr/bin/env python3
"""
Script para verificar y gestionar el archivo de altitudes de Puno.
"""

import sys
from pathlib import Path
import json

# Agregar rutas para importar
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from backend.services.altitude_loader import (
    get_altitude,
    get_all_cities,
    update_city_altitude,
    reload_data,
)


def main():
    print("🏔️ VERIFICACIÓN DE ALTITUDES - DEPARTAMENTO DE PUNO")
    print("=" * 60)

    # 1. Recargar datos
    print("\n🔄 1. Recargando datos de altitudes...")
    data = reload_data()

    if not data:
        print("❌ No se pudieron cargar los datos de altitudes")
        return

    print(f"✅ Datos cargados: {len(data)} ciudades")

    # 2. Listar todas las ciudades disponibles
    print("\n📋 2. Ciudades disponibles:")
    print("-" * 40)

    for i, (city, altitude) in enumerate(data.items(), 1):
        print(f"{i:2d}. {city:<20} - {altitude:4d} msnm")

    # 3. Verificar función get_all_cities
    print("\n🔍 3. Verificando función get_all_cities()...")
    cities = get_all_cities()
    print(f"✅ Función retorna: {len(cities)} ciudades")
    print(f"   Ejemplo: {cities[:3] if cities else '[]'}")

    # 4. Probar get_altitude con algunas ciudades
    print("\n🎯 4. Probando get_altitude()...")
    test_cities = ["Puno", "Juliaca", "Ilave", "CiudadInexistente"]

    for city in test_cities:
        altitude = get_altitude(city)
        if altitude:
            print(f"   {city:<20} → {altitude:4d} msnm ✅")
        else:
            print(f"   {city:<20} → No encontrada ❌")

    # 5. Opción para agregar nueva ciudad
    print("\n➕ 5. ¿Deseas agregar o actualizar alguna ciudad?")
    print("   Formato: nombre_ciudad,altitud")
    print("   Ejemplo: Lima,1543")
    print("   Presiona Enter para continuar...")

    try:
        user_input = input("   Ciudad y altitud (o Enter para continuar): ").strip()

        if user_input and "," in user_input:
            parts = user_input.split(",", 1)
            new_city = parts[0].strip()
            new_altitude = int(parts[1].strip())

            print(f"\n💾 Agregando/Actualizando: {new_city} - {new_altitude}m")

            if update_city_altitude(new_city, new_altitude):
                print(f"✅ '{new_city}' actualizada exitosamente")

                # Recargar para mostrar cambios
                updated_data = reload_data()
                print(f"📊 Total ciudades ahora: {len(updated_data)}")
            else:
                print(f"❌ Error al actualizar '{new_city}'")
        elif user_input:
            print("❌ Formato inválido. Usa: ciudad,altitud")

    except KeyboardInterrupt:
        print("\n👋 Operación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n🏁 Verificación completada!")


if __name__ == "__main__":
    main()
