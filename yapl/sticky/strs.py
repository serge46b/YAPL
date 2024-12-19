from typing import Optional, Literal
import os
import re


def visible_length(s):
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


class WidthNormilizedString:
    __string: str
    __width: int
    __align: Literal["left", "center", "right"]
    __string_shift: int = 0

    __cached_str: Optional[str] = None

    def __init__(
        self,
        string: str,
        width: Optional[int] = None,
        align: Literal["left", "center", "right"] = "left",
    ):
        self.__string = string
        if width is None:
            width = visible_length(self.__string)
        self.__width = width
        self.__align = align

    def update_str(self, string: str, update_width: bool = True):
        self.__cached_str = None
        self.__string = string
        if update_width:
            self.__width = visible_length(self.__string)

    def shift_str(self) -> None:
        self.__cached_str = None
        self.__string_shift += 1
        if self.__string_shift >= self.__width + visible_length(self.__string):
            self.__string_shift = 0

    @property
    def string(self) -> str:
        if self.__cached_str is not None:
            return self.__cached_str
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
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new_width: int) -> None:
        self.__cached_str = None
        self.__width = new_width

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


class StickyString:
    __wn_strs: list[WidthNormilizedString]
    __wn_strs_width: list[float | int | Literal["auto"]]

    # TODO: remake constructor arguments (because separate string list and parameters list is inconvinient.)
    def __init__(self, strs: list[str], params: Optional[list[dict]] = None):
        self.__wn_strs = []
        self.__wn_strs_width = []
        for i, string in enumerate(strs):
            if params is None:
                pr = {}
            else:
                pr = params[i]
            try:
                wd = pr["width"]
                self.__wn_strs_width.append(wd)
                if type(wd) != int:
                    pr.pop("width")
            except KeyError:
                self.__wn_strs_width.append(len(string))
            self.__wn_strs.append(WidthNormilizedString(string, **pr))
        self.__recalculate_widths()

    def __recalculate_widths(self):
        term_width = os.get_terminal_size().columns
        width_left = term_width
        auto_sized_strs = []
        auto_strs_sz = 0
        for i, wn_str in enumerate(self.__wn_strs):
            wd = self.__wn_strs_width[i]
            if type(wd) == int:
                wn_str.__width = wd
                width_left -= wd
                continue
            if type(wd) == float:
                wd = int(wd * term_width)
                wn_str.__width = wd
                width_left -= wd
                continue
            auto_sized_strs.append(wn_str)
            auto_strs_sz += visible_length(wn_str.string)
        # TODO: remake auto size section, so it tries to optimize space by size of the strings
        for as_wn_str in auto_sized_strs:
            as_wn_str.width = width_left // len(auto_sized_strs)

    def update_str(
        self, str_idx: int, new_str: str, params: Optional[dict] = None
    ) -> None:
        if self.__wn_strs[str_idx].raw_str == new_str:
            return
        self.__wn_strs[str_idx].string = new_str
        if params is None:
            return
        for key in params:
            setattr(self.__wn_strs[str_idx], key, params[key])
        self.__recalculate_widths()

    @property
    def summary_string(self) -> str:
        self.__recalculate_widths()
        ret_str = ""
        for wn_str in self.__wn_strs:
            ret_str += wn_str.string
        term_width = os.get_terminal_size().columns
        if visible_length(ret_str) > term_width:
            return ret_str[: term_width - 1]
        return ret_str
