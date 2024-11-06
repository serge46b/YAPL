from yapl.errors import LinkToSameDestinationError
from yapl.styling.stylingABC import LogStyle
from yapl.styling import standart_styles
from yapl.datagens import get_caller_location, get_date_and_time
from typing import Callable, Literal, Any


class BaseLogger:
    __lgr_dst: Literal["stdout"] | str | None
    __logging_callback: Callable[[dict], None]
    __optional_data_gens: dict[str, Callable[[], Any]]
    style: LogStyle

    def __init__(
        self,
        logging_callback: Callable[[dict], None],
        log_destination: Literal["stdout"] | str | None = None,
        style: LogStyle = standart_styles.stdout,
    ):
        self.__lgr_dst = log_destination
        self.__logging_callback = logging_callback
        self.style = style
        self.__optional_data_gens = {}
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

    @property
    def optional_datagens(self) -> dict[str, Callable[[], Any]]:
        return self.__optional_data_gens

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
        for key in self.__optional_data_gens:
            val = self.__optional_data_gens[key]()
            if type(val) == dict:
                log_obj.update(val)
                continue
            log_obj[key] = val
        # log_obj["location"] = self.__get_caller_location()
        # log_obj.update(date_and_time)
        self.__logging_callback(log_obj)
        self.log_json(log_obj)

    @property
    def destination(self):
        return self.__lgr_dst


class LoggerContainer:
    __passive_loggers: list[BaseLogger]
    __active_loggers: list[BaseLogger]
    __optional_data_gens: dict[str, Callable[[], Any]]

    def __init__(self):
        self.__passive_loggers = []
        self.__active_loggers = []
        self.__optional_data_gens = {}

    def __call__(self):
        self.__passive_loggers.append(BaseLogger(self.__gen_logger_callback()))
        self.__passive_loggers[-1].optional_datagens.update(self.__optional_data_gens)
        return self.__passive_loggers[-1]

    def __gen_logger_callback(self):
        def lgr_cb(json: dict) -> None:
            for lgr in self.__active_loggers:
                lgr.log_json(json)

        return lgr_cb

    def add_log_destination(
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

    def update_optional_datagens(self, key: str, datagen: Callable[[], Any]) -> None:
        self.__optional_data_gens[key] = datagen
        for lgr in self.__passive_loggers:
            lgr.optional_datagens[key] = datagen


Logger = LoggerContainer()
Logger.add_log_destination("stdout", standart_styles.stdout)
Logger.update_optional_datagens("location", get_caller_location)
Logger.update_optional_datagens("date and time", get_date_and_time)
