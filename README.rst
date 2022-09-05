==================================================================================
unimpeded: Universal model comparison & parameter estimation over diverse datasets
==================================================================================
:unimpeded: Universal model comparison & parameter estimation over diverse datasets
:Author: Will Handley
:Version: 1.0.0a0
:Homepage: https://github.com/handley-lab/unimpeded
:Documentation: http://unimpeded.readthedocs.io/

.. image:: https://github.com/handley-lab/unimpeded/workflows/CI/badge.svg?branch=master
   :target: https://github.com/handley-lab/unimpeded/actions?query=workflow%3ACI+branch%3Amaster
   :alt: Build Status
.. image:: https://codecov.io/gh/handley-lab/unimpeded/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/handley-lab/unimpeded
   :alt: Test Coverage Status
.. image:: https://readthedocs.org/projects/anesthetic/badge/?version=latest
   :target: https://anesthetic.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://badge.fury.io/py/anesthetic.svg
   :target: https://badge.fury.io/py/anesthetic
   :alt: PyPi location
.. image:: https://zenodo.org/badge/175663535.svg
   :target: https://zenodo.org/badge/latestdoi/175663535
   :alt: Permanent DOI for this release
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/handley-lab/unimpeded/blob/master/LICENSE
   :alt: License information





``unimpeded`` 

It can be viewed as an extension to the Planck legacy archive across models and datasets

It provides mcmc and nested sampling chains, allowing parameter estimation, model comparison and tension quantification.

Current functionality includes:


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
    cd anesthetic
    python setup.py install --user

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

   cd docs
   make html


Citation
--------

If you use ``unimpeded`` to generate plots for a publication, please cite
as: ::

   Handley, (2023) unimpeded: cosmological inference across models and datasets. 

or using the BibTeX:

.. code:: bibtex

   @article{unimpeded,
       year  = {2023},
       author = {Will Handley},
       title = {unimpeded: cosmological inference across models and datasets},
       journal = {In preparation}
   }


Contributing
------------
There are many ways you can contribute via the `GitHub repository <https://github.com/handley-lab/unimpeded>`__.

- You can `open an issue <https://github.com/handley-lab/unimpeded/issues>`__ to report bugs or to propose new features.
- Pull requests are very welcome. Note that if you are going to propose major changes, be sure to open an issue for discussion first, to make sure that your PR will be accepted before you spend effort coding it.
- Adding models and data to the grid. Contact `Will Handley <mailto:wh260@cam.ac.uk>`__ to request models or ask for your own to be uploaded.


Questions/Comments
------------------
