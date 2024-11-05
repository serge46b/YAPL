class StyleDictParseError(Exception):
    """Raises when style dictionary is incorrectly compiled"""


class LinkToSameDestinationError(Exception):
    """Raises when multiple loggers tries to point at the same destination"""
