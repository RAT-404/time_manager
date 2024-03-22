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
