# notifications_service/consumer.py
import asyncio
from aio_pika import ExchangeType, Message
from config.rabbit import get_connection
import json

async def handle_message(message):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            order_id = payload.get("order_id")
            print(f"[notifications_service] New order received: {order_id}", flush=True)
        except Exception as e:
            print(f"[notifications_service] Failed to process message: {e}")
            # message will be requeued/acked based on process policy

async def main():
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue("orders_queue", durable=True)
        await queue.consume(handle_message, no_ack=False)
        print("[notifications_service] Listening on orders_queue...")
        # Prevent exit
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Consumer stopped")
