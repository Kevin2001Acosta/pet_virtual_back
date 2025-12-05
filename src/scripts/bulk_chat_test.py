import pandas as pd
import requests
import time

# Ruta al archivo Excel
excel_path = 'src/rag_system/excel_test/test.xlsx'

# Cargar el Excel
df = pd.read_excel(excel_path).fillna('')

# Endpoint de la api
url = 'http://localhost:8000/chatbot/chat'
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrZTE2YWNvc3RhQGdtYWlsLmNvbSIsImV4cCI6MTc2MjcyODk0NywidHlwZSI6ImFjY2VzcyJ9.VtPucWItTMr6yW_pt9i4zDA_I612ebC70Uo6p88Clas"
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
        emotion = response.json().get('emotion', '')
    else:
        respuesta_bot = f"Error: {response.status_code}"
        emotion="Error"
        
    
    df.at[idx, 'test'] = str(respuesta_bot)
    df.at[idx, 'time'] = tiempo_respuesta
    df.at[idx, 'emotion'] = emotion

    # Espera 1 segundo entre cada petición
    time.sleep(1)
    

# Guardar el DataFrame actualizado en un nuevo archivo
df.to_excel('src/rag_system/excel_test/test.xlsx', index=False)