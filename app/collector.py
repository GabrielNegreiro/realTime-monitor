import asyncio
import logging
import os
from datetime import datetime

import psutil

from app.database import SessionLocal
from app.services.metrics_service import create_metric
from app.websocket import manager


DEFAULT_COLLECTION_INTERVAL = 2
logger = logging.getLogger(__name__)


def get_collection_interval() -> float:
    value = os.getenv("COLLECTION_INTERVAL", str(DEFAULT_COLLECTION_INTERVAL))
    try:
        interval = float(value)
    except ValueError:
        return DEFAULT_COLLECTION_INTERVAL
    return max(0.5, interval)


def collect_current_metric() -> dict:
    memory = psutil.virtual_memory()
    timestamp = datetime.now().replace(microsecond=0)

    return {
        "timestamp": timestamp,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": memory.percent,
        "ram_used": memory.used,
        "ram_total": memory.total,
    }


def serialize_metric(metric: dict) -> dict:
    return {
        "timestamp": metric["timestamp"].isoformat(),
        "cpu_percent": metric["cpu_percent"],
        "ram_percent": metric["ram_percent"],
        "ram_used": metric["ram_used"],
        "ram_total": metric["ram_total"],
    }


async def collect_metrics_forever() -> None:
    psutil.cpu_percent(interval=None)
    interval = get_collection_interval()

    while True:
        metric_data = collect_current_metric()
        db = SessionLocal()
        try:
            create_metric(db, **metric_data)
        except Exception:
            logger.exception("Erro ao salvar metrica no banco de dados.")
        finally:
            db.close()

        await manager.broadcast(serialize_metric(metric_data))
        await asyncio.sleep(interval)
