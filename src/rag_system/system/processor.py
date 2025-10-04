
def procesar_texto(texto: str) -> str:
    # Limpieza básica: quitar espacios extra, saltos de línea
    texto = texto.replace("\n", " ").strip()
    # Aquí podrías agregar: lower(), eliminar stopwords, etc.
    return texto


