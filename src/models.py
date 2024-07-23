import datetime
from typing import Optional, Annotated
from sqlalchemy import ForeignKey, Table, Column, Integer, String, MetaData, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, str_200
import enum


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )]


class WorkersOrm(Base):
    __tablename__ = 'Workers'
    id: Mapped[int]
    username: Mapped[str]


class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"


class ResumeOrm(Base):
    __tablename__ = "resumes"

    id: Mapped[int]
    title: Mapped[str_200]
    compensation: Mapped[Optional[int]]
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

# metadata_obj = MetaData()


# workers_table = Table(
#     "workers",
#     metadata_obj,
#     Column("id", Integer, primary_key=True),
#     Column("username", String),
# )
