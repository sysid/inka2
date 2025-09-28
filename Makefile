.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory

# You can set these variables from the command line, and also from the environment for the first two.
BUILDDIR      = build
MAKE          = make
VERSION       = $(shell cat VERSION)
IMAGE_NAME = inka2
PACKAGE_NAME  = inka2

app_root := $(if $(PROJ_DIR),$(PROJ_DIR),$(CURDIR))
pkg_src  = $(app_root)/src/$(PACKAGE_NAME)
tests_src = $(app_root)/tests

.PHONY: all
all: clean build install-edit  ## Build and install-local
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"


################################################################################
# Developing \
DEVELOP: ## ############################################################
.PHONY: init
init:  ## init
	-pkill anki
	@rm -f *.db
	rm -fr "$(HOME)/Library/Application Support/Anki2/User 1"
	rm -fr './tests/resources/anki_data/User 1'
	rm -fr ~/xxx
	mkdir -p ~/xxx
	@cp -v tests/resources/test_inka_data_init.md tests/resources/test_inka_data.md
	@cp -v tests/resources/math_example_init.md tests/resources/math_example.md
	@cp -v tests/resources/math_example2_init.md tests/resources/math_example2.md
	@cp -v ./src/inka2/config.ini.original ./src/inka2/config.ini
	@echo "Using default configuration!"

.PHONY: anki
anki:  ## anki
	pkill anki
	# specify base folder with -b
	open /Applications/Anki.app --args -b $(PROJ_DIR)/tests/resources/anki_data

.PHONY: test-unit
test-unit:  ## run all tests except "integration" marked
	RUN_ENV=local python -m pytest -m "not (integration or e2e)" --cov-config=pyproject.toml --cov-report=html --cov-report=xml --cov-report=term --cov=$(pkg_src) $(tests_src)

.PHONY: test
test: init  test-unit  ## run all tests

.PHONY: test-cicd
test-cicd: test-unit  ## run cicd tsts

.PHONY: test_interactive_create_notes_from_files
test_interactive_create_notes_from_files: init   ## test_interactive_create_notes_from_files: expect Anki to show one rendered card
	RUN_ENV=local python -m pytest -s tests/test_cli.py::test_interactive_create_notes_from_files --no-summary


################################################################################
# Building, Deploying \
BUILDING:  ## ############################################################
.PHONY: publish
publish:  ## publish
	@echo "upload to Pypi"
	twine upload --verbose dist/*

.PHONY: build
build:  ## build
	#pdm build  # did not work?
	python -m build

.PHONY: install
install:  uninstall ## install
	uv tool install inka2
	@cp -vf $(HOME)/dev/s/private/other-anki/inka/config.tw.ini $(HOME)/.local/pipx/venvs/inka2/lib/python3.12/site-packages/inka2/config.ini

.PHONY: install-edit
install-edit: uninstall  ## pipx install-edit
	uv tool install -e .
	#pipx install -e .
	@cp -vf $(HOME)/dev/s/private/other-anki/inka/config.tw.ini ./src/inka2/config.ini  # get the prod config into editable install

.PHONY: uninstall
uninstall:  ## uninstall
	-pipx uninstall inka2
	-uv tool uninstall inka2

.PHONY: bump-minor
bump-minor: check-github-token  ## bump-minor, tag and push
	bump-my-version bump --commit --tag minor
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: bump-patch
bump-patch: check-github-token  ## bump-patch, tag and push
	bump-my-version bump --commit --tag patch
	git push
	git push --tags
	@$(MAKE) create-release

.PHONY: create-release
create-release: check-github-token  ## create a release on GitHub via the gh cli
	@if ! command -v gh &>/dev/null; then \
		echo "You do not have the GitHub CLI (gh) installed. Please create the release manually."; \
		exit 1; \
	else \
		echo "Creating GitHub release for v$(VERSION)"; \
		gh release create "v$(VERSION)" --generate-notes; \
	fi

.PHONY: check-github-token
check-github-token:  ## Check if GITHUB_TOKEN is set
	@if [ -z "$$GITHUB_TOKEN" ]; then \
		echo "GITHUB_TOKEN is not set. Please export your GitHub token before running this command."; \
		exit 1; \
	fi
	@echo "GITHUB_TOKEN is set"

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
	isort $(pkg_src) $(tests_src) --profile black

.PHONY: style
style: sort-imports format  ## perform code style format (black, isort)

.PHONY: lint
lint:  ## check style with ruff
	@ruff check $(pkg_src) $(tests_src)

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
