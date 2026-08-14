"""Tests for the unimpeded database module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from unimpeded.database import (
    DEFAULT_GRID_ROOT,
    Database,
    DatabaseCreator,
    DatabaseExplorer,
)


class TestDatabase:
    """Test the base Database class."""

    @pytest.mark.vcr
    def test_supported_models(self):
        """Test that supported models list is correct and sorted."""
        db = Database()
        # Models are now fetched from Zenodo and sorted alphabetically
        assert isinstance(db.models, list)
        assert len(db.models) > 0
        # Check that the list is sorted
        assert db.models == sorted(db.models)
        # Check that common models exist
        common_models = ["lcdm", "wlcdm", "klcdm"]
        assert all(model in db.models for model in common_models)

    @pytest.mark.vcr
    def test_supported_data(self):
        """Test that supported datasets list is correct."""
        db = Database()
        expected_data = [
            "planck_2018_CamSpec",
            "planck_2018_plik",
            "bao.sdss_dr16",
            "bicep_keck_2018",
            "des_y1.joint",
            "sn.pantheon",
        ]
        assert all(data in db.datasets for data in expected_data)

    @pytest.mark.vcr
    def test_combinations(self):
        """Test fetching available combinations from Zenodo."""
        db = Database(sandbox=False)

        # Check combinations is a set of tuples
        assert isinstance(db.combinations, set)
        assert all(isinstance(c, tuple) and len(c) == 2 for c in db.combinations)

        # Check that models and datasets are derived correctly
        assert isinstance(db.models, list)
        assert isinstance(db.datasets, list)
        assert db.models == sorted(db.models)
        assert db.datasets == sorted(db.datasets)

        # Check that all models/datasets in combinations appear in the properties
        for model, dataset in db.combinations:
            assert model in db.models
            assert dataset in db.datasets

    @pytest.mark.vcr
    def test_datasets_for(self):
        """Test looking up datasets for a given model."""
        db = Database(sandbox=False)
        if db.models:
            model = db.models[0]
            result = db.datasets_for(model)
            assert isinstance(result, list)
            assert result == sorted(result)
            assert all((model, d) in db.combinations for d in result)

        # Non-existent model returns empty list
        assert db.datasets_for("nonexistent_model") == []

    @pytest.mark.vcr
    def test_models_for(self):
        """Test looking up models for a given dataset."""
        db = Database(sandbox=False)
        if db.datasets:
            dataset = db.datasets[0]
            result = db.models_for(dataset)
            assert isinstance(result, list)
            assert result == sorted(result)
            assert all((m, dataset) in db.combinations for m in result)

        # Non-existent dataset returns empty list
        assert db.models_for("nonexistent_dataset") == []

    @pytest.mark.vcr
    def test_is_available(self):
        """Test checking whether a model-dataset combination exists."""
        db = Database(sandbox=False)
        if db.combinations:
            model, dataset = next(iter(db.combinations))
            assert db.is_available(model, dataset) is True

        assert db.is_available("nonexistent_model", "nonexistent_dataset") is False

    def test_combinations_empty(self):
        """Test handling when no unimpeded deposits exist."""
        with patch("requests.get") as mock_get:
            # Mock empty response
            mock_response = MagicMock()
            mock_response.json.return_value = {"hits": {"hits": [], "total": 0}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            db = Database(sandbox=True)

            assert db.combinations == set()
            assert db.models == []
            assert db.datasets == []

    def test_fetch_combinations_handles_errors(self):
        """Test error handling in _fetch_combinations."""
        import requests

        with patch("requests.get") as mock_get:
            # Mock request exception
            mock_get.side_effect = requests.RequestException("Network error")

            # Capture printed output
            import io
            import sys

            captured_output = io.StringIO()
            sys.stdout = captured_output

            db = Database(sandbox=True)

            # Restore stdout
            sys.stdout = sys.__stdout__

            # Should return empty set on error
            assert db.combinations == set()
            assert db.models == []
            assert db.datasets == []

            # Verify error was printed
            output = captured_output.getvalue()
            assert "Error fetching deposits" in output

    @pytest.mark.vcr
    def test_get_filename_samples(self):
        """Test filename generation for samples."""
        db = Database()
        filename = db.get_filename("ns", "lcdm", "planck_2018_plik", "samples")
        assert filename == "ns_lcdm_planck_2018_plik.csv"

    @pytest.mark.vcr
    def test_get_filename_info(self):
        """Test filename generation for info files."""
        db = Database()
        filename = db.get_filename("mcmc", "wlcdm", "bao.sdss_dr16", "info")
        assert filename == "mcmc_wlcdm_bao.sdss_dr16.yaml"

    @pytest.mark.vcr
    def test_get_filename_prior_info(self):
        """Test filename generation for prior_info files."""
        db = Database()
        filename = db.get_filename("ns", "klcdm", "planck_2018_CamSpec", "prior_info")
        assert filename == "ns_klcdm_planck_2018_CamSpec.prior_info"

    @pytest.mark.vcr
    def test_get_filename_invalid_file_type(self):
        """Test that invalid file types raise ValueError."""
        db = Database()
        with pytest.raises(ValueError, match="Invalid file type"):
            db.get_filename("ns", "lcdm", "planck_2018_plik", "invalid_type")

    @pytest.mark.vcr
    def test_get_filename_with_special_characters(self):
        """Test filename generation handles special characters properly."""
        db = Database()
        # Test dataset with dot notation
        filename = db.get_filename("ns", "lcdm", "bao.sdss_dr16", "samples")
        assert filename == "ns_lcdm_bao.sdss_dr16.csv"

        # Test combined datasets with plus sign
        filename = db.get_filename(
            "mcmc", "lcdm", "planck_2018_plik+bao.sdss_dr16", "info"
        )
        assert filename == "mcmc_lcdm_planck_2018_plik+bao.sdss_dr16.yaml"


class TestDatabaseCreator:
    """Test the DatabaseCreator class with VCR."""

    @pytest.mark.vcr
    def test_create_deposit(self, zenodo_access_token):
        """Test creating a new deposit."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN=zenodo_access_token)
        deposit_id = creator.create_deposit()
        assert isinstance(deposit_id, int)
        assert deposit_id > 0

    @pytest.mark.vcr
    def test_create_metadata(self):
        """Test metadata creation for different models and datasets."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")

        # Test basic metadata creation
        metadata = creator.create_metadata("lcdm", "planck_2018_plik")
        assert "metadata" in metadata
        assert metadata["metadata"]["title"] == "unimpeded: lcdm planck_2018_plik"
        assert metadata["metadata"]["upload_type"] == "dataset"

        # Test with different model
        metadata = creator.create_metadata("wlcdm", "bao.sdss_dr16")
        assert metadata["metadata"]["title"] == "unimpeded: wlcdm bao.sdss_dr16"

    @pytest.mark.vcr
    def test_create_description(self):
        """Test description creation for deposits."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")

        description = creator.create_description("lcdm", "planck_2018_plik")
        assert description == "cosmological model:lcdm, dataset:planck_2018_plik"

    @pytest.mark.vcr
    def test_initialization(self):
        """Test DatabaseCreator initialization."""
        # Test sandbox initialization
        creator_sandbox = DatabaseCreator(sandbox=True, ACCESS_TOKEN="test-token")
        assert creator_sandbox.sandbox == True
        assert "sandbox.zenodo.org" in creator_sandbox.base_url

        # Test production initialization
        creator_prod = DatabaseCreator(sandbox=False, ACCESS_TOKEN="test-token")
        assert creator_prod.sandbox == False
        assert creator_prod.base_url == "https://zenodo.org/api/deposit/depositions"

    @pytest.mark.vcr
    def test_database_creator_inherits_base_methods(self):
        """Test that DatabaseCreator inherits Database methods."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")

        # Should have access to base Database methods
        filename = creator.get_filename("ns", "lcdm", "planck_2018_plik", "samples")
        assert filename == "ns_lcdm_planck_2018_plik.csv"

        # Should have access to models and datasets
        assert hasattr(creator, "models")
        assert hasattr(creator, "datasets")
        # Check that models list is populated (sandbox may have different models)
        assert len(creator.models) > 0
        assert isinstance(creator.models, list)


class TestDatabaseExplorer:
    """Test the DatabaseExplorer class with VCR."""

    @pytest.mark.vcr
    def test_get_deposit_id_by_title_users(self):
        """Test searching for published deposits by title."""
        explorer = DatabaseExplorer(sandbox=False)

        # This may return None if no matching deposits exist in sandbox
        deposit_id = explorer.get_deposit_id_by_title_users("lcdm", "planck_2018_plik")
        if deposit_id is not None:
            assert isinstance(deposit_id, int)
            assert deposit_id > 0

    @pytest.mark.vcr
    def test_download_samples_no_deposit(self):
        """Test download_samples when no deposit exists."""
        import requests

        explorer = DatabaseExplorer(sandbox=False)

        # Should raise HTTPError when trying to download from non-existent deposit
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            explorer.download_samples("ns", "nonexistent_model", "nonexistent_data")

        # Verify it's a 404 error for the expected reason
        assert "404 Client Error" in str(exc_info.value)
        assert "api/records/None" in str(exc_info.value)

    @pytest.mark.vcr
    def test_title_formatting(self):
        """Test consistent title formatting between Creator and Explorer."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")
        explorer = DatabaseExplorer(sandbox=True)

        # Both should use the same title format logic
        # (DatabaseExplorer searches for titles created by DatabaseCreator)
        metadata = creator.create_metadata("lcdm", "planck_2018_plik")
        expected_title = metadata["metadata"]["title"]
        assert expected_title == "unimpeded: lcdm planck_2018_plik"

    @pytest.mark.vcr
    def test_database_explorer_url_construction(self):
        """Test that DatabaseExplorer constructs URLs correctly."""
        explorer = DatabaseExplorer(sandbox=False)

        # Check that the URL properties are set correctly
        assert hasattr(explorer, "records_url")
        assert hasattr(explorer, "base_url")
        assert explorer.base_url == "https://zenodo.org/api/deposit/depositions"
        assert explorer.records_url == "https://zenodo.org/api/records"


class TestDatabaseIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.vcr
    def test_filename_consistency(self):
        """Test that Creator and Explorer use consistent filenames."""
        creator = DatabaseCreator(sandbox=True)
        explorer = DatabaseExplorer(sandbox=True)

        # Both should generate the same filename
        creator_filename = creator.get_filename(
            "ns", "lcdm", "planck_2018_plik", "samples"
        )
        explorer_filename = explorer.get_filename(
            "ns", "lcdm", "planck_2018_plik", "samples"
        )

        assert creator_filename == explorer_filename
        assert creator_filename == "ns_lcdm_planck_2018_plik.csv"


@pytest.mark.vcr
@pytest.mark.parametrize(
    "sampler,model,dataset,file_type",
    [
        ("ns", "lcdm", "planck_2018_plik", "samples"),
        ("mcmc", "wlcdm", "bao.sdss_dr16", "info"),
        ("ns", "klcdm", "planck_2018_CamSpec", "prior_info"),
        ("mcmc", "lcdm", "planck_2018_plik+bao.sdss_dr16", "samples"),
    ],
)
def test_filename_generation_parametrized(sampler, model, dataset, file_type):
    """Parametrized test for filename generation across different combinations."""
    db = Database()
    filename = db.get_filename(sampler, model, dataset, file_type)

    # Basic structure check - actual format is method_model_dataset.extension
    if file_type == "samples":
        expected_filename = f"{sampler}_{model}_{dataset}.csv"
    elif file_type == "info":
        expected_filename = f"{sampler}_{model}_{dataset}.yaml"
    elif file_type == "prior_info":
        expected_filename = f"{sampler}_{model}_{dataset}.prior_info"

    assert filename == expected_filename


@pytest.fixture
def mock_creator(monkeypatch):
    """DatabaseCreator with HTTP-free __init__ for mock-based tests."""
    monkeypatch.setattr(
        "unimpeded.database.Database._fetch_combinations", lambda self: set()
    )
    return DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")


class TestGridKwarg:
    """Tests for the `grid` kwarg added to upload methods and path helpers."""

    @pytest.mark.vcr
    def test_get_yaml_path_hpc_default_grid(self):
        """Default grid='new_grid' for loc='hpc' yields a /new_grid/ path."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_yaml_path("ns", "lcdm", "bao.sdss_dr16", "hpc")
        assert "/new_grid/ns/lcdm/bao.sdss_dr16/" in path
        assert path.endswith("bao.sdss_dr16.updated.yaml")

    @pytest.mark.vcr
    def test_get_yaml_path_hpc_old_grid(self):
        """Passing grid='grid' selects the old-paper layout."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_yaml_path("ns", "lcdm", "bao.sdss_dr16", "hpc", grid="grid")
        assert "/grid/ns/lcdm/" in path
        assert "/new_grid/" not in path

    @pytest.mark.vcr
    def test_get_yaml_path_honours_root(self):
        """An explicit root replaces the default grid location."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_yaml_path(
            "mcmc", "wlcdm", "sn.pantheon", root="/data/chains"
        )
        assert path == (
            "/data/chains/new_grid/mcmc/wlcdm/sn.pantheon/sn.pantheon.updated.yaml"
        )

    @pytest.mark.vcr
    def test_get_yaml_path_defaults_to_grid_root(self):
        """Without a root, paths fall back to DEFAULT_GRID_ROOT."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_yaml_path("mcmc", "wlcdm", "sn.pantheon")
        assert path.startswith(DEFAULT_GRID_ROOT)
        assert "/new_grid/mcmc/wlcdm/sn.pantheon/" in path
        assert path.endswith("sn.pantheon.updated.yaml")

    @pytest.mark.vcr
    def test_get_prior_info_path_hpc_default_grid(self):
        """Default grid='new_grid' on get_prior_info_path yields a /new_grid/ path."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_prior_info_path("ns", "lcdm", "bao.sdss_dr16", "hpc")
        assert "/new_grid/ns/lcdm/bao.sdss_dr16/" in path
        assert "_polychord_raw/" in path
        assert path.endswith(".prior_info")

    @pytest.mark.vcr
    def test_get_prior_info_path_hpc_old_grid(self):
        """Old grid selects /grid/ path for prior_info."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_prior_info_path(
            "ns", "lcdm", "bao.sdss_dr16", "hpc", grid="grid"
        )
        assert "/grid/ns/" in path
        assert "/new_grid/" not in path

    @pytest.mark.vcr
    def test_get_prior_info_path_honours_root(self):
        """An explicit root replaces the default grid location."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        path = creator.get_prior_info_path(
            "ns", "lcdm", "bao.sdss_dr16", root="/data/chains"
        )
        assert path == (
            "/data/chains/new_grid/ns/lcdm/bao.sdss_dr16/"
            "bao.sdss_dr16_polychord_raw/bao.sdss_dr16.prior_info"
        )

    @pytest.mark.vcr
    def test_get_samples_honours_root(self):
        """get_samples reads chains from an explicit root."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        with patch("unimpeded.database.read_chains") as mock_read:
            mock_read.return_value = MagicMock()
            creator.get_samples("ns", "lcdm", "bao.sdss_dr16", root="/data/chains")
        assert mock_read.call_args[0][0].startswith("/data/chains/new_grid/ns/lcdm/")

    @pytest.mark.vcr
    def test_get_samples_rejects_unknown_method(self):
        """An unrecognised method raises rather than failing obscurely later."""
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        with pytest.raises(ValueError, match="Invalid method"):
            creator.get_samples("badmethod", "lcdm", "bao.sdss_dr16")

    @pytest.mark.vcr
    @patch("unimpeded.database.read_chains")
    def test_get_samples_ns_hpc_forwards_grid(self, mock_read):
        """get_samples passes a /new_grid/ path with _polychord_raw to read_chains for NS."""
        mock_read.return_value = MagicMock()
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        creator.get_samples("ns", "lcdm", "bao.sdss_dr16", "hpc", grid="new_grid")
        called_path = mock_read.call_args[0][0]
        assert "/new_grid/ns/lcdm/bao.sdss_dr16/" in called_path
        assert "_polychord_raw" in called_path

    @pytest.mark.vcr
    @patch("unimpeded.database.read_chains")
    def test_get_samples_ns_hpc_old_grid(self, mock_read):
        """get_samples honours grid='grid' (old paper)."""
        mock_read.return_value = MagicMock()
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        creator.get_samples("ns", "lcdm", "bao.sdss_dr16", "hpc", grid="grid")
        called_path = mock_read.call_args[0][0]
        assert "/grid/ns/" in called_path

    @pytest.mark.vcr
    @patch("unimpeded.database.read_chains")
    def test_get_samples_mcmc_hpc(self, mock_read):
        """MCMC paths have a different layout: no _polychord_raw subfolder."""
        mock_read.return_value = MagicMock()
        creator = DatabaseCreator(sandbox=False, ACCESS_TOKEN="fake-token")
        creator.get_samples("mcmc", "lcdm", "bao.sdss_dr16", "hpc", grid="new_grid")
        called_path = mock_read.call_args[0][0]
        assert "/new_grid/mcmc/lcdm/bao.sdss_dr16/" in called_path
        assert "polychord_raw" not in called_path


class TestGetDepositIdsByTitlePagination:
    """Tests for the paginated retrieval of deposit IDs.

    Uses mocks (not VCR) so we can simulate edge cases like empty pages,
    partial pages, and the dict-shaped response form without recording
    real Zenodo interactions.
    """

    @staticmethod
    def _make_resp(items):
        r = MagicMock()
        r.raise_for_status = MagicMock()
        r.json = MagicMock(return_value=items)
        return r

    @patch("unimpeded.database.requests.get")
    def test_paginates_until_empty_page(self, mock_get, mock_creator):
        """Two full pages of 25 followed by an empty page should stop after 3 calls."""
        page1 = [{"id": i, "submitted": True} for i in range(1, 26)]
        page2 = [{"id": i, "submitted": False} for i in range(26, 51)]
        page3_empty = []
        mock_get.side_effect = [
            self._make_resp(page1),
            self._make_resp(page2),
            self._make_resp(page3_empty),
        ]

        ids = mock_creator.get_deposit_ids_by_title("unimpeded")

        assert len(ids["published"]) == 25
        assert len(ids["unpublished"]) == 25
        assert mock_get.call_count == 3
        pages_used = [call.kwargs["params"]["page"] for call in mock_get.call_args_list]
        assert pages_used == [1, 2, 3]

    @patch("unimpeded.database.requests.get")
    def test_stops_on_partial_page(self, mock_get, mock_creator):
        """A partial last page (fewer than size) ends iteration without an extra call."""
        page1 = [{"id": i, "submitted": True} for i in range(1, 26)]
        page2_partial = [{"id": i, "submitted": False} for i in range(26, 36)]
        mock_get.side_effect = [
            self._make_resp(page1),
            self._make_resp(page2_partial),
        ]

        ids = mock_creator.get_deposit_ids_by_title("unimpeded")

        assert len(ids["published"]) == 25
        assert len(ids["unpublished"]) == 10
        assert mock_get.call_count == 2

    @patch("unimpeded.database.requests.get")
    def test_default_size_is_25(self, mock_get, mock_creator):
        """Default page size should be 25 (Zenodo's deposit API cap)."""
        mock_get.side_effect = [self._make_resp([])]
        mock_creator.get_deposit_ids_by_title("unimpeded")
        assert mock_get.call_args.kwargs["params"]["size"] == 25

    @patch("unimpeded.database.requests.get")
    def test_dict_shaped_response(self, mock_get, mock_creator):
        """Should also accept dict {'hits': {'hits': [...]}} responses."""
        hits = [{"id": i, "submitted": True} for i in range(1, 6)]
        dict_resp = {"hits": {"hits": hits}}
        r = MagicMock()
        r.raise_for_status = MagicMock()
        r.json = MagicMock(return_value=dict_resp)
        mock_get.side_effect = [r]

        ids = mock_creator.get_deposit_ids_by_title("unimpeded")

        assert len(ids["published"]) == 5
        assert mock_get.call_count == 1  # 5 < size=25 => stops after first page


class TestPublishReturnValue:
    """Tests for the success/failure bool now returned by publish()."""

    @patch("unimpeded.database.requests.post")
    def test_publish_returns_true_on_success(self, mock_post, mock_creator):
        """publish() returns True on a 2xx response."""
        ok_resp = MagicMock()
        ok_resp.raise_for_status = MagicMock()
        ok_resp.json = MagicMock(return_value={"conceptdoi": "10.5281/zenodo.1"})
        ok_resp.status_code = 202
        mock_post.return_value = ok_resp

        result = mock_creator.publish(12345, {"title": "unimpeded: lcdm bao.sdss_dr16"})
        assert result is True

    @patch("unimpeded.database.requests.post")
    def test_publish_returns_false_on_http_error(self, mock_post, mock_creator):
        """publish() returns False on a 4xx/5xx response."""
        import requests as _requests

        fail_resp = MagicMock()
        fail_resp.status_code = 400
        http_err = _requests.exceptions.HTTPError("400 Bad Request")
        fail_resp.raise_for_status = MagicMock(side_effect=http_err)
        mock_post.return_value = fail_resp

        result = mock_creator.publish(12345, {"title": "unimpeded: lcdm bao.sdss_dr16"})
        assert result is False

    @patch("unimpeded.database.requests.post")
    def test_publish_returns_false_on_generic_error(self, mock_post, mock_creator):
        """publish() returns False on any non-HTTP exception (e.g. connection)."""
        mock_post.side_effect = RuntimeError("connection exploded")
        result = mock_creator.publish(12345, {"title": "unimpeded: lcdm bao.sdss_dr16"})
        assert result is False


class TestUploadMethodsForwardGrid:
    """Tests that upload_samples / upload_yaml / upload_prior_info pass
    the grid kwarg through to their respective path helpers."""

    @patch("unimpeded.database.os.remove")
    @patch("unimpeded.database.read_chains")
    @patch("unimpeded.database.requests.put")
    @patch("unimpeded.database.requests.get")
    def test_upload_samples_uses_grid_in_path(
        self,
        mock_get,
        mock_put,
        mock_read,
        mock_rm,
        mock_creator,
        tmp_path,
        monkeypatch,
    ):
        """upload_samples reads chains from a path containing the grid name."""
        monkeypatch.chdir(tmp_path)

        get_resp = MagicMock()
        get_resp.raise_for_status = MagicMock()
        get_resp.json = MagicMock(return_value={"links": {"bucket": "http://bucket"}})
        mock_get.return_value = get_resp

        put_resp = MagicMock()
        put_resp.raise_for_status = MagicMock()
        put_resp.status_code = 201
        mock_put.return_value = put_resp

        samples = MagicMock()

        def fake_to_csv(filename):
            (tmp_path / filename).write_text("dummy,csv\n1,2\n")

        samples.to_csv = fake_to_csv
        mock_read.return_value = samples

        mock_creator.upload_samples(
            12345, "ns", "lcdm", "bao.sdss_dr16", "hpc", grid="new_grid"
        )

        called_path = mock_read.call_args[0][0]
        assert "/new_grid/ns/lcdm/bao.sdss_dr16/" in called_path

    @patch("unimpeded.database.requests.put")
    @patch("unimpeded.database.requests.get")
    def test_upload_yaml_uses_grid_in_path(
        self, mock_get, mock_put, mock_creator, tmp_path, monkeypatch
    ):
        """upload_yaml opens the yaml file at a path containing the grid name."""
        yaml_file = tmp_path / "fake.updated.yaml"
        yaml_file.write_text("dummy: 1\n")

        captured = {}
        original = mock_creator.get_yaml_path

        def patched(method, model, dataset, loc="hpc", grid="new_grid", root=None):
            captured["grid"] = grid
            captured["path"] = original(method, model, dataset, loc, grid=grid)
            return str(yaml_file)

        monkeypatch.setattr(mock_creator, "get_yaml_path", patched)

        get_resp = MagicMock()
        get_resp.raise_for_status = MagicMock()
        get_resp.json = MagicMock(return_value={"links": {"bucket": "http://bucket"}})
        mock_get.return_value = get_resp

        put_resp = MagicMock()
        put_resp.raise_for_status = MagicMock()
        put_resp.status_code = 201
        mock_put.return_value = put_resp

        mock_creator.upload_yaml(
            12345, "ns", "lcdm", "bao.sdss_dr16", "hpc", grid="grid"
        )

        assert captured["grid"] == "grid"
        assert "/grid/ns/" in captured["path"]

    @patch("unimpeded.database.requests.put")
    @patch("unimpeded.database.requests.get")
    def test_upload_prior_info_uses_grid_in_path(
        self, mock_get, mock_put, mock_creator, tmp_path, monkeypatch
    ):
        """upload_prior_info opens prior_info at a path containing the grid name."""
        prior_file = tmp_path / "fake.prior_info"
        prior_file.write_text("dummy prior\n")

        captured = {}
        original = mock_creator.get_prior_info_path

        def patched(method, model, dataset, loc="hpc", grid="new_grid", root=None):
            captured["grid"] = grid
            captured["path"] = original(method, model, dataset, loc, grid=grid)
            return str(prior_file)

        monkeypatch.setattr(mock_creator, "get_prior_info_path", patched)

        get_resp = MagicMock()
        get_resp.raise_for_status = MagicMock()
        get_resp.json = MagicMock(return_value={"links": {"bucket": "http://bucket"}})
        mock_get.return_value = get_resp

        put_resp = MagicMock()
        put_resp.raise_for_status = MagicMock()
        put_resp.status_code = 201
        mock_put.return_value = put_resp

        mock_creator.upload_prior_info(
            12345, "ns", "lcdm", "bao.sdss_dr16", "hpc", grid="new_grid"
        )

        assert captured["grid"] == "new_grid"
        assert "/new_grid/ns/" in captured["path"]
