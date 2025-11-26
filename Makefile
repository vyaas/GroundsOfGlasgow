# Check for virtual environment activation script
VENV_ACTIVATE := $(shell \
    for d in env .env .venv; do \
        if [ -f $$d/bin/activate ]; then \
            echo "$$d/bin/activate"; \
            break; \
        fi; \
    done \
)

.PHONY: install

deps:
ifeq ($(VENV_ACTIVATE),)
	@echo "Error: No virtual environment found. Please create one named 'env' or '.env'."
	@exit 1
else
	@echo "Using virtual environment from $(shell dirname $(VENV_ACTIVATE))"
	. $(VENV_ACTIVATE); uv pip install -r requirements.txt
endif
