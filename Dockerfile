# Usa una imagen base oficial de Python 3.11 en su versión slim.
# Esta versión es más ligera que la estándar, ideal para producción.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
# Aquí se copiarán los archivos de la aplicación.
WORKDIR /app

# Copia el archivo requirements.txt para instalar las dependencias primero.
# Esto mejora la eficiencia del cache de Docker.
COPY requirements.txt .

# Instala todas las dependencias de Python.
# El flag '--no-cache-dir' reduce el tamaño de la imagen.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de tu proyecto al directorio de trabajo.
COPY . .

# Expone el puerto que usará la aplicación.
# Por defecto, FastAPI se ejecuta en el puerto 8000.
EXPOSE 8000

# Comando para ejecutar la aplicación con Uvicorn.
# 'main:app' se refiere al objeto 'app' en el archivo 'main.py'.
# '--host 0.0.0.0' hace que la aplicación sea accesible desde fuera del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
