from sqlalchemy import update, delete, select, insert

from ..db import models, database as db
from ..db.schemas.EventSchema import EventCreate, RemainderTimeCreate


class DBRecord:
    def __init__(self, session: db.AsyncSession, model: models.Event | models.RemainderTime, new_record_params: EventCreate | RemainderTimeCreate | None = None):
        self.model = model
        self.new_record_params = new_record_params
        self.session = session
        
    async def create_record(self, remainder_time_list: list[RemainderTimeCreate] | None = None) -> int | None:
        if self.model is models.Event:
            record_exists = await self.__get_exists_event_id()
            if record_exists is None:
                await self.session.execute(insert(self.model).values(**self.new_record_params.model_dump()))
        
        elif self.model is models.RemainderTime and remainder_time_list:
            json_remainder_time_list = [remaind_time.model_dump() for remaind_time in remainder_time_list]
            await self.session.execute(insert(self.model).values(json_remainder_time_list))

    async def patch_record(self, record_id: int):
        await self.session.execute(update(self.model).where(self.model.id == record_id).values(**self.new_record_params.model_dump()))

    async def delete_record(self, record_id: int):
        await self.session.execute(delete(self.model).where(self.model.id == record_id))

    async def __get_exists_event_id(self) -> int | None:
        db_response = await self.session.execute(select(self.model.id, self.model.chat_id
                                                    ).where(self.model.chat_id == self.new_record_params.chat_id
                                                            ).where(self.model.event_name == self.new_record_params.event_name))
        list_with_id = [row[0] for row in db_response]

        if list_with_id != []:
            id_ = list_with_id[0]
            return id_ 
        return None