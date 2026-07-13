from functools import cache

import numpy as np
from anesthetic.samples import NestedSamples, Samples
from anesthetic.tension import tension_stats as anesthetic_tension_stats
from scipy.special import erfcinv
from scipy.stats import chi2

from unimpeded.database import DatabaseExplorer


def _loglike_columns(data):
    """Return the per-experiment ``loglike__*`` columns of a run, if any.

    Cobaya stores the log-likelihood of each experiment in a
    ``loglike__<name>`` column; their sum is the pure data log-likelihood.
    This is the quantity the suspiciousness ``logS`` and the Bayesian model
    dimensionality ``d_G`` are defined in terms of. Returns an empty list when
    no such columns are present.
    """
    cols = []
    for c in data.columns:
        name = c[0] if isinstance(c, tuple) else c
        if isinstance(name, str) and name.startswith("loglike__"):
            cols.append(c)
    return cols


def _stats(data, nsamples=None, beta=None):
    r"""Nested sampling stats using the *data* likelihood for the moments.

    Identical to :meth:`anesthetic.samples.NestedSamples.stats` except that the
    posterior-averaged log-likelihood ``logL_P``, the Kullback--Leibler
    divergence ``D_KL`` and the Bayesian model dimensionality ``d_G`` are
    computed from the summed ``loglike__*`` columns (the pure data
    log-likelihood) instead of the ``logL`` column. The evidence ``logZ`` and
    the posterior weights are still taken from the run's ``logL`` column, so the
    evidence -- and hence ``logR`` -- is unchanged.

    This matters for chains produced by stock Cobaya's PolyChord wrapper, whose
    stored ``logL`` column is ``loglike + logprior + logvolume`` rather than the
    pure likelihood: using it for the moments injects the prior's variance into
    ``d_G`` and its mean into ``logS``. Because ``d_G`` and ``logS`` are by
    definition data-likelihood moments, summing the ``loglike__*`` columns is
    the correct choice for *every* run -- for chains where ``logL`` already
    equals the summed likelihoods (the vast majority) this returns identical
    results. Falls back to the standard computation when no ``loglike__*``
    columns are present, or for array-valued ``beta``.
    """
    loglike_cols = _loglike_columns(data)
    if not loglike_cols or np.ndim(beta) > 0:
        return data.stats(nsamples=nsamples, beta=beta)

    # Evidence and posterior weights from the run's own logL column: correct,
    # because the evidence integral legitimately includes the prior.
    logw = data.logw(nsamples, beta)
    if nsamples is None and beta is None:
        samples = data._constructor_sliced(index=data.columns[:0], dtype=float)
    else:
        samples = Samples(index=logw.columns, columns=data.columns[:0])
    samples["logZ"] = data.logZ(logw)
    samples.set_label("logZ", r"$\ln\mathcal{Z}$")
    w = np.exp(logw - samples["logZ"])

    # Likelihood moments from the summed per-experiment loglike__ columns.
    beta_val = data.beta if beta is None else beta
    betalogL = beta_val * data[loglike_cols].sum(axis=1)
    S = (logw * 0).add(betalogL, axis=0) - samples.logZ

    samples["D_KL"] = (S * w).sum()
    samples.set_label("D_KL", r"$\mathcal{D}_\mathrm{KL}$")
    samples["logL_P"] = samples["logZ"] + samples["D_KL"]
    samples.set_label("logL_P", r"$\langle\ln\mathcal{L}\rangle_\mathcal{P}$")
    samples["d_G"] = ((S - samples.D_KL) ** 2 * w).sum() * 2
    samples.set_label("d_G", r"$d_\mathrm{G}$")
    samples.label = data.label
    return samples


def tension_stats(
    joint, *separate, joint_f=1.0, separate_fs=None, nsamples=None, beta=None
):
    r"""Compute tension statistics between two or more samples.

    With the Bayesian (log-)evidence ``logZ``, Kullback--Leibler divergence
    ``D_KL``, posterior average of the log-likelihood ``logL_P``, Gaussian
    model dimensionality ``d_G``, and correction factors ``F`` for discarded
    prior samples, we can compute tension statistics between two or more
    samples (example here for simplicity just with two datasets A and B):

    - ``logR``: R statistic for dataset consistency

      .. math::
        \log R = \log Z_{AB} - \log Z_{A} - \log Z_{B}

    - ``I``: mutual information estimate between data and params

      .. math::
        \mathcal{I} = D_{KL}^{A} + D_{KL}^{B} - D_{KL}^{AB}

    - ``logS``: suspiciousness

      .. math::
        \log S = \log L_{AB} - \log L_{A} - \log L_{B}

    - ``d_G``: Gaussian model dimensionality of shared constrained parameters

      .. math::
        d = d_{A} + d_{B} - d_{AB}

    - ``p``: p-value for the tension between two samples

      .. math::
        p = \int_{d-2\log{S}}^{\infty} \chi^2_d(x) dx

    - ``sigma``: tension quantification in terms of numbers of sigma
      calculated from p

      .. math::
        \sqrt{2} \rm{erfc}^{-1}(p)

    Parameters
    ----------
    joint : :class:`anesthetic.samples.Samples`
        Bayesian stats from a nested sampling run using all the datasets from
        the list in ``separate`` jointly. This can be a ``stats`` object
        or a :class:`anesthetic.samples.NestedSamples` object.

    *separate
        A variable number of Bayesian stats from independent nested sampling
        runs using various datasets (A, B, ...) separately. Each can be a
        ``stats`` object or a :class:`anesthetic.samples.NestedSamples`
        object.

    joint_f : float, optional
        Correction factor `F = nprior / ndiscarded` for the `joint` sample.
        Defaults to 1.0 (no correction).

    separate_fs : list or tuple of float, optional
        A list of correction factors `F` for each of the `separate` samples.
        If None, defaults to 1.0 for all. The order is irrelevant.

    nsamples : int, optional
        - If nsamples is not supplied, calculate mean value.
        - If nsamples is an integer, draw nsamples from the distribution of
          values inferred by nested sampling. This is only used if the inputs
          are :class:`anesthetic.samples.NestedSamples` objects.

    beta : float, array-like, default=1
        Inverse temperature(s) `beta=1/kT`. This is only used if the inputs
        are :class:`anesthetic.samples.NestedSamples` objects.


    Returns
    -------
    samples : :class:`anesthetic.samples.Samples`
        DataFrame containing the following tension statistics in columns:
        ['logR', 'I', 'logS', 'd_G', 'p', 'sigma']
    """
    columns = ["logZ", "D_KL", "logL_P", "d_G"]

    def get_stats(data):
        if isinstance(data, NestedSamples) and not set(columns).issubset(data.columns):
            return _stats(data, nsamples=nsamples, beta=beta)
        return data

    joint_stats = get_stats(joint)
    separate_stats = [get_stats(s) for s in separate]

    # Call the original anesthetic function with the stats DataFrames
    samples = anesthetic_tension_stats(joint_stats, *separate_stats)

    if separate_fs is None:
        separate_fs = [1.0] * len(separate)
    elif len(separate_fs) != len(separate):
        raise ValueError(
            f"The number of 'separate_fs' ({len(separate_fs)}) must match "
            f"the number of 'separate' samples ({len(separate)})."
        )

    log_f_joint = np.log(joint_f)
    log_f_separate_sum = np.sum([np.log(f) for f in separate_fs])
    log_F_correction = log_f_joint - log_f_separate_sum

    # Apply the corrections
    samples["logR"] += log_F_correction
    samples["I"] += log_F_correction

    # The p-value and tension calculations from the second snippet
    p = chi2.sf(samples["d_G"] - 2 * samples["logS"], df=samples["d_G"])
    samples["p"] = p
    samples.set_label("p", "$p$")

    samples["sigma"] = erfcinv(p) * np.sqrt(2)
    samples.set_label("sigma", r"$\sigma$")

    return samples


@cache
def download_tension_inputs(method, model, *datasets):
    """
    Automates the downloading and preparation of data for tension_stats.
    Accepts any number of datasets (2 or more).

    This function is cached. The download process will only run once for
    each unique combination of method, model, and datasets. Subsequent
    calls with the same arguments will return the stored result instantly.
    """
    dbe = DatabaseExplorer()
    # The joint dataset name is a '+' separated string of the sorted dataset names.
    joint_dataset_name = "+".join(sorted(datasets))

    print("---")
    print(f"Running Data Preparation for ({method}, {model}, {datasets})")
    print("This should only appear ONCE for each set of inputs.")
    print("Downloading required files...")

    # Download samples and prior info for each individual dataset
    separate_samples = [dbe.download_samples(method, model, ds) for ds in datasets]
    separate_prior_info = [dbe.download_prior_info(model, ds) for ds in datasets]

    # Download for the joint dataset
    samples_joint = dbe.download_samples(method, model, joint_dataset_name)
    prior_info_joint = dbe.download_prior_info(model, joint_dataset_name)

    print("Downloads complete. Caching results.")
    print("---")

    # Calculate F factors for separate datasets
    fs_separate = [info["nprior"] / info["ndiscarded"] for info in separate_prior_info]
    # Calculate F factor for the joint dataset
    f_joint = prior_info_joint["nprior"] / prior_info_joint["ndiscarded"]

    return {
        "joint": samples_joint,
        "separate": separate_samples,
        "joint_f": f_joint,
        "separate_fs": fs_separate,
    }


def tension_calculator(method, model, *datasets, nsamples=None, beta=None):
    """
    High-level calculator for tension statistics directly from dataset names.
    Accepts any number of datasets (2 or more).
    """
    print(f"Starting tension calculation with nsamples={nsamples}...")

    # This call is now cached. It will be slow the first time, and
    # instantaneous every time after.
    # The *datasets tuple is unpacked into individual arguments for the call.
    tension_args = download_tension_inputs(method, model, *datasets)

    # We need to copy the dictionary because we will be modifying it,
    # and we don't want to alter the cached object.
    args_for_this_run = tension_args.copy()

    joint_arg = args_for_this_run.pop("joint")
    separate_arg_list = args_for_this_run.pop("separate")

    print("Data retrieved from cache (if not first run). Passing to tension_stats...")
    return tension_stats(
        joint_arg,
        *separate_arg_list,  # Unpacks the list of separate samples
        nsamples=nsamples,
        beta=beta,
        **args_for_this_run,  # Passes remaining args like joint_f, separate_fs
    )
