from yapl.errors import LinkToSameDestinationError
from yapl.styling.stylingABC import LogStyle
from yapl.styling import basic_styles
from yapl.basic_datagens import get_caller_location, get_date_and_time
from typing import Callable, Literal, Any, Optional
from abc import ABC, abstractmethod
from io import TextIOWrapper


class BaseLogger(ABC):
    __log_destination: Literal["stdout"] | str | None
    __optional_data_gens: dict[str, Callable[[], Any]]
    event_types: list[str] | Literal["any"]
    logging_callback: Optional[Callable[..., Any]]
    style: LogStyle
    initial_callback: Optional[Callable[..., Any]]
    destruction_callback: Optional[Callable[..., Any]]

    def __init__(
        self,
        log_destination: Literal["stdout"] | str | None,
        style: LogStyle,
        event_list: list[str] | Literal["any"],
        logging_callback: Optional[Callable[..., Any]] = None,
        ininial_callback: Optional[Callable[..., Any]] = None,
        destruction_callback: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.__log_destination = log_destination
        self.__optional_data_gens = {}
        self.event_types = event_list
        self.style = style
        self.logging_callback = logging_callback
        self.initial_callback = ininial_callback
        self.destruction_callback = destruction_callback
        if self.style.initial_string:
            self.log_raw(self.style.initial_string)
        if self.initial_callback:
            self.initial_callback(self)

    def __del__(self):
        if self.style.final_string:
            self.log_raw(self.style.final_string)
        if self.destruction_callback:
            self.destruction_callback()

    def __getattr__(self, name: str) -> Any:
        norm_name = name.upper()
        if self.event_types != "any" and norm_name not in self.event_types:
            raise AttributeError(
                f"'{BaseLogger.__name__}' object has no attribute '{name}'"
            )

        def lg(msg: str):
            self.log_message(norm_name, msg)

        return lg

    @property
    def optional_datagens(self) -> dict[str, Callable[[], Any]]:
        return self.__optional_data_gens

    @property
    def log_destination(self) -> str | None:
        return self.__log_destination

    def log_json(self, json: dict) -> None:
        self.log_raw(self.style.to_format_string(json))
        if self.logging_callback:
            self.logging_callback(json)

    def log_message(self, evt_type: str, msg: str) -> None:
        log_obj = {"event_type": evt_type, "message": msg}
        for key in self.__optional_data_gens:
            val = self.__optional_data_gens[key]()
            if type(val) == dict:
                log_obj.update(val)
                continue
            log_obj[key] = val
        self.log_json(log_obj)

    @abstractmethod
    def log_raw(self, raw_msg: str) -> None: ...


class ConsoleLogger(BaseLogger):
    __log_destination: Literal["stdout"]

    def __init__(
        self,
        style: LogStyle,
        event_list: list[str] | Literal["any"],
        logging_callback: Optional[Callable[..., Any]] = None,
        ininial_callback: Callable[..., Any] | None = None,
        destruction_callback: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(
            "stdout",
            style,
            event_list,
            logging_callback,
            ininial_callback,
            destruction_callback,
        )

    def log_raw(self, raw_msg):
        print(raw_msg)


class FileLogger(BaseLogger):
    __log_destination: str
    __file: TextIOWrapper

    def __init__(
        self,
        log_destination: str,
        style: LogStyle,
        event_list: list[str] | Literal["any"],
        logging_callback: Callable[..., Any] | None = None,
        ininial_callback: Callable[..., Any] | None = None,
        destruction_callback: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(
            log_destination,
            style,
            event_list,
            logging_callback,
            ininial_callback,
            destruction_callback,
        )
        self.__file = open(log_destination, "w")

    def __del__(self):
        self.__file.close()
        return super().__del__()

    def log_raw(self, raw_msg: str) -> None:
        self.__file.write(raw_msg + "\n")


class FunctionLogger(BaseLogger):
    __log_destination: Optional[Callable[[str], None]] = None

    def __init__(
        self,
        event_list: list[str] | Literal["any"],
        style: Optional[LogStyle] = basic_styles.none_style,
        logging_callback: Callable[..., Any] | None = None,
        ininial_callback: Callable[..., Any] | None = None,
        destruction_callback: Callable[..., Any] | None = None,
    ) -> None:
        if style is None:
            style = basic_styles.none_style
        if style is basic_styles.none_style:
            super().__init__(
                None,
                style,
                event_list,
                logging_callback,
                ininial_callback,
                destruction_callback,
            )
            return
        self.__log_destination = logging_callback
        super().__init__(
            None,
            style,
            event_list,
            ininial_callback=ininial_callback,
            destruction_callback=destruction_callback,
        )

    def log_raw(self, raw_msg: str) -> None:
        if self.__log_destination is None:
            return
        self.__log_destination(raw_msg)


# class BaseLogger:
#     __lgr_dst: Literal["stdout"] | str | None
#     __logging_callback: Callable[[dict], None]
#     __optional_data_gens: dict[str, Callable[[], Any]]
#     style: LogStyle
#     init_callback: Optional[Callable]
#     del_callback: Optional[Callable]

#     def __init__(
#         self,
#         logging_callback: Callable[[dict], None],
#         log_destination: Literal["stdout"] | str | None = None,
#         style: LogStyle = basic_styles.stdout,
#         init_callback: Optional[Callable] = None,
#         finish_callback: Optional[Callable] = None,
#     ):
#         self.__lgr_dst = log_destination
#         self.__logging_callback = logging_callback
#         self.style = style
#         self.__optional_data_gens = {}
#         if log_destination is not None and log_destination != "stdout":
#             self.__f = open(log_destination, "w")
#         self.init_callback = init_callback
#         self.finish_callback = finish_callback
#         if init_callback is not None:
#             init_callback(self)

#     def __del__(self):
#         if self.finish_callback is not None:
#             self.finish_callback(self)
#         if self.__lgr_dst is not None and self.__lgr_dst != "stdout":
#             self.__f.close()

#     def __getattr__(self, name: str) -> Any:
#         norm_name = name.upper()
#         if not self.style.is_event(norm_name):
#             raise AttributeError(
#                 f"'{BaseLogger.__name__}' object has no attribute '{name}'"
#             )

#         def lg(msg: str):
#             self.log(norm_name, msg)

#         return lg

#     def __log_stdout(self, string: str) -> None:
#         print(string)

#     def log_file(self, string: str) -> None:
#         self.__f.write(string)

#     @property
#     def optional_datagens(self) -> dict[str, Callable[[], Any]]:
#         return self.__optional_data_gens

#     @property
#     def destination(self):
#         return self.__lgr_dst

#     def log_json(self, json: dict) -> None:
#         if self.__lgr_dst is None:
#             self.__logging_callback(json)
#             return
#         if self.__lgr_dst == "stdout":
#             self.__log_stdout(self.style.to_format_string(json))
#             return
#         self.__f.write(self.style.to_format_string(json))
#         self.__f.write("\n")

#     def log(self, evt_type: str, msg: str) -> None:
#         log_obj = {"event_type": evt_type, "message": msg}
#         for key in self.__optional_data_gens:
#             val = self.__optional_data_gens[key]()
#             if type(val) == dict:
#                 log_obj.update(val)
#                 continue
#             log_obj[key] = val
#         # log_obj["location"] = self.__get_caller_location()
#         # log_obj.update(date_and_time)
#         self.__logging_callback(log_obj)
#         if self.__lgr_dst is None:
#             return
#         self.log_json(log_obj)


class LoggerContainer:
    __passive_loggers: list[BaseLogger]
    __active_loggers: dict[str | Callable, BaseLogger]
    __optional_data_gens: dict[str, Callable[[], Any]]
    __event_types_list: list[str] | Literal["any"]

    def __init__(self):
        self.__passive_loggers = []
        self.__active_loggers = {}
        self.__optional_data_gens = {}
        self.__event_types_list = basic_styles.STANDART_EVENT_TYPES

    def __call__(self, **kwargs):
        std_cb = self.__gen_logger_callback()
        if "logging_callback" in kwargs:
            old_cb = kwargs["logging_callback"]

            def new_cb(json):
                std_cb(json)
                old_cb(json)

            kwargs["logging_callback"] = new_cb
        else:
            kwargs["logging_callback"] = std_cb
        kwargs.pop("style", None)
        self.__passive_loggers.append(FunctionLogger(self.__event_types_list, **kwargs))
        self.__passive_loggers[-1].optional_datagens.update(self.__optional_data_gens)
        return self.__passive_loggers[-1]

    def __gen_logger_callback(self):
        def lgr_cb(json: dict) -> None:
            for lgr in self.__active_loggers:
                self.__active_loggers[lgr].log_json(json)

        return lgr_cb

    def add_log_destination(
        self,
        log_destination: Literal["stdout"] | str | Callable[..., None],
        style: Optional[LogStyle] = None,
        **kwargs,
    ):
        if log_destination in self.__active_loggers:
            raise LinkToSameDestinationError(
                f"Logger, that linked to destination: '{log_destination}' already exists"
            )
        if log_destination == "stdout":
            if style is None:
                raise ValueError(
                    f"For destination '{log_destination}' style argument must be provided (None were given)"
                )
            self.__active_loggers[log_destination] = ConsoleLogger(
                style, self.__event_types_list, **kwargs
            )
            return
        if isinstance(log_destination, str):
            if style is None:
                raise ValueError(
                    f"For destination '{log_destination}' style argument must be provided (None were given)"
                )
            self.__active_loggers[log_destination] = FileLogger(
                log_destination, style, self.__event_types_list, **kwargs
            )
            return
        self.__active_loggers[log_destination] = FunctionLogger(
            self.__event_types_list, style, log_destination, **kwargs
        )

    def update_style(
        self, dst: Literal["stdout"] | str | Callable[..., None], new_style: LogStyle
    ):
        self.__active_loggers[dst].style = new_style

    def update_event_list(self, new_evt_list: list[str] | Literal["any"]) -> None:
        self.__event_types_list = new_evt_list
        for lgr in self.__passive_loggers:
            lgr.event_types = self.__event_types_list
        for lgr in self.__active_loggers.values():
            lgr.event_types = self.__event_types_list

    def update_optional_datagens(self, key: str, datagen: Callable[[], Any]) -> None:
        self.__optional_data_gens[key] = datagen
        for lgr in self.__passive_loggers:
            lgr.optional_datagens[key] = datagen


Logger = LoggerContainer()
Logger.add_log_destination("stdout", basic_styles.stdout)
Logger.update_optional_datagens("location", get_caller_location)
Logger.update_optional_datagens("date and time", get_date_and_time)
