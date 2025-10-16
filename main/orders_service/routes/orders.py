# orders_service/routes/orders.py
from fastapi import APIRouter, HTTPException, status
from models import OrderCreate, OrderResponse
from config.database import get_db
from config.rabbit import get_rabbit_connection
from aio_pika import Message
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import datetime
import json
import asyncio

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate):
    try:
        # Obtener la instancia de la base de datos
        db: AsyncIOMotorDatabase = await get_db()

        # Save order to MongoDB
        order_doc = payload.dict()
        order_doc["created_at"] = datetime.datetime.utcnow()
        result = await db.orders.insert_one(order_doc)
        order_id = str(result.inserted_id)

        # Publish to RabbitMQ
        try:
            conn = await get_rabbit_connection()
            async with conn.channel() as channel:
                q = await channel.declare_queue("orders_queue", durable=True)
                body = json.dumps({"order_id": order_id}).encode()
                await channel.default_exchange.publish(
                    Message(body, delivery_mode=2),
                    routing_key=q.name
                )
        except Exception as e:
            print(f"[orders_service] Failed to publish message for order {order_id}: {e}")

        # Get created order
        created = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not created:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found after creation"
            )

        return {
            "id": order_id,
            "customer_name": created["customer_name"],
            "product_id": created["product_id"],
            "quantity": created["quantity"],
            "created_at": created["created_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
