import sys
from enum import Enum, auto
from typing import Tuple

try:
    from ctypes import windll
except ImportError:
    sys.exit('This script is only compatible with Windows')

_DC = windll.user32.GetDC(0)

# TODO write calibration tool to accommodate different brightness settings

_COLORS = {  # (RRR, GGG, BBB)
    'menu_left': (16, 28, 41),  # (16, 28, 41)
    'menu_middle': (21, 24, 43),  # (21, 24, 43)
    'waiting': (67, 85, 195),  # (67,85,195)
    'launching': (67, 85, 195),  # (67,85,195)
    'can_parachute': (101, 159, 55),  # (101,159,55)
    'storm_waiting': (0, 211, 246),  # (0,211,246)
}

_PIXELS = {
    'menu_left': [(0, 1022), (4, 1022), (9, 1022), (10, 1022)],
    'menu_middle': [(500, 1022), (800, 1022), (1600, 1022), (1919, 1022)],
    'waiting': [(1681, 231), (1688, 331), (1693, 319)],
    'launching': [(1648, 314), (1666, 314), (1656, 335)],
    'can_parachute': [(1648, 314), (1666, 314), (1665, 331)],
    'storm_waiting': [(1651, 318), (1656, 332), (1662, 319)],

}

_DISTANCE = 3


def _get_pixel(x: int, y: int) -> int:
    """
    Get a pixel from the screen at (x, y)
    :param x: The x-coordinate
    :param y: The y-coordinate
    :return: An integer in the byte format 0xBBGGRR
    :note: These integers are calculated by taking the hex values of the RGB, then converting 0xBBGGRR to base 10
    """
    return windll.gdi32.GetPixel(_DC, x, y)


def _pixel_to_rgb(pixel: int) -> Tuple[int, int, int]:
    """
    Convert a pixel in the byte format 0xBBGGRR to a tuple
    :param pixel: The pixel to convert
    :return: A tuple in the format (R, G, B)
    """
    r = pixel & 0xff
    g = (pixel >> 8) & 0xff
    b = (pixel >> 16) & 0xff
    return r, g, b


def _in_acceptable_range(color_to_check: Tuple[int, int, int], color_ref: Tuple[int, int, int], distance: int) -> bool:
    """
    Check if each color value of a pixel is with a specified distance of the color values in the reference color
    :param color_to_check: The color to perform the bounds check on
    :param color_ref: The color to use as the reference
    :param distance: The maximum allowed distance
    :return: True if color_to_check is within the distance, false otherwise
    """
    if color_ref[0] - distance < color_to_check[0] < color_ref[0] + distance:
        if color_ref[1] - distance < color_to_check[1] < color_ref[1] + distance:
            if color_ref[2] - distance < color_to_check[2] < color_ref[2] + distance:
                return True
    return False


def _in_menu() -> bool:
    """
    Check if the Fortnite main menu is visible
    :return: True if the main menu is visible, false otherwise
    """
    # Check the bottom menu bar at the far left.
    errors = len([pair for pair in _PIXELS['menu_left']
                  if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['menu_left'], distance=_DISTANCE)])
    # and check the the middle to the end of the bar
    errors += len([pair for pair in _PIXELS['menu_middle']
                   if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['menu_middle'], distance=_DISTANCE)])
    # Allow one error because the mouse may be covering one of the spots
    return errors < 2


def _waiting() -> bool:
    """
    Check if the Fortnite is waiting for players
    :return: True if the game is in the waiting state, false otherwise
    """
    errors = len([pair for pair in _PIXELS['waiting']
                  if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['waiting'], distance=_DISTANCE)])
    return errors < 2


def _launching() -> bool:
    """
    Check if the Battle Bus is launching
    :return: True if the Battle Bus is launching, false otherwise
    """
    errors = len([pair for pair in _PIXELS['launching']
                  if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['launching'], distance=_DISTANCE)])
    return errors < 2


def _can_parachute() -> bool:
    """
    Check if the game is in the parachuting state
    :return: True if players can still parachute, false otherwise
    """
    errors = len([pair for pair in _PIXELS['can_parachute']
                  if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['can_parachute'], distance=_DISTANCE)])
    return errors < 2


def _storm_waiting() -> bool:
    """
    Check if the storm is currently not closing
    :return: True if the storm is stopped, false otherwise
    """
    errors = len([pair for pair in _PIXELS['storm_waiting']
                  if not _in_acceptable_range(_pixel_to_rgb(_get_pixel(*pair)), _COLORS['storm_waiting'], distance=_DISTANCE)])
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
