# VCR Cassette Generation

This document explains how the VCR cassettes in `tests/cassettes/` were generated.

## What are VCR cassettes?

VCR cassettes are recordings of HTTP requests/responses that allow tests to run without making real API calls to Zenodo. They're created by the `pytest-vcr` plugin.

## How cassettes are generated

Cassettes are automatically generated when you run tests marked with `@pytest.mark.vcr` using the `--vcr-record=once` flag.

### Configuration

The VCR behavior is configured in `tests/conftest.py`:

- `vcr_config()` fixture: Sets recording mode, matching criteria, and cassette location
- `strip_csv_response_body()` function: Reduces cassette size by truncating large CSV responses to first 1000 lines

### Generating cassettes for database tests

```bash
# Activate your virtual environment first
source /path/to/venv/bin/activate

# Generate all database cassettes
pytest tests/test_database.py -v --vcr-record=once
```

This creates cassettes in `tests/cassettes/` for all tests marked with `@pytest.mark.vcr` in `test_database.py`.

### Generating cassettes for tension tests

```bash
# Activate your virtual environment first
source /path/to/venv/bin/activate

# Generate all tension cassettes
pytest tests/test_tension.py -v --vcr-record=once
```

This creates cassettes in `tests/cassettes/` for all tests marked with `@pytest.mark.vcr` in `test_tension.py`.

### Generating a specific cassette

To regenerate just one cassette:

```bash
pytest tests/test_database.py::TestDatabase::test_supported_models -v --vcr-record=once
```

## Important Notes

1. **VCR record modes:**
   - `none`: Only use existing cassettes (fails if missing) - used in CI
   - `once`: Record if cassette doesn't exist, otherwise use existing
   - `new_episodes`: Record new requests, keep existing ones
   - `all`: Re-record everything

2. **Cassette size reduction:**
   The `strip_csv_response_body()` function in `conftest.py` automatically reduces cassette sizes by:
   - Truncating CSV response bodies to first 1000 lines
   - Keeping files under GitHub's 100 MB limit
   - Original cassettes would be ~238 MB each, reduced to ~2.5 MB

3. **When to regenerate cassettes:**
   - When Zenodo API responses change
   - When adding new tests that make HTTP requests
   - When test behavior changes (different API calls)

4. **Requirements:**
   - Tests that download data need `ACCESS_TOKEN_ZENODO_HPC_OFFICIAL` environment variable set
   - Internet connection required during cassette generation
   - After generation, tests run offline using cassettes

## Testing with cassettes

Regular test runs (CI and local) use existing cassettes:

```bash
pytest tests/  # Uses cassettes, no internet needed
```

The `record_mode: "none"` in `vcr_config()` ensures tests fail if cassettes are missing rather than making real API calls.
