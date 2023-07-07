import eafpy as eaf

X = eaf.read_datasets("input1.dat")
subset = X[X[:, 2] == 3, :2]
nondominated = eaf.is_nondominated(subset)
print(nondominated)
print(subset[nondominated])
