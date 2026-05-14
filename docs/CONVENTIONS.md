# Conventions

Human-readable patterns for developing the Claude YouTube skill.

## Project Structure

```
skills/claude-youtube/
  SKILL.md              # Orchestrator only. Routes, gathers context, loads templates.
  sub-skills/           # One file per command. Contains step-by-step instructions.
  references/           # Knowledge bases loaded on demand by sub-skills.
  templates/            # Channel-type templates (education, entertainment, etc.).
  execution/            # Python scripts for YouTube API integration.
    utils/              # Shared auth and quota utilities.
```

## Naming

- **Directories:** kebab-case (`sub-skills/`, `execution/`)
- **Files:** kebab-case (`fetch-channel-data.py` would be ideal; existing files use snake_case for Python)
- **Python functions:** snake_case
- **Constants:** UPPER_SNAKE_CASE

## Markdown Style

- Use ATX headers (`#`) only, no setext
- Keep reference files under 200 lines
- Keep sub-skills under 300 lines
- Keep SKILL.md under 500 lines
- Use tables for structured data (benchmarks, commands)
- Use code blocks with language tags

## Python Style

- Target Python 3.8+
- Use type annotations on all public functions
- Use `from __future__ import annotations` for forward compatibility
- Use `pathlib.Path` over `os.path`
- Return errors as JSON to stderr; never raise unhandled exceptions to the CLI user
- Docstrings for every module, script, and public function
- Use f-strings for formatting
- Prefer `dict.get()` with defaults over `KeyError` handling

## Error Handling

- Python scripts must be CLI-friendly: print JSON to stdout on success, JSON to stderr on error, exit with non-zero code
- Never expose raw API keys or tokens in output
- Graceful degradation: if yt-dlp is missing, return instructions; if API key missing, return setup steps

## Testing

- Unit tests for `execution/utils/` (pure logic, no API calls)
- Mock external API calls in tests
- Use `tmp_path` pytest fixture for filesystem tests
- Minimum coverage target: 80% for `execution/utils/`

## Git Workflow

- Conventional commits: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Scope examples: `skill`, `script`, `seo`, `audit`
- Branch naming: `feat/short-description`, `fix/issue-description`
