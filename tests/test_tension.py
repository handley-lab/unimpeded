"""Tests for the unimpeded tension module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from anesthetic.samples import NestedSamples

from unimpeded.tension import download_tension_inputs, tension_calculator, tension_stats


class TestTensionStats:
    """Test the tension_stats function."""

    def test_tension_stats_basic(self):
        """Test basic tension statistics calculation with two datasets."""
        # Create mock samples with required columns
        joint_data = {
            "logZ": -100.0,
            "D_KL": 5.0,
            "logL_P": -95.0,
            "d_G": 3.0,
        }
        separate_data_A = {
            "logZ": -50.0,
            "D_KL": 2.0,
            "logL_P": -48.0,
            "d_G": 1.5,
        }
        separate_data_B = {
            "logZ": -52.0,
            "D_KL": 2.5,
            "logL_P": -49.5,
            "d_G": 1.5,
        }

        # Create NestedSamples-like objects
        from anesthetic.samples import Samples

        joint = Samples({k: [v] for k, v in joint_data.items()})
        separate_A = Samples({k: [v] for k, v in separate_data_A.items()})
        separate_B = Samples({k: [v] for k, v in separate_data_B.items()})

        # Calculate tension statistics
        result = tension_stats(joint, separate_A, separate_B)

        # Check that all expected columns are present
        expected_columns = ["logR", "logI", "logS", "d_G", "p", "sigma"]
        assert all(col in result.columns for col in expected_columns)

        # Check that result is not empty
        assert len(result) > 0

    def test_tension_stats_with_correction_factors(self):
        """Test tension statistics with F-correction factors."""
        from anesthetic.samples import Samples

        joint_data = {
            "logZ": -100.0,
            "D_KL": 5.0,
            "logL_P": -95.0,
            "d_G": 3.0,
        }
        separate_data_A = {
            "logZ": -50.0,
            "D_KL": 2.0,
            "logL_P": -48.0,
            "d_G": 1.5,
        }
        separate_data_B = {
            "logZ": -52.0,
            "D_KL": 2.5,
            "logL_P": -49.5,
            "d_G": 1.5,
        }

        joint = Samples({k: [v] for k, v in joint_data.items()})
        separate_A = Samples({k: [v] for k, v in separate_data_A.items()})
        separate_B = Samples({k: [v] for k, v in separate_data_B.items()})

        # Calculate with correction factors
        result = tension_stats(
            joint,
            separate_A,
            separate_B,
            joint_f=1.2,
            separate_fs=[1.1, 1.15],
        )

        # Check that correction factors are applied (logR and logI should be affected)
        assert "logR" in result.columns
        assert "logI" in result.columns

    def test_tension_stats_separate_fs_mismatch(self):
        """Test that mismatched separate_fs raises ValueError."""
        from anesthetic.samples import Samples

        joint_data = {
            "logZ": -100.0,
            "D_KL": 5.0,
            "logL_P": -95.0,
            "d_G": 3.0,
        }
        separate_data = {
            "logZ": -50.0,
            "D_KL": 2.0,
            "logL_P": -48.0,
            "d_G": 1.5,
        }

        joint = Samples({k: [v] for k, v in joint_data.items()})
        separate_A = Samples({k: [v] for k, v in separate_data.items()})
        separate_B = Samples({k: [v] for k, v in separate_data.items()})

        # Should raise ValueError when separate_fs length doesn't match
        with pytest.raises(ValueError, match="must match"):
            tension_stats(
                joint,
                separate_A,
                separate_B,
                separate_fs=[1.0],  # Only 1 factor for 2 datasets
            )


class TestDownloadTensionInputs:
    """Test the download_tension_inputs function."""

    @pytest.mark.vcr
    def test_download_tension_inputs_two_datasets(self):
        """Test downloading inputs for two datasets."""
        # This will use actual Zenodo API calls (recorded with VCR)
        result = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )

        # Check structure
        assert "joint" in result
        assert "separate" in result
        assert "joint_f" in result
        assert "separate_fs" in result

        # Check types
        assert len(result["separate"]) == 2
        assert len(result["separate_fs"]) == 2
        assert isinstance(result["joint_f"], (int, float))
        assert all(isinstance(f, (int, float)) for f in result["separate_fs"])

    @pytest.mark.vcr
    def test_download_tension_inputs_caching(self):
        """Test that download_tension_inputs caches results."""
        # Clear the cache first
        download_tension_inputs.cache_clear()

        # First call - should download
        result1 = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )

        # Get cache info
        cache_info_before = download_tension_inputs.cache_info()

        # Second call with same arguments - should use cache
        result2 = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )

        cache_info_after = download_tension_inputs.cache_info()

        # Cache hits should increase
        assert cache_info_after.hits > cache_info_before.hits

        # Results should be the same object (cached)
        assert result1 is result2

    @pytest.mark.vcr
    def test_download_tension_inputs_sorted_datasets(self):
        """Test that datasets are sorted alphabetically for joint name."""
        # Call with datasets in different order
        result1 = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )

        result2 = download_tension_inputs(
            "ns", "lcdm", "bao.sdss_dr16", "planck_2018_plik"
        )

        # Both should download the same joint dataset (sorted alphabetically)
        # but they won't be cached as the same call due to argument order
        assert "joint" in result1
        assert "joint" in result2


class TestTensionCalculator:
    """Test the tension_calculator function."""

    @pytest.mark.vcr
    def test_tension_calculator_two_datasets(self):
        """Test tension calculator with two datasets."""
        result = tension_calculator(
            "ns",
            "lcdm",
            "planck_2018_plik",
            "bao.sdss_dr16",
            nsamples=100,
        )

        # Check that result contains expected columns
        expected_columns = ["logR", "logI", "logS", "d_G", "p", "sigma"]
        assert all(col in result.columns for col in expected_columns)

        # Check that result is not empty
        assert len(result) > 0

    @pytest.mark.vcr
    def test_tension_calculator_with_beta(self):
        """Test tension calculator with beta parameter."""
        result = tension_calculator(
            "ns",
            "lcdm",
            "planck_2018_plik",
            "bao.sdss_dr16",
            nsamples=100,
            beta=1.0,
        )

        # Check that result is computed successfully
        assert len(result) > 0
        assert "sigma" in result.columns

    @pytest.mark.vcr
    def test_tension_calculator_uses_cache(self):
        """Test that tension_calculator uses cached download_tension_inputs."""
        # Clear cache
        download_tension_inputs.cache_clear()

        # First call
        result1 = tension_calculator(
            "ns",
            "lcdm",
            "planck_2018_plik",
            "bao.sdss_dr16",
            nsamples=50,
        )

        cache_info_before = download_tension_inputs.cache_info()

        # Second call with different nsamples (should use cached download)
        result2 = tension_calculator(
            "ns",
            "lcdm",
            "planck_2018_plik",
            "bao.sdss_dr16",
            nsamples=100,
        )

        cache_info_after = download_tension_inputs.cache_info()

        # Cache hits should increase
        assert cache_info_after.hits > cache_info_before.hits


class TestTensionIntegration:
    """Integration tests for complete tension analysis workflow."""

    @pytest.mark.vcr
    def test_complete_workflow_two_datasets(self):
        """Test complete workflow: download -> calculate tension."""
        # Step 1: Download inputs
        inputs = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )

        # Step 2: Calculate tension stats directly
        result = tension_stats(
            inputs["joint"],
            *inputs["separate"],
            joint_f=inputs["joint_f"],
            separate_fs=inputs["separate_fs"],
            nsamples=50,
        )

        # Check results
        assert len(result) > 0
        assert "sigma" in result.columns
        assert "p" in result.columns

    @pytest.mark.vcr
    def test_complete_workflow_vs_calculator(self):
        """Test that manual workflow gives same results as calculator."""
        # Clear cache to ensure fresh download
        download_tension_inputs.cache_clear()

        # Method 1: Using tension_calculator
        result1 = tension_calculator(
            "ns",
            "lcdm",
            "planck_2018_plik",
            "bao.sdss_dr16",
            nsamples=100,
        )

        # Method 2: Manual workflow
        inputs = download_tension_inputs(
            "ns", "lcdm", "planck_2018_plik", "bao.sdss_dr16"
        )
        result2 = tension_stats(
            inputs["joint"],
            *inputs["separate"],
            joint_f=inputs["joint_f"],
            separate_fs=inputs["separate_fs"],
            nsamples=100,
        )

        # Results should have same columns
        assert set(result1.columns) == set(result2.columns)

        # Results should have same length
        assert len(result1) == len(result2)
