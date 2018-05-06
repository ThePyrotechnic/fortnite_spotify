import sys
from enum import Enum, auto
try:
    from ctypes import windll
except ImportError:
    sys.exit('This script is only compatible with Windows')


_DC = windll.user32.GetDC(0)

# TODO write calibration tool to accommodate different brightness settings
# These integers are calculated by taking the hex values of the RGB,
# then converting 0xBBGGRR to base 10
_COLORS = {                     # (RRR, GGG, BBB)
    'menu_left': 2694160,       # (16, 28, 41)
    'menu_middle': 2824213,     # (21, 24, 43)
    'waiting': 12801347,        # (67,85,195)
    'launching': 12801347,      # (67,85,195)
    'can_parachute': 3645285,   # (101,159,55)
    'storm_waiting': 16175872,  # (0,211,246)
}


def _get_pixel(x: int, y: int) -> int:
    """
    Get a pixel from the screen at (x, y)
    :param x: The x-coordinate
    :param y: The y-coordinate
    :return: An integer in the byte format 0xBBGGRR
    """
    return windll.gdi32.GetPixel(_DC, x, y)


def _pixel_to_rgb(pixel: int) -> (int, int, int):
    """
    Convert a pixel in the byte format 0xBBGGRR to a tuple
    :param pixel: The pixel to convert
    :return: A tuple in the format (R, G, B)
    """
    r = pixel & 0xff
    g = (pixel >> 8) & 0xff
    b = (pixel >> 16) & 0xff
    return r, g, b


def _in_menu() -> bool:
    """
    Check if the Fortnite main menu is visible
    :return: True if the main menu is visible, false otherwise
    """
    # Check the bottom menu bar at the far left.
    errors = len([x for x in [0, 4, 9, 10] if _get_pixel(x, 1022) != _COLORS['menu_left']])
    # and check the the middle to the end of the bar
    errors += len([x for x in [500, 800, 1600, 1919] if _get_pixel(x, 1022) != _COLORS['menu_middle']])
    # Allow one error because the mouse may be covering one of the spots
    return errors < 2


def _waiting() -> bool:
    """
    Check if the Fortnite is waiting for players
    :return: True if the game is in the waiting state, false otherwise
    """
    errors = len([pair for pair in [(1681, 231), (1688, 331), (1693, 319)] if _get_pixel(*pair) != _COLORS['waiting']])
    return errors < 2


def _launching() -> bool:
    """
    Check if the Battle Bus is launching
    :return: True if the Battle Bus is launching, false otherwise
    """
    errors = len([pair for pair in [(1648, 314), (1666, 314), (1656, 335)] if _get_pixel(*pair) != _COLORS['launching']])
    return errors < 2


def _can_parachute() -> bool:
    """
    Check if the game is in the parachuting state
    :return: True if players can still parachute, false otherwise
    """
    errors = len([pair for pair in [(1648, 314), (1666, 314), (1665, 331)] if _get_pixel(*pair) != _COLORS['can_parachute']])
    return errors < 2


def _storm_waiting() -> bool:
    """
    Check if the storm is currently not closing
    :return: True if the storm is stopped, false otherwise
    """
    errors = len([pair for pair in [(1651, 318), (1656, 332), (1662, 319)] if _get_pixel(*pair) != _COLORS['storm_waiting']])
    return errors < 2


class GameState(Enum):
    UNKNOWN = auto()

    IN_MENU = auto()
    WAITING = auto()
    LAUNCHING = auto()
    CAN_PARACHUTE = auto()
    STORM_WAITING = auto()


def get_state() -> GameState:
    if _waiting():
        return GameState.WAITING
    if _launching():
        return GameState.LAUNCHING
    if _can_parachute():
        return GameState.CAN_PARACHUTE
    if _storm_waiting():
        return GameState.STORM_WAITING
    if _in_menu():
        return GameState.IN_MENU
    return GameState.UNKNOWN
