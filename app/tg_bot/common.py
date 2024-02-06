from pydantic import BaseModel, Field


class EventLabels(BaseModel):
    append_caption: str = Field(default='Append', description='Caption for Append button')
    cancel_caption: str = Field(default='Cancel', description='Caption for Cancel button')



class GenericEvent:
    def __init__(
        self,
        append_btn: str = None,
        cancel_btn: str = None,
        show_alerts: bool = False
    ) -> None:
        
        self._labels = EventLabels()
        
        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if append_btn:
            self._labels.append_caption = append_btn

        self.show_alerts = show_alerts

    # async def check_event_select(self, data, query):
    #     """Checks selected date is in allowed range of dates"""
    #     date = datetime(int(data.year), int(data.month), int(data.day))
    #     if self.min_date and self.min_date > date:
    #         await query.answer(
    #             f'The date have to be later {self.min_date.strftime("%d/%m/%Y")}',
    #             show_alert=self.show_alerts
    #         )
    #         return False, None
    #     elif self.max_date and self.max_date < date:
    #         await query.answer(
    #             f'The date have to be before {self.max_date.strftime("%d/%m/%Y")}',
    #             show_alert=self.show_alerts
    #         )
    #         return False, None
    #     await query.message.delete_reply_markup()  # removing inline keyboard
    #     return True, date