import pandas as pd
import requests

# Ruta al archivo Excel
excel_path = 'src/rag_system/excel_test/preguntas.xlsx'

# Cargar el Excel
df = pd.read_excel(excel_path)

# Endpoint de tu API
url = 'http://localhost:8000/chatbot/chat'
email = "ke16acosta@gmail.com"  # Cambia por el email de prueba

# Iterar sobre las preguntas y guardar la respuesta en la columna
for idx, row in df.iterrows():
    pregunta = row['Preguntas']
    payload = {"message": pregunta, "email": email}
    response = requests.post(url, json=payload)
    if response.ok:
        respuesta_bot = response.json().get('response', '')
    else:
        respuesta_bot = f"Error: {response.status_code}"
    df.at[idx, 'Respuesta_sin_RAG'] = str(respuesta_bot)

# Guardar el DataFrame actualizado en un nuevo archivo
df.to_excel('src/rag_system/excel_test/preguntas_con_respuestas.xlsx', index=False)