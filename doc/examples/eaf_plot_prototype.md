---
file_format: mystnb
kernelspec:
  name: python3
---
# plot 2d eaf

```{code-cell}
import eafpy as eaf
dat = eaf.read_datasets("input1.dat")
eafs = eaf.get_eaf(dat, percentiles = [25, 50, 75, 100])
fig = eaf.plot.eaf_plot(eafs)
fig.show()
```
