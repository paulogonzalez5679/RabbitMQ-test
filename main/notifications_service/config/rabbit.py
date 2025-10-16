# notifications_service/config/rabbit.py
import os
import time
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv
from aio_pika import connect_robust

# Cargar variables de entorno desde .env (usar .env.dev si prefieres)
load_dotenv('.env.dev')

# Leer RABBITMQ_URL desde .env
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

if not RABBITMQ_URL:
    raise ValueError("RABBITMQ_URL debe estar definido en .env")
else:
    # mypy-friendly: asegurar que es str
    RABBITMQ_URL = str(RABBITMQ_URL)

_connection = None

from typing import Optional, List


def _build_alternate_urls(url: Optional[str]) -> List[str]:
    """Genera una lista de URLs candidatas a probar a partir de la URL original.

    Si la URL original apunta a localhost o 127.0.0.1 se generarán alternativas
    reemplazando el host por `host.docker.internal` (útil en macOS) y por
    `rabbitmq` (nombre del servicio en docker-compose).
    """
    if not url:
        return []
    parsed = urlparse(url)
    host = parsed.hostname
    candidates = [url]
    if host in ("localhost", "127.0.0.1", "::1"):
        for alt_host in ("host.docker.internal", "rabbitmq"):
            # reconstruir netloc preservando usuario, contraseña y puerto
            userinfo = ""
            if parsed.username:
                userinfo += parsed.username
                if parsed.password:
                    userinfo += f":{parsed.password}"
                userinfo += "@"
            netloc = userinfo + alt_host
            if parsed.port:
                netloc += f":{parsed.port}"
            alt = parsed._replace(netloc=netloc)
            candidates.append(urlunparse(alt))
    return candidates

async def get_connection(retries_per_candidate: int = 2, backoff: float = 1.0):
    """Devuelve una conexi\xf3n robusta cacheada a RabbitMQ.

    Intenta la URL configurada y, si apunta a localhost, prueba alternativas
    comunes usadas en entornos Docker/macOS. Lanza un error claro si ninguna
    URL funciona.
    """
    global _connection
    if _connection and not _connection.is_closed:
        return _connection

    tried = []
    last_exc = None
    candidates = _build_alternate_urls(RABBITMQ_URL)

    for candidate in candidates:
        for attempt in range(1, retries_per_candidate + 1):
            try:
                _connection = await connect_robust(candidate)
                return _connection
            except Exception as e:
                tried.append((candidate, attempt, str(e)))
                last_exc = e
                # pequeño backoff entre reintentos
                time.sleep(backoff)

    # Si llegamos aquí, ninguna candidate conectó
    message_lines = [f"No se pudo conectar a RabbitMQ. Se intentaron las siguientes URLs:"]
    for u, attempt, err in tried:
        message_lines.append(f" - {u} (intento {attempt}): {err}")
    message_lines.append("Asegúrate de ejecutar con docker-compose (el servicio 'rabbitmq') o de establecer RABBITMQ_URL a la dirección correcta.")
    raise ConnectionError("\n".join(message_lines)) from last_exc
