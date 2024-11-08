from yapl.styling.stylingABC import LogStyle

STANDART_EVENT_TYPES = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]

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


stdout = LogStyle(
    "{date}{location}{event}{message}",
    {
        "date": "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{microsecond}|",
        "location": "\x1b[1m<{location}>\x1b[0m",
        "event": "[{EVENT_TYPE_style_modifier}{event_type}\x1b[0m]:",
        "message": "{EVENT_TYPE_msg_style_modifier}{message}\x1b[0m",
    },
    STDOUT_STANDART_MODIFIERS,
)
stdout_simple = LogStyle(
    "{event}{message}",
    {
        "event": "[{EVENT_TYPE_style_modifier}{event_type}\x1b[0m]:",
        "message": "{EVENT_TYPE_msg_style_modifier}{message}\x1b[0m",
    },
    STDOUT_STANDART_MODIFIERS,
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
        stdout.to_format_string(
            {
                "location": "main.py",
                "event_type": "INFO",
                "message": "Hi there!",
                **date_and_time,
            }
        )
    )
