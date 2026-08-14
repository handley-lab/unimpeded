"""Tests for the unimpeded command-line entry points."""

import importlib
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from unimpeded.cli import (
    FILENAME,
    download_unimpeded_tutorial,
    launch_unimpeded_tutorial,
)


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path, monkeypatch):
    """Run every test in an empty directory with a predictable argv.

    Both entry points read ``sys.argv`` directly and operate on the current
    working directory, so leaking either from the pytest process would make
    results depend on how the suite was invoked.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["unimpeded-cli"])
    return tmp_path


def _response(content=b'{"cells": []}'):
    """Build a stand-in for a successful requests response."""
    r = MagicMock()
    r.content = content
    r.raise_for_status = MagicMock()
    return r


class TestDownloadTutorial:
    """Tests for the download-unimpeded-tutorial entry point."""

    @pytest.mark.parametrize("flag", ["--help", "-h"])
    def test_help_prints_usage_and_downloads_nothing(
        self, flag, isolated_cwd, monkeypatch, capsys
    ):
        """Both help flags print usage and make no network call."""
        monkeypatch.setattr(sys, "argv", ["download-unimpeded-tutorial", flag])
        with patch("unimpeded.cli.requests.get") as mock_get:
            download_unimpeded_tutorial()
        mock_get.assert_not_called()
        assert "Usage: download-unimpeded-tutorial" in capsys.readouterr().out
        assert not (isolated_cwd / FILENAME).exists()

    def test_downloads_notebook_when_absent(self, isolated_cwd, capsys):
        """A missing notebook is fetched and written to the working directory."""
        with patch("unimpeded.cli.requests.get") as mock_get:
            mock_get.return_value = _response(b'{"cells": [1]}')
            download_unimpeded_tutorial()

        assert (isolated_cwd / FILENAME).read_bytes() == b'{"cells": [1]}'
        assert f"Saved to ./{FILENAME}" in capsys.readouterr().out

    def test_overwrites_when_user_confirms(self, isolated_cwd, monkeypatch, capsys):
        """Answering 'y' at the prompt replaces the existing notebook."""
        (isolated_cwd / FILENAME).write_bytes(b"stale")
        monkeypatch.setattr("builtins.input", lambda _: "y")

        with patch("unimpeded.cli.requests.get") as mock_get:
            mock_get.return_value = _response(b"fresh")
            download_unimpeded_tutorial()

        assert (isolated_cwd / FILENAME).read_bytes() == b"fresh"
        assert "already exists" in capsys.readouterr().out

    @pytest.mark.parametrize("answer", ["n", "", "no", "anything else"])
    def test_aborts_without_confirmation(
        self, answer, isolated_cwd, monkeypatch, capsys
    ):
        """Anything other than 'y' leaves the existing notebook untouched."""
        (isolated_cwd / FILENAME).write_bytes(b"stale")
        monkeypatch.setattr("builtins.input", lambda _: answer)

        with patch("unimpeded.cli.requests.get") as mock_get:
            download_unimpeded_tutorial()

        mock_get.assert_not_called()
        assert (isolated_cwd / FILENAME).read_bytes() == b"stale"
        assert "Aborted." in capsys.readouterr().out

    def test_confirmation_is_case_and_space_insensitive(
        self, isolated_cwd, monkeypatch
    ):
        """' Y ' is accepted, since the answer is stripped and lowercased."""
        (isolated_cwd / FILENAME).write_bytes(b"stale")
        monkeypatch.setattr("builtins.input", lambda _: "  Y  ")

        with patch("unimpeded.cli.requests.get") as mock_get:
            mock_get.return_value = _response(b"fresh")
            download_unimpeded_tutorial()

        assert (isolated_cwd / FILENAME).read_bytes() == b"fresh"

    def test_network_failure_exits_nonzero(self, isolated_cwd, capsys):
        """A request exception reports the error and exits 1."""
        with patch("unimpeded.cli.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("no route to host")
            with pytest.raises(SystemExit) as exc:
                download_unimpeded_tutorial()

        assert exc.value.code == 1
        assert "Error downloading tutorial" in capsys.readouterr().out
        assert not (isolated_cwd / FILENAME).exists()

    def test_http_error_exits_nonzero(self, isolated_cwd):
        """A non-2xx response is surfaced via raise_for_status and exits 1."""
        failing = MagicMock()
        failing.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch("unimpeded.cli.requests.get", return_value=failing):
            with pytest.raises(SystemExit) as exc:
                download_unimpeded_tutorial()

        assert exc.value.code == 1
        assert not (isolated_cwd / FILENAME).exists()


class TestLaunchTutorial:
    """Tests for the launch-unimpeded-tutorial entry point."""

    @pytest.mark.parametrize("flag", ["--help", "-h"])
    def test_help_prints_usage_and_launches_nothing(self, flag, monkeypatch, capsys):
        """Both help flags print usage without invoking jupyter."""
        monkeypatch.setattr(sys, "argv", ["launch-unimpeded-tutorial", flag])
        with patch("unimpeded.cli.subprocess.run") as mock_run:
            launch_unimpeded_tutorial()
        mock_run.assert_not_called()
        assert "Usage: launch-unimpeded-tutorial" in capsys.readouterr().out

    def test_missing_notebook_exits_nonzero(self, capsys):
        """Launching without a downloaded notebook explains how to get one."""
        with patch("unimpeded.cli.subprocess.run") as mock_run:
            with pytest.raises(SystemExit) as exc:
                launch_unimpeded_tutorial()

        mock_run.assert_not_called()
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "not found in the current directory" in out
        assert "download-unimpeded-tutorial" in out

    def test_invokes_jupyter_on_the_notebook(self, isolated_cwd):
        """An existing notebook is handed to 'jupyter notebook'."""
        (isolated_cwd / FILENAME).write_bytes(b"{}")

        with patch("unimpeded.cli.subprocess.run") as mock_run:
            launch_unimpeded_tutorial()

        mock_run.assert_called_once_with(["jupyter", "notebook", FILENAME])

    def test_missing_jupyter_exits_with_install_hint(self, isolated_cwd, capsys):
        """A missing jupyter binary is reported with installation instructions."""
        (isolated_cwd / FILENAME).write_bytes(b"{}")

        with patch("unimpeded.cli.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("jupyter")
            with pytest.raises(SystemExit) as exc:
                launch_unimpeded_tutorial()

        assert exc.value.code == 1
        assert "pip install jupyter" in capsys.readouterr().out


class TestEntryPointsAreWired:
    """The console scripts declared in pyproject.toml must actually resolve."""

    def test_declared_scripts_resolve_to_callables(self):
        """Every [project.scripts] target imports and is callable.

        Guards against renaming a function in cli.py without updating
        pyproject.toml, which produces a package that installs cleanly and
        then fails the moment a user runs the command.
        """
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        block = re.search(
            r"^\[project\.scripts\]\s*$(.*?)(?=^\[|\Z)",
            pyproject.read_text(),
            re.MULTILINE | re.DOTALL,
        )
        assert block, "no [project.scripts] section found in pyproject.toml"

        targets = re.findall(
            r'^\s*[\w-]+\s*=\s*"([\w.]+):([\w]+)"\s*$', block.group(1), re.MULTILINE
        )
        assert targets, "no console scripts parsed from [project.scripts]"

        for module_name, attr in targets:
            module = importlib.import_module(module_name)
            assert callable(getattr(module, attr)), f"{module_name}:{attr}"

    def test_both_documented_commands_are_declared(self):
        """The two commands the docs tell users to run are the ones declared."""
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        text = pyproject.read_text()
        assert "download-unimpeded-tutorial" in text
        assert "launch-unimpeded-tutorial" in text
