Installation
============

Using Virtual Environments
---------------------------

It is **strongly recommended** to install ``unimpeded`` in a virtual environment to avoid package conflicts and maintain reproducibility.

Virtual environments provide isolated Python environments for your projects, ensuring that dependencies for different projects don't interfere with each other. This is considered best practice in Python development.

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
    conda create -n unimpeded_env python=3.10

    # Activate the environment
    conda activate unimpeded_env

    # Install from conda-forge
    conda install -c handley-lab unimpeded

    # Or install via pip
    pip install unimpeded

Quick Install
-------------

If you prefer not to use a virtual environment, you can install ``unimpeded`` directly:

.. code:: bash

    pip install unimpeded

**Note:** While this method works, using a virtual environment is strongly recommended for better package management and reproducibility.

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

Jupyter Notebook Tutorial
-------------------------

A tutorial notebook is available to help you get started. After installing ``unimpeded``, download the notebook:

.. code:: bash

    download-unimpeded-tutorial

Then install Jupyter and launch the notebook:

.. code:: bash

    pip install jupyter
    launch-unimpeded-tutorial

Troubleshooting
~~~~~~~~~~~~~~~

``jupyter: command not found``
    Make sure you've installed jupyter:

    .. code:: bash

        pip install jupyter

``ModuleNotFoundError: No module named 'unimpeded'``
    Make sure you've installed unimpeded in your active virtual environment:

    .. code:: bash

        pip install unimpeded

Old pip version causing installation errors
    Upgrade pip first:

    .. code:: bash

        python -m pip install --upgrade pip

Windows: Cannot run scripts (PowerShell execution policy)
    Enable script execution temporarily:

    .. code:: powershell

        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

Dependencies
------------

Basic requirements:

- Python 3.10+
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
