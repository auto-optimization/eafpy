---
file_format: mystnb
kernelspec:
  name: python3
---
# Style plots with plot_datasets
The plot_datasets function has a parameter `layout_kwargs` - any extra named arguments will be passed into `figure.update_layout()` (a plotly function for changing graphs after they are created), this is how plots should be styled.

For a list of all available layout options see [layout plotly reference](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout). Here are some examples:

## Changing title and axis titles 

```{code-cell}
import eafpy as eaf
sets = eaf.read_datasets("input1.dat")
subset = eaf.subset(sets, range = [6,10])
plot = eaf.plot_datasets(subset, type="points, lines",title="Tastiness of fruit vs ease of eating",
                         xaxis_title="Ease of eating score", yaxis_title="Tastiness of fruit score")
plot.show()
```

## Changing the template 
Plotly allows for 11 basic templates that can be selected to change the colour scheme and basic visual appearance. These include: 'ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 'plotly_dark', 'presentation','xgridoff','ygridoff', 'gridon', 'none'

The default look is "plotly". Custom templates can be created and used [template plotly reference](https://plotly.com/python/templates/)

Example of changing template to "plotly_dark"

```{code-cell}
import eafpy as eaf
sets = eaf.read_datasets("input1.dat")
subset = eaf.subset(sets, range = [6,10])
plot = eaf.plot_datasets(subset, type="lines", template="plotly_dark")
plot.show()
```

## Changing graph colour scheme
Use the `colorway` argument to change the color sequence of the traces. This can be:
* a list of colours in string form `['red', 'green', 'blue']`
* a list of rgb values in string form eg. `['rgb(123,23,12)', 'rgb(13,12,32)']`
* One of the pre-set sequences defined in `px.colors.qualitative` (see below)
```{code-cell}
import plotly.express as px
print("available presets: " + str(dir(px.colors.qualitative)))
print("Example of a preset: " + str(px.colors.qualitative.Prism))

```
The `colorway` argument takes priority over the `template` colorway (A template includes its own colorway)

```{code-cell}
import eafpy as eaf
import plotly.express as px
sets = eaf.read_datasets("input1.dat")
subset = eaf.subset(sets, range = [6,10])
plot = eaf.plot_datasets(subset, type="lines", template="plotly_dark", colorway=px.colors.qualitative.Vivid)
plot.show()
```

