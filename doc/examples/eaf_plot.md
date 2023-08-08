---
file_format: mystnb
kernelspec:
  name: python3
---
# Empirical attainment function plot
## Plot a 2d eaf surface
The empirical attainment function can used to visualise the spread of solutions when looking at a multi-objective optimisation problem. This can be especially usefuly when comparing two different algorithms, or different parameters of the same algorithm.
When plotting a single algorithm,the `plot_eaf` function a numpy array of EAF points, such as is created by the `get_eaf` function. 

```{code-cell}
import eafpy as eaf
dat = eaf.read_datasets("input1.dat")
eafs = eaf.get_eaf(dat, percentiles = [25, 50, 75, 100])
fig = eaf.plot_eaf(eafs)
fig.show()
```
## Plot different algorithms on the same graph
To plot multiple EAF data on the same graph, such as comparing the mean result of two algorithms, the `dataset` argument should be a dictionary. The `type` argument can be any of `lines`, `fill` or `points`. 

```{code-cell}
import eafpy as eaf

# Generate random non-dominated data points for demonstration
data_points1 = eaf.rand_non_dominated_sets(num_points= 100, num_sets=10)
data_points2 = eaf.rand_non_dominated_sets(num_points= 100, num_sets=10)

eaf1 = eaf.get_eaf(data_points1,percentiles=[0,25,50, 75, 100] )
eaf2 = eaf.get_eaf(data_points2, percentiles=[0,25, 50, 75, 100])

fig = eaf.plot_eaf({'NSGA-II' : eaf1, 'MOEA/D ' : eaf2}, type ="lines", percentiles=[50])
fig.show()
```

## Customising EAF plot examples
In this example, the median value (50th percentile) of algorithm 2 is compared to the filled EAF plot of algorithm 1. 

* The `type` argument can be a list defining the plot type of each dataset instead of for the whole plot
* The `colorway`, `fill_border_colours` and `percentiles` arguments can accept a 2d list, configuring each EAF seperately
  * The "colorway" argument configures the colours of the traces. [See more about colorway](colorway-section)
  * The `fill_border_colours` argument defines the colour of the percentile boundary lines in a fill plot. It can be set to `"rgba(0,0,0,0)"` (invisible) to remove them.
* The `trace_names` argument can over-ride the default figure names
* Plotly layout named arguments can be used such as `legend_title_text`. See [style plots page](style-plots-section)

```{code-cell}
import eafpy as eaf

# Generate random non-dominated data points
data_points1 = eaf.rand_non_dominated_sets(num_points= 50, num_sets=10)
data_points2 = eaf.rand_non_dominated_sets(num_points= 50, num_sets=10)

eaf1 = eaf.get_eaf(data_points1,percentiles=[0,25,50, 75, 100] )
eaf2 = eaf.get_eaf(data_points2, percentiles=[0,25, 50, 75, 100])

colorway1 = ["darkgrey", "grey", "black"]

fig = eaf.plot_eaf({'NSGA-II' : eaf1, 'MOEA/D ' : eaf2}, 
                   type =["fill", "line"], 
                   percentiles=[[0,50,100], [50]],
                   colorway= [colorway1, ["darkblue"]], 
                   fill_border_colours = "rgba(0,0,0,0)",
                   trace_names=["Algorithm 1 Best", "Algorithm 1 Mean", "Algorithm 1 Worst", "Algorithm 2 Mean"],
                   legend_title_text="Cool legend title"
                   )
fig.show()
```




