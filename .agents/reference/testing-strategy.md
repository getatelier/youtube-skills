# Testing Strategy

## Philosophy

- Unit tests for pure logic in `execution/utils/`
- Integration tests mock all external API calls
- No real network requests in tests

## Fixtures

- Use `tmp_path` for filesystem isolation
- Use `monkeypatch` for env vars and config paths
- Mock `googleapiclient.discovery.build` for API tests

## Coverage

- Target 80% for `execution/utils/`
- Target 60% for `execution/` scripts overall
- Exclude CLI boilerplate (`if __name__ == "__main__"`) from coverage where practical
