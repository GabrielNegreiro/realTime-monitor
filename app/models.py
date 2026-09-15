from sqlalchemy import BigInteger, Column, DateTime, Float, Integer

from app.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    cpu_percent = Column(Float, nullable=False)
    ram_percent = Column(Float, nullable=False)
    ram_used = Column(BigInteger, nullable=False)
    ram_total = Column(BigInteger, nullable=False)
