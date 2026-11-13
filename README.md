# TechSolutions — versión Django

Conversión del proyecto Flask original a **Django** con plantillas, CSS y funcionalidades equivalentes. Se mantienen los tres servicios presentes en el ZIP original.

## Ejecutar localmente (Windows)

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ . El superusuario puede entrar al panel personalizado en `/admin` y al administrador nativo de Django en `/django-admin/`.

## GitHub

```bash
git init
git add .
git commit -m "TechSolutions Django"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Si el repositorio ya tiene un remoto `origin`, no vuelvas a agregarlo; utiliza `git remote -v`.

## Publicación en Render

Crear **Web Service** conectado al repositorio. Configurar:

- Build command: `bash build.sh`
- Start command: `gunicorn config.wsgi:application`
- Environment variables: `SECRET_KEY` (clave aleatoria larga), `DEBUG=False`, `ALLOWED_HOSTS=tu-app.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://tu-app.onrender.com`

**Persistencia:** Render puede tener almacenamiento efímero. SQLite perderá registros tras reinicios o despliegues si no hay disco persistente. Para un sitio real, configura una base de datos persistente (por ejemplo PostgreSQL) antes de recibir registros de clientes. Este proyecto viene con SQLite para pruebas locales. No subas bases de datos ni secretos a GitHub.

## Datos originales

No se incluyen usuarios, contraseñas ni registros de la base SQLite original. Se crea una base nueva con `migrate` por seguridad. La migración de datos históricos requiere un proceso aparte.
