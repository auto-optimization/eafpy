import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

_3d_margin = dict(r=5, l=5, b=20, t=20)


def _get_3d_title(title):
    return {"text": title, "y": 0.9, "x": 0.45, "xanchor": "center", "yanchor": "top"}


def _parse_plot_type(line_type, dimension):
    if not isinstance(line_type, str):
        raise TypeError("Type argument must be a string")
    type_arr = line_type.replace(" ", "").lower().split(",")
    if len(type_arr) > 2:
        raise ValueError("Error parsing Type command: Too many commas")
    allowed_types = ["lines", "points", "surface", "cube"]
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
    else:
        raise ValueError(f"Type argument for plot_datasets not recognised: {type}")


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


# Might be better to do this in C?
""" Take a numpy array of points and create a numpy array holding the remaing 8 points

:param np_dataset: Numpy dataset, it should be fetched using the read_dataset function
:type np_dataset: numpy float ndarray
...
:return: Returns a numpy array with shape [8x dataset rows,  dataset columns + 1]. Every 4th row contains the point from the input dataset. 
         the proceding 3 rows contain one dimension of the point. For example if the first data point in the input argument is [3,3,3, set]
         then the array will look like this:
         [3,3,3, set, cubenumber = 0]
         [3,0,0, set, 0]
         [0,3,0, set, 0]
         [0,0,3, set, 0]
:rtype: numpy float ndarray
"""


def _get_cube_points(dataset):
    ds_cube = np.zeros((dataset.shape[0] * 8, 5), dtype=float)
    cube_num = 0
    for row in range(ds_cube.shape[0]):
        if row % 8 == 0:
            cube_num = cube_num + 1
        i = (row % 8) >> 2
        j = ((row % 8) >> 1) & 1
        k = (row % 8) & 1
        ds_cube[row, 0] = dataset[int(row / 8), 0] * float(i)
        ds_cube[row, 1] = dataset[int(row / 8), 1] * float(j)
        ds_cube[row, 2] = dataset[int(row / 8), 2] * float(k)
        ds_cube[row, 3] = dataset[int(row / 8), 3]
        ds_cube[row, 4] = cube_num

    return ds_cube


# The order of the points does matter
# Need to select the triangles using i,j,k
# Where each is an index of a point from the x,y,z list
# We can make each cuboid out of 12 triangles


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
    cube_nums = cube_df["Cube Number"].unique()
    for cube in cube_nums:
        single_cube = cube_df[cube_df["Cube Number"] == cube]
        fig.add_trace(
            go.Mesh3d(
                x=single_cube["Objective 1"],
                y=single_cube["Objective 2"],
                z=single_cube["Objective 3"],
                i=[1, 1, 4, 4, 2, 2, 0, 3, 3, 6, 4, 4],
                j=[3, 5, 5, 1, 4, 4, 2, 2, 2, 7, 6, 7],
                k=[7, 7, 1, 0, 6, 0, 1, 1, 6, 3, 7, 5],
                name="Cube " + str(cube),
            ),
        )
    return fig


def plot_datasets(datasets, type="points"):
    datasets = np.asarray(datasets)
    if not isinstance(datasets, np.ndarray):
        raise TypeError("Dataset must be of type numpy array")
    dim = datasets.shape[1] - 1
    if dim > 3:
        raise ValueError(
            "Dataset must contain 2 or 3 objectives "
            "the last column must be the set number"
        )
    type_parsed = _parse_plot_type(type, dim)

    column_names = ["Objective 1", "Objective 2", "Set Number"]
    if dim == 3:
        column_names.insert(2, "Objective 3")
    sets_df = pd.DataFrame(datasets, columns=column_names)

    # convert to string without decimal points, plotly interprets ints as discrete colour sequences

    sets_df["Set Number"] = sets_df["Set Number"].astype(int).astype(str)

    if dim == 2:
        df_sorted = sets_df.groupby("Set Number").apply(
            lambda x: x.sort_values("Objective 1")
        )
        figure = px.line(
            df_sorted,
            x="Objective 1",
            y="Objective 2",
            color="Set Number",
            title="Plot of a two objective dataset",
        )
        figure.update_traces(line_shape="hv", mode=type_parsed)

    elif dim == 3:
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

    return figure
