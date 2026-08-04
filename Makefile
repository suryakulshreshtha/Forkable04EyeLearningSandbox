.PHONY: help install test smoke api ui parallel headed debug trace lint format check clean
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies and browsers
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt
	python -m playwright install --with-deps chromium

test:     ## Run every example
	pytest -m "not wip"
smoke:    ## The stable subset CI gates on
	pytest -m smoke
api:      ## API examples only, no browser
	pytest -m api
ui:       ## Browser examples only
	pytest -m ui
parallel: ## One worker per core
	pytest -m "not wip" -n auto
headed:   ## Watch the browser work
	pytest -m smoke --headed --slowmo 500
debug:    ## Playwright Inspector
	PWDEBUG=1 pytest -m smoke --headed -s
trace:    ## Open the newest trace
	python -m playwright show-trace $$(ls -t reports/test-results/**/trace.zip | head -1)
lint:     ## Ruff + black, same as CI
	ruff check .
	black --check .
format:   ## Autofix
	ruff check --fix .
	black .
check: lint  ## Lint + import every test without running it
	pytest --collect-only -q
clean:    ## Remove artifacts
	rm -rf reports .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
