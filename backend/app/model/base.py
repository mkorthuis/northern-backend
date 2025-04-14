from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class BaseMixin(SQLModel):
    id: int = Field(default=None, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    date_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate":datetime.utcnow})


class UUIDBaseMixin(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    date_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})

