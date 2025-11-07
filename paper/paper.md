---
title: 'unimpeded: A Public Nested Sampling Database for Cosmology'
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
date: 01 November 2025
bibliography: paper.bib
---

# Summary

Bayesian inference is central to modern cosmology. While parameter estimation is achievable with unnormalised posteriors traditionally obtained via MCMC methods, comprehensive model comparison and tension quantification require Bayesian evidences and normalised posteriors, which remain computationally prohibitive for many researchers. To address this, we present `unimpeded`, a publicly available Python library and data repository providing DiRAC-funded (DP192 and 264) pre-computed nested sampling and MCMC chains with their normalised posterior samples, computed using `Cobaya` [@Torrado2021] and the Boltzmann solver CAMB [@Lewis1999; @Lewis2002]. `unimpeded` delivers systematic analysis across a grid of eight cosmological models (including ΛCDM and seven extensions) and 39 modern cosmological datasets (comprising individual probes and their pairwise combinations). The built-in tension statistics calculator enables rapid computation of six tension quantification metrics. All chains are hosted on Zenodo with permanent access via the `unimpeded` API, analogous to the renowned Planck Legacy Archive [@Dupac2015] but utilising nested sampling [@Skilling2006] rather than traditional MCMC methods.

# Motivation

With the advancement of observational cosmology, more cosmological datasets have become available and revealed tensions, such as the Hubble tension [@Verde2019], $\sigma_8$ tension [@Joudaki2017], and $\Omega_K$ tension [@Handley2021; @DiValentino2020]. Our standard model of cosmology faces several significant challenges, giving rise to alternative models additional to the baseline ΛCDM model, aiming to better understand our universe. We need a systematic exploration across a wide range of models and datasets to accurately quantify tension when comparing and combining datasets under different cosmological models.

The Planck Legacy Archive (PLA) [@Dupac2015] provides a trusted set of MCMC chains that have become a cornerstone for cosmological analysis. However, MCMC is primarily designed for parameter estimation and is inefficient at calculating the Bayesian evidence, and hence normalised posteriors, which are the key quantities for model comparison and tension quantification. Nested sampling algorithms [@Feroz2009; @Handley2015a; @Speagle2020] compute the evidence as a primary output, making them the superior tool. Despite their advantages, nested sampling runs are computationally expensive, creating a significant barrier for many researchers. Furthermore, the lack of a centralised, public archive for nested sampling products has hampered reproducibility and large-scale comparative studies.

# unimpeded

`unimpeded` addresses these challenges directly. It provides a pip-installable tool that leverages the `anesthetic` package [@Handley2019] for analysis and introduces a seamless Zenodo integration for data management. The nested sampling theory and methodology are detailed in Ong & Handley (2025). Its main features are:

1.  **A Public Nested Sampling Grid:** The package provides access to a pre-computed grid of nested sampling chains for 8 cosmological models (standard $\Lambda$CDM and seven extensions), run against 39 datasets (comprising individual probes and their pairwise combinations). This saves the community significant computational resources and provides a common baseline for new analyses. Evidence and Kullback-Leibler divergence can be calculated jointly with `anesthetic` for model comparison and quantifying the constraining power of datasets and models, respectively. The scientific results from this grid are presented in Ong & Handley (in prep).
2.  **Archival and Reproducibility via Zenodo:** `unimpeded` automates the process of archiving analysis products. The `DatabaseCreator` class bundles chains and metadata, uploading them to a Zenodo community to generate a permanent, citable Digital Object Identifier (DOI). The `DatabaseExplorer` class allows public user to easily download and analyse these chains, promoting open science and effortless reproducibility. Figure 1 illustrates the `unimpeded` ecosystem, showing how the tool connects data generation (HPC sampling), archival (Zenodo), and analysis (`anesthetic`) workflows.
3.  **Tension Statistics Calculator:** With the nested sampling chains and the built-in tension statistics calculator, six tension quantification metrics with different characteristics are available, including the $R$ statistic, information ratio $I$, suspiciousness $S$, Gaussian model dimensionality $d_G$, tension significance in units of $\sigma$, and p-value. Each of them has unique characteristics optimised for different tasks, thoroughly discussed in Ong & Handley (2025). `unimpeded` implements these statistics with the necessary F-correction to account for discarded prior volume [@Handley2019a; @Handley2021]. Figure 2 demonstrates the tension calculator output showing p-value derived tension significance ($\sigma$) for 31 pairwise dataset combinations across 8 cosmological models, sorted by significance to highlight the most problematic dataset pairs.

![The `unimpeded` ecosystem and workflow. At the centre, `unimpeded` manages data archival and retrieval through Zenodo, providing permanent DOIs and public access to pre-computed chains. For data generation, `unimpeded` configures YAML files for resource-intensive HPC nested sampling using `Cobaya`, `PolyChord`, and `CAMB`. For analysis, users download chains via `DatabaseExplorer` and leverage `anesthetic` for visualisation (corner plots, posterior distributions, constraint contours) and tension quantification (six metrics: $R$ statistic, information ratio $I$, suspiciousness $S$, Bayesian model dimensionality $d_G$, significance $\sigma$, and $p$-value).\label{fig:workflow}](flowchart.pdf)

![Tension analysis heatmap produced by `unimpeded` displaying p-value derived tension significance ($\sigma$ values) for 31 pairwise dataset combinations across 8 cosmological models. Rows are sorted by significance, with the most problematic dataset pairs (highest tension) at the top. This demonstrates `unimpeded`'s capability to systematically quantify tensions and their model dependence.\label{fig:tension_heatmap}](tension_stats_p_sorted_by_p.pdf)

While tools like `getdist` [@Lewis2019] are excellent for MCMC analysis, and frameworks like `CosmoSIS` [@Zuntz2015] or `MontePython` [@Brinckmann2019] are used for running simulations with samplers like `Cobaya` [@Torrado2021], `unimpeded` fills a unique niche. It is not a sampler but a high-level analysis and database management tool that extends the capabilities of its underlying engine, `anesthetic`, to create a public, reproducible, and statistically robust nested sampling resource for the cosmology community.

The package is fully documented, tested, and available for installation via the Python Package Index (PyPI).

# Acknowledgements

We thank the developers of the open-source packages that this work relies upon, including `anesthetic`, `numpy`, `scipy`, `pandas`, and `corner.py`. This work was performed using the Cambridge Service for Data Driven Discovery (CSD3), operated by the University of Cambridge Research Computing Service, provided by Dell EMC and Intel using Tier-2 funding from the Engineering and Physical Sciences Research Council (capital grant EP/P020259/1), and DiRAC funding from the Science and Technology Facilities Council (www.dirac.ac.uk).

# References
