from datetime import datetime

class Event:

    event_code: str
    location: str
    start: datetime
    end: datetime
    title: str

    def __init__(self, event_code: str, location: str, start: datetime, end: datetime, title: str):
        self.event_code = event_code
        self.location = location
        self.start = start
        self.end = end
        self.title = title

    def to_dict(self):

        return {
            "event_code": self.event_code,
            "location": self.location,
            "start": self.start,
            "end": self.end,
            "title": self.title
        }

    @staticmethod
    def from_dict(data):

        return Event(
            event_code=data.get("event_code", ""),
            location=data.get("location", ""),
            start=data.get("start", None),
            end=data.get("end", None),
            title=data.get("title", "")
        )