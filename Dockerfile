# 1. Usar una imagen base de Python oficial, optimizada para slim (poco tamaño)
FROM python:3.11-slim

# 2. Configurar variables de entorno cruciales para PyTorch (CPU)
ENV PYTHONUNBUFFERED 1
# Le dice a PyTorch que solo use CPU y que no necesite librerías de GPU (lo que ahorra espacio)
ENV TORCH_NO_CUDA 1
ENV CUDA_VISIBLE_DEVICES -1

# 3. Crear y establecer el directorio de trabajo
WORKDIR /app

# 4. Copiar los archivos de requisitos e instalar las librerías
COPY requirements.txt .

# Utilizar --no-cache-dir para ahorrar espacio de disco
# El --break-system-packages es necesario en imágenes slim
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# 5. Copiar el resto del código de la aplicación (src, data, etc.)
COPY . .

# 6. Exponer el puerto (debe coincidir con la configuración de DigitalOcean)
EXPOSE 8080

# 7. Comando de inicio (CMD)
# El comando que corre tu app, igual al que pusiste en la configuración de la App Platform
CMD ["gunicorn", "src.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]