from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Metric


def create_metric(
    db: Session,
    *,
    timestamp: datetime,
    cpu_percent: float,
    ram_percent: float,
    ram_used: int,
    ram_total: int,
) -> Metric:
    metric = Metric(
        timestamp=timestamp,
        cpu_percent=cpu_percent,
        ram_percent=ram_percent,
        ram_used=ram_used,
        ram_total=ram_total,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_latest_metrics(db: Session, limit: int = 10) -> list[Metric]:
    limit = max(1, min(limit, 200))
    return (
        db.query(Metric)
        .order_by(Metric.timestamp.desc(), Metric.id.desc())
        .limit(limit)
        .all()
    )


def count_metrics(db: Session) -> int:
    return db.query(Metric).count()


def get_metrics_between(db: Session, start: datetime, end: datetime) -> list[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.timestamp >= start, Metric.timestamp <= end)
        .order_by(Metric.timestamp.asc(), Metric.id.asc())
        .all()
    )


def get_average_metrics(db: Session, minutes: int) -> tuple[float, float]:
    since = datetime.now() - timedelta(minutes=max(1, minutes))
    result = (
        db.query(
            func.avg(Metric.cpu_percent),
            func.avg(Metric.ram_percent),
        )
        .filter(Metric.timestamp >= since)
        .one()
    )
    return float(result[0] or 0), float(result[1] or 0)


def get_peak_cpu_metric(db: Session, minutes: int) -> Metric | None:
    since = datetime.now() - timedelta(minutes=max(1, minutes))
    return (
        db.query(Metric)
        .filter(Metric.timestamp >= since)
        .order_by(Metric.cpu_percent.desc(), Metric.timestamp.desc())
        .first()
    )


def get_peak_ram_metric(db: Session, minutes: int) -> Metric | None:
    since = datetime.now() - timedelta(minutes=max(1, minutes))
    return (
        db.query(Metric)
        .filter(Metric.timestamp >= since)
        .order_by(Metric.ram_percent.desc(), Metric.timestamp.desc())
        .first()
    )
