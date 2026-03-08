APP_NAME=yui
ENTRY=app.py

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
NUITKA=$(PYTHON) -m nuitka

# Setup venv + install nuitka
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install nuitka

# Build executable
build: setup
	$(NUITKA) \
	--onefile \
	--output-filename=$(APP_NAME) \
	$(ENTRY)

# Clean semua
clean:
	rm -rf $(VENV) $(APP_NAME) *.build *.dist *.onefile-build
