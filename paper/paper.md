---
title: 'unimpeded: A Public Nested Sampling Database for Bayesian Cosmology'
tags:
  - Python
  - cosmology
  - Bayesian inference
  - nested sampling
  - data analysis
  - model comparison
  - Zenodo
authors:
  - name: Dily Duan Yi Ong
    orcid: 0009-0004-8688-5088
    affiliation: "1, 2, 3"
    corresponding: true
  - name: Will Handley
    orcid: 0000-0002-5866-0445
    affiliation: "1, 2"
affiliations:
 - name: Kavli Institute for Cosmology, Madingley Road, Cambridge, CB3 0HA, UK
   index: 1
 - name: Astrophysics Group, Cavendish Laboratory, J.J. Thomson Avenue, Cambridge, CB3 0HE, UK
   index: 2
 - name: Newnham College, Sidgwick Avenue, Cambridge, CB3 9DF, UK
   index: 3
date: 30 May 2026
bibliography: paper.bib
---

# Summary

Bayesian inference is central to modern cosmology. While parameter estimation is achievable with unnormalised posteriors traditionally obtained via MCMC methods, comprehensive model comparison and tension quantification require Bayesian evidences and normalised posteriors, which remain computationally prohibitive for many researchers. To address this, we present `unimpeded`, a publicly available Python library and data repository providing pre-computed nested sampling and MCMC chains with their normalised posterior samples, computed using `Cobaya` [@Torrado2021] and the Boltzmann solver CAMB [@Lewis1999; @Lewis2002]. `unimpeded` delivers a public grid of nested-sampling chains across eight cosmological models (ΛCDM and seven extensions) and 12 modern cosmological surveys. The pairwise and triplet combinations of these surveys form 77 dataset configurations, totalling 616 (model, dataset) chains. Producing this grid required more than 12 million CPU hours, supported by UKRI DiRAC grants DP192 and DP264. The built-in tension statistics calculator enables rapid computation of five tension quantification metrics. All chains are hosted on Zenodo^[https://zenodo.org/] with permanent access via the `unimpeded` API, analogous to the renowned Planck Legacy Archive [@Dupac2015] but utilising nested sampling [@Skilling2006] in addition to traditional MCMC methods.

# Statement of need

`unimpeded` addresses these challenges directly. It provides a pip-installable tool that leverages the `anesthetic` package [@Handley2019] for analysis and introduces a seamless Zenodo integration for data management. The nested sampling theory and methodology are detailed in [@Ong2025].

The package is fully documented, tested, and available for installation via the Python Package Index (PyPI), as well as conda-forge and the Arch User Repository (AUR). A Jupyter notebook tutorial is also available to help users get started.

# State of the field

While tools like `getdist` [@Lewis2019] are excellent for MCMC analysis, and frameworks like `CosmoSIS` [@Zuntz2015] or `MontePython` [@Brinckmann2019] are used for running simulations with samplers like `Cobaya` [@Torrado2021], `unimpeded` fills a unique niche. It is not a sampler but a high-level analysis and database management tool that extends the capabilities of its underlying engine, `anesthetic`, to create a public, reproducible, and statistically robust nested sampling resource for the cosmology community.

# Software design

1.  **A Public Nested Sampling Grid:** The package provides access to a pre-computed grid of nested sampling chains and MCMC chains for 8 cosmological models (standard $\Lambda$CDM and seven extensions), run against 77 datasets (the pairwise and triplet combinations of 12 modern cosmological surveys). This saves the community significant computational resources and provides a common baseline for new analyses. Evidence and Kullback-Leibler divergence can be calculated jointly with `anesthetic` for model comparison and quantifying the constraining power of datasets and models, respectively. The scientific results from this grid are presented in [@Ong2025].
2.  **Archival and Reproducibility via Zenodo:** `unimpeded` automates the process of archiving analysis products. The `DatabaseCreator` class bundles chains and metadata, uploading them to a Zenodo community to generate a permanent, citable Digital Object Identifier (DOI). The `DatabaseExplorer` class allows public user to easily download and analyse these chains, promoting open science and effortless reproducibility. Figure 1 illustrates the `unimpeded` ecosystem, detailing its three core functions. For data generation, it configures YAML files for HPC nested sampling. It then archives the chains on Zenodo, ensuring reproducibility with permanent DOIs, and finally provides an interface for post-processing analysis and visualisation with `anesthetic`. The following example demonstrates downloading chains:
```python
from unimpeded.database import DatabaseExplorer

# Initialise DatabaseExplorer
dbe = DatabaseExplorer()

# Get a list of currently available models and datasets
models_list = dbe.models
datasets_list = dbe.datasets

# Choose model, dataset and sampling method
method = 'ns'  # 'ns' for nested sampling, 'mcmc' for MCMC
model = "klcdm"  # from models_list
dataset = "des_y1.joint+planck_2018_CamSpec"  # from datasets_list

# Download samples chain
samples = dbe.download_samples(method, model, dataset)

# Download Cobaya and PolyChord run settings
info = dbe.download_info(method, model, dataset)
```
3.  **Tension Statistics Calculator:** With the nested sampling chains and the built-in tension statistics calculator, five tension quantification metrics with different characteristics are available, including the $R$ statistic, information ratio $I$, suspiciousness $S$, Gaussian model dimensionality $d_G$, and $p$-value $\sigma$. Each of them has unique characteristics optimised for different tasks, thoroughly discussed in [@Ong2025]. `unimpeded` implements these statistics with the necessary correction to account for discarded prior volume [@Ong2025; @Handley2019a; @Handley2021]. Figure 2 demonstrates the tension calculator output showing p-value derived tension significance ($\sigma$) for 31 pairwise dataset combinations across 8 cosmological models, sorted by significance to highlight the datasets in tension. Caution should be exercised when combining them. The following minimal example demonstrates the usage:
```python
from unimpeded.tension import tension_calculator

tension_samples = tension_calculator(method='ns',
                                      model='lcdm',
                                      datasetA='planck_2018_CamSpec',
                                      datasetB='des_y1.joint',
                                      nsamples=1000)
```

![The `unimpeded` ecosystem and workflow. At the centre, `unimpeded` manages data archival and retrieval through Zenodo, providing permanent DOIs and public access to pre-computed chains. For data generation, `unimpeded` configures YAML files for resource-intensive HPC nested sampling using `Cobaya`, `PolyChord`, and `CAMB`. For analysis, users download chains via `DatabaseExplorer` and leverage `anesthetic` for visualisation (corner plots, posterior distributions, constraint contours) and tension quantification (five metrics: $R$ statistic, information ratio $I$, suspiciousness $S$, Bayesian model dimensionality $d_G$, and $p$-value $\sigma$).\label{fig:workflow}](flowchart.pdf)

# Research impact statement

The methodology underlying `unimpeded`'s tension statistics is presented in [@Ong2025] (8 citations to date). The software and data grid are described in a companion preprint [@Ong2025unimpeded] (5 citations since release six months ago). The database has been used in [@Ong2026desi] (12 citations) to analyse the Dark Energy Spectroscopic Instrument (DESI) DR2 data, and in [@Ong2025dark] (19 citations) to perform a Bayesian analysis of evidence for evolving dark energy. The scale of the data product — 616 (model, dataset) chain combinations produced using more than 12 million CPU hours — represents a significant contribution of computational resources to the community. Figure 2 shows an example of a scientific result produced with the package: a heatmap of tension significances across 31 dataset pairs and 8 cosmological models, which systematically identifies points of tension in current cosmological data.

![Tension analysis heatmap produced by `unimpeded` and `anesthetic` displaying p-value derived tension significance ($\sigma$ values) for 31 pairwise dataset combinations across 8 cosmological models. Rows are sorted by significance, with the most problematic dataset pairs (highest tension) at the top. This demonstrates `unimpeded`'s capability to systematically quantify tensions and their model dependence.\label{fig:tension_heatmap}](tension_stats_p_sorted_by_p.pdf)

# AI Usage Disclosure

The core `unimpeded` package was written by the human authors prior to the availability of Claude Code. Anthropic's Claude Code (Claude Opus 4.7) was later used for a limited set of targeted contributions: small additions to `unimpeded.database`, writing unit tests for those additions, and drafting workflow documentation. All AI-assisted outputs were reviewed, edited, and validated by the human authors, who retained all core design decisions.

# Acknowledgements

We thank the developers of the open-source packages that this work relies upon, including `anesthetic`, `numpy`, `scipy`, `pandas`, and `corner.py`. This work was performed using the Cambridge Service for Data Driven Discovery (CSD3), operated by the University of Cambridge Research Computing Service, provided by Dell EMC and Intel using Tier-2 funding from the Engineering and Physical Sciences Research Council (capital grant EP/P020259/1), and DiRAC funding from the Science and Technology Facilities Council (www.dirac.ac.uk).

# References
