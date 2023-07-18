.PHONY : install build test doc

install: build
	python3 -m pip install -e .

build:
	python3 -m build

test:
	tox

doc:
	$(MAKE) -C doc html
