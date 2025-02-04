## Local Setup

### 1. Update submodule
```shell
git submodule update --init --remote
```

### 2. Follow steps for basic docker compose setup in `stack` repository

### 3. Install GDAL, GEOS: https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/geolibs/

### 4. Create `.env` file. Working example for docker-compose local deploy (replace GDAL_LIBRARY_PATH and GEOS_LIBRARY_PATH):
```dotenv
DJANGO_SECRET_KEY=eJWuyaUEO7W8SmiAR2AYmzmosHT25zTyRRx2sz8JA0buWvqppUHjVuFfESF9Vw4h
DJANGO_DEBUG=true
POSTGIS_HOST=localhost
POSTGIS_USER=postgres
POSTGIS_PASSWORD=pass
POSTGIS_PORT=9990
REDIS_HOST=localhost
REDIS_PORT=9991
AMQP_HOST=localhost
AMQP_PORT=9992
AMQP_USER=user
AMQP_PASSWORD=pass
KAFKA_HOST=localhost
KAFKA_PORT=9993
GDAL_LIBRARY_PATH=/opt/homebrew/Cellar/gdal/3.10.0_3/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/Cellar/geos/3.13.0/lib/libgeos_c.dylib
KAFKA_CONSUMER_TOPIC=polygons_back
KAFKA_PRODUCER_TOPIC=polygons
CORS_ORIGIN_WHITELIST='["http://localhost:5173"]'
DJANGO_LOG_LEVEL=INFO
APP_LOG_LEVEL=DEBUG
```

### 5. Install python dependencies
```shell
pip install -r requirements.txt
```

## Run

### Web app
```shell
python manage.py runserver 8000
```

### Celery
```shell
celery -A backend worker -l INFO
# Apple Silicon
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES; celery -A backend worker -l INFO
```

### Kafka consumer
```shell
python manage.py run_kafka_consumer
```

## Urls
- Rest api docs (swagger): [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)
- Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
