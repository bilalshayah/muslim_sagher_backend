# Muslim Sagher Backend

Django REST API backend for Muslim Sagher application.

## Features

- Django REST Framework
- JWT Authentication
- Swagger/OpenAPI Documentation
- CORS Support
- Video and Person Management

## Setup for Railway Deployment

### 1. Environment Variables

في Railway، أضف المتغيرات التالية في Settings > Variables:

- `SECRET_KEY`: Django secret key (استخدم `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` لتوليد واحد)
- `DEBUG`: `False` للإنتاج
- `ALLOWED_HOSTS`: `your-app-name.railway.app,localhost,127.0.0.1`

### 2. Database

المشروع يستخدم SQLite افتراضياً. للإنتاج، يُنصح باستخدام PostgreSQL:

1. أضف PostgreSQL service في Railway
2. احصل على `DATABASE_URL` من Railway
3. أضف `dj-database-url` إلى `requirements.txt`
4. عدّل `settings.py` لاستخدام PostgreSQL

### 3. Static Files

الملفات الثابتة يتم خدمتها عبر WhiteNoise تلقائياً.

### 4. Deploy

1. ارفع الكود على GitHub
2. اربط المشروع مع Railway
3. Railway سيقوم تلقائياً بـ:
   - تثبيت المكتبات من `requirements.txt`
   - تشغيل `collectstatic`
   - تشغيل المشروع عبر Gunicorn

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## API Documentation

بعد النشر، يمكنك الوصول إلى:
- Swagger UI: `https://your-app.railway.app/swagger/`
- ReDoc: `https://your-app.railway.app/redoc/`

## Project Structure

- `person/`: Person management app
- `video/`: Video management app
- `moslem/`: Main Django project settings