from datetime import datetime
import inspect


def get_caller_location() -> str:
    caller_frame = inspect.stack()[4]
    return caller_frame.filename.replace("\\", "/")


def get_date_and_time() -> dict:
    date_and_time = {}
    date_and_time["year"] = datetime.now().year
    date_and_time["month"] = datetime.now().month
    date_and_time["day"] = datetime.now().day
    date_and_time["hour"] = datetime.now().hour
    date_and_time["minute"] = datetime.now().minute
    date_and_time["second"] = datetime.now().second
    date_and_time["microsecond"] = datetime.now().microsecond
    return date_and_time
