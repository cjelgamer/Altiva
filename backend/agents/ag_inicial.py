from backend.services.altitude_loader import get_altitude
from backend.services.database import user_profiles
from datetime import datetime

def run_ag_inicial(user_id, data: dict) -> dict:
    """
    AG-INICIAL: Inicializa el perfil fisiológico del usuario
    
    Entradas: Edad, Sexo, Peso, Altura, Ciudad, Nivel de actividad
    Salidas: Perfil con agua_base_ml y sueno_base_h calculados
    """
    
    # Convertir user_id a string si es ObjectId
    user_id_str = str(user_id)
    
    # Verificar si ya existe perfil
    existing = user_profiles.find_one({"user_id": user_id_str})
    if existing:
        return existing
    
    # Obtener altitud desde JSON local
    altitud = get_altitude(data["ciudad"])
    if altitud is None:
        raise ValueError("Ciudad no válida")

    # Calcular agua base según sexo
    agua_base_ml = 3700 if data["sexo"] == "M" else 2700
    # Ajustar por altitud (>1500 msnm)
    if altitud > 1500:
        agua_base_ml += int((altitud - 1500) / 1000 * 300)

    # Calcular sueño base
    sueno_base_h = 8
    # Ajustar por altitud (>3500 msnm)
    if altitud > 3500:
        sueno_base_h += 0.5

    profile = {
        "user_id": user_id_str,
        "edad": data["edad"],
        "sexo": data["sexo"],
        "peso": data["peso"],
        "altura": data["altura"],
        "ciudad": data["ciudad"],
        "nivel_actividad": data.get("nivel_actividad", "medio"),
        "altitud": altitud,
        "agua_base_ml": agua_base_ml,
        "sueno_base_h": sueno_base_h,
        "created_at": datetime.utcnow(),
        "created_by": "AG-INICIAL"
    }

    user_profiles.insert_one(profile)
    return profile

