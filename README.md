# Integrantes:

- Ezequiel Jaramillo
- Ivan Suarez
- Erick Minda

# EcoSoft: Clasificación Inteligente de Residuos

_EcoSoft_ es una plataforma web desarrollada en Django que utiliza inteligencia artificial (YOLO) para la clasificación automática de residuos sólidos urbanos. Permite a los usuarios identificar el tipo de residuo (plástico, papel, vidrio, metal) a través de imágenes, visualizar información ambiental relevante y localizar puntos de reciclaje cercanos.

![image](https://github.com/user-attachments/assets/c18279f7-cb34-4549-b97b-af9ff645512c)


## Características principales

- **Clasificación automática de residuos** mediante imágenes (subidas o en tiempo real con cámara).
- **Visualización de información ambiental** sobre el residuo detectado: tiempo de degradación, impacto ambiental y recomendaciones de reciclaje.
- **Historial personal** de residuos clasificados por usuario.
- **Gestión de usuarios** con autenticación, registro y perfiles personalizados (incluye foto de perfil almacenada en AWS S3).
- **Mapa interactivo** de puntos de reciclaje registrados por los usuarios.
- **Noticias y consejos** sobre reciclaje y sostenibilidad.

## Tecnologías utilizadas

- **Backend:** Django 5.2.1, PostgreSQL
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **IA:** Ultralytics YOLO (detección de objetos)
- **Almacenamiento de imágenes:** AWS S3 (fotos de perfil), almacenamiento local (residuos)
- **Otros:** Django Storages, python-decouple, dotenv

## Estructura del proyecto

```
├── manage.py
├── requirements.txt
├── .env
├── mysite/                # Configuración principal de Django
├── clasificador/          # App principal (modelos, vistas, IA)
│   ├── Modelos/best.pt    # Modelo YOLO entrenado
│   └── view/              # Vistas especializadas (clasificación, autenticación, etc.)
├── media/                 # Imágenes de usuarios y residuos
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── templates/             # Plantillas HTML
└── ...
```

## Instalación y configuración

1. **Clona el repositorio y entra al directorio:**
   ```bash
   git clone <repo_url>

   cd Proyecto_pruebas_IA_V2
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate 

   # En Linux/Mac
   source venv/bin/activate  
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   - Renombra `.env.example` a `.env` (o edita el existente) y completa los datos de la base de datos y AWS S3.

   ## Variables de entorno (`.env`)

      Ejemplo:
      ```
      #Base de datos - Aqui se uso Postgresql
      DB_ENGINE=django.db.backends.postgresql
      DB_DATABASE=nombre_db
      DB_USERNAME=usuario
      DB_PASSWORD=contraseña
      DB_SOCKET=localhost
      DB_PORT=5432

      #Amazon S3 se debe crear un bucket y un usuario y configurarlos
      AWS_ACCESS_KEY_ID=...
      AWS_SECRET_ACCESS_KEY=...
      AWS_DEFAULT_REGION=us-east-2
      AWS_STORAGE_BUCKET_NAME=...

      #Api para que aparezcan las noticias
      API_KEY_NEWSAPI=...

      # Email settings
      EMAIL_BACKEND =... 
      EMAIL_HOST =... 
      EMAIL_PORT =...
      EMAIL_USE_TLS = True
      EMAIL_USE_SSL = False
      EMAIL_HOST_USER =... 
      EMAIL_HOST_PASSWORD =...
      DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
      ```

5. **Realiza las migraciones y crea un superusuario:**
   **(asegurate de haber creado tu base de datos y agregar las variables de entorno en antes de hacer realizar las migraciones)**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Ejecuta el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

7. **Accede a la aplicación:**
   - Ve a `http://127.0.0.1:8000/` en tu navegador.

## Uso

- **Clasificar residuos:**
  - Sube una imagen o usa la cámara para identificar el tipo de residuo.
  - Visualiza la información ambiental y recomendaciones.
- **Historial:**
  - Consulta tu historial de residuos clasificados.
- **Mapa:**
  - Visualiza y registra puntos de reciclaje.
- **Noticias y consejos:**
  - Accede a información actualizada sobre reciclaje y sostenibilidad.

## Créditos

- Proyecto desarrollado por estudiantes de la UNEMI 2025.
- Modelo YOLO entrenado con Ultralytics.

## Licencia

Este proyecto es de uso académico y educativo. Consulta la licencia específica en el repositorio.
