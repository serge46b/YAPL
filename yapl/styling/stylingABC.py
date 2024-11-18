from ..errors import StyleDictParseError
from abc import ABC, abstractmethod
from string import Formatter


class LogStyleABC(ABC):
    @abstractmethod
    def __init__(
        self,
        log_str: str,
        log_str_parts: dict[str, str],
        modifiers: dict,
        initial_str: str = "",
        final_str: str = "",
    ): ...
    @abstractmethod
    def to_format_string(self, json_log: dict) -> str: ...


class LogStyle(LogStyleABC):
    __log_str: str
    __log_str_parts: dict[str, str]
    __modifiers: dict[str, dict[str, str]]
    __template_keys: dict[str, list[str | tuple[str, str]]]
    skip_modifiers: bool = True
    initial_string: str
    final_string: str

    def __init__(
        self,
        log_str: str,
        log_str_parts: dict[str, str],
        modifiers: dict,
        initial_str: str = "",
        final_str: str = "",
    ) -> None:
        self.__log_str = log_str
        self.__log_str_parts = log_str_parts
        self.__template_keys = {}
        self.__modifiers = {}
        self.initial_string = initial_str
        self.final_string = final_str
        for lsp_key in self.__log_str_parts:
            self.__template_keys[lsp_key] = [
                i[1]
                for i in Formatter().parse(self.__log_str_parts[lsp_key])
                if i[1] is not None
            ]
            self.__modifiers[lsp_key] = {}
            for key_i, key in enumerate(self.__template_keys[lsp_key]):
                if type(key) != str:
                    continue
                if key[0].islower():
                    continue
                modifier_key = ""
                modifier_dependency = ""
                non_alpha_buf = ""
                for s in key:
                    if not s.isalpha():
                        non_alpha_buf += s
                        continue
                    if s.islower() or len(modifier_dependency) > 0:
                        if len(modifier_dependency) == 0:
                            non_alpha_buf = ""
                        modifier_dependency += non_alpha_buf + s
                        non_alpha_buf = ""
                        continue
                    modifier_key += non_alpha_buf + s
                    non_alpha_buf = ""
                try:
                    self.__modifiers[lsp_key][key] = modifiers[
                        f"{modifier_key}_modifiers"
                    ][modifier_dependency].copy()
                except KeyError:
                    try:
                        _ = modifiers[f"{modifier_key}_modifiers"]
                    except KeyError:
                        raise StyleDictParseError(
                            f"style dictionary missing property '{modifier_key}_modifiers'. If property '{key}' is not dependent property, do not use capital letters at the beginning of the property"
                        )
                    raise StyleDictParseError(
                        f"style dictionary modifier set '{modifier_key}_modifiers' missing modifiers for '{modifier_dependency}' ('{key}' in log_str)"
                    )
                except AttributeError:
                    raise StyleDictParseError(
                        f"dictionary was expected in '{modifier_key}_modifiers'->'{modifier_dependency}'. got '{type(modifiers[f"{modifier_key}_modifiers"][
                        modifier_dependency
                    ]).__name__}' instead"
                    )
                self.__template_keys[lsp_key][key_i] = (
                    key,
                    modifier_key.lower(),
                )

    def to_format_string(self, json_log: dict) -> str:
        out_dct = {}
        for i, mandatory_key in enumerate(self.__template_keys):
            key_list = self.__template_keys[mandatory_key]
            out_dct[mandatory_key] = ""
            ins_dct = {}
            for template_key in key_list:
                if type(template_key) == str:
                    try:
                        ins_dct[template_key] = json_log[template_key]
                        continue
                    except KeyError:
                        break
                key_name, dep_name = template_key
                mod = self.__modifiers[mandatory_key][key_name]
                try:
                    ins_dct[key_name] = mod[json_log[dep_name]]
                except KeyError:
                    if not self.skip_modifiers:
                        break
                    ins_dct[key_name] = ""
            else:
                out_dct[mandatory_key] = self.__log_str_parts[mandatory_key].format(
                    **ins_dct
                ) + ("" if i == len(self.__template_keys) - 1 else " ")
        return self.__log_str.format(**out_dct)
