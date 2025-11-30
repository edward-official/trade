PYTHON      ?= python
VENV_DIR    ?= .venv
PIP         := $(VENV_DIR)/bin/pip
PYTHON_VENV := $(VENV_DIR)/bin/python

.PHONY: venv install run-ionq run-qqq run-tsla run-googl run-all

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run-ionq:
	$(PYTHON_VENV) -m backtest.runners.run_ionq

run-qqq:
	$(PYTHON_VENV) -m backtest.runners.run_qqq

run-tsla:
	$(PYTHON_VENV) -m backtest.runners.run_tsla

run-googl:
	$(PYTHON_VENV) -m backtest.runners.run_googl

run-all: run-ionq run-qqq run-tsla run-googl

