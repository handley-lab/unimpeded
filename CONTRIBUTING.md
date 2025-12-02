# Contributing to unimpeded

Thank you for your interest in contributing to `unimpeded`! We welcome contributions from the community.

## Ways to Contribute

### Reporting Bugs

If you find a bug, please [open an issue](https://github.com/handley-lab/unimpeded/issues) with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected vs actual behavior
- Your environment (OS, Python version, `unimpeded` version)
- Any relevant code snippets or error messages

### Requesting Features

Feature requests are welcome! Please [open an issue](https://github.com/handley-lab/unimpeded/issues) describing:
- The proposed feature and its use case
- Why it would be valuable to the community
- Any implementation ideas you have

### Adding Models and Datasets

We welcome additions to the nested sampling grid. To request new models or datasets, or to propose uploading your own chains:
- [Open an issue](https://github.com/handley-lab/unimpeded/issues) describing what you'd like to add
- Contact [Dily Ong](mailto:dlo26@cam.ac.uk) or [Will Handley](mailto:wh260@cam.ac.uk) to discuss computational requirements and upload procedures

## Submitting Pull Requests

We appreciate code contributions! Please follow these steps:

1. **Fork the repository** and create a new branch from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines (see below)

3. **Add tests** for any new functionality in the `tests/` directory

4. **Run the test suite** to ensure nothing breaks:
   ```bash
   export MPLBACKEND=Agg  # only necessary for OSX users
   python -m pytest
   flake8 unimpeded tests
   pydocstyle --convention=numpy unimpeded
   ```

5. **Update documentation** if you've changed functionality:
   - Docstrings should follow NumPy style
   - Update relevant `.rst` files in `docs/` if needed

6. **Commit your changes** with clear, descriptive commit messages

7. **Push to your fork** and [open a pull request](https://github.com/handley-lab/unimpeded/compare)

8. **Describe your changes** in the PR:
   - What problem does it solve?
   - What testing have you done?
   - Link to any related issues

## Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style conventions
- Use `flake8` for linting
- Docstrings should follow [NumPy documentation style](https://numpydoc.readthedocs.io/en/latest/format.html)
- Maximum line length: 79 characters for code, 72 for docstrings
- Use meaningful variable names

## Development Setup

To set up a development environment:

```bash
git clone https://github.com/handley-lab/unimpeded
cd unimpeded
python -m pip install -e ".[all,docs,test]"
```

## Testing

We use `pytest` for testing. Tests are located in the `tests/` directory.

Run all tests:
```bash
python -m pytest
```

Run with coverage:
```bash
pytest --cov=unimpeded tests
```

Run a specific test:
```bash
python -m pytest tests/test_database.py::test_function_name
```

## Documentation

Documentation is built with Sphinx and hosted on ReadTheDocs.

To build documentation locally:
```bash
cd docs
make html
```

View the built documentation at `docs/build/html/index.html`.

## Questions?

If you have questions about contributing, feel free to:
- [Open an issue](https://github.com/handley-lab/unimpeded/issues)
- Contact [Dily Ong](mailto:dlo26@cam.ac.uk) or [Will Handley](mailto:wh260@cam.ac.uk)

## Recognition

Contributors will be acknowledged in the project. Significant contributions may warrant co-authorship on future papers utilizing the expanded database, subject to discussion with the maintainers.

Thank you for helping make `unimpeded` better!
