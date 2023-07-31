---
file_format: mystnb
kernelspec:
  name: python3
---
# Plot a 2d eaf surface
The `plot_eaf` function expects an argument of data created from the `get_eaf` function. See how to style such plots [here](style-plots-section)

```{code-cell}
import eafpy as eaf
dat = eaf.read_datasets("input1.dat")
eafs = eaf.get_eaf(dat, percentiles = [25, 50, 75, 100])
fig = eaf.plot_eaf(eafs)
fig.show()
```
