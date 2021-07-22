from datetime import datetime
from typing import Optional


class TimeFormatter:

    POPULAR_TIME_FORMATS = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    @classmethod
    def getDateTime(cls, time, timeFormats=None) -> Optional[datetime]:
        if time is None:
            return None

        if isinstance(time, datetime):
            return time

        elif isinstance(time, str):
            if time == "today":
                return datetime.today()
            elif time == "now":
                return datetime.now()

            if timeFormats is None:
                timeFormats = cls.POPULAR_TIME_FORMATS
            elif isinstance(timeFormats, str):
                timeFormats = [timeFormats]

            dt = None
            for df in timeFormats:
                try:
                    dt = datetime.strptime(time, df)
                    break
                except ValueError:
                    continue

            return dt

        elif isinstance(time, int) or isinstance(time, float):
            if time > 1000000000000:  # in microseconds
                time /= 1000
            return datetime.fromtimestamp(time)

        else:
            return None

    @classmethod
    def getDate(cls, time, timeFormats=None):
        dt = cls.getDateTime(time, timeFormats)
        return datetime.strftime(dt, "%Y-%m-%d") if dt is not None else None

    @classmethod
    def getTimestamp(cls, time, timeFormats=None):
        dt = cls.getDateTime(time, timeFormats)
        return dt.timestamp() if dt is not None else None
