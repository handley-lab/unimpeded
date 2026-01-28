Installation
============

``unimpeded`` can be installed in several ways depending on your use case.

Quick Install
-------------

For most users, a simple pip install is sufficient:

.. code:: bash

    pip install unimpeded

Installation from Source
-------------------------

To install the latest development version from GitHub:

.. code:: bash

    git clone https://github.com/handley-lab/unimpeded.git
    cd unimpeded
    python -m pip install .

For an editable installation (useful for development):

.. code:: bash

    git clone https://github.com/handley-lab/unimpeded.git
    cd unimpeded
    pip install -e .

Using Virtual Environments
---------------------------

It is strongly recommended to install ``unimpeded`` in a virtual environment to avoid package conflicts and maintain reproducibility.

Python venv
~~~~~~~~~~~

.. code:: bash

    # Create a virtual environment
    python -m venv venv_unimpeded

    # Activate the virtual environment
    # On macOS/Linux:
    source venv_unimpeded/bin/activate
    # On Windows:
    # venv_unimpeded\Scripts\activate

    # Install unimpeded
    pip install unimpeded

Conda
~~~~~

``unimpeded`` is also available via conda:

.. code:: bash

    # Create a conda environment
    conda create -n unimpeded_env python=3.9

    # Activate the environment
    conda activate unimpeded_env

    # Install from conda-forge
    conda install -c handley-lab unimpeded

    # Or install via pip
    pip install unimpeded

Jupyter Notebook Setup
----------------------

For users who want to use the tutorial Jupyter notebook, please refer to `JUPYTER_SETUP.md <https://github.com/handley-lab/unimpeded/blob/master/JUPYTER_SETUP.md>`_ in the repository for comprehensive setup instructions including platform-specific guidance.

Dependencies
------------

Basic requirements:

- Python 3.8+
- `anesthetic <https://pypi.org/project/anesthetic/>`__
- `requests <https://pypi.org/project/requests/>`__

Optional dependencies for documentation:

- `sphinx <https://pypi.org/project/Sphinx/>`__
- `numpydoc <https://pypi.org/project/numpydoc/>`__

Optional dependencies for testing:

- `pytest <https://pypi.org/project/pytest/>`__
- `pytest-cov <https://pypi.org/project/pytest-cov/>`__
- `flake8 <https://pypi.org/project/flake8/>`__
- `pydocstyle <https://pypi.org/project/pydocstyle/>`__

Verifying Installation
----------------------

You can verify that ``unimpeded`` is installed correctly by running:

.. code:: python

    import unimpeded
    print(unimpeded.__version__)

Testing
-------

To run the test suite:

.. code:: bash

    export MPLBACKEND=Agg     # only necessary for macOS users
    python -m pytest

To check code style:

.. code:: bash

    flake8 unimpeded tests
    pydocstyle --convention=numpy unimpeded
