.PHONY: install run build clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install py2app
	@echo ""
	@echo "✅  Done. Place your credentials.json in ~/.motesmochi/ then run: make run"

run:
	$(PYTHON) app.py

build:
	$(PYTHON) setup.py py2app
	@echo ""
	@echo "✅  Built: dist/MötesMochi.app"
	@echo "    Drag it to /Applications or double-click to launch."

clean:
	rm -rf build dist __pycache__ *.pyc
