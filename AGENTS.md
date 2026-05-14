# Claude YouTube — Agent Context

## Project Overview

Claude Code skill for YouTube creators. 14 sub-skills, 9 reference guides, 9 channel templates, 6 Python execution scripts. Primary language: Markdown (skill definitions). Execution layer: Python 3.8+.

## Stack

- **Docs:** Markdown (SKILL.md orchestrator, sub-skills, references, templates)
- **Execution:** Python 3.8+ (YouTube Data API v3, Analytics API, yt-dlp)
- **Automation:** pre-commit, Make, pytest, ruff, mypy
- **Repo:** GitHub, MIT license

## Architecture

```
skills/claude-youtube/
  SKILL.md              # Orchestrator: routing, context-gathering, quality gates
  sub-skills/           # 14 command definitions (.md)
  references/           # 9 data-grounded knowledge guides (.md)
  templates/            # 9 channel-type templates (.md)
  execution/            # 6 Python scripts + utils/
```

### Rules

- SKILL.md is the single entry point; sub-skills are instruction files, not standalone skills.
- Reference files are loaded on demand by sub-skills; keep them focused (< 200 lines).
- Python scripts in `execution/` must have docstrings, CLI interface, and graceful error handling.
- All kebab-case naming for directories and files.

## Tooling Reference

| Command | What it does |
|---------|-------------|
| `make install` | Install Python deps + dev deps + pre-commit hooks |
| `make test` | Run pytest |
| `make lint` | Run ruff check |
| `make format` | Run ruff format |
| `make type-check` | Run mypy |
| `make security-audit` | Run bandit + pip-audit |
| `make check` | Run lint + type-check + test |
| `make clean` | Remove cache and build artifacts |

## AI Assistant Guardrails

### Forbidden

- Never add a new Python dependency without pinning it in `requirements.txt` and `requirements-dev.txt`
- Never disable linter, formatter, or type-checker rules to make code pass — fix the root cause
- Never write Python code without corresponding tests for utility functions
- Never modify generated files (lock files, migration files) by hand
- Never commit secrets, API keys, or `.env` files
- Never introduce new patterns/abstractions without checking existing ones first
- Never bloat SKILL.md beyond 500 lines; extract into sub-skills or references

### Mandatory

- Always run `make check` before claiming a task is complete
- Always update AGENTS.md if you change architectural patterns or tooling
- Always use factories/fixtures for test data, never hardcode domain values
- Always type-annotate public functions; dynamic typing is banned except at explicit boundaries (e.g., googleapiclient service objects typed as `Any`)
- Always prefer composition over inheritance
- Always keep functions small and focused; extract helpers rather than nesting logic
- Always ensure Python scripts fail gracefully with JSON error output to stderr

### Agentic Workflow Guardrails

- Always produce a PRD before writing code for any feature >1 day of work
- Always review the plan.md before implementation; never skip human validation
- Always run self-validation (make check) before declaring a task complete
- Always update `.agents/learnings.jsonl` after a bug or misalignment
- Never plan and implement in the same session; clear context between phases
- Use sub-agents for research; keep main context clean
- Load `.agents/reference/` docs only when working on the relevant task type

## Context Budget

- Keep AGENTS.md under 200 lines; detailed rules live in `.agents/reference/`
- Planning session: free-form conversation OK, but clear before implementing
- Sub-agents: use for any research consuming >50k tokens
- If context feels "full" (agent repeating itself, missing obvious things), clear and restart

## Decision Log

- **Python quality stack:** ruff (lint + format), mypy (strict mode), pytest, bandit, pip-audit — chosen for speed and Python 3.8+ compatibility.
- **No CI service:** All automation is local (Make, pre-commit). No GitHub Actions required.
- **CLAUDE.md preserved:** Retained as human-readable project overview. AGENTS.md is the authoritative agent context file.
- **Type annotations added progressively:** Execution scripts annotated; googleapiclient service objects use `Any` at boundaries.
