from datetime import datetime

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLFloat,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)

from app.database import SessionLocal
from app.models import Metric
from app.services.metrics_service import (
    count_metrics,
    get_average_metrics,
    get_latest_metrics,
    get_metrics_between,
    get_peak_cpu_metric,
    get_peak_ram_metric,
)


def format_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat(timespec="seconds")


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ValueError("Use datas no formato ISO, por exemplo: 2026-09-15T16:30:00") from exc


def to_metric_dict(metric: Metric) -> dict:
    return {
        "id": metric.id,
        "timestamp": format_timestamp(metric.timestamp),
        "cpuPercent": metric.cpu_percent,
        "ramPercent": metric.ram_percent,
        "ramUsed": metric.ram_used,
        "ramTotal": metric.ram_total,
    }


MetricType = GraphQLObjectType(
    name="Metric",
    fields={
        "id": GraphQLField(GraphQLNonNull(GraphQLInt)),
        "timestamp": GraphQLField(GraphQLNonNull(GraphQLString)),
        "cpuPercent": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "ramPercent": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "ramUsed": GraphQLField(GraphQLNonNull(GraphQLInt)),
        "ramTotal": GraphQLField(GraphQLNonNull(GraphQLInt)),
    },
)

AverageMetricsType = GraphQLObjectType(
    name="AverageMetrics",
    fields={
        "averageCpu": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "averageRam": GraphQLField(GraphQLNonNull(GraphQLFloat)),
    },
)

PeakMetricsType = GraphQLObjectType(
    name="PeakMetrics",
    fields={
        "peakCpu": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "peakCpuTimestamp": GraphQLField(GraphQLString),
        "peakRam": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "peakRamTimestamp": GraphQLField(GraphQLString),
    },
)


def resolve_latest_metrics(_obj, _info, limit: int = 10) -> list[dict]:
    db = SessionLocal()
    try:
        return [to_metric_dict(metric) for metric in get_latest_metrics(db, limit)]
    finally:
        db.close()


def resolve_average_metrics(_obj, _info, minutes: int = 10) -> dict:
    db = SessionLocal()
    try:
        average_cpu, average_ram = get_average_metrics(db, minutes)
        return {"averageCpu": average_cpu, "averageRam": average_ram}
    finally:
        db.close()


def resolve_peak_metrics(_obj, _info, minutes: int = 10) -> dict:
    db = SessionLocal()
    try:
        cpu_metric = get_peak_cpu_metric(db, minutes)
        ram_metric = get_peak_ram_metric(db, minutes)
        return {
            "peakCpu": cpu_metric.cpu_percent if cpu_metric else 0,
            "peakCpuTimestamp": format_timestamp(cpu_metric.timestamp) if cpu_metric else None,
            "peakRam": ram_metric.ram_percent if ram_metric else 0,
            "peakRamTimestamp": format_timestamp(ram_metric.timestamp) if ram_metric else None,
        }
    finally:
        db.close()


def resolve_metrics_between(_obj, _info, start: str, end: str) -> list[dict]:
    start_date = parse_datetime(start)
    end_date = parse_datetime(end)
    db = SessionLocal()
    try:
        return [
            to_metric_dict(metric)
            for metric in get_metrics_between(db, start_date, end_date)
        ]
    finally:
        db.close()


def resolve_metrics_count(_obj, _info) -> int:
    db = SessionLocal()
    try:
        return count_metrics(db)
    finally:
        db.close()


QueryType = GraphQLObjectType(
    name="Query",
    fields={
        "latestMetrics": GraphQLField(
            GraphQLNonNull(GraphQLList(GraphQLNonNull(MetricType))),
            args={"limit": GraphQLArgument(GraphQLInt, default_value=10)},
            resolve=resolve_latest_metrics,
        ),
        "averageMetrics": GraphQLField(
            GraphQLNonNull(AverageMetricsType),
            args={"minutes": GraphQLArgument(GraphQLInt, default_value=10)},
            resolve=resolve_average_metrics,
        ),
        "peakMetrics": GraphQLField(
            GraphQLNonNull(PeakMetricsType),
            args={"minutes": GraphQLArgument(GraphQLInt, default_value=10)},
            resolve=resolve_peak_metrics,
        ),
        "metricsBetween": GraphQLField(
            GraphQLNonNull(GraphQLList(GraphQLNonNull(MetricType))),
            args={
                "start": GraphQLArgument(GraphQLNonNull(GraphQLString)),
                "end": GraphQLArgument(GraphQLNonNull(GraphQLString)),
            },
            resolve=resolve_metrics_between,
        ),
        "metricsCount": GraphQLField(
            GraphQLNonNull(GraphQLInt),
            resolve=resolve_metrics_count,
        ),
    },
)

schema = GraphQLSchema(query=QueryType)
