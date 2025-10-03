.PHONY: build-locally check-code
build-locally:
	uv sync

ruff:
	uv run ruff check . --fix

ruff-unsafe-fixes:
	uv run ruff check . --fix --unsafe-fixes

ruff-format:
	uv run ruff format .

ruff-format-check:
	uv run ruff format . --check

ruff-check:
	uv run ruff check .

check-mypy:
	uv run mypy --strict . --explicit-package-bases
