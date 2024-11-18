from datetime import datetime
import inspect


class GetCallerLocationClass:
    folder_depth: int = 0

    def __call__(self) -> str:
        caller_frame = inspect.stack()[4]
        f_name = caller_frame.filename.replace("\\", "/")
        f_name_parts = f_name.split("/")
        if self.folder_depth > len(f_name_parts):
            return f_name
        return " ".join(f_name_parts[self.folder_depth :])


get_caller_location = GetCallerLocationClass()


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
