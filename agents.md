# Agent Guidelines

This file contains instructions and preferences for AI agents working on this repository.

## Environment and Package Management

- **Tool**: Use `uv` for all environment and package management tasks.
- **Running Scripts**: Use `uv run <script>` (e.g., `uv run python main.py`) to ensure the correct environment is used.
- **Adding Dependencies**: Use `uv add <package>` to add new dependencies to `pyproject.toml`.
- **Installing Dependencies**: Use `uv sync` to ensure the environment is up to date.