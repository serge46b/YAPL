from typing import Optional, Literal
import os


class WidthNormilizedString:
    __string: str
    width: int
    align: Literal["left", "center", "right"]
    string_shift: int = 0

    def __init__(
        self,
        string: str,
        width: Optional[int] = None,
        align: Literal["left", "center", "right"] = "left",
    ):
        self.__string = string
        if width is None:
            width = len(self.__string)
        self.width = width
        self.align = align

    def update_str(self, string: str, update_width: bool = True):
        self.__string = string
        if update_width:
            self.width = len(self.__string)

    def shift_str(self) -> None:
        self.string_shift += 1
        if self.string_shift >= self.width + len(self.__string):
            self.string_shift = 0

    @property
    def string(self) -> str:
        if len(self.__string) > self.width:
            end_idx = self.string_shift + self.width
            if end_idx > len(self.__string) + self.width:
                padding = " " * (len(self.__string) + self.width * 2 - end_idx)
                return (
                    padding
                    + self.__string[: (end_idx - len(self.__string) - self.width)]
                )
            if end_idx > len(self.__string):
                padding = " " * (end_idx - len(self.__string))
                return self.__string[self.string_shift :] + padding
            return self.__string[self.string_shift : end_idx]

        if self.align == "center":
            padding = " " * ((len(self.__string) - self.width) // 2)
            return padding + self.__string + padding
        padding = " " * (len(self.__string) - self.width)
        if self.align == "left":
            return self.__string + padding
        return padding + self.__string

    @string.setter
    def string(self, new_str: str) -> None:
        self.__string = new_str
        self.string_shift = 0


class StickyString:
    __wn_strs: list[WidthNormilizedString]
    __wn_strs_width: list[float | int | Literal["auto"]]

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
                wn_str.width = wd
                width_left -= wd
                continue
            if type(wd) == float:
                wd = int(wd * term_width)
                wn_str.width = wd
                width_left -= wd
                continue
            auto_sized_strs.append(wn_str)
            auto_strs_sz += len(wn_str.string)
        # TODO: remake auto size section, so it tries to optimize space by size of the strings
        for as_wn_str in auto_sized_strs:
            as_wn_str.width = width_left // 3

    @property
    def summary_string(self) -> str:
        ret_str = ""
        for wn_str in self.__wn_strs:
            ret_str += wn_str.string
        term_width = os.get_terminal_size().columns
        if len(ret_str) > term_width:
            return ret_str[: term_width - 1]
        ret_str += " " * (term_width - len(ret_str))
        return ret_str
