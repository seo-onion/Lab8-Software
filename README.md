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
cp .env.example .env   # completar credenciales
```

## Pruebas y cobertura

```bash
pytest                 # corre tests y genera coverage.xml (objetivo >= 85%)
```

## Análisis de calidad (SonarQube)

```bash
sonar-scanner          # usa sonar-project.properties
```
