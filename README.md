# Sistema de Gestión Universitaria

## Descripción

Este proyecto consiste en un sistema de gestión universitaria desarrollado con:

- Backend con FastAPI
- Base de datos relacional
- Docker y Docker Compose
- Variables de entorno mediante `.env`

El objetivo del sistema es administrar procesos universitarios como:

- Alumnos
- Carreras
- Materias
- Servicio social
- Prácticas profesionales
- Titulación
- Seguimiento de egresados
- Documentación académica

---

# Tecnologías utilizadas

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- MySQL
- Docker
- Docker Compose

---

# Requisitos previos

Antes de ejecutar el proyecto necesitas instalar:

- Docker Desktop
- Docker Compose
- Git

## Verificar instalación

```bash
docker --version
docker compose version
git --version
```

---

# Clonar el repositorio

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO
```

---

# Crear archivo .env

En la raíz del proyecto crea un archivo llamado:

```bash
.env
```

## Ejemplo de configuración

```env
# Base de datos
DB_HOST=db
DB_PORT=5432
DB_NAME=universidad
DB_USER=postgres
DB_PASSWORD=postgres

# Aplicación
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Seguridad
SECRET_KEY=CAMBIAR_POR_UNA_CLAVE_SEGURA
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Ajusta los valores dependiendo de tu configuración.

---

# Construir los contenedores

Para construir los contenedores por primera vez:

```bash
docker compose build
```

O construir y levantar todo automáticamente:

```bash
docker compose up --build
```

---

# Ejecutar el proyecto

## Levantar los contenedores

```bash
docker compose up
```

## Ejecutar en segundo plano

```bash
docker compose up -d
```

---

# Detener los contenedores

```bash
docker compose down
```

---

# Eliminar contenedores, volúmenes e imágenes

## Eliminar contenedores

```bash
docker compose down
```

## Eliminar contenedores y volúmenes

```bash
docker compose down -v
```

## Eliminar imágenes generadas

```bash
docker compose down --rmi all
```

## Eliminar todo completamente

```bash
docker compose down -v --rmi all
```

---

# Ver logs del proyecto

## Ver logs generales

```bash
docker compose logs
```

## Ver logs en tiempo real

```bash
docker compose logs -f
```

## Ver logs de un servicio específico

```bash
docker compose logs -f universidad_api
```

---

# Reiniciar contenedores

```bash
docker compose restart
```

---

# Acceder al contenedor

## Entrar al backend

```bash
docker exec -it universidad_api bash
```

## Entrar a la base de datos

```bash
docker exec -it universidad_db bash
```

---

# Ejecutar migraciones

Si el proyecto utiliza Alembic:

```bash
alembic upgrade head
```

Crear nueva migración:

```bash
alembic revision --autogenerate -m "descripcion"
```

---

# Acceso a la documentación

Una vez iniciado el proyecto, la API estará disponible en:

## Swagger UI

```text
http://localhost:8000/docs
```

## ReDoc

```text
http://localhost:8000/redoc
```

---

# Estructura del proyecto

```text
proyecto/
│
├── app/
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── crud/
│   ├── services/
│   └── main.py
│
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

---

# Comandos útiles

## Ver contenedores activos

```bash
docker ps
```

## Ver todas las imágenes

```bash
docker images
```

## Eliminar imágenes sin uso

```bash
docker image prune -a
```

## Eliminar volúmenes sin uso

```bash
docker volume prune
```

---

# Solución de problemas

## Reconstruir desde cero

```bash
docker compose down -v --rmi all
docker compose up --build
```

---

## Problema: cambios no reflejados

Reconstruir contenedores:

```bash
docker compose up --build
```

---

## Problema: puerto ocupado

Cambiar el puerto en:

- `.env`
- `docker-compose.yml`

---

## Problema: módulos faltantes

Instalar dependencias nuevamente:

```bash
pip install -r requirements.txt
```

---

# Variables importantes

| Variable                    | Descripción                    |
| --------------------------- | ------------------------------ |
| DB_HOST                     | Host de la base de datos       |
| DB_PORT                     | Puerto de la base de datos     |
| DB_NAME                     | Nombre de la base de datos     |
| DB_USER                     | Usuario de la base de datos    |
| DB_PASSWORD                 | Contraseña de la base de datos |
| SECRET_KEY                  | Clave secreta JWT              |
| ACCESS_TOKEN_EXPIRE_MINUTES | Tiempo de expiración del token |

---

# Recomendaciones

- No subir el archivo `.env` al repositorio.
- Agregar `.env` al `.gitignore`.
- Utilizar variables seguras en producción.
- Mantener las dependencias actualizadas.
- Utilizar migraciones para cambios en la base de datos.

---

# Archivo .gitignore recomendado

```gitignore
# Entorno
.env
venv/
__pycache__/

# Python
*.pyc
*.pyo

# Docker
*.log

# IDE
.vscode/
.idea/
```

---

# Autor

Proyecto desarrollado para la administración universitaria.
