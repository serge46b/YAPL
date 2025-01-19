from typing import Optional, Literal, Any
from string import Formatter
import os
import re


def visible_length(s):
    # WARNING: Sketchy untested regex. Just copied it from internet.
    cleaned_string = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", s)
    return len(cleaned_string)


def visible_cut_from_to(s: str, st_idx: int = 0, end_idx: Optional[int] = None):
    if end_idx is None:
        end_idx = len(s)
    escape_patterns = re.findall(r"\x1B\[[0-?]*[ -/]*[@-~]", s)
    if len(escape_patterns) == 0:
        return s[st_idx:end_idx]
    splitted_str = re.split(r"\x1B\[[0-?]*[ -/]*[@-~]", s)
    is_pattern_first = s.find(escape_patterns[0]) == 0
    ret_str = ""
    i = 0
    for str_i, string in enumerate(splitted_str):
        if i + len(string) < st_idx:
            i += len(string)
            continue
        pat = escape_patterns[str_i - (not is_pattern_first)]
        new_end = end_idx - i
        new_st = st_idx - i
        if new_st < 0:
            new_st = 0
        if new_end < len(string):
            ret_str += pat + string[new_st:new_end]
            break
        ret_str += pat + string[new_st:]
        i += len(string)
    ret_str += escape_patterns[-1]
    return ret_str


class NoParameterError(Exception):
    """Raises whenever string has more parameters than user provided"""


class WidthNormilizedString:
    __string: str
    __width: int
    __align: Literal["left", "center", "right"]
    __string_shift: int = 0
    __str_variables: dict
    __unformatted_str: str

    __cached_str: Optional[str] = None

    def __init__(
        self,
        string: str,
        width: Optional[int] = None,
        align: Literal["left", "center", "right"] = "left",
        str_params={},
    ):
        if width is None:
            width = visible_length(string)
        self.__width = width
        self.__align = align
        self.__str_variables = {}
        self.update_str(string, update_width=False, param_update=str_params)

    def update_str(
        self, string: str, update_width: bool = True, param_update: dict = {}
    ):
        self.__unformatted_str = string
        self.update_variables(param_update)
        self.__string = self.__unformatted_str.format(**self.__str_variables)
        if update_width:
            self.__width = visible_length(self.__string)

    def update_variables(self, update_var_dct: dict):
        self.__cached_str = None
        self.__str_variables.update(update_var_dct)
        args = [
            i[1] for i in Formatter().parse(self.__unformatted_str) if i[1] is not None
        ]
        for arg in args:
            if arg not in self.__str_variables.keys():
                raise NoParameterError(
                    f"variable '{arg}' found in user string ({self.__unformatted_str}), but not found in string parameters."
                )

    def shift_str(self) -> None:
        self.__cached_str = None
        self.__string_shift += 1
        if self.__string_shift >= self.__width + visible_length(self.__string):
            self.__string_shift = 0

    @property
    def string(self) -> str:
        if self.__cached_str is not None:
            return self.__cached_str
        self.__string = self.__string.format(**self.__str_variables)
        str_len = visible_length(self.__string)
        if str_len > self.__width:
            end_idx = self.__string_shift + self.__width
            if end_idx > str_len + self.__width:
                padding = " " * (str_len + self.__width * 2 - end_idx)
                ret_str = padding + visible_cut_from_to(
                    self.__string, 0, end_idx - str_len - self.__width
                )
                self.__cached_str = ret_str
                return ret_str
            if end_idx > str_len:
                padding = " " * (end_idx - str_len)
                ret_str = (
                    visible_cut_from_to(self.__string, self.__string_shift) + padding
                )
                self.__cached_str = ret_str
                return ret_str
            ret_str = visible_cut_from_to(self.__string, self.__string_shift, end_idx)
            self.__cached_str = ret_str
            return ret_str

        if self.__align == "center":
            padding = " " * ((self.__width - str_len) // 2)
            ret_str = padding + self.__string + padding
            self.__cached_str = ret_str
            return ret_str
        padding = " " * (self.__width - str_len)
        if self.__align == "left":
            ret_str = self.__string + padding
            self.__cached_str = ret_str
            return ret_str
        ret_str = padding + self.__string
        self.__cached_str = ret_str
        return ret_str

    @string.setter
    def string(self, new_str: str) -> None:
        self.__cached_str = None
        self.__string = new_str
        self.__string_shift = 0

    @property
    def raw_str(self) -> str:
        return self.__string

    @property
    def unformatted_str(self) -> str:
        return self.__unformatted_str

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new_width: int) -> None:
        self.__cached_str = None
        self.__width = new_width

    @property
    def is_cut(self) -> bool:
        if self.__cached_str is not None:
            return visible_length(self.__cached_str) > self.__width
        self.__string = self.__unformatted_str.format(**self.__str_variables)
        return visible_length(self.__string) > self.__width

    @property
    def align(self) -> Literal["left", "center", "right"]:
        return self.__align

    @align.setter
    def align(self, new_align: Literal["left", "center", "right"]) -> None:
        self.__cached_str = None
        self.__align = new_align

    @property
    def string_shift(self) -> int:
        return self.__string_shift

    @string_shift.setter
    def string_shift(self, new_string_shift: int) -> None:
        self.__cached_str = None
        self.__string_shift = new_string_shift
        max_shift = self.__width + visible_length(self.__string)
        if self.__string_shift >= max_shift:
            self.__string_shift -= max_shift

    @property
    def str_variables(self) -> dict:
        return self.__str_variables.copy()

    @str_variables.setter
    def str_variables(self, new_dct: dict) -> None:
        self.__str_variables = new_dct.copy()
        self.update_variables({})


class StickyString:
    __wn_strs: dict[str, WidthNormilizedString]
    __wn_strs_width: dict[str, float | int | Literal["auto"]]

    def __init__(self, strs_and_params: dict[str, dict[str, Any]]):
        self.__wn_strs = {}
        self.__wn_strs_width = {}
        for str_name in strs_and_params:
            params = strs_and_params[str_name]
            string = params.pop("s", "")
            try:
                wd = params["width"]
                self.__wn_strs_width[str_name] = wd
                if type(wd) != int:
                    params.pop("width")
            except KeyError:
                self.__wn_strs_width[str_name] = len(string)
            self.__wn_strs[str_name] = WidthNormilizedString(string, **params)

    def __recalculate_widths(self):
        term_width = os.get_terminal_size().columns
        width_left = term_width
        auto_sized_strs = []
        auto_strs_sz = 0
        for str_name in self.__wn_strs:
            wd = self.__wn_strs_width[str_name]
            wn_str = self.__wn_strs[str_name]
            if type(wd) == int:
                wn_str.width = wd
                width_left -= wd
                continue
            if type(wd) == float:
                wd = int(wd * term_width)
                wn_str.width = wd
                width_left -= wd
                continue
            auto_sized_strs.append(wn_str)
            auto_strs_sz += visible_length(wn_str.string)
        # TODO: remake auto size section, so it tries to optimize space by size of the strings
        for as_wn_str in auto_sized_strs:
            as_wn_str.width = width_left // len(auto_sized_strs)

    def update_str(
        self, str_idx: str, new_str: str, params: Optional[dict] = None
    ) -> None:
        if self.__wn_strs[str_idx].raw_str == new_str:
            return
        self.__wn_strs[str_idx].string = new_str
        if params is None:
            return
        self.update_params(str_idx, params)

    def update_params(self, str_idx: str, params: dict):
        for key in params:
            setattr(self.__wn_strs[str_idx], key, params[key])
        self.__recalculate_widths()

    def update_variables(self, str_idx: str, variables_dct: dict):
        self.__wn_strs[str_idx].str_variables = variables_dct

    def shift_stsr(self, cut_only: bool = True):
        for str_name in self.__wn_strs:
            wns = self.__wn_strs[str_name]
            if cut_only and not wns.is_cut:
                continue
            wns.shift_str()

    @property
    def summary_string(self) -> str:
        self.__recalculate_widths()
        ret_str = ""
        for str_name in self.__wn_strs:
            ret_str += self.__wn_strs[str_name].string
        term_width = os.get_terminal_size().columns
        if visible_length(ret_str) > term_width:
            return visible_cut_from_to(ret_str, end_idx=term_width - 1)
        return ret_str
