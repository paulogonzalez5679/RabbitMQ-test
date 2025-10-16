# orders_service/config/rabbit.py
import os
import asyncio
from aio_pika import connect_robust
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.dev
load_dotenv('.env.dev')

# Usar la URL de RabbitMQ desde .env.dev
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

if not RABBITMQ_URL:
    raise ValueError("RABBITMQ_URL debe estar definido en .env.dev")

_connection = None

async def get_rabbit_connection():
    global _connection
    if _connection and not _connection.is_closed:
        return _connection
    _connection = await connect_robust(RABBITMQ_URL)
    print(f"Connected to RabbitMQ at {RABBITMQ_URL}")
    return _connection
