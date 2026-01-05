import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "puno_altitudes.json"


def get_altitude(city: str) -> int:
    """
    Obtiene la altitud de una ciudad del departamento de Puno.

    Args:
        city: Nombre de la ciudad

    Returns:
        Altitud en metros, o 0 si no se encuentra
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(city, 0)
    except FileNotFoundError:
        print(f"⚠️ Archivo de altitudes no encontrado: {DATA_PATH}")
        return 0
    except json.JSONDecodeError as e:
        print(f"⚠️ Error al leer JSON de altitudes: {e}")
        return 0


def get_all_cities() -> list:
    """
    Obtiene todas las ciudades disponibles en el archivo de altitudes.

    Returns:
        Lista de ciudades disponibles
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.keys())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error al cargar ciudades: {e}")
        return []


def update_city_altitude(city: str, altitude: int) -> bool:
    """
    Actualiza o agrega la altitud de una ciudad en el archivo JSON.

    Args:
        city: Nombre de la ciudad
        altitude: Altitud en metros

    Returns:
        True si se actualizó correctamente, False si hubo error
    """
    try:
        # Cargar datos existentes
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Actualizar o agregar la ciudad
        data[city] = altitude

        # Guardar datos actualizados
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Ciudad '{city}' actualizada con altitud {altitude}m")
        return True

    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"❌ Error al actualizar altitud de '{city}': {e}")
        return False


def reload_data() -> dict:
    """
    Recarga los datos del archivo JSON y los retorna.

    Returns:
        Diccionario completo de ciudades y altitudes
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"🔄 Datos de altitudes recargados: {len(data)} ciudades")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al recargar datos: {e}")
        return {}
