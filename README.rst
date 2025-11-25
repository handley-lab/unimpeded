===========================================================================================
unimpeded: Universal model comparison & parameter estimation distributed over every dataset
===========================================================================================
:unimpeded: Universal model comparison & parameter estimation distributed over every dataset 

:Author: Dily Ong & Will Handley
:Version: 1.0.0
:Homepage: https://github.com/handley-lab/unimpeded
:Documentation: http://unimpeded.readthedocs.io/

.. image:: https://github.com/handley-lab/unimpeded/workflows/CI/badge.svg?branch=master
   :target: https://github.com/handley-lab/unimpeded/actions?query=workflow%3ACI+branch%3Amaster
   :alt: Build Status
.. image:: https://codecov.io/gh/handley-lab/unimpeded/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/handley-lab/unimpeded
   :alt: Test Coverage Status
.. image:: https://readthedocs.org/projects/unimpeded/badge/?version=latest
   :target: https://unimpeded.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://badge.fury.io/py/unimpeded.svg
   :target: https://badge.fury.io/py/unimpeded
   :alt: PyPi location
.. image:: https://zenodo.org/badge/532924237.svg
   :target: https://zenodo.org/badge/latestdoi/532924237
   :alt: Permanent DOI for this release
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/handley-lab/unimpeded/blob/master/LICENSE
   :alt: License information

``unimpeded`` is a Python package providing access to a comprehensive database of nested sampling and MCMC chains for cosmological analysis. It can be viewed as an extension to the Planck legacy archive across multiple models and datasets.

The package provides:

- **Public Nested Sampling Database**: Pre-computed chains for 8 cosmological models across 39 datasets
- **Tension Statistics Calculator**: Six tension quantification metrics with proper nested sampling corrections
- **Zenodo Integration**: Automated archival and retrieval with permanent DOIs
- **Analysis Tools**: Built on anesthetic for visualization and statistical analysis

Features
--------

Installation
------------

``unimpeded`` can be installed via pip

.. code:: bash

    pip install unimpeded

or via the setup.py

.. code:: bash

    git clone https://github.com/handley-lab/unimpeded
    cd unimpeded
    python -m pip install .

You can check that things are working by running the test suite:

.. code:: bash

    export MPLBACKEND=Agg     # only necessary for OSX users
    python -m pytest
    flake8 unimpeded tests
    pydocstyle --convention=numpy unimpeded


Dependencies
~~~~~~~~~~~~

Basic requirements:

- Python 3.6+
- `anesthetic <https://pypi.org/project/anesthetic/>`__

Documentation:

- `sphinx <https://pypi.org/project/Sphinx/>`__
- `numpydoc <https://pypi.org/project/numpydoc/>`__

Tests:

- `pytest <https://pypi.org/project/pytest/>`__

Documentation
-------------

Full Documentation is hosted at `ReadTheDocs <http://unimpeded.readthedocs.io/>`__.  To build your own local copy of the documentation you'll need to install `sphinx <https://pypi.org/project/Sphinx/>`__. You can then run:

.. code:: bash

    python -m pip install ".[all,docs]"
    cd docs
    make html

and view the documentation by opening ``docs/build/html/index.html`` in a browser. To regenerate the automatic RST files run:

.. code:: bash

    sphinx-apidoc -fM -t docs/templates/ -o docs/source/ unimpeded/

Citation
--------

If you use ``unimpeded`` in your research, please cite the following papers:

**For the software and database:**

.. code:: bibtex

   @article{Ong2025unimpeded,
       author = {Ong, Dily Duan Yi and Handley, Will},
       title = {unimpeded: A Public Nested Sampling Database for Bayesian Cosmology},
       journal = {Journal of Open Source Software},
       year = {2025},
       note = {arXiv:2511.05470}
   }

**For the tension statistics methodology:**

.. code:: bibtex

   @article{Ong2025tension,
       author = {Ong, Dily Duan Yi and Handley, Will},
       title = {Tension statistics for nested sampling},
       journal = {arXiv e-prints},
       year = {2025},
       eprint = {2511.04661},
       archivePrefix = {arXiv},
       primaryClass = {astro-ph.CO}
   }

Links:

- Software paper: `arXiv:2511.05470 <https://arxiv.org/abs/2511.05470>`__
- Tension statistics: `arXiv:2511.04661 <https://arxiv.org/abs/2511.04661>`__


Contributing
------------
There are many ways you can contribute via the `GitHub repository <https://github.com/handley-lab/unimpeded>`__.

- You can `open an issue <https://github.com/handley-lab/unimpeded/issues>`__ to report bugs or to propose new features.
- Pull requests are very welcome. Note that if you are going to propose major changes, be sure to open an issue for discussion first, to make sure that your PR will be accepted before you spend effort coding it.
- Adding models and data to the grid. Contact `Will Handley <mailto:wh260@cam.ac.uk>`__ to request models or ask for your own to be uploaded.


Questions/Comments
------------------
