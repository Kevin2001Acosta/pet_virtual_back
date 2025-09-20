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
