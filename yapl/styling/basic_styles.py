from .stylingABC import LogStyle

STANDART_EVENT_TYPES = ["DEBUG", "WARNING", "ERROR", "INFO", "CRITICAL"]

STDOUT_STANDART_MODIFIERS = {
    "EVENT_TYPE_modifiers": {
        "style_modifier": {
            "INFO": "",
            "DEBUG": "\x1b[38;5;2m",
            "WARNING": "\x1b[38;5;3m",
            "ERROR": "\x1b[38;5;1m",
            "CRITICAL": "\x1b[38;5;15m\x1b[48;5;1m",
        },
        "msg_style_modifier": {
            "INFO": "",
            "DEBUG": "\x1b[38;5;15m",
            "WARNING": "\x1b[38;5;15m",
            "ERROR": "\x1b[1m\x1b[38;5;15m",
            "CRITICAL": "\x1b[1m\x1b[38;5;1m",
        },
    },
}

FILE_STANDART_MODIFIERS = {}


def preprocess_msg(msg: str) -> str:
    is_in_quote = False
    is_in_brackets = False
    is_between_spaces = False
    st_idx = -1
    l_w = 0
    ret_str = ""
    for i, s in enumerate(msg + "\0"):
        if s == ")" and is_in_brackets:
            is_in_brackets = False
            ret_str += (
                msg[l_w:st_idx] + "\x1b[38;5;8m" + msg[st_idx : i + 1] + "\x1b[0m"
            )
            l_w = i + 1
            st_idx = -1
            continue
        if s == "'" and is_in_quote:
            is_in_quote = False
            ret_str += (
                msg[l_w:st_idx] + "\x1b[38;5;2m" + msg[st_idx : i + 1] + "\x1b[0m"
            )
            l_w = i + 1
            st_idx = -1
            continue
        if is_in_brackets or is_in_quote:
            continue
        if s == "(":
            is_in_brackets = True
            is_between_spaces = False
            st_idx = i
            continue
        if s == "'":
            if i != 0 and msg[i - 1].isalpha():
                continue
            is_in_quote = True
            is_between_spaces = False
            st_idx = i
            continue
        if s == " " and not is_between_spaces:
            is_between_spaces = True
            continue
        if (
            (s.isupper() or (s.isdigit() or s == "-"))
            and is_between_spaces
            and st_idx == -1
        ):
            st_idx = i
            continue
        if (
            not (
                s.isupper()
                or (s.isdigit() or s == "-" or (s == "." and msg[st_idx].isdigit()))
            )
            and not s.isalpha()
            and st_idx != -1
        ):
            if msg[i - 1] == "-":
                continue
            ret_str += (
                msg[l_w:st_idx]
                + (
                    "\x1b[38;5;6m"
                    if (msg[st_idx].isdigit() or msg[st_idx] == "-")
                    else "\x1b[38;5;5m"
                )
                + msg[st_idx : i + s.isdigit()]
                + "\x1b[0m"
                + ("" if s.isdigit() else s)
            )
            l_w = i + 1
            st_idx = -1
            if s != " ":
                is_between_spaces = False
        if not (s.isupper() or (s.isdigit() or s == ".")) and s != " ":
            is_between_spaces = False
            st_idx = -1
    ret_str += msg[l_w:]
    return ret_str


stdout_full_info = LogStyle(
    "{date}{location}{event}{message}",
    {
        "date": "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{microsecond}|",
        "location": "\x1b[1m<{location}>\x1b[0m",
        "event": "[{EVENT_TYPE_style_modifier}{event_type}\x1b[0m]:",
        "message": "{EVENT_TYPE_msg_style_modifier}{message}\x1b[0m",
    },
    STDOUT_STANDART_MODIFIERS,
    function_modifiers={"message": preprocess_msg},
)
stdout = LogStyle(
    "{location}{event}{message}",
    {
        "location": "\x1b[1m<{location}>\x1b[0m",
        "event": "[{EVENT_TYPE_style_modifier}{event_type}\x1b[0m]:",
        "message": "{EVENT_TYPE_msg_style_modifier}{message}\x1b[0m",
    },
    STDOUT_STANDART_MODIFIERS,
    function_modifiers={"message": preprocess_msg},
)
stdout_simple = LogStyle(
    "{event}{message}",
    {
        "event": "[{EVENT_TYPE_style_modifier}{event_type}\x1b[0m]:",
        "message": "{EVENT_TYPE_msg_style_modifier}{message}\x1b[0m",
    },
    STDOUT_STANDART_MODIFIERS,
    function_modifiers={"message": preprocess_msg},
)
file = LogStyle(
    "{date}{location}{event}{message}",
    {
        "date": "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{microsecond}|",
        "location": "<{location}>",
        "event": "[{event_type}]:",
        "message": "{message}",
    },
    FILE_STANDART_MODIFIERS,
)
none_style = LogStyle("", {}, {})
if __name__ == "__main__":
    from datetime import datetime

    date_and_time = {}
    date_and_time["year"] = datetime.now().year
    date_and_time["month"] = datetime.now().month
    date_and_time["day"] = datetime.now().day
    date_and_time["hour"] = datetime.now().hour
    date_and_time["minute"] = datetime.now().minute
    date_and_time["second"] = datetime.now().second
    date_and_time["microsecond"] = datetime.now().microsecond
    print(
        stdout_full_info.to_format_string(
            {
                "location": "main.py",
                "event_type": "INFO",
                "message": "Hi there!",
                **date_and_time,
            }
        )
    )
