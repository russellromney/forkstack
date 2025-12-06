.PHONY: help envs-new envs-switch envs-delete envs-list

help:
	@echo "Fork Stack environment commands:"
	@echo ""
	@echo "  make envs-new <name>        Create new environment (e.g., make envs-new alice)"
	@echo "  make envs-switch <name>     Switch to environment (e.g., make envs-switch alice)"
	@echo "  make envs-delete <name>     Delete environment (e.g., make envs-delete alice)"
	@echo "  make envs-list              List all environments"
	@echo ""
	@echo "After switching environments, restart your app:"
	@echo "  make down && make up"
	@echo ""

envs-new:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make envs-new <env-name>"; \
		exit 1; \
	fi
	python envs.py create $(filter-out $@,$(MAKECMDGOALS))

envs-switch:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make envs-switch <env-name>"; \
		exit 1; \
	fi
	python envs.py switch $(filter-out $@,$(MAKECMDGOALS))

envs-delete:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make envs-delete <env-name>"; \
		exit 1; \
	fi
	python envs.py delete $(filter-out $@,$(MAKECMDGOALS))

envs-list:
	python envs.py list

# Prevent "no targets specified" errors when passing env names
%:
	@:
