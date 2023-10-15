from sqlalchemy import (
    String,
    func,
    ForeignKey,
    Date,
    Time,
    DateTime
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from datetime import datetime, date, time
import pytz

from .database import Base


class Event(Base):
    __tablename__ = 'event'

    event_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    date_start: Mapped['date'] = mapped_column(Date, index=True, nullable=False, server_default=func.now())
    time_start: Mapped['time'] = mapped_column(Time(timezone=True), index=True, nullable=False, server_default=func.now())

    date_end: Mapped['date'] = mapped_column(Date, index=True, nullable=True)
    time_end: Mapped['time'] = mapped_column(Time(timezone=True), index=True, nullable=True)

    created_at: Mapped['datetime'] = mapped_column(DateTime(timezone=True), index=True, nullable=False, server_default=func.now())
    updated_at: Mapped['datetime'] = mapped_column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), onupdate=datetime.now(tz=pytz.timezone('Europe/Moscow')))

    remainder_times: Mapped['RemainderTime'] = relationship(back_populates='current_event')


class RemainderTime(Base):
    __tablename__ = 'remainder_time'

    time_to_remaind: Mapped['datetime'] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('event.id'))

    current_event: Mapped['Event'] = relationship(back_populates='remainder_times')


