from datetime import datetime


def date(tag: str):
    return datetime.strptime(tag, "%Y.%m.%d")


def date_fmt(dt: datetime):
    return f"{dt.year:04}.{dt.month:02}.{dt.day:02}"


def date_tag(tag: str):
    return date_fmt(date(tag))
