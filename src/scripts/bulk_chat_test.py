import pandas as pd
import requests
import time

# Ruta al archivo Excel
excel_path = 'src/rag_system/excel_test/test2.xlsx'

# Cargar el Excel
df = pd.read_excel(excel_path).fillna('')

# Endpoint de tu API
url = 'http://localhost:8000/chatbot/chat'
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtb25pY2EyM0BnbWFpbC5jb20iLCJleHAiOjE3NjI0NjgyMjYsInR5cGUiOiJhY2Nlc3MifQ.rNtNLi0IbYQMyuS5iU2dSLL1dLdw7qGHd8Le3ugizD0"
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
        
    
    df.at[idx, 'test5'] = str(respuesta_bot)
    df.at[idx, 'tiempo_test5'] = tiempo_respuesta

# Guardar el DataFrame actualizado en un nuevo archivo
df.to_excel('src/rag_system/excel_test/test2.xlsx', index=False)