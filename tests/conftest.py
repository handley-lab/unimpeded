"""Test configuration and fixtures for unimpeded tests."""

import re

import pytest


def strip_csv_response_body(response):
    """Strip large CSV response bodies to only keep first 1000 lines."""
    # Check if response has a body
    if "body" not in response or "string" not in response["body"]:
        return response

    body = response["body"]["string"]

    # Decode if bytes
    if isinstance(body, bytes):
        body = body.decode("utf-8")

    # Check if body looks like CSV data (has commas and multiple lines)
    # and is large (> 1MB)
    if len(body) > 1_000_000 and "," in body and "\n" in body:
        # Keep only first 1000 lines to reduce size
        lines = body.split("\n")
        if len(lines) > 1000:
            lines = lines[:1000]
            lines.append("# ... (truncated for testing)")
            response["body"]["string"] = "\n".join(lines).encode("utf-8")

    return response


@pytest.fixture(scope="session")
def vcr_config():
    """VCR configuration for recording HTTP interactions with Zenodo API."""
    return {
        # Recording behavior - only use existing cassettes
        "record_mode": "none",
        "decode_compressed_response": True,
        # Matching criteria for requests (exclude query to match regardless of token)
        "match_on": ["method", "scheme", "host", "port", "path"],
        # Serialization
        "serializer": "yaml",
        # Never write credentials into a cassette. Zenodo takes the token as a
        # query parameter, so it lands in the recorded URI unless filtered here;
        # ``filter_headers`` covers the ``Authorization`` form as well as the
        # session cookies Zenodo sets. Because ``match_on`` deliberately omits
        # the query string, replacing the value cannot break cassette matching.
        "filter_query_parameters": [("access_token", "FILTERED_TOKEN")],
        "filter_headers": [
            ("authorization", "FILTERED_TOKEN"),
            ("cookie", "FILTERED_COOKIE"),
            ("set-cookie", "FILTERED_COOKIE"),
        ],
        # Strip large CSV bodies and scrub tokens out of response bodies
        "before_record_response": sanitize_response,
        # Use flat cassette directory structure
        "cassette_library_dir": "tests/cassettes",
    }


def sanitize_response(response):
    """Strip large CSV bodies and scrub any token out of a recorded response.

    Wired into ``vcr_config`` as ``before_record_response``. The request side is
    handled by ``filter_query_parameters`` / ``filter_headers``, which are
    applied by vcrpy itself and cannot be bypassed the way a hand-written hook
    can if it is left unregistered.
    """
    response = strip_csv_response_body(response)

    if "body" not in response or "string" not in response["body"]:
        return response

    body_str = response["body"]["string"]
    was_bytes = isinstance(body_str, bytes)
    if was_bytes:
        body_str = body_str.decode("utf-8", errors="replace")

    if "access_token" in body_str:
        body_str = re.sub(
            r'"access_token"\s*:\s*"[^"]*"',
            '"access_token": "FILTERED_TOKEN"',
            body_str,
        )
        body_str = re.sub(
            r"access_token=[^&\"'\s]+",
            "access_token=FILTERED_TOKEN",
            body_str,
        )
        response["body"]["string"] = body_str.encode("utf-8") if was_bytes else body_str

    return response


@pytest.fixture
def zenodo_access_token():
    """Provide a placeholder Zenodo access token for tests.

    Deliberately never reads a real credential from the environment. Every
    authenticated interaction is replayed from a cassette, so a live token buys
    nothing -- and supplying one is what previously caused it to be recorded
    into ``TestDatabaseCreator.test_create_deposit.yaml`` and committed.
    """
    return "fake-token-for-tests"


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing file uploads."""
    return """# Sample cosmological parameter chain
# columns: omegab, omegac, h, logA, ns, tau
0.02242,0.11965,0.67556,3.0448,0.9649,0.0543
0.02238,0.11933,0.67712,3.0441,0.9652,0.0541
0.02245,0.11998,0.67423,3.0455,0.9646,0.0545
"""


@pytest.fixture
def sample_yaml_info():
    """Sample YAML info data for testing."""
    return {
        "analysis": {"log_evidence": -1234.56, "log_evidence_err": 0.12},
        "sampler": "PolyChord",
        "model": "lcdm",
        "dataset": "planck_2018_plik",
    }


@pytest.fixture
def sample_prior_info():
    """Sample prior info for nested sampling."""
    return """# Prior information for nested sampling
omegab [0.005, 0.1]
omegac [0.001, 0.99]
h [0.2, 1.0]
logA [1.61, 3.91]
ns [0.8, 1.2]
tau [0.01, 0.8]
"""


@pytest.fixture
def temp_data_files(tmp_path, sample_csv_data, sample_yaml_info, sample_prior_info):
    """Create temporary data files for testing file operations."""
    import yaml

    # Create sample files
    csv_file = tmp_path / "samples.csv"
    yaml_file = tmp_path / "info.yaml"
    prior_file = tmp_path / "prior_info.txt"

    csv_file.write_text(sample_csv_data)
    yaml_file.write_text(yaml.dump(sample_yaml_info))
    prior_file.write_text(sample_prior_info)

    return {
        "csv": str(csv_file),
        "yaml": str(yaml_file),
        "prior": str(prior_file),
        "dir": str(tmp_path),
    }
