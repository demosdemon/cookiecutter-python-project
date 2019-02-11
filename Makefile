export PYTHON_VERSION ?= 3.7
export VIRTUAL_ENV ?= $(CURDIR)/.venv

# ignore .venv and {{cookiecutter.project_slug}}
python_files := $(shell find $(CURDIR)/hooks $(CURDIR)/tests -type f -name '*.py')

.PHONY: all
all: help

.PHONY: help
help:
	@echo 'Usage: make <target>'
	@echo ''
	@echo 'Targets:'
	@echo '    format       - Format source files with an appropriate formatter.'
	@echo '    help         - Display this message and exit.'
	@echo '    install      - Install development requirements.'
	@echo '    tests        - Execute unit tests.'
	@echo '    venv         - Create the python virtual environment using python $(PYTHON_VERSION).'
	@echo ''
	@echo 'Variables:'
	@echo '    CURDIR         = $(CURDIR)'
	@echo '    PYTHON_VERSION = $(PYTHON_VERSION)'
	@echo '    VIRTUAL_ENV    = $(VIRTUAL_ENV)'

.PHONY: format
format:
	$(VIRTUAL_ENV)/bin/black $(python_files)
	$(VIRTUAL_ENV)/bin/isort $(python_files)

.PHONY: install
install: requirements-dev.txt requirements-test.txt requirements.txt | $(VIRTUAL_ENV)
	pip install -r $<

.PHONY: tests
tests:
	$(VIRTUAL_ENV)/bin/pytest

.PHONY: venv
venv: $(VIRTUAL_ENV)

$(VIRTUAL_ENV): requirements.txt requirements-dev.txt requirements-test.txt
	virtualenv --clear --python python$(PYTHON_VERSION) $(VIRTUAL_ENV)
	@ln -sf python$(PYTHON_VERSION) $(VIRTUAL_ENV)/bin/python
	@touch $@

$(VIRTUAL_ENV)/bin/pip-compile $(VIRTUAL_ENV)/bin/pip-sync: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install -U pip-tools
	@touch $@
