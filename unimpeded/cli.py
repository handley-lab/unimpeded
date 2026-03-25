"""Command-line interface for unimpeded."""

import os
import subprocess
import sys

import requests

TUTORIAL_URL = (
    "https://raw.githubusercontent.com/handley-lab/unimpeded"
    "/master/unimpeded_tutorial.ipynb"
)

FILENAME = "unimpeded_tutorial.ipynb"


def download_unimpeded_tutorial():
    """Download the unimpeded tutorial notebook to the current directory."""
    if os.path.exists(FILENAME):
        print(f"'{FILENAME}' already exists in the current directory.")
        response = input("Overwrite? [y/N] ").strip().lower()
        if response != "y":
            print("Aborted.")
            return

    print(f"Downloading {FILENAME}...")
    try:
        r = requests.get(TUTORIAL_URL)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading tutorial: {e}")
        sys.exit(1)

    with open(FILENAME, "wb") as f:
        f.write(r.content)

    print(f"Saved to ./{FILENAME}")


def launch_unimpeded_tutorial():
    """Launch the tutorial notebook in the browser."""
    if not os.path.exists(FILENAME):
        print(
            f"'{FILENAME}' not found in the current directory.\n"
            "Download it first with:\n"
            "  download-unimpeded-tutorial"
        )
        sys.exit(1)

    try:
        subprocess.run(["jupyter", "notebook", FILENAME])
    except FileNotFoundError:
        print(
            "\njupyter is not installed. Install it with:\n"
            "  pip install jupyter\n"
            f"\nThen run:\n"
            f"  jupyter notebook {FILENAME}"
        )
        sys.exit(1)
