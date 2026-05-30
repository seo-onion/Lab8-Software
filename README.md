# Sistema de Recompensas para Restaurantes

Solución orientada a eventos (EDA + Clean Architecture) para un programa de
fidelización de restaurantes. Una cena registrada por un restaurante se publica
en **RabbitMQ**; un microservicio de recompensas la consume, calcula puntos y
cashback, y actualiza la cuenta del cliente.

> Tarea 8 — CS3081 Ingeniería de Software (UTEC). Ver [`DESIGN.md`](DESIGN.md)
> para el análisis y diseño completo.

## Arquitectura

```
Restaurant Service (FastAPI) --publish--> [Exchange -> Queue] --consume--> Rewards Service --> SQLite
                                                                                  |
                                                                          (recompensa > 0)
                                                                                  v
                                                                       [Queue notificaciones] --> Notifier (simulado)
```

| Módulo | Rol |
|--------|-----|
| `shared/` | Contrato de eventos, serialización, topología AMQP y utilidades de seguridad |
| `restaurant_service/` | Producer: API REST que registra cenas y publica eventos |
| `rewards_service/` | Consumer: calcula recompensas, persiste en SQLite y notifica |

## Requisitos

- Python 3.14
- Acceso al RabbitMQ del curso (ver variables de entorno)

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno

Configúralas en un archivo `.env` (ignorado por git):

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `RABBITMQ_HOST` | Host del broker | `213.199.42.57` |
| `RABBITMQ_PORT` | Puerto AMQP | `5672` |
| `RABBITMQ_USER` | Usuario | `students` |
| `RABBITMQ_PASSWORD` | Contraseña | *(provista por el curso)* |
| `RABBITMQ_VHOST` | Virtual host | `/` |
| `REWARDS_DB_PATH` | Ruta de la BD SQLite | `rewards.db` |

## Pruebas y cobertura

```bash
pytest                 # corre tests y genera coverage.xml (objetivo >= 85%)
```

## Análisis de calidad (SonarQube)

El token **no** se versiona; se pasa por la variable de entorno `SONAR_TOKEN`,
que `sonar-scanner` lee de forma automática:

```bash
pytest                                   # 1. genera coverage.xml
export SONAR_TOKEN=sqa_xxxxxxxxxxxxxxxx   # 2. token de SonarQube
sonar-scanner                            # 3. analiza y sube al servidor
```

Como atajo, el token puede guardarse en un `.env.sonar` (ignorado por git):

```bash
set -a && source .env.sonar && set +a && sonar-scanner
```
