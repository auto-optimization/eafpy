import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from . import eaf
from . import colour


_3d_margin = dict(r=5, l=5, b=20, t=20)


def _apply_default_themes(fig):
    # This theme may be preferable as it has a white background so could make for a more "scientific" look
    fig.update_layout(
        plot_bgcolor="white",
    )
    fig.update_xaxes(
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    fig.update_yaxes(
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )


def _get_3d_title(title):
    return {"text": title, "y": 0.9, "x": 0.45, "xanchor": "center", "yanchor": "top"}


def _parse_plot_type(line_type, dimension):
    if not isinstance(line_type, str):
        raise TypeError("Type argument must be a string")
    type_arr = line_type.replace(" ", "").lower().split(",")
    if len(type_arr) > 2:
        raise ValueError("Error parsing Type command: Too many commas")
    allowed_types = ["lines", "points", "surface", "cube", "fill"]
    selected_types = [
        t for t in allowed_types if any(t.startswith(x) for x in type_arr)
    ]

    if ("surface" in selected_types or "cube" in selected_types) and dimension == 2:
        raise ValueError("Surface and cube types only valid for 3 objective plot")
    if "points" in selected_types and "lines" in selected_types:
        return "lines+markers"
    elif "points" in selected_types and "surface" in selected_types:
        return "surface+markers"
    elif "points" in selected_types:
        return "markers"
    elif "lines" in selected_types:
        return "lines"
    elif "surface" in selected_types:
        return "surface"
    elif "cube" in selected_types:
        return "cube"
    elif "fill" in selected_types:
        return "fill"
    else:
        raise ValueError(f"Type argument for plot_datasets not recognised: {type}")


# Generates smooth 3d mesh plot from dataset
def _gen_3d_mesh_plot(dataset, type):
    num_sets = dataset["Set Number"].unique()
    fig = go.Figure()
    for set in num_sets:
        df_one_set = dataset[dataset["Set Number"] == set]
        fig.add_trace(
            go.Mesh3d(
                x=df_one_set["Objective 1"],
                y=df_one_set["Objective 2"],
                z=df_one_set["Objective 3"],
                opacity=0.85,
                name="Set " + set,
            ),
        )
        if "markers" in type:
            fig.add_scatter3d(
                mode="markers",
                x=df_one_set["Objective 1"],
                y=df_one_set["Objective 2"],
                z=df_one_set["Objective 3"],
                name="Set " + set + " points",
                marker=dict(size=3),
            )
    fig.update_traces(showlegend=True)
    fig.update_layout(
        margin=_3d_margin,
        legend_title_text="Set Number",
        scene=dict(
            xaxis_title="Objective 1",
            yaxis_title="Objective 2",
            zaxis_title="Objective 3",
        ),
        title=_get_3d_title("Surface plot of three objective dataset"),
    )
    return fig


def _get_cube_points(dataset):
    ds_cube = np.zeros((dataset.shape[0] * 8, 5), dtype=float)
    cube_num = 0
    for row in range(ds_cube.shape[0]):
        if row % 8 == 0:
            cube_num = cube_num + 1

        # i,j,k represent binary digits that are counted up from 0 to 7 for each cube
        # these are multiplied by the co-ordinates of the orignal point to create 8 total points
        # Each point is a corner of a cube
        i = (row % 8) >> 2
        j = ((row % 8) >> 1) & 1
        k = (row % 8) & 1
        ds_cube[row, 0] = dataset[int(row / 8), 0] * float(i)
        ds_cube[row, 1] = dataset[int(row / 8), 1] * float(j)
        ds_cube[row, 2] = dataset[int(row / 8), 2] * float(k)
        ds_cube[row, 3] = dataset[int(row / 8), 3]
        ds_cube[row, 4] = cube_num

    return ds_cube


def _get_tri_indexs(num_cubes):
    # Each number in i,j,k represents an index of a point
    # Each column of i,j,k forms a triangle from three points
    # This pre-configuration forms a cube from 12 triangles
    i = [1, 1, 4, 4, 2, 2, 0, 3, 3, 6, 4, 4]
    j = [3, 5, 5, 1, 4, 4, 2, 2, 2, 7, 6, 7]
    k = [7, 7, 1, 0, 6, 0, 1, 1, 6, 3, 7, 5]
    # tri_index is a numpy array that contains indexs for n number of cubes
    tri_index = np.zeros((3, num_cubes * 12), dtype=int)
    tri_index[:3, :12] = np.array([i, j, k]).reshape(3, 12)
    for n in range(num_cubes):
        # Copy the triangle index preconfiguration to every cube
        tri_index[0:3, n * 12 : (n + 1) * 12] = (
            np.array([i, j, k]).reshape(3, 12) + 8 * n
        )
    return tri_index


# Returns a cube point. This is
def _get_cube_plot(dataset):
    fig = go.Figure()
    np_cubes = _get_cube_points(dataset)
    col_names = [
        "Objective 1",
        "Objective 2",
        "Objective 3",
        "Set Number",
        "Cube Number",
    ]

    cube_df = pd.DataFrame(np_cubes, columns=col_names)
    for set in cube_df["Set Number"].unique():
        set_n_df = cube_df[cube_df["Set Number"] == set]
        num_cubes = set_n_df["Cube Number"].nunique()
        # Define the corners of all triangles in all cubes
        cube_indexs = _get_tri_indexs(num_cubes)
        fig.add_trace(
            go.Mesh3d(
                x=set_n_df["Objective 1"],
                y=set_n_df["Objective 2"],
                z=set_n_df["Objective 3"],
                i=cube_indexs[0, :],
                j=cube_indexs[1, :],
                k=cube_indexs[2, :],
                showlegend=True,
                name="Set " + str(int(set)),
            )
        )
    fig.update_layout(
        margin=_3d_margin,
        legend_title_text="Set Number",
        scene=dict(
            xaxis_title="Objective 1",
            yaxis_title="Objective 2",
            zaxis_title="Objective 3",
        ),
        title=_get_3d_title("Cube plot of three objective dataset"),
    )
    return fig


def add_extremes(x, y, maximise):
    best_x = np.max(x) if maximise[0] else np.min(x)
    best_y = np.max(y) if maximise[1] else np.min(y)
    dtype = np.finfo(x.dtype)
    inf_x = dtype.min if maximise[0] else dtype.max
    inf_y = dtype.min if maximise[1] else dtype.max
    return np.concatenate([[best_x], x, [inf_x]]), np.concatenate(
        [[inf_y], y, [best_y]]
    )


# Parse different types of colorway arguments into an acceptable format, or choose default
def parse_colorway(name, length, default, **kwargs):
    if name in kwargs:
        # Change colorway arguments to follow "rgba()" format
        if isinstance(kwargs[name], str):
            arg_to_parse = colour.parse_colour_to_nparray(kwargs[name], strings=True)
        elif isinstance(kwargs[name], list):
            arg_to_parse = [
                colour.parse_colour_to_nparray(name, strings=True)
                for name in kwargs[name]
            ]
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
        raise TypeError(f"Type of {name} argument is not recognised")

    return arg_to_parse


def plot_datasets(datasets, type="points", filter_dominated=True, **layout_kwargs):
    """The `plot_datasets(dataset, type="points")` function plots Pareto front datasets
    It can produce an interactive point graph, stair step graph or 3d surface graph. It accept 2 or 3 objectives

    Parameters
    ----------

    dataset : numpy array
        The `dataset` argument must be Numpy array produced by the `read_datasets()` function - an array with 3-4 columns including the objective data and set numbers.
    type : str *default* : `"points"`
        The `type` argument can be `"points"`, `"lines"`, `"points,lines"` for two objective datasets,
        Or `"points"`, `"surface"` or `"cube"` for three objective datasets

        `"points"` produces a scatter-like point graph *(2 or 3 objective)*

        `"lines"` produces a stepped line graph *(2 objective only)*

        `"points,lines"` produces a stepped line graph with points *(2 objective only)*

        `"fill"` produces a stepped line graph with filled areas between lines - see :func:`plot_eaf` *(2 objective only)*

        `"surface"` produces a smoothed 3d surface *(3 objective only*)

        `"surface, points"` produces a smoothed 3d surface with datapoints plotted *(3 objective only*)

        `"cube"` produces a discrete cube surface *(3 objective only*) 

        The function parses the type argument, so accepts abbrieviations such as `p` or `"p,l"`
    filter_dominated : boolean
        Boolean value for whether to automatically filter dominated points each set. default is True

    layout_kwargs : keyword arguments
        Update features of the graph such as title axis titles, colours etc. These additional parameters are passed to \
        plotly update_layout, See here for all the layout features that can be accessed: `Layout Plotly reference <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html#plotly.graph_objects.Layout/>`_

    Returns
    -------
    Plotly GO figure
        The function returns a `Plotly GO figure` object: `Plotly Figure reference <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html#id0/>`_

        This means that the user can customise any part of the graph after it is created

    """
    try:
        datasets = np.asarray(datasets)
    except Exception as ex:
        raise TypeError("dataset cannot be converted to a numpy array") from ex

    if len(datasets.shape) != 2:
        raise ValueError("dataset must be a numpy 2D matrix")

    dim = datasets.shape[1] - 1
    if dim > 3:
        raise ValueError(
            "Dataset must contain 2 or 3 objectives "
            "the last column must be the set number"
        )

    if filter_dominated:
        datasets = eaf.filter_dominated_sets(datasets)
    num_sets = len(np.unique(datasets[:, -1]))

    type_parsed = _parse_plot_type(type, dim)

    column_names = ["Objective 1", "Objective 2", "Set Number"]
    if dim == 3:
        column_names.insert(2, "Objective 3")
    sets_df = pd.DataFrame(datasets, columns=column_names)

    # convert set num to string without decimal points, plotly interprets ints as discrete colour sequences
    sets_df["Set Number"] = sets_df["Set Number"].astype(int).astype(str)

    if dim == 2:
        if type_parsed == "fill":
            num_percentiles = len(np.unique(datasets[:, -1]))
            default_fill_colorway = colour.get_default_fill_colorway(num_percentiles)

            colorway = parse_colorway(
                "colorway", num_sets, default_fill_colorway, **layout_kwargs
            )
            line_colours = parse_colorway(
                "line_colours", num_sets, default_fill_colorway, **layout_kwargs
            )

            figure = create_fill_plot(datasets, colorway, line_colours)
            layout_kwargs.pop(
                "line_colours", None
            )  # Make sure these arguments are not used twice
            layout_kwargs.pop("colorway", None)

        else:
            colorway = parse_colorway(
                "colorway", num_sets, px.colors.qualitative.Plotly, **layout_kwargs
            )
            layout_kwargs["colorway"] = colorway
            # Sort the the points by Objective 1 within each set, while keeping the set order (May be inefficient)
            for set in sets_df["Set Number"].unique():
                mask = sets_df["Set Number"] == set
                sets_df.loc[mask] = (
                    sets_df.loc[mask].sort_values(by="Objective 1").values
                )

            figure = px.line(
                sets_df,
                x="Objective 1",
                y="Objective 2",
                color="Set Number",
                title="Plot of a two objective dataset",
                color_discrete_sequence=colorway,
            )

            maximise = [False, False]
            # Extend lines past the figure boundaries.
            for trace in figure.data:
                trace.x, trace.y = add_extremes(trace.x, trace.y, maximise)

            figure.update_traces(line_shape="hv", mode=type_parsed)

    elif dim == 3:
        colorway = parse_colorway(
            "colorway", num_sets, px.colors.qualitative.Plotly, **layout_kwargs
        )

        if "surface" in type_parsed:
            # Currently creates a surface with points joined for each
            figure = _gen_3d_mesh_plot(sets_df, type_parsed)
        elif "markers" in type_parsed:
            figure = px.scatter_3d(
                sets_df,
                x="Objective 1",
                y="Objective 2",
                z="Objective 3",
                color="Set Number",
                color_discrete_sequence=colorway,
            )
            figure.update_traces(marker_size=4)
            figure.update_layout(
                margin=_3d_margin,
                title=_get_3d_title("Point plot of three objective dataset"),
            )
        elif "cube" in type_parsed:
            figure = _get_cube_plot(datasets)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    figure.update_layout(layout_kwargs)
    return figure


# Create a fill plot -> Such as EAF percentile  plot.
# If a figure is given, update the figure insteaf of creating a new one
def create_fill_plot(dataset, colorway, line_colours, figure=None, type="points"):
    # Get a line plot and sort by the last column eg. Set number or percentile
    lines_plot = plot_datasets(dataset, type="line", filter_dominated=False)
    ordered_lines = sorted(lines_plot.data, key=lambda x: int(x["name"]))
    float_inf = np.finfo(dataset.dtype).max  # Interpreted as infinite value by plotly

    # Add an line to fill down from infinity to the last percentile
    infinity_line = dict(
        x=np.array([0, float_inf]),
        y=np.array([float_inf, float_inf]),
        # name=ordered_lines.data[-1].name,
    )
    ordered_lines.append(infinity_line)
    percentile_names = np.unique(dataset[:, -1]).astype(int)
    num_percentiles = len(percentile_names)

    # If figure argument is given, add to an existing figure, else create new figure
    if figure:
        fig = figure
    else:
        fig = go.Figure()
    is_fill = "fill" in type
    choose_mode = (
        "lines"
        if ("lines" in type or is_fill)
        else ("markers" if "points" in type else "lines")
    )
    for i, line in enumerate(ordered_lines):
        fill_i = i - 1 if i > 0 else i
        name_i = fill_i if is_fill else min(i, num_percentiles - 1)

        fig.add_trace(
            go.Scatter(
                x=line["x"],
                y=line["y"],
                mode=choose_mode,
                fill="none" if (i == 0 or not is_fill) else "tonexty",
                line={"shape": "hv"},
                fillcolor=colorway[fill_i],
                name=str(percentile_names[name_i]),
                legendgroup=str(percentile_names[name_i]),
                showlegend=False
                if (is_fill and i == 0 or not is_fill and i == len(ordered_lines) - 1)
                else True,
                marker=dict(
                    color=line_colours[name_i] if type == "fill" else colorway[name_i]
                ),
            )
        )
    return fig


def _combine_2d_figures(datasets, names, types):
    combined_figure = go.Figure()
    for i, dataset in enumerate(datasets):
        num_sets = len(np.unique(dataset[:, -1]))
        colorway = colour.get_default_fill_colorway(num_sets)
        combined_figure = create_fill_plot(
            dataset, colorway, colorway, figure=combined_figure, type=types[i]
        )
    return combined_figure


def plot_eaf(dataset, type="fill", percentiles=[], **layout_kwargs):
    """eaf_plot() conviently plots attainment surfaces in 2d

    Parameters
    ----------
    dataset : numpy.ndarray
        The `dataset` argument must be Numpy array produced by the `get_eaf()` function - an array with 3 columns including the objective data and percentiles
    percentiles : list
        A list of percentiles to plot. These must exist in the dataset argument 
    type: string
        The type argument can be "fill", "points", "lines" to define the plot type (See :func:`plot_datasets` for more details). If multiple EAFs are input \
        then this can be a list of types
    colorway : list 
        Colorway is a single colour, or list of colours, for the percentile groups. The colours can be CSS colours such as 'black', 8-digit hexedecimal RGBA integers \
        or strings of RGBA values such as `rgba(1,1,0,0.5)`. Default is "black". You can use the :func:`colour.discrete_colour_gradient` to create a gradient between two colours \
    line_colours :
        The same as colorway but defining the boundaries between percentile groups. The default value is to follow colorway. You can set it to `rgb(0,0,0,0)` to make the boundaries invisible
    layout_kwargs : keyword arguments
        Update features of the graph such as title axis titles, colours etc. These additional parameters are passed to \
        plotly update_layout, See here for all the layout features that can be accessed: `Layout Plotly reference <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html#plotly.graph_objects.Layout/>`_

    Returns
    -------
    Plotly GO figure
        The function returns a `Plotly GO figure` object `Figure Plotly reference <https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html#id0/>`_

        This means that the user can customise any part of the graph after it is created

    """
    if isinstance(dataset, np.ndarray):
        if percentiles:
            # If specific values are given, only select data from these given percentiles
            dataset = dataset[np.isin(dataset[:, -1], percentiles)]

        fig = plot_datasets(
            dataset,
            type=type,
            legend_title_text="Percentile",
            xaxis_title="Objective 0",
            yaxis_title="Objective 1",
            title="2d Empirical Attainment Function",
            **layout_kwargs,
        )
    elif isinstance(dataset, dict):
        """Expect dictionaries with this format:
        {'alg_name' : dataset}
        """
        if isinstance(type, str):
            type = [type] * len(dataset)
        elif len(type) != len(dataset):
            raise ValueError("type list must be same length as dataset dictionary")
        traces_list = []
        names_list = []
        for i, (name, set) in enumerate(dataset.items()):
            names_list.append(name)
            traces_list.append(set)
        fig = _combine_2d_figures(traces_list, names_list, type)

    return fig
