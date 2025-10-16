<h1 align="center">🪄 Sistema de Órdenes y Notificaciones con RabbitMQ</h1>

Este proyecto implementa un sistema de microservicios con FastAPI, MongoDB y RabbitMQ para la gestión de órdenes y notificaciones.

---

## 🧱 Arquitectura del sistema

El sistema está compuesto por dos microservicios principales:

- **orders_service**: API REST para crear y consultar órdenes (FastAPI + MongoDB).
- **notifications_service**: Consumidor de eventos de órdenes desde RabbitMQ.

<details>
<summary>Diagrama conceptual</summary>

```
┌──────────────┐      POST /orders      ┌────────────────────┐
│  Cliente     │ ────────────────────▶ │  orders_service    │
└──────────────┘                       └─────────┬──────────┘
                                                │
                                                │ Evento (RabbitMQ)
                                                ▼
                                      ┌────────────────────┐
                                      │ notifications_     │
                                      │ service            │
                                      └────────────────────┘
```
</details>

---

## ⚙️ Variables de entorno necesarias

Ejemplo de archivo `.env`:

```env
# MongoDB
MONGO_URI=mongodb://mongo:27017
MONGO_DB=orders_db

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

---

## 🐇 Cómo levantar RabbitMQ y MongoDB localmente

1. Desde la carpeta principal ejecuta:
   ```bash
   docker compose up --build
   ```
2. Esto levantará:
   - RabbitMQ (puertos 5672 AMQP, 15672 UI)
   - MongoDB (puerto 27018 en host, 27017 en red Docker)
   - orders_service (puerto 8000)
   - notifications_service (solo consumidor)

---

## 🧪 Cómo probar el flujo completo (end-to-end)

1. Abre Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
2. Haz un POST a `/orders` con un cuerpo como:
   ```json
   {
     "customer_name": "Juan",
     "product_id": "ABC123",
     "quantity": 2,
     "note": "Entrega rápida"
   }
   ```
3. El pedido se guarda en MongoDB y se publica un mensaje en RabbitMQ.
4. El servicio `notifications_service` consume el mensaje y verás en los logs:
   ```bash
   docker compose logs -f notifications_service
   ```
   Salida esperada:
   ```
   [notifications_service] New order received: {'customer_name': 'Juan', 'product_id': 'ABC123', 'quantity': 2, 'note': 'Entrega rápida'}
   ```
5. Puedes ver la cola y los mensajes en la UI de RabbitMQ: [http://localhost:15672](http://localhost:15672)

---

## 💻 Ejecución individual de microservicios

### orders_service
```bash
cd main/orders_service
pip install -r requirements.txt
uvicorn main:app --reload
```

### notifications_service
```bash
cd main/notifications_service
pip install -r requirements.txt
python consumer.py
```

---

## 🧭 Accesos rápidos

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- RabbitMQ UI: [http://localhost:15672](http://localhost:15672) (guest/guest)
- MongoDB URI (host): `mongodb://localhost:27018`
- MongoDB URI (contenedor): `mongodb://mongo:27017`

---

## 🧰 Estructura del proyecto

```text
main/
├─ docker-compose.yml         # Orquestación de servicios
├─ README.md                  # Documentación principal
├─ notifications_service/
│  ├─ consumer.py             # Consumidor de eventos RabbitMQ
│  ├─ config/                 # Configuración
│  ├─ requirements.txt        # Dependencias
│  └─ Dockerfile
├─ orders_service/
│  ├─ main.py                 # API de órdenes (FastAPI)
│  ├─ routes/                 # Rutas
│  ├─ models.py               # Modelos
│  ├─ config/                 # Configuración
│  ├─ requirements.txt        # Dependencias
│  └─ Dockerfile
├─ .env.example               # Variables de entorno ejemplo
└─ ...
```

---

## 🚪 Puertos utilizados

- `8000`: orders_service (API REST)
- `5672`: RabbitMQ (AMQP)
- `15672`: RabbitMQ (UI web)
- `27018`: MongoDB (host)
- `27017`: MongoDB (red Docker)

---

## 🐳 Ejecución rápida con Docker Compose

```bash
docker compose up --build
```
1. Accede a:
	- API de órdenes (Swagger): http://localhost:8000/docs
	- RabbitMQ UI: http://localhost:15672 (guest/guest)
	- MongoDB: mongodb://localhost:27018
2. Prueba el flujo creando una orden desde Swagger y verifica el log del consumidor:
	```bash
	docker compose logs -f notifications_service
	```
   Abre Swagger UI en [http://localhost:8000/docs](http://localhost:8000/docs)
   <br/>
3. Haz un POST a `/orders` con un cuerpo como:
	```json
	{
	  "customer_name": "Juan",
	  "product_id": "ABC123",
	  "quantity": 2,
	  "note": "Entrega rápida"
	}
	```
   <br/>
4. El pedido se guardará en MongoDB y se publicará un mensaje en RabbitMQ.<br/>

5. El servicio `notifications_service` consumirá el mensaje y verás en sus logs, puedes ejecutar `docker compose logs -f notifications_service` para ver a nivel de los logs:
	```
	[notifications_service] New order received: {'customer_name': 'Juan', 'product_id': 'ABC123', 'quantity': 2, 'note': 'Entrega rápida'}
	```

<br/>Tambien puedes ver los mensajes en la cola `orders_queue` desde la UI de RabbitMQ.

---

## 🛡️ Notas y advertencias

- Asegúrate de tener Docker y Docker Compose instalados.
- Los puertos pueden variar si ya tienes servicios corriendo en tu máquina.
- Para desarrollo local, puedes usar MongoDB Compass o el cliente `mongo` para inspeccionar la base de datos.
- Si modificas las variables de entorno, reinicia los servicios para aplicar los cambios.