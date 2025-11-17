from pysentimiento import create_analyzer
import transformers

# Desactivar logs molestos de transformers
transformers.logging.set_verbosity(transformers.logging.ERROR)

# Crear el analizador para emociones en español
emotion_analyzer = create_analyzer(task="emotion", lang="es")

def analyze_emotion(text: str) -> str:
    """
    Analiza la emoción principal de un texto en español.
    Devuelve el label de la emoción más probable.
    """
    result = emotion_analyzer.predict(text)
    return result.output  # Ejemplo: "joy", "sadness", "anger", etc.

def calculate_emotional_status(history) -> dict:
    """
    Calcula el estado emocional basado en el historial de emociones.

    Args:
        history (List[ChatHistory]): Lista de entradas de historial de chat.

    Returns:
        dict: Un diccionario con el estado emocional ('status') y un detalle ('detail').
    """
    # Definir las emociones negativas
    negative_emotions = {"anger", "disgust", "fear", "sadness"}

    if not history:
        return {"status": "verde", "detail": "No se encontró historial de chat con emociones para el usuario"}

    # Contar las emociones negativas
    negative_count = sum(1 for chat in history if chat.emotion in negative_emotions)
    total_chats = len(history)
    
    if total_chats < 8:
        return {"status": "verde", "detail": "No Hay suficientes conversaciones para determinar un estado emocional efectivamente."}

    # Calcular el porcentaje de emociones negativas
    negative_percentage = (negative_count / total_chats) * 100
    
    # Determinar el estado del semáforo
    if negative_percentage >= 70:
        return {"status": "rojo", "detail": f"El {negative_percentage:.2f}% de las emociones son negativas."}
    elif negative_percentage >= 40:
        return {"status": "amarillo", "detail": f"El {negative_percentage:.2f}% de las emociones son negativas."}
    else:
        return {"status": "verde", "detail": f"El {negative_percentage:.2f}% de las emociones son negativas."}




def calculate_weekly_emotional_levels(history, start_date_obj, end_date_obj):
    """
    Calcula los niveles emocionales para cada día de un rango de fechas, especialmente una semana.

    Args:
        history (list): Lista de objetos ChatHistory con información emocional.
        start_date_obj (datetime): Fecha inicial del rango.
        end_date_obj (datetime): Fecha final del rango.

    Returns:
        dict: Diccionario con los niveles emocionales por día de la semana.
    """
    from datetime import timedelta
    import locale
    
    print(locale.getlocale(), "configuración locale")

    # Crear un diccionario para almacenar los niveles emocionales por día
    emotional_levels = {}

    # Iterar sobre cada día en el rango de fechas
    current_date = start_date_obj
    while current_date <= end_date_obj:
        # Obtener el nombre del día de la semana
        day_name = current_date.strftime("%A")  # En español si locale está configurado

        # Filtrar el historial para el día actual
        day_history = [
            chat for chat in history if chat.timestamp.date() == current_date.date()
        ]

        # Calcular el nivel emocional para el día actual (puedes personalizar esta lógica)
        if day_history:
            emotional_level = calculate_daily_emotional_level(day_history, day_name)
        else:
            emotional_level = 0
        
        formatted_date = current_date.strftime("%Y-%m-%d")

        emotional_levels[formatted_date] = {"emotional_level": emotional_level, "day_name": day_name}

        # Avanzar al siguiente día
        current_date += timedelta(days=1)

    return emotional_levels

def calculate_daily_emotional_level(day_history, day_name):
    """
    Calcula el nivel emocional para un día específico.

    Args:
        day_history (list): Lista de objetos ChatHistory para el día específico.
        day_name (str): Nombre del día de la semana.

    Returns:
        dict: Diccionario con el nivel emocional del día objetivo.
    """

    # Especificar los valores de cada emoción
    emotion_values = {
        "sadness": -2,
        "fear": -2,
        "disgust": -2,
        "anger": -1,
        "others": 0,
        "surprise": 1,
        "joy": 2,
    }
    
    # Mapear toda la lista para crear una lista de valores dependiendo de la emoción
    mapped_values = [emotion_values.get(chat.emotion, 0) for chat in day_history]
    print(f"Valores mapeados para {day_name}: {mapped_values}")
    
    # calcular el promedio de los valores mapeados
    if mapped_values:
        average_value = sum(mapped_values) / len(mapped_values)
    else:
        average_value = 0
        
    if average_value <= -1.5:
        return "Muy Negativo"
    elif average_value <= -0.5:
        return "Negativo"
    elif average_value <= 0.5:
        return "Neutral"
    elif average_value < 1.5:
        return "Positivo"
    else:
        return "Muy Positivo"