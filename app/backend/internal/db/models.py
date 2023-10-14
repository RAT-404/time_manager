from sqlalchemy import (
    DateTime, 
    String,
    func,
    ForeignKey
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from datetime import datetime

from database import Base


class Event(Base):
    __tablename__ = 'event'

    event_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    date_start: Mapped['datetime'] = mapped_column(DateTime, index=True, nullable=False, server_default=func.now())
    date_end: Mapped['datetime'] = mapped_column(DateTime, index=True, nullable=True)

    created_at: Mapped['datetime'] = mapped_column(DateTime, index=True, nullable=False, server_default=func.now())
    updated_at: Mapped['datetime'] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), onupdate=datetime.now)

    remainder_times: Mapped['Remainder_time'] = relationship(back_populates='current_event')


class Remainder_time(Base):
    __tablename__ = 'remainder_time'

    time_to_remaind: Mapped['datetime'] = mapped_column(DateTime, index=True, nullable=True)
    event_id: Mapped[int] = ForeignKey('event.id')

    current_event: Mapped['Event'] = relationship(back_populates='remainder_times')


