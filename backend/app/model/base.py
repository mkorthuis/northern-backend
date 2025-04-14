from datetime import datetime
from sqlmodel import Field, SQLModel


class BaseMixin(SQLModel):
    id: int = Field(default=None, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    date_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate":datetime.utcnow})

