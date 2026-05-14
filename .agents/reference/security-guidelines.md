# Security Guidelines

## Credential Handling

- Store credentials only in `~/.claude/` (already gitignored)
- Never hardcode API keys, even in test files
- Use `os.environ.get()` or config file fallback, never bare strings
- Mask keys in all output and logs

## Input Validation

- Validate all channel IDs, video IDs, and handles with regex
- Sanitize file paths to prevent traversal
- Reject unknown URL formats with clear error messages

## Dependency Security

- Run `make security-audit` before releases
- Pin minimum versions in `requirements.txt`
- Review `pip-audit` findings before dismissing

## Data Privacy

- Analytics data is private; never cache competitor analytics
- Transcripts may contain PII; don't persist beyond cache TTL
