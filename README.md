# 🌟 ALTIVA  
### Sistema Multiagente de Fatiga y Productividad en Altura

ALTIVA es un sistema multiagente diseñado para analizar fatiga física y cognitiva en personas que viven o estudian en zonas de gran altitud, como el departamento de Puno (Perú). El sistema utiliza agentes cooperativos para inicializar perfiles fisiológicos, monitorear estados diarios y generar recomendaciones personalizadas de recuperación y productividad.

Este proyecto fue desarrollado como parte del curso de Inteligencia Artificial Multiagente, priorizando claridad arquitectónica, cooperación entre agentes y justificando el uso de IA.

---

## 🧠 Arquitectura General

El sistema está compuesto por **4 agentes**, cada uno con responsabilidades bien definidas.  
Se sigue el principio de **separación de responsabilidades**, evitando duplicación de lógica entre agentes.

> **Importante:** En el MVP actual NO se utilizan APIs externas de geolocalización ni clima.  
> La altitud se obtiene desde una base de datos local (JSON) para garantizar reproducibilidad y evitar errores por geolocalización.

---

## 🤖 Agentes del Sistema

### 1️⃣ Agente Inicial de Configuración (AG-INICIAL)

**Tipo:** Agente determinístico (NO LLM)

**Rol principal:**  
Inicializar el perfil fisiológico del usuario una sola vez.

**Entradas:**
- Edad  
- Sexo  
- Peso  
- Altura corporal  
- Ciudad (seleccionada manualmente)  
- Nivel de actividad base  

**Procesamiento:**
- Obtiene la altitud desde un archivo JSON local (ciudades del departamento de Puno).
- Calcula:
  - Agua diaria base recomendada
  - Horas de sueño base
- Ajusta valores según la altitud (> 3500 msnm).

**Salidas:**
- Perfil fisiológico persistente almacenado en base de datos.
- Valores base utilizados posteriormente por AG-FISIO.

**Justificación:**  
Este agente no utiliza LLM porque sus cálculos son determinísticos, repetibles y basados en reglas fisiológicas claras.

---

### 2️⃣ Agente Fisiológico (AG-FISIO)

**Tipo:** Agente determinístico (sin LLM en el MVP)

**Rol principal:**  
Monitorear el estado fisiológico del usuario de forma progresiva durante el día.

**Entradas progresivas:**
- Agua consumida en el momento
- Horas de sueño acumuladas
- Actividad física (minutos o pasos)
- Nivel subjetivo de energía (1–5)
- Altitud (recibida del perfil inicial)

**Salidas:**
- Estado fisiológico actual
- Indicadores de deshidratación y fatiga
- Alertas inmediatas (ej. falta de hidratación)

**Comunicación:**  
Envía su estado al AG-FATIGA para análisis inteligente.

---

### 3️⃣ Agente Predictor de Fatiga (AG-FATIGA)

**Tipo:** Agente con LLM

**Rol principal:**  
Analizar la fatiga acumulada utilizando razonamiento contextual.

**Entradas:**
- Estado fisiológico (AG-FISIO)
- Actividad mental (estudio/trabajo)
- Estado emocional (opcional)

**Salidas:**
- Nivel de fatiga (Bajo / Medio / Alto)
- Índice de Fatiga en Altura (IFA 0–100)
- Justificación textual del análisis

**Justificación del LLM:**  
Se requiere razonamiento causal, análisis contextual y generación de explicaciones en lenguaje natural.

---

### 4️⃣ Agente Planificador de Recuperación (AG-PLAN)

**Tipo:** Agente con LLM

**Rol principal:**  
Generar planes dinámicos de recuperación y productividad.

**Entradas:**
- Índice de fatiga (AG-FATIGA)
- Historial del día
- Condiciones fisiológicas actuales

**Salidas:**
- Recomendaciones inmediatas (hidratación, descanso)
- Horarios óptimos de estudio/trabajo
- Pausas activas y consejos por altitud

---

## 🔁 Flujo de Interacción del Usuario

1. **Inicio de sesión**
2. **Configuración inicial (AG-INICIAL)**  
   Se ejecuta una sola vez.
3. **Registro progresivo diario**
   - Agua
   - Sueño
   - Actividad
4. **Análisis de fatiga (AG-FATIGA)**
5. **Plan dinámico de recuperación (AG-PLAN)**

---

## 🗄️ Persistencia de Datos

Se utilizan tres colecciones independientes en MongoDB:

- `users` → autenticación
- `user_profiles` → perfil fisiológico estático
- `daily_states` → estados diarios dinámicos

Esto garantiza trazabilidad y claridad entre agentes.

---

## ⚙️ Tecnologías Utilizadas

- Python 3
- Streamlit (interfaz)
- MongoDB (persistencia)
- CrewAI (orquestación multiagente)
- Arquitectura basada en agentes cooperativos

---

## 🎓 Enfoque Académico

- El sistema justifica el uso de múltiples agentes.
- Cada agente tiene un rol claro y no redundante.
- El uso de LLM se limita únicamente a tareas que requieren razonamiento avanzado.
- Se prioriza reproducibilidad y claridad sobre complejidad innecesaria.

---

## 📌 Estado del Proyecto

- MVP funcional
- AG-INICIAL implementado
- Sistema de login operativo
- Arquitectura multiagente lista para expansión

