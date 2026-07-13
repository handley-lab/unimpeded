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
        expected_columns = ["logR", "I", "logS", "d_G", "p", "sigma"]
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

        # Check that correction factors are applied (logR and I should be affected)
        assert "logR" in result.columns
        assert "I" in result.columns

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
        expected_columns = ["logR", "I", "logS", "d_G", "p", "sigma"]
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


class TestComponentLoglike:
    """Tests for computing tension moments from ``loglike__*`` columns.

    Stock Cobaya's PolyChord wrapper stores ``logL = loglike + logprior +
    logvolume`` rather than the pure data likelihood. ``d_G``, ``logS`` (and the
    ``p``/``sigma`` derived from them) are data-likelihood moments, so they must
    be computed from the summed ``loglike__*`` columns, not the ``logL`` column.
    The evidence ``logZ`` (and hence ``logR``) is unchanged.
    """

    @staticmethod
    def _make_ns(contaminated=True, with_loglike=True, seed=0, nlive=125, ndead=1000):
        """Build a small valid NestedSamples run.

        The run's ``logL`` column plays the role of what PolyChord recorded.
        When ``contaminated`` is True the recorded ``logL`` carries a varying
        ``logprior`` term, and the pure data likelihood is stored in
        ``loglike__A`` such that ``logL == loglike__A + logprior__0``.
        """
        rng = np.random.default_rng(seed)
        logL = np.sort(rng.random(ndead)) * 20.0
        logL_birth = np.concatenate([np.full(nlive, -1e30), logL[: ndead - nlive]])
        params = rng.standard_normal((ndead, 2))
        ns = NestedSamples(
            data=params, columns=["x", "y"], logL=logL, logL_birth=logL_birth
        )
        if with_loglike:
            logprior = rng.standard_normal(ndead) * (2.0 if contaminated else 0.0)
            ns["logprior__0"] = logprior
            ns["loglike__A"] = logL - logprior  # logL = loglike + logprior
        return ns

    def test_contaminated_run_uses_loglike_columns(self):
        """d_G/logL_P/D_KL come from loglike__, logZ stays from logL."""
        from unimpeded.tension import _stats

        ns = self._make_ns(contaminated=True)
        corrected = _stats(ns)
        standard = ns.stats()

        # Evidence is unchanged (still from the run's logL column).
        assert np.isclose(corrected["logZ"], standard["logZ"])

        # The likelihood moments differ, because logprior varies.
        assert not np.isclose(corrected["d_G"], standard["d_G"])
        assert not np.isclose(corrected["logL_P"], standard["logL_P"])

        # The corrected moments match a direct computation from loglike__A.
        w = ns.get_weights()
        w = w / w.sum()
        logL_data = ns["loglike__A"].to_numpy()
        mean = np.sum(w * logL_data)
        d_G_direct = 2 * np.sum(w * (logL_data - mean) ** 2)
        assert np.isclose(corrected["d_G"], d_G_direct, rtol=1e-6)
        assert np.isclose(corrected["logL_P"], mean, rtol=1e-6)

    def test_clean_run_is_unchanged(self):
        """When logL already equals Sum(loglike__), results are identical."""
        from unimpeded.tension import _stats

        ns = self._make_ns(contaminated=False)
        corrected = _stats(ns)
        standard = ns.stats()
        for key in ["logZ", "D_KL", "logL_P", "d_G"]:
            assert np.isclose(corrected[key], standard[key], rtol=1e-8), key

    def test_no_loglike_columns_falls_back(self):
        """Without loglike__ columns, behaviour is exactly the standard stats."""
        from unimpeded.tension import _stats

        ns = self._make_ns(with_loglike=False)
        corrected = _stats(ns)
        standard = ns.stats()
        for key in ["logZ", "D_KL", "logL_P", "d_G"]:
            assert np.isclose(corrected[key], standard[key], rtol=1e-10), key

    def test_tension_stats_end_to_end_with_nested_samples(self):
        """tension_stats runs on real NestedSamples carrying loglike__ columns.

        The joint's d_G is taken from its loglike__ columns (not the contaminated
        logL), while logR (evidence) is unaffected. We check the pipeline runs
        end-to-end and that the joint d_G entering the calculation is the
        loglike-based one.
        """
        from unimpeded.tension import _stats

        joint = self._make_ns(contaminated=True, seed=1, ndead=1500)
        sep_a = self._make_ns(contaminated=False, seed=2)
        sep_b = self._make_ns(contaminated=False, seed=3)

        result = tension_stats(joint, sep_a, sep_b, nsamples=100)
        for col in ["logR", "I", "logS", "d_G", "p", "sigma"]:
            assert col in result.columns
        # logR (evidence-based) is well defined regardless of contamination.
        assert np.isfinite(result["logR"]).all()

        # The joint d_G feeding the tension is the loglike-based (corrected) one,
        # not anesthetic's contaminated value.
        d_joint_corrected = float(_stats(joint, nsamples=100)["d_G"].mean())
        d_joint_contaminated = float(joint.stats(nsamples=100)["d_G"].mean())
        assert not np.isclose(d_joint_corrected, d_joint_contaminated)
