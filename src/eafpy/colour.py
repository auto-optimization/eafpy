import numpy as np
from matplotlib import colors
import re

# FIXME add tests for this module


class colour_gradient:
    gradient = []
    _col_a = ""
    _col_b = ""

    def __init__(self, colour_a, colour_b):
        self._col_a = colour_a
        self._col_b = colour_b

    def create_gradient(self, steps):
        self.gradient = discrete_colour_gradient(self._col_a, self._col_b, steps)
        return self.gradient


def RGBA_arr_to_string(rgba_arr):
    """RGBA array to RGBA string

    Convert a matrix of RGBA values to list of rgba strings. If the input array has only one row, then return single string

    Parameters
    ----------
    rgba_arr : numpy array (n, 4)
        Numpy array with n rows and 4 columns, where each row represents a different colour and each column is a float representing one of RGBA
        If n=1, then return a single string instead of a list

    Returns
    -------
    list
        A list of `rgba(w,x,y,z)` strings compatible with a plotly colorscale
    """
    if len(rgba_arr.shape) != 1:
        rgba_strings = []
        rgba_arr = np.asarray(rgba_arr)
        for i in range(rgba_arr.shape[0]):
            rgba = np.round(rgba_arr[i], 4)
            rgba_strings.append(f"rgba({rgba[0]},{rgba[1]},{rgba[2]},{rgba[3]})")
        return rgba_strings
    else:
        return f"rgba({rgba_arr[0]},{rgba_arr[1]},{rgba_arr[2]},{rgba_arr[3]})"


def parse_colour_to_nparray(colour, strings=False):
    """parse a single colour argument to a (1,4) numpy array representing its RGBA values
    This can be used to manipulate the values before converting it back to RGBA string using :func:`RGBA_arr_to_string`

    Parameters
    ----------
    colour : Named CSS colour, RGBA string or 8 character hex RGBA integer
        A colour argument can be one of the following:
            Named CSS colour string: "red" or "hotpink"
            RGBA string: "rgba(0.2, 0.5, 0.1, 0.5)"
            8 character hex RGBA integer: 0x1234abcde
    strings : boolean
        If strings=True then the argument will return a list of 'rgba(w,x,y,z)' strings instead of a numpy array

    Returns
    -------
    numpy array (1,4)
        A (1,4) numpy array where each index represents one of the red, green, blue, alpha values (from 0-1)
    """
    if isinstance(colour, str):
        # Match strings similar to rgba(0,0,0,0) with whitespace allowed
        rgba_matches = re.findall(
            "rgba\s*\((?=[\d. ]*[\d])\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)",
            colour,
        )
        rgb_matches = re.findall(
            "rgb\s*\((?=[\d. ]*[\d])\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)",
            colour,
        )

        if colors.is_color_like(colour):
            # Allow CSS colour strings such as "blue" or "hotpink"
            rgba_colour = np.array(list(colors.to_rgba(colour)), dtype=np.float64)
        elif rgba_matches:
            # Parse strings such as rgba(0, 1, 2,3 ), removing the whitespace
            rgba_colour = np.array(
                [x.strip() for x in list(rgba_matches[0])], dtype=np.float64
            )
        elif rgb_matches:
            # Convert RGB match to RGBA by appending alpha=1
            rgb_matches = list(rgb_matches[0])
            rgb_matches.append("1")
            rgba_colour = np.array([x.strip() for x in rgb_matches], dtype=np.float64)
        else:
            raise ValueError(
                f"String color argument : '{colour}' is not recognised. It must be known CSS4 color or 'rgba(w,x,y,z)' string"
            )
    elif isinstance(colour, int):
        # Accept 8 digit hexadecimal number where every 2 digits represent one of (RGBA). Alpha value is the least significant byte
        rgba_colour = (
            np.array(
                [((colour >> 8 * i) & 0xFF) for i in reversed(range(4))],
                dtype=np.float64,
            )
            / 255.0
        )
    else:
        raise TypeError(f"Color argument '{colour}' not recognised, may be wrong type")
    if strings:
        return RGBA_arr_to_string(rgba_colour)
    else:
        return rgba_colour


def discrete_opacity_gradient(colour, num_steps, start_opacity=0.0, end_opacity=1.0):
    """Create opacity gradient colour list for use in plotly colorscales

        Linearly interpolates between starting and ending opacity

    Parameters
    ----------
    color : string
        The name of a standard CSS colour
    steps : integer
        Number of steps between the start and end opacity. Also the size of the list returned
    start_opacity, end_opacity : floats
        Choose what the starting and ending values of opacity are for the list of colours (between 0 and 1)

    Returns
    -------
    list
        A list of RGBA string values compatible with plotly colorscales, interpolating opacity between two values
    # TODO FIXME add examples of this in the styling tutorial
    """
    rgba_color = parse_colour_to_nparray(colour)

    # Create a 2d array of colours, where the alpha value is linearly interpolated from the start to end value
    gradient = np.tile(rgba_color, ((num_steps, 1)))
    gradient[:, -1] = np.linspace(start_opacity, end_opacity, num=num_steps)

    gradient_strings = RGBA_arr_to_string(gradient)
    return gradient_strings


def discrete_colour_gradient(colour_a, colour_b, num_steps):
    """Create colour gradient list for use in plotly colorscales
    Linearly interpolates between two colours using a define amount of steps

    Parameters
    ----------
    color_a, color_b : string
        The names of standard CSS colours to create a gradient
    steps : integer
        Number of steps between between the starting and ending colour. Also the size of the list returned

    Returns
    -------
    list
        A list of RGBA string values compatible with plotly colorscales
    """
    a_rgba = parse_colour_to_nparray(colour_a)
    b_rgba = parse_colour_to_nparray(colour_b)
    colour_gradient = np.ndarray((num_steps, 4))
    if num_steps <= 1:
        return RGBA_arr_to_string(a_rgba)  # If no gradient, return first colour
    for step in range(num_steps):
        difference = b_rgba - a_rgba
        colour_gradient[step, :] = a_rgba + step * (difference / (num_steps - 1))
    colour_gradient_strings = RGBA_arr_to_string(colour_gradient)
    return colour_gradient_strings


def get_default_fill_colorway(num_steps):
    return discrete_opacity_gradient("black", num_steps, start_opacity=0.6)


def get_2d_colorway_from_colour(num_steps, colour):
    # Input single colour, return 2d list of colours populated with same colour
    colour = parse_colour_to_nparray(colour, strings=True)
    colour_list = []
    for steps in num_steps:
        colour_list.append([colour] * steps)
    return colour_list


# Parse different types of colorway arguments into an acceptable format, or choose default
def parse_single_colorway(length, default, colorway):
    if colorway:
        # Change colorway arguments to follow "rgba()" format
        if isinstance(colorway, str) or isinstance(colorway, int):
            arg_to_parse = parse_colour_to_nparray(colorway, strings=True)
        elif isinstance(colorway, list):
            arg_to_parse = [
                parse_colour_to_nparray(col, strings=True) for col in colorway
            ]
        else:
            raise TypeError(
                "Colorway argument needs to be string, int or list of (string or int)"
            )
    else:
        # Set to a default value if argument is not included
        arg_to_parse = default
    if isinstance(arg_to_parse, list):
        # Ensure colorway is not smaller than required size
        arg_to_parse = arg_to_parse * 2 * length
    elif isinstance(arg_to_parse, str):
        # Eg if a colorway is a single string - "red", make it into lsit
        arg_to_parse = [arg_to_parse] * 2 * length
    else:
        raise TypeError(f"Type of colorway argument is not recognised")
    return arg_to_parse


def parse_colorway(length, default, colorway, expect_2d=False):
    if colorway:
        if isinstance(colorway, list) and isinstance(colorway[0], list):
            if not (len(length) == len(colorway)):
                raise ValueError()
            # Default is required to be a list in 2d case
            colorway = [
                parse_single_colorway(length[i], default[i], colour)
                for i, colour in enumerate(colorway)
            ]
            return colorway
    # This seems incomplete
    if expect_2d:
        if not isinstance(length, list):
            raise TypeError("length should be list if 2d expected")
        return [
            parse_colorway(len, default[i], colorway) for i, len in enumerate(length)
        ]
    else:
        return parse_single_colorway(length, default, colorway)


# THese gradients are generated using a language model and are untested so the values may be wrong
# fmt: off
def get_example_gradients(num_steps, as_list=False, choice = "arctic_exploration" ):
    example_gradients = {
        "arctic_exploration" :{
            "frosty_blue": colour_gradient(0x93c5fdFF, 0x3693e1FF),
            "icy_cyan": colour_gradient(0xa8e6cfFF, 0x5eb5a6FF),
            "glacier_teal": colour_gradient(0x6cc3d5FF, 0x408c9eFF),
            "snowy_white": colour_gradient(0xf0f8ffFF, 0xc8e1eaFF),
            "arctic_blue": colour_gradient(0x65c1ecFF, 0x3088abFF),
            "polar_silver": colour_gradient(0xcfd8dcFF, 0x89979fFF),
            "frozen_gray": colour_gradient(0xabb9c2FF, 0x6c7d86FF),
            "cold_ice": colour_gradient(0xb5d9ebFF, 0x7fa8d4FF),
            "crisp_blue": colour_gradient(0x6daad5FF, 0x3773a0FF),
            "arctic_sky": colour_gradient(0x9ec9e8FF, 0x4b80a7FF),
        }, 
        "scientific" :{
            "blue_to_gray": colour_gradient(0x1f77b4FF, 0x808080FF),
            "green_to_gray": colour_gradient(0x2ca02cFF, 0x808080FF),
            "orange_to_gray": colour_gradient(0xff7f0eFF, 0x808080FF),
            "purple_to_gray": colour_gradient(0x9467bdFF, 0x808080FF),
            "teal_to_gray": colour_gradient(0x17becfFF, 0x808080FF),
            "red_to_gray": colour_gradient(0xd62728FF, 0x808080FF),
            "pink_to_gray": colour_gradient(0xe377c2FF, 0x808080FF),
            "brown_to_gray": colour_gradient(0x8c564bFF, 0x808080FF),
            "gray_to_black": colour_gradient(0x808080FF, 0x000000FF),
            "blue_to_cyan": colour_gradient(0x1f77b4FF, 0x17becfFF),
        },
        "contrast" : {
            "frosty_blue": colour_gradient(0x93c5fdFF, 0x3693e1FF),
            "vibrant_green": colour_gradient(0x00ff00FF, 0x00cc00FF),
            "intense_purple": colour_gradient(0x9b59b6FF, 0x5d328bFF),
            "brilliant_orange": colour_gradient(0xffa500FF, 0xff8000FF),
            "deep_cyan": colour_gradient(0x17becfFF, 0x008b8bFF),
            "hot_pink": colour_gradient(0xff69b4FF, 0xff1493FF),
            "bright_turquoise": colour_gradient(0x40e0d0FF, 0x00ced1FF),
            "fiery_red": colour_gradient(0xff0000FF, 0xcc0000FF),
            "luminous_lime": colour_gradient(0x00ff00FF, 0x32cd32FF),
            "electric_yellow": colour_gradient(0xffff00FF, 0xffcc00FF),
        },

        "warm" : {
            "red_to_yellow": colour_gradient(0xff0000FF, 0xffff00FF),
            "orange_to_yellow": colour_gradient(0xffa500FF, 0xffff00FF),
            "orange_to_red": colour_gradient(0xffa500FF, 0xff0000FF),
            "brown_to_orange": colour_gradient(0x8b4513FF, 0xffa500FF),
            "red_to_brown": colour_gradient(0xff0000FF, 0x8b4513FF),
            "yellow_to_brown": colour_gradient(0xffff00FF, 0x8b4513FF),
            "red_to_pink": colour_gradient(0xff0000FF, 0xff69b4FF),
            "orange_to_pink": colour_gradient(0xffa500FF, 0xff69b4FF),
            "yellow_to_red": colour_gradient(0xffff00FF, 0xff0000FF),
            "yellow_to_orange": colour_gradient(0xffff00FF, 0xffa500FF)}
        }
# fmt: on
    if as_list:
        if isinstance(num_steps, list):
            return [gradient.create_gradient(num_steps[i%len(num_steps)]) for i,(name, gradient) in enumerate(example_gradients[choice].items())]
        elif isinstance(num_steps, int):
            return [gradient.create_gradient(num_steps) for name, gradient in example_gradients[choice].items()]
    else:
        if isinstance(num_steps, list):
            return {name: gradient.create_gradient(num_steps[i % len(num_steps)]) for i, (name, gradient) in enumerate(example_gradients[choice].items())}
        elif isinstance(num_steps, int):
            return {name: gradient.create_gradient(num_steps) for name, gradient in example_gradients[choice].items()}
