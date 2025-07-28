#!/usr/bin/env python3
"""Manual script to create VCR cassette"""
import os
from datetime import datetime

import yaml

from unimpeded.database import DatabaseCreator

# Create the actual API response
token = os.environ.get("ACCESS_TOKEN_ZENODO_HPC_OFFICIAL")
creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN=token)

print("Making real API call...")
deposit_id = creator.create_deposit()
print(f"Created deposit: {deposit_id}")

# Create VCR cassette manually
cassette_data = {
    "interactions": [
        {
            "request": {
                "method": "POST",
                "uri": "https://zenodo.org/api/deposit/depositions",
                "body": {"string": "{}", "encoding": "utf-8"},
                "headers": {
                    "Content-Type": ["application/json"],
                    "User-Agent": ["python-requests/2.32.3"],
                },
            },
            "response": {
                "status": {"code": 201, "message": "CREATED"},
                "headers": {"Content-Type": ["application/json"], "Server": ["nginx"]},
                "body": {
                    "string": f'{{"id": {deposit_id}, "created": "{datetime.utcnow().isoformat()}Z", "state": "unsubmitted"}}',
                    "encoding": "utf-8",
                },
            },
        }
    ],
    "version": 1,
}

# Ensure directory exists
os.makedirs("tests/cassettes/test_database", exist_ok=True)

# Write cassette
with open(
    "tests/cassettes/test_database/TestDatabaseCreator.test_create_deposit.yaml", "w"
) as f:
    yaml.dump(cassette_data, f, default_flow_style=False)

print("Cassette created successfully!")
