import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_llm(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """
    Función helper para llamar a OpenAI API
    
    Args:
        prompt: El prompt a enviar
        model: Modelo a usar (default: gpt-4o-mini para eficiencia)
        temperature: Creatividad de la respuesta (0-1)
    
    Returns:
        Respuesta del modelo como string
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente médico especializado en fisiología de altura y análisis de fatiga."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error al llamar a OpenAI API: {str(e)}")
