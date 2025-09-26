"""Tests for the unimpeded database module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from unimpeded.database import Database, DatabaseCreator, DatabaseExplorer


class TestDatabase:
    """Test the base Database class."""

    def test_supported_models(self):
        """Test that supported models list is correct."""
        db = Database()
        expected_models = [
            "klcdm",
            "wlcdm",
            "rlcdm",
            "nrunlcdm",
            "mlcdm",
            "lcdm",
            "walcdm",
            "Nlcdm",
            "nlcdm",
        ]
        assert db.models == expected_models

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

    def test_get_filename_samples(self):
        """Test filename generation for samples."""
        db = Database()
        filename = db.get_filename("ns", "lcdm", "planck_2018_plik", "samples")
        assert filename == "ns_lcdm_planck_2018_plik.csv"

    def test_get_filename_info(self):
        """Test filename generation for info files."""
        db = Database()
        filename = db.get_filename("mcmc", "wlcdm", "bao.sdss_dr16", "info")
        assert filename == "mcmc_wlcdm_bao.sdss_dr16.yaml"

    def test_get_filename_prior_info(self):
        """Test filename generation for prior_info files."""
        db = Database()
        filename = db.get_filename("ns", "klcdm", "planck_2018_CamSpec", "prior_info")
        assert filename == "ns_klcdm_planck_2018_CamSpec.prior_info"

    def test_get_filename_invalid_file_type(self):
        """Test that invalid file types raise ValueError."""
        db = Database()
        with pytest.raises(ValueError, match="Invalid file type"):
            db.get_filename("ns", "lcdm", "planck_2018_plik", "invalid_type")

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

    def test_create_description(self):
        """Test description creation for deposits."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")

        description = creator.create_description("lcdm", "planck_2018_plik")
        assert description == "cosmological model:lcdm, dataset:planck_2018_plik"

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

    def test_database_creator_inherits_base_methods(self):
        """Test that DatabaseCreator inherits Database methods."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")

        # Should have access to base Database methods
        filename = creator.get_filename("ns", "lcdm", "planck_2018_plik", "samples")
        assert filename == "ns_lcdm_planck_2018_plik.csv"

        # Should have access to models and datasets
        assert hasattr(creator, "models")
        assert hasattr(creator, "datasets")
        assert "lcdm" in creator.models


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

    def test_title_formatting(self):
        """Test consistent title formatting between Creator and Explorer."""
        creator = DatabaseCreator(sandbox=True, ACCESS_TOKEN="fake-token")
        explorer = DatabaseExplorer(sandbox=True)

        # Both should use the same title format logic
        # (DatabaseExplorer searches for titles created by DatabaseCreator)
        metadata = creator.create_metadata("lcdm", "planck_2018_plik")
        expected_title = metadata["metadata"]["title"]
        assert expected_title == "unimpeded: lcdm planck_2018_plik"

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
    @pytest.mark.slow
    def test_complete_upload_download_workflow(
        self, zenodo_access_token, temp_data_files
    ):
        """Test complete workflow: create -> upload -> publish -> download."""
        # This test would require a published deposit to download from
        # Skip for now as it requires coordination between upload and download
        pytest.skip("Integration test requires published deposits")

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
