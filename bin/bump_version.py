#!/usr/bin/env python
import sys

from packaging import version
from utils import run

vfile = "unimpeded/_version.py"
README = "README.rst"

current_version = run("cat", vfile)
current_version = current_version.split("=")[-1].strip().strip('"')
current_version = version.parse(current_version)

if len(sys.argv) > 1:
    update_type = sys.argv[1]
else:
    update_type = "micro"

major = current_version.major
minor = current_version.minor
micro = current_version.micro

if update_type == "micro":
    micro += 1
elif update_type == "minor":
    minor += 1
    micro = 0
elif update_type == "major":
    major += 1
    minor = 0
    micro = 0

new_version = version.parse(f"{major}.{minor}.{micro}")

sed_string = f"s/{current_version}/{new_version}/g".replace(".", "\.")

for f in [vfile, README]:
    run("sed", "-i", sed_string, f)

run("git", "add", vfile, README)
run("git", "commit", "-m", f"bump version to {new_version}")
