.DEFAULT_GOAL := help
.PHONY: help new-skill validate sync sync-check check list package

PYTHON ?= python3

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  Example: make new-skill NAME=somnio-skill-creator DESC=\"Creates new Somnio skills.\""

new-skill: ## Scaffold a new skill (NAME=<skill-name> [DESC="..."])
ifndef NAME
	$(error NAME is required — e.g. make new-skill NAME=somnio-skill-creator)
endif
	@./scripts/new-skill.sh "$(NAME)" $(if $(DESC),"$(DESC)",)

validate: ## Validate frontmatter, naming and plugin symlinks
	@$(PYTHON) scripts/validate-skills.py

sync: ## Regenerate the README skills table
	@$(PYTHON) scripts/sync-readme.py

sync-check: ## Fail if the README skills table is out of date
	@$(PYTHON) scripts/sync-readme.py --check

check: validate sync-check ## Everything CI runs

list: ## List the skills in this repository
	@$(PYTHON) -c "from pathlib import Path; import sys; sys.path.insert(0, 'scripts'); \
	from skill_index import load_skills; \
	[print(f'{s.path.name:<32} {s.description[:80]}') for s in load_skills()]"

package: check ## Build plugins/somnio-ai-solutions.zip for Claude Desktop
	@./scripts/package-plugin.sh
