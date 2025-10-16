# orders_service/config/database.py
import os
from typing import Any, Optional
from dotenv import load_dotenv
from pymongo.errors import CollectionInvalid
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Definir cliente y db a nivel de módulo
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    """Retorna la instancia de la base de datos"""
    global db
    if db is None:
        db = await connect_to_mongo()
    if db is None:
        raise RuntimeError("No se pudo establecer la conexión con la base de datos")
    return db

# Cargar variables de entorno desde .env.dev
load_dotenv('.env.dev')

# Usar las variables específicas de tu .env.dev
MONGODB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "orders_db")

if not MONGODB_URI or not MONGO_DB:
    raise ValueError("MONGO_URI y MONGO_DB deben estar definidos en .env.dev o como variables de entorno")

async def ensure_indexes(db_instance):
    """Asegura que los índices necesarios existan en la colección de órdenes"""
    try:
        # Crear índices para búsquedas comunes
        await db_instance.orders.create_index("customer_email")
        await db_instance.orders.create_index([("created_at", -1)])  # -1 para orden descendente
        print("Índices creados/verificados correctamente")
    except Exception as e:
        print(f"Error creando índices: {e}")

async def ensure_collections(db_instance):
    """Asegura que las colecciones necesarias existan"""
    try:
        # Crear la colección orders si no existe
        if "orders" not in await db_instance.list_collection_names():
            await db_instance.create_collection("orders")
            print("Colección 'orders' creada")
        
        # Crear cualquier otra colección necesaria aquí
        
    except CollectionInvalid:
        # La colección ya existe
        pass
    except Exception as e:
        print(f"Error creando colecciones: {e}")

async def connect_to_mongo() -> AsyncIOMotorDatabase:
    """Establece la conexión con MongoDB y retorna la instancia de la base de datos"""
    global client, db
    
    if MONGO_DB is None:
        raise RuntimeError("La variable de entorno MONGO_DB no está definida")
    
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGO_DB]
        
        # Asegurar colecciones e índices
        await ensure_collections(db)
        await ensure_indexes(db)
        
        print(f"Connected to MongoDB at {MONGODB_URI} (orders_service)")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection (orders_service)")
