# Chatbot PYMES Aeroespacial

## Descripción
Chatbot inteligente desarrollado para proporcionar soporte técnico y consultas a empresas PyMES en el sector aeroespacial, utilizando modelos de lenguaje avanzados y una base de datos optimizada.

## Requisitos Previos
- Python 3.8 o superior
- MySQL Server instalado y ejecutándose
- Git
- Una cuenta en Groq para obtener API Key

## Pasos de Instalación y Uso

### 1. Crear una API Key en Groq
1. Visita https://console.groq.com/home
2. Inicia sesión o crea una cuenta (es gratuito)
3. Genera una nueva API Key para usar el modelo Llama3
4. Copia la API Key para usarla más adelante

### 2. Clonar el Repositorio
```bash
git clone https://github.com/testabet/chatbot-PYMES-aeroespacial.git
cd chatbot-PYMES-aeroespacial
```

### 3. Crear el Entorno Virtual
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Crear el Archivo .env
Crea un archivo llamado `.env` en la raíz del proyecto con las siguientes variables de entorno:

```
DB_user=TU_USUARIO
DB_pass=TU_CONTRASEÑA
GROQ_API_KEY=TU_API_KEY_GROQ
```

Reemplaza:
- `TU_USUARIO`: Tu usuario de MySQL
- `TU_CONTRASEÑA`: Tu contraseña de MySQL
- `TU_API_KEY_GROQ`: La API Key obtenida de Groq

### 6. Descargar la Base de Datos
Descarga los archivos CSV de la base de datos 2024 desde el siguiente enlace de Google Drive:

https://drive.google.com/drive/u/0/folders/1ZIFgCKua0kuRv_YWN80PxUbQR4RYZ1HF

**Nota**: También está disponible la base de datos de 2023:
https://drive.google.com/drive/folders/1ZCa32yqy8d9b9Ark6e0kgyuski-UWVky?usp=sharing

Coloca los archivos descargados en una carpeta accesible del proyecto.

### 7. Crear la Base de Datos en MySQL
```bash
# Inicia sesión en MySQL
mysql -u TU_USUARIO -p

# En la consola de MySQL, ejecuta:
CREATE DATABASE chatbot_pymes;
USE chatbot_pymes;
```

### 8. Cargar los Datos en la Base de Datos
Ejecuta el script de carga de datos:

```bash
python cargar_datos_sql.py
```

Este script leerá los archivos CSV descargados y los cargará en la base de datos MySQL.

### 9. Iniciar el Servidor API
Ejecuta el servidor API:

```bash
python api_server.py
```

El servidor se iniciará y quedará escuchando las solicitudes (típicamente en `http://localhost:5000` o el puerto configurado).

### 10. Abrir el Frontend
Abre el archivo `index.html` en tu navegador web preferido:

```bash
# En Windows
start index.html

# En macOS
open index.html

# En Linux
xdg-open index.html
```

O simplemente navega hasta la ubicación del archivo `index.html` y haz doble clic en él.

## Base de Datos

- **2024**: https://drive.google.com/drive/u/0/folders/1ZIFgCKua0kuRv_YWN80PxUbQR4RYZ1HF
- **2023**: https://drive.google.com/drive/folders/1ZCa32yqy8d9b9Ark6e0kgyuski-UWVky?usp=sharing

## API KEY Groq

Obtener una API KEY para usar el modelo Llama3 (gratuito): https://console.groq.com/home

## Solución de Problemas

- **Error de conexión a MySQL**: Verifica que MySQL esté ejecutándose y que las credenciales en `.env` sean correctas.
- **Error de API Key Groq**: Asegúrate de que la clave está correctamente configurada en el archivo `.env`.
- **Problemas al cargar datos**: Verifica que los archivos CSV estén en el formato correcto y en la ruta esperada.
- **Frontend no se muestra**: Asegúrate de que el servidor API esté ejecutándose antes de abrir `index.html`.

## Contacto y Soporte

Para problemas o sugerencias, por favor abre un issue en el repositorio.
