"""Database creation and classification record operations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base, ClassificationRecord, SensorReading
from src.domain import (
    ClassificationOutcome,
    SensorMeasurement,
    StoredClassification,
    StoredSensorReading,
)


class ClassificationRepository:
    def __init__(self, database_path: str | Path) -> None:
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = path
        self.engine: Engine = create_engine(f"sqlite:///{path.as_posix()}")
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        """Create missing tables without deleting existing records."""

        Base.metadata.create_all(self.engine)

    def save_classification(
        self,
        outcome: ClassificationOutcome,
        sensor: SensorMeasurement,
        image_path: str,
        processing_time_ms: float,
        captured_at: datetime,
    ) -> StoredClassification:
        with self._sessions.begin() as session:
            sensor_row = SensorReading(
                temperature_c=sensor.temperature_c,
                humidity_pct=sensor.humidity_pct,
                recorded_at=sensor.recorded_at,
            )
            session.add(sensor_row)
            session.flush()

            record = ClassificationRecord(
                image_path=image_path,
                disease_label=outcome.label,
                confidence=outcome.confidence,
                prediction_status=outcome.status,
                severity=outcome.severity,
                probabilities_json=json.dumps(outcome.probabilities, sort_keys=True),
                model_version=outcome.model_version,
                processing_time_ms=processing_time_ms,
                captured_at=captured_at,
                sensor_reading_id=sensor_row.id,
            )
            session.add(record)
            session.flush()
            return self._to_domain(record, sensor_row)

    def latest(self) -> StoredClassification | None:
        with self._sessions() as session:
            statement = (
                select(ClassificationRecord, SensorReading)
                .join(SensorReading, ClassificationRecord.sensor_reading_id == SensorReading.id)
                .order_by(ClassificationRecord.id.desc())
                .limit(1)
            )
            row = session.execute(statement).first()
            if row is None:
                return None
            return self._to_domain(row[0], row[1])

    def get_by_id(self, record_id: int) -> StoredClassification | None:
        with self._sessions() as session:
            statement = (
                select(ClassificationRecord, SensorReading)
                .join(SensorReading, ClassificationRecord.sensor_reading_id == SensorReading.id)
                .where(ClassificationRecord.id == record_id)
            )
            row = session.execute(statement).first()
            if row is None:
                return None
            return self._to_domain(row[0], row[1])

    def list_recent(self, limit: int = 20) -> list[StoredClassification]:
        records, _ = self.query_classifications(limit=limit)
        return records

    def query_classifications(
        self,
        limit: int = 20,
        offset: int = 0,
        disease: str | None = None,
        status: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> tuple[list[StoredClassification], int]:
        safe_limit = min(max(limit, 1), 100)
        safe_offset = max(offset, 0)
        conditions = self._classification_conditions(disease, status, from_time, to_time)
        with self._sessions() as session:
            statement = (
                select(ClassificationRecord, SensorReading)
                .join(SensorReading, ClassificationRecord.sensor_reading_id == SensorReading.id)
                .where(*conditions)
                .order_by(ClassificationRecord.id.desc())
                .offset(safe_offset)
                .limit(safe_limit)
            )
            records = [
                self._to_domain(record, sensor) for record, sensor in session.execute(statement)
            ]
            total = session.scalar(select(func.count(ClassificationRecord.id)).where(*conditions))
            return records, int(total or 0)

    def all_classifications(
        self,
        disease: str | None = None,
        status: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        maximum_records: int = 10_000,
    ) -> list[StoredClassification]:
        conditions = self._classification_conditions(disease, status, from_time, to_time)
        with self._sessions() as session:
            statement = (
                select(ClassificationRecord, SensorReading)
                .join(SensorReading, ClassificationRecord.sensor_reading_id == SensorReading.id)
                .where(*conditions)
                .order_by(ClassificationRecord.id.asc())
                .limit(maximum_records)
            )
            return [
                self._to_domain(record, sensor) for record, sensor in session.execute(statement)
            ]

    def latest_sensor_reading(self) -> StoredSensorReading | None:
        with self._sessions() as session:
            row = session.scalar(select(SensorReading).order_by(SensorReading.id.desc()).limit(1))
            return self._sensor_to_domain(row) if row is not None else None

    def query_sensor_readings(
        self,
        limit: int = 100,
        offset: int = 0,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> tuple[list[StoredSensorReading], int]:
        safe_limit = min(max(limit, 1), 500)
        safe_offset = max(offset, 0)
        conditions = []
        if from_time is not None:
            conditions.append(SensorReading.recorded_at >= from_time)
        if to_time is not None:
            conditions.append(SensorReading.recorded_at <= to_time)
        with self._sessions() as session:
            statement = (
                select(SensorReading)
                .where(*conditions)
                .order_by(SensorReading.id.desc())
                .offset(safe_offset)
                .limit(safe_limit)
            )
            readings = [self._sensor_to_domain(row) for row in session.scalars(statement)]
            total = session.scalar(select(func.count(SensorReading.id)).where(*conditions))
            return readings, int(total or 0)

    def count(self) -> int:
        with self._sessions() as session:
            return int(session.scalar(select(func.count(ClassificationRecord.id))) or 0)

    def ping(self) -> bool:
        try:
            with self._sessions() as session:
                session.execute(select(1)).scalar_one()
            return True
        except Exception:
            return False

    @staticmethod
    def _classification_conditions(
        disease: str | None,
        status: str | None,
        from_time: datetime | None,
        to_time: datetime | None,
    ) -> list[object]:
        conditions: list[object] = []
        if disease:
            conditions.append(ClassificationRecord.disease_label == disease)
        if status:
            conditions.append(ClassificationRecord.prediction_status == status)
        if from_time is not None:
            conditions.append(ClassificationRecord.captured_at >= from_time)
        if to_time is not None:
            conditions.append(ClassificationRecord.captured_at <= to_time)
        return conditions

    @staticmethod
    def _to_domain(record: ClassificationRecord, sensor: SensorReading) -> StoredClassification:
        return StoredClassification(
            id=record.id,
            image_path=record.image_path,
            disease_label=record.disease_label,
            confidence=record.confidence,
            prediction_status=record.prediction_status,
            severity=record.severity,
            model_version=record.model_version,
            processing_time_ms=record.processing_time_ms,
            captured_at=record.captured_at,
            temperature_c=sensor.temperature_c,
            humidity_pct=sensor.humidity_pct,
            probabilities=json.loads(record.probabilities_json),
        )

    @staticmethod
    def _sensor_to_domain(sensor: SensorReading) -> StoredSensorReading:
        return StoredSensorReading(
            id=sensor.id,
            temperature_c=sensor.temperature_c,
            humidity_pct=sensor.humidity_pct,
            recorded_at=sensor.recorded_at,
        )

    def close(self) -> None:
        self.engine.dispose()


def open_session(repository: ClassificationRepository) -> Session:
    """Return a session for future advanced queries."""

    return Session(repository.engine)
