.DEFAULT_GOAL := help

# You can set these variables from the command line, and also from the environment for the first two.
PREFIX ?= /usr/local
BINPREFIX ?= "$(PREFIX)/bin"

VERSION       = $(shell cat VERSION)

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
#MAKEFLAGS += --no-print-directory

MAKEFILE_PWD := $(CURDIR)
WORKTREE_ROOT := $(shell git rev-parse --show-toplevel 2> /dev/null)

app_root ?= .
pkg_src =  $(app_root)/src
tests_src = $(app_root)/tests

# define files
MANS = $(wildcard ./*.md)
MAN_HTML = $(MANS:.md=.html)
MAN_PAGES = $(MANS:.md=.1)
# avoid circular targets
MAN_BINS = $(filter-out ./tw-extras.md, $(MANS))

################################################################################
# Admin \
ADMIN::  ## ####################################################################

.PHONY: dummy
dummy:  ## dummy
	:

################################################################################
# Building, Deploying \
BUILDING:  ## ##################################################################
.PHONY: build
build: clean format isort  ## format and build
	@echo "building"
	python -m build

.PHONY: upload
upload:  ## upload to PyPi
	@echo "upload"
	twine upload --verbose dist/*

.PHONY: bump-major
bump-major:  ## bump-major, tag and push
	bumpversion --commit --tag major
	git push --tags

.PHONY: bump-minor
bump-minor:  ## bump-minor, tag and push
	bumpversion --commit --tag minor
	git push --tags

.PHONY: bump-patch
bump-patch:  ## bump-patch, tag and push
	bumpversion --commit --tag patch
	git push --tags

################################################################################
# Testing \
TESTING:  ## ###################################################################
.PHONY: coverage
coverage:  ## Run tests with coverage
	python -m coverage erase
	python -m coverage run --include=$(pkg_src)/* -m pytest -ra
	python -m coverage report -m

.PHONY: test
test:  ## run tests
	PYTHONPATH=src python -m pytest -ra --junitxml=report.xml --cov-config=setup.cfg --cov-report=xml --cov-report term --cov=$(pkg_src) tests/

.PHONY: tox
tox:   ## Run tox
	tox

################################################################################
# Code Quality \
QUALITY:  ## ###################################################################
.PHONY: style
style: isort format  ## perform code style format (black, isort)

.PHONY: format
format:  ## perform black formatting
	black $(pkg_src) tests

.PHONY: isort
isort:  ## apply import sort ordering
	isort . --profile black

.PHONY: lint
lint: flake8 mypy ## lint code with all static code checks

.PHONY: flake8
flake8:  ## check style with flake8
	@flake8 $(pkg_src)

.PHONY: mypy
mypy:  ## check type hint annotations
	# keep config in setup.cfg for integration with PyCharm
	mypy --config-file setup.cfg $(pkg_src)

################################################################################
# Clean \
CLEAN:  ## #####################################################################

.PHONY: clean
clean:  ## clean
	@echo "Cleaning

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


################################################################################
# Misc \
MISC:  ## ######################################################################

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([%a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		if target != "dummy":
			print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

debug:  ## debug
	@echo "-D- CODE_DIR: $(CODE_DIR)"


.PHONY: list
list: *  ## list
	@echo $^

.PHONY: list2
%: %.md  ## list2
	@echo $^


%-plan:  ## call with: make <whatever>-plan
	@echo $@ : $*
	@echo $@ : $^
