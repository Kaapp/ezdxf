# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

BUILD_OPTIONS = setup.py build_ext -i
ACC = src/ezdxf/acc

PYTHON39 = py -3.9
PYTHON38 = py -3.8
PYTHON37 = py -3.7

# Don't use the Cython extensions with pypy3 - it is much slower than the
# JIT compiled pure Python code.

.PHONY: build

build:
	$(PYTHON38) $(BUILD_OPTIONS)

test0: build
	$(PYTHON38) -m pytest tests

test1: test0
	$(PYTHON38) -m pytest integration_tests

all:
	$(PYTHON37) $(BUILD_OPTIONS)
	$(PYTHON38) $(BUILD_OPTIONS)
	$(PYTHON39) $(BUILD_OPTIONS)

clean:
	rm -f $(ACC)/*.pyd
	rm -f $(ACC)/*.html
# Autogenerated C source files
	rm -f $(ACC)/vector.c
	rm -f $(ACC)/matrix44.c
	rm -f $(ACC)/bezier4p.c

packages:
	$(PYTHON37) setup.py bdist_wheel
	$(PYTHON38) setup.py bdist_wheel
	$(PYTHON39) setup.py bdist_wheel
	$(PYTHON38) setup.py sdist --formats=zip
