import numpy as np
from matplotlib import colors
import re

# FIXME add tests for this module


def RGBA_arr_to_string(rgba_arr):
    """RGBA array to RGBA string

    Convert a matrix of RGBA values to list of rgba strings

    Parameters
    ----------
    rgba_arr : numpy array (n, 4)
        Numpy array with n rows and 4 columns, where each row represents a different colour and each column is a float representing one of RGBA

    Returns
    -------
    list
        A list of `rgba(w,x,y,z)` strings compatible with a plotly colorscale
    """
    rgba_strings = []
    rgba_arr = np.asarray(rgba_arr)
    for i in range(rgba_arr.shape[0]):
        rgba = np.round(rgba_arr[i], 4)
        rgba_strings.append(f"rgba({rgba[0]},{rgba[1]},{rgba[2]},{rgba[3]})")
    return rgba_strings


def parse_colour_to_nparray(colour):
    """parse a single colour argument to a (1,4) numpy array representing its RGBA values
    This can be used to manipulate the values before converting it back to RGBA string using :func:`RGBA_arr_to_string`

    Parameters
    ----------
    colour : Named CSS colour, RGBA string or 8 character hex RGBA integer
        A colour argument can be one of the following:
            Named CSS colour string: "red" or "hotpink"
            RGBA string: "rgba(0.2, 0.5, 0.1, 0.5)"
            8 character hex RGBA integer: 0x1234abcde


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
        if colors.is_color_like(colour):
            # Allow CSS colour strings such as "blue" or "hotpink"
            rgba_colour = np.array(list(colors.to_rgba(colour)), dtype=np.float64)
        elif rgba_matches:
            # Parse strings such as rgba(0, 1, 2,3 ), removing the whitespace
            rgba_colour = np.array(
                [x.strip() for x in list(rgba_matches[0])], dtype=np.float64
            )
        else:
            raise ValueError(
                f"String color argument : '{colour}' is not recognised. It must be CSS color or 'rgba(w,x,y,z)' string"
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
    for step in range(num_steps):
        difference = b_rgba - a_rgba
        colour_gradient[step, :] = a_rgba + step * (difference / (num_steps - 1))
    colour_gradient_strings = RGBA_arr_to_string(colour_gradient)
    return colour_gradient_strings
