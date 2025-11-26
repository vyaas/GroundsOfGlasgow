# Check for virtual environment activation script
VENV_ACTIVATE := $(shell if [ -f env/bin/activate ]; then echo "env/bin/activate"; elif [ -f .env/bin/activate ]; then echo ".env/bin/activate"; fi)

.PHONY: install

deps:
ifeq ($(VENV_ACTIVATE),)
	@echo "Error: No virtual environment found. Please create one named 'env' or '.env'."
	@exit 1
else
	@echo "Using virtual environment from $(shell dirname $(VENV_ACTIVATE))"
	. $(VENV_ACTIVATE); uv pip install -r requirements.txt
endif
