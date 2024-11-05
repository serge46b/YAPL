from yapl.errors import LinkToSameDestinationError
from yapl.styling.StylingABC import LogStyle
from yapl.styling import StdStyling
from typing import Callable, Literal, Any
from datetime import datetime
import inspect


class BaseLogger:
    __lgr_dst: Literal["stdout"] | str | None
    __logging_callback: Callable[[dict], None]
    style: LogStyle

    def __init__(
        self,
        logging_callback: Callable[[dict], None],
        log_destination: Literal["stdout"] | str | None = None,
        style: LogStyle = StdStyling.stdout,
    ):
        self.__lgr_dst = log_destination
        self.__logging_callback = logging_callback
        self.style = style
        if log_destination is not None and log_destination != "stdout":
            f = open(log_destination, "w")
            f.close()

    def __getattr__(self, name: str) -> Any:
        norm_name = name.upper()
        if not self.style.is_event(norm_name):
            raise AttributeError(
                f"'{BaseLogger.__name__}' object has no attribute '{name}'"
            )

        def lg(msg: str):
            self.log(norm_name, msg)

        return lg

    def __get_caller_location(self) -> str:
        caller_frame = inspect.stack()[3]
        return caller_frame.filename

    def __log_stdout(self, string: str) -> None:
        print(string)

    def log_json(self, json: dict) -> None:
        if self.__lgr_dst is None:
            return
        if self.__lgr_dst == "stdout":
            self.__log_stdout(self.style.to_format_string(json))
            return
        f = open(self.__lgr_dst, "a")
        f.write(self.style.to_format_string(json))
        f.write("\n")

    def log(self, evt_type: str, msg: str) -> None:
        log_obj = {"event_type": evt_type, "message": msg}
        log_obj["location"] = self.__get_caller_location()
        date_and_time = {}
        date_and_time["year"] = datetime.now().year
        date_and_time["month"] = datetime.now().month
        date_and_time["day"] = datetime.now().day
        date_and_time["hour"] = datetime.now().hour
        date_and_time["minute"] = datetime.now().minute
        date_and_time["second"] = datetime.now().second
        date_and_time["microsecond"] = datetime.now().microsecond
        log_obj.update(date_and_time)
        self.__logging_callback(log_obj)
        self.log_json(log_obj)

    @property
    def destination(self):
        return self.__lgr_dst


class LoggerContainer:
    __passive_loggers: list[BaseLogger]
    __active_loggers: list[BaseLogger]

    def __init__(self):
        self.__passive_loggers = []
        self.__active_loggers = []

    def __call__(self):
        self.__passive_loggers.append(BaseLogger(self.__gen_logger_callback()))
        return self.__passive_loggers[-1]

    def __gen_logger_callback(self):
        def lgr_cb(json: dict) -> None:
            for lgr in self.__active_loggers:
                lgr.log_json(json)

        return lgr_cb

    def add_logger(
        self,
        destination: Literal["stdout"] | str | Callable[[dict], None],
        style: LogStyle,
    ):
        for logger in self.__active_loggers:
            if logger.destination == destination:
                raise LinkToSameDestinationError(
                    f"Logger, that linked to destination: '{destination}' already exists"
                )
        cb = lambda x: None
        dst = destination
        if isinstance(dst, Callable):
            cb = dst  # type: Callable[[dict], None]
            dst = None
        self.__active_loggers.append(BaseLogger(cb, dst, style))

    def update_style(
        self, dst: Literal["stdout"] | str | Callable[[dict], None], new_style: LogStyle
    ):
        for lgr in self.__active_loggers:
            if lgr.destination == dst:
                lgr.style = new_style


Logger = LoggerContainer()
Logger.add_logger("stdout", StdStyling.stdout)
