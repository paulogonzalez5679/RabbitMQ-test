#!/bin/sh
set -e
host=${RABBITMQ_HOST:-rabbitmq}
port=${RABBITMQ_PORT:-5672}
echo "Esperando a que RabbitMQ esté disponible en $host:$port..."
while ! nc -z $host $port; do
  sleep 1
done
echo "RabbitMQ está listo, iniciando consumidor..."
exec python consumer.py
