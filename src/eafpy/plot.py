import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def _parse_line_type(line_type):
    if not isinstance(line_type, str):
        raise TypeError("Type argument must be a string")
    type_arr = line_type.replace(" ", "").lower().split(",")
    if len(type_arr) > 2:
        raise ValueError("Error parsing Type command: Too many commas")
    has_line = any("lines".startswith(x) for x in type_arr)
    has_point = any("points".startswith(x) for x in type_arr)
    if has_line and has_point:
        return "lines+markers"
    elif has_point:
        return "markers"
    elif has_line:
        return "lines"
    else:
        raise ValueError(f"Type argument for plot_datasets not recognised: {type}")


def plot_datasets(datasets, type="points"):
    type_parsed = _parse_line_type(type)
    datasets = np.asarray(datasets)
    if not isinstance(datasets, np.ndarray):
        raise TypeError("Dataset must be of type numpy array")
    dim = datasets.shape[1] - 1
    if dim > 3:
        raise ValueError(
            "Dataset must contain 2 or 3 objectives "
            "the last column must be the set number"
        )

    column_names = ["Objective 1", "Objective 2", "Set Number"]
    if dim == 3:
        column_names.insert(2, "Objective 3")
    sets_df = pd.DataFrame(datasets, columns=column_names)

    # convert to string without decimal points
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
            title="Two objective dataset",
        )

        figure.update_traces(line_shape="hv", mode=type_parsed)

    elif dim == 3:
        if "lines" in type_parsed:
            # I think I will have to add some more complicated calculation here
            # In order to get a kind of "box" plot
            figure = go.Figure(data=[go.Surface(z=sets_df.values)])

        else:
            figure = px.scatter_3d(
                sets_df,
                x="Objective 1",
                y="Objective 2",
                z="Objective 3",
                color="Set Number",
                title="Three objective dataset",
            )
            figure.update_traces(marker_size=4)
    else:
        raise NotImplementedError

    return figure
