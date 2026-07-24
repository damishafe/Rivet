from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


class ProjectRow(SQLModel, table=True):
    __tablename__ = "projects"

    id: str = Field(primary_key=True)
    name: str
    status: str
    campaign_seed: int
    created_at: datetime
    updated_at: datetime
    active_version: int
    brand_dna: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    shots: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))


class AssetRow(SQLModel, table=True):
    __tablename__ = "assets"

    id: str = Field(primary_key=True)
    project_id: str = Field(index=True)
    payload: dict[str, Any] = Field(sa_column=Column(JSON))


class EventRow(SQLModel, table=True):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("job_id", "seq"),)

    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    seq: int
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
