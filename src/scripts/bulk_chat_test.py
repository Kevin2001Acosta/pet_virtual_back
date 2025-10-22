import pandas as pd
import requests
import time

# Ruta al archivo Excel
excel_path = 'src/rag_system/excel_test/test2.xlsx'

# Cargar el Excel
df = pd.read_excel(excel_path)

# Endpoint de tu API
url = 'http://localhost:8000/chatbot/chat'
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrZTE2YWNvc3RhQGdtYWlsLmNvbSIsImV4cCI6MTc2MTE1NDgyOSwidHlwZSI6ImFjY2VzcyJ9.sU_6DPQN_I79TdVCDPpfsyup7jYXAqLKEsL5awr38-k"  # Cambia por el email de prueba

headers = {'Authorization': f'Bearer {token}'}

# Iterar sobre las preguntas y guardar la respuesta en la columna
for idx, row in df.iterrows():
    pregunta = row['Preguntas']
    payload = {"message": pregunta}
    
    start = time.time()
    response = requests.post(url, json=payload, headers=headers)
    end = time.time()
    tiempo_respuesta = end - start
    print(f"Tiempo de respuesta para la pregunta {idx+1}: {tiempo_respuesta} segundos")
    
    if response.ok:
        respuesta_bot = response.json().get('response', '')
    else:
        respuesta_bot = f"Error: {response.status_code}"
        
    
    df.at[idx, 'test2_chroma'] = str(respuesta_bot)
    df.at[idx, 'tiempo_test2_chroma'] = tiempo_respuesta

# Guardar el DataFrame actualizado en un nuevo archivo
df.to_excel('src/rag_system/excel_test/test2.xlsx', index=False)