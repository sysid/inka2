.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory

# You can set these variables from the command line, and also from the environment for the first two.
BUILDDIR      = build
MAKE          = make
VERSION       = $(shell cat VERSION)
IMAGE_NAME = inka

app_root = $(PROJ_DIR)
app_root ?= .
pkg_src =  $(app_root)/src/inka
tests_src = $(app_root)/tests

################################################################################
# Developing \
DEVELOP: ## ############################################################

.PHONY: update
update:  ## update
	python src/inka/main.py

.PHONY: create
create: init  ## create
	python src/inka/main.py

.PHONY: init
init:  ## init
	pkill anki
	@rm -f *.db
	@rm -fr '/Users/Q187392/Library/Application Support/Anki2/User 1'
	@rm -fr './tests/resources/anki_data/User 1'
	rm -fr ~/xxx
	mkdir -p ~/xxx

.PHONY: anki
anki:  ## anki
	pkill anki
	open /Applications/Anki.app --args -b $(PROJ_DIR)/tests/resources/anki_data

.PHONY: query-experiment
query-experiment:  ## query-experiment
	@sqlite-utils query test_daily.db "\
	SELECT \
	    document.*, \
	    general.*, \
	    meeting.* \
	FROM document \
	LEFT JOIN general ON document.name = general.document_name \
	LEFT JOIN list ON document.name = list.document_name \
	LEFT JOIN meeting ON document.name = meeting.document_name;" | jq

.PHONY: schema
schema:  ## schema
	@sqlite-utils schema test_daily.db

.PHONY: test
test: init  ## run all tests
	RUN_ENV=testing python -m pytest --cov-report=xml --cov-report term --cov=$(pkg_src) $(tests_src)


################################################################################
# Building, Deploying \
BUILDING:  ## ############################################################

.PHONY: install
install:  ## install
	pipx install -e .

.PHONY: uninstall
uninstall:  ## uninstall
	pipx uninstall inka

.PHONY: bump-major
bump-major:  ## bump-major, tag and push
	bump-my-version bump --commit --tag major
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: bump-minor
bump-minor:  ## bump-minor, tag and push
	bump-my-version bump --commit --tag minor
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: bump-patch
bump-patch:  ## bump-patch, tag and push
	bump-my-version bump --commit --tag patch
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: create-release
create-release:  ## create a release on GitHub via the gh cli
	@if command -v gh version &>/dev/null; then \
		echo "Creating GitHub release for v$(VERSION)"; \
		gh release create "v$(VERSION)" --generate-notes; \
	else \
		echo "You do not have the github-cli installed. Please create release from the repo manually."; \
		exit 1; \
	fi


################################################################################
# Code Quality \
QUALITY:  ## ############################################################

.PHONY: format
format:  ## perform ruff formatting
	@ruff format $(pkg_src) $(tests_src)

.PHONY: format-check
format-check:  ## perform black formatting
	@ruff format --check $(pkg_src) $(tests_src)

.PHONY: sort-imports
sort-imports:  ## apply import sort ordering
	@isort $(pkg_src) $(tests_src) --profile black

.PHONY: style
style: sort-imports format  ## perform code style format (black, isort)

.PHONY: lint
lint:  ## check style with ruff
	@ruff $(pkg_src)

.PHONY: mypy
mypy:  ## check type hint annotations
	#@mypy --config-file pyproject.toml $(pkg_src)
	@mypy --config-file pyproject.toml --install-types --non-interactive $(pkg_src)


.PHONY: bandit
bandit:  ## bandit
	@bandit --skip B101 -r -lll $(pkg_src)
	@bandit --skip B101 -r -lll $(pkg_src) -f html -o bandit-report.html

################################################################################
# Clean \
CLEAN:  ## ############################################################

.PHONY: clean
clean: clean-build clean-pyc  ## remove all build, test, coverage and Python artifacts

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
MISC:  ## ############################################################
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
