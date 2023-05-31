# Usar un runtime oficial de Python como imagen padre
FROM python:3.10-slim
LABEL maintainer="patxijuaristi@uma.es"

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el contenido del directorio actual en el contenedor en /app
COPY app /app

# Instalar los paquetes necesarios especificados en requirements.txt
RUN apt-get update -y && apt-get install -y python3-opencv

# Establecer la variable de entorno para el archivo de credenciales de Google Cloud
ENV GOOGLE_APPLICATION_CREDENTIALS=clave_google.json

RUN pip install -r requirements.txt

# Haz que el puerto 4000 esté disponible para el mundo fuera de este contenedor
EXPOSE 4000

# Ejecutar app.py cuando se inicie el contenedor
CMD ["python", "app.py"]
