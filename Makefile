INSTALL_PATH ?= ~/.local/bin
SCRIPT := main.py
SCRIPT_TARGET := waybar-autohide


DEV_DEPENDENCIES := \
	ruff


# Check if all required binaries are installed when the Makefile is loaded

check_dev_dependencies:
	$(foreach bin,$(DEV_DEPENDENCIES),\
	  $(if $(shell command -v $(bin) 2> /dev/null),,$(error Please install `$(bin)`)))


setup-dev: check_dev_dependencies
	@echo "Syncing dependencies with uv"
	@uv sync --active --script ${SCRIPT}


lint: check_dev_dependencies
	@echo "Linting ${SCRIPT} with ruff"
	@ruff check --config ruff.toml --fix ${SCRIPT}


format: check_dev_dependencies
	@echo "Formatting ${SCRIPT} with ruff"
	@ruff format --config ruff.toml ${SCRIPT}


install:
	@echo "Installing ${SCRIPT} to ${INSTALL_PATH}" as ${SCRIPT_TARGET}
	@install -m 755 ${SCRIPT} ${INSTALL_PATH}/${SCRIPT_TARGET}


.PHONY: setup-dev lint format install check_dev_dependencies