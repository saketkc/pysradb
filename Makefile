.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

# Use python3 if a bare `python` isn't on PATH (macOS ships only python3).
PYTHON ?= $(shell command -v python || command -v python3)

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := $(PYTHON) -c "$$BROWSER_PYSCRIPT"

help:
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -path ./.venv\* -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . -path ./.venv\* -prune -o -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 pysradb tests

test: ## run tests quickly with the default Python
	pytest -s -v tests

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source pysradb -m pytest
	coverage report -m
	coverage html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/pysradb.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ pysradb
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

servedocs: docs ## compile the docs watching for changes
	#watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .
	watchmedo shell-command -p '*.md|*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	$(PYTHON) -m build
	twine upload dist/*

dist: clean ## builds source and wheel package
	$(PYTHON) -m build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	@if command -v uv >/dev/null 2>&1; then uv pip install -e .; else $(PYTHON) -m pip install -e .; fi
