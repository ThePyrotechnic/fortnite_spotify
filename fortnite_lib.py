import sys
try:
    from ctypes import windll
except ImportError:
    sys.exit('This script is only compatible with Windows')


DC = windll.user32.GetDC(0)


def get_pixel(x: int, y: int) -> int:
    """
    Get a pixel from the screen at (x, y)
    :param x: The x-coordinate
    :param y: The y-coordinate
    :return: An integer in the byte format 0xBBGGRR
    """
    return windll.gdi32.GetPixel(DC, x, y)


def pixel_to_rgb(pixel: int) -> (int, int, int):
    """
    Convert a pixel in the byte format 0xBBGGRR to a tuple
    :param pixel: The pixel to convert
    :return: A tuple in the format (R, G, B)
    """
    r = pixel & 0xff
    g = (pixel >> 8) & 0xff
    b = (pixel >> 16) & 0xff
    return r, g, b


def in_menu() -> bool:
    """
    Check if the Fortnite main menu is visible
    :return: True if the main menu is visible, false otherwise
    """
    # Check the bottom menu bar. The beginning should be colored (16, 28, 41)
    errors = len([x for x in [0, 4, 9, 10] if get_pixel(x, 1022) != 2694160])
    # and the middle to the end should be colored (21, 24, 43)
    errors += len([x for x in [500, 800, 1600, 1919] if get_pixel(x, 1022) != 2824213])
    # Allow one error because the mouse may be covering one of the spots
    return errors < 2
