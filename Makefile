# Thin entry points to the harness. The harness itself lives in the skills:
#   skills/somnio-skill-creator   — creates skills
#   skills/somnio-skill-verifier  — validates them
# Ask Claude Code for those skills instead of driving them by hand when you can.

.DEFAULT_GOAL := help
.PHONY: help validate fix sync sync-check check zip

PYTHON ?= python3
PLUGIN_NAME := somnio-ai-solutions
VALIDATOR := skills/somnio-skill-verifier/scripts/validate_skills.py
SYNC_README := skills/somnio-skill-creator/scripts/sync_readme.py

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  To create a skill, ask Claude Code for the somnio-skill-creator skill."

validate: ## Validate every skill (what CI runs on pull requests)
	@$(PYTHON) $(VALIDATOR)

fix: ## Recreate missing plugin symlinks and drop orphans
	@$(PYTHON) $(VALIDATOR) --fix

sync: ## Regenerate the README skills table
	@$(PYTHON) $(SYNC_README)

sync-check: ## Fail if the README skills table is out of date
	@$(PYTHON) $(SYNC_README) --check

check: validate sync-check ## Everything CI checks on a pull request

zip: check ## Build the plugin archive locally (CI does this automatically on main)
	@cd plugins && rm -f $(PLUGIN_NAME).zip && zip -r $(PLUGIN_NAME).zip $(PLUGIN_NAME)/ \
		--exclude "*.DS_Store" \
		--exclude "*/.venv/*" \
		--exclude "*/.ruff_cache/*" \
		--exclude "*/__pycache__/*" \
		--exclude "*/.git/*"
	@echo "Built plugins/$(PLUGIN_NAME).zip — do not commit it, CI rebuilds it on merge."
