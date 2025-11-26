# Detect virtual environment
VENV_DIR := $(shell for d in env .env .venv; do \
    if [ -d $$d ]; then echo $$d; break; fi; \
done)
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
VENV_TIMESTAMP := $(VENV_DIR)/.last_freeze

.PHONY: freeze deps

# requirements.txt depends on the timestamp
requirements.txt: $(VENV_TIMESTAMP)
	@echo "Freezing dependencies..."
	. $(VENV_ACTIVATE); uv pip freeze > requirements.txt

# Update the timestamp after installing packages
$(VENV_TIMESTAMP): $(VENV_ACTIVATE)
	@echo "Updating virtualenv timestamp..."
	@touch $(VENV_TIMESTAMP)

deps:
ifeq ($(VENV_DIR),)
	@echo "Error: No virtual environment found. Please create one named 'env', '.env', or '.venv'."
	@exit 1
else
	@echo "Using virtual environment from $(VENV_DIR)"
	. $(VENV_ACTIVATE); uv pip install -r requirements.txt
	@touch $(VENV_TIMESTAMP)
endif

freeze: requirements.txt
	@echo "requirements.txt is up-to-date."

