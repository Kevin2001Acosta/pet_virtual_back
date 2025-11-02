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
