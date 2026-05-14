# API Conventions

Rules for YouTube API integration in `skills/claude-youtube/execution/`.

## Quota Discipline

- Every API call must record quota consumption via `consume_quota()`
- Prefer cheaper endpoints: `playlistItems.list` (1 unit) over `search.list` (100 units)
- Cache aggressively; default cache TTL is 1 day
- Warn users when quota usage exceeds 80%

## Auth Patterns

- API key auth for public data (channel info, public videos)
- OAuth 2.0 for private analytics (only own channel)
- Never log or print raw credentials
- Mask API keys in status output: `ABCD...WXYZ`

## Error Handling

- Return `{"error": "...", "fix": "..."}` as JSON to stderr
- Distinguish between: missing dependency, missing credentials, API error, quota exceeded
- Always suggest the fix path (e.g., `pip install ...`, env var name)
