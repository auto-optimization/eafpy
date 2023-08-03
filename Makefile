.PHONY : install build test doc

install: build
	python3 -m pip install -e .

build:
	python3 -m build

test:
	tox

doc: clean
	tox -e docs
	$(MAKE) -C doc html

clean:
	$(RM) -rf .pytest_cache/ .tox/ build/ src/eafpy.egg-info/ __pycache__/
	$(MAKE) -C doc clean

