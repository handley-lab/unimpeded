"""Test configuration and fixtures for unimpeded tests."""

import os

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
        # Strip large CSV bodies before recording
        "before_record_response": strip_csv_response_body,
    }


def sanitize_response(response):
    """Remove or replace sensitive data in recorded responses."""
    # Convert response body to string if it's bytes
    if hasattr(response["body"], "string"):
        body_str = response["body"]["string"]
        if isinstance(body_str, bytes):
            body_str = body_str.decode("utf-8")

        # Replace any access tokens in response bodies
        if "access_token" in body_str:
            import re

            body_str = re.sub(
                r'"access_token"\s*:\s*"[^"]*"',
                '"access_token": "FILTERED_TOKEN"',
                body_str,
            )
            response["body"]["string"] = body_str.encode("utf-8")

    return response


def sanitize_request(request):
    """Remove or replace sensitive data in recorded requests."""
    # Filter out access_token from query parameters in the recorded cassette
    if hasattr(request, "query") and request.query:
        filtered_query = []
        for item in request.query:
            if item[0] != "access_token":
                filtered_query.append(item)
            else:
                filtered_query.append(("access_token", "FILTERED_TOKEN"))
        request.query = filtered_query
    return request


@pytest.fixture
def zenodo_access_token():
    """Provide Zenodo access token for tests."""
    return os.environ.get("ACCESS_TOKEN_ZENODO_HPC_OFFICIAL", "fake-token-for-tests")


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
