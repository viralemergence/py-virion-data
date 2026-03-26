# py-virion-data

[![PyPI - Version](https://img.shields.io/pypi/v/py-virion-data.svg)](https://pypi.org/project/py-virion-data)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-virion-data.svg)](https://pypi.org/project/py-virion-data)
[![codecov](https://codecov.io/github/viralemergence/py-virion-data/graph/badge.svg?token=PNEFR3NP4T)](https://codecov.io/github/viralemergence/py-virion-data)
-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install py-virion-data
```

## License

`py-virion-data` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Package development and maintenance 

This package was developed using the [PyOpenSci package tutorial](https://www.pyopensci.org/python-package-guide/tutorials/intro.html) and follows their best practices as closely as possible. 

Therefore we use [hatch](https://hatch.pypa.io/1.16/) to build, test, and document the package.

### Versioning

major - changes to defined classes that break previous releases 
minor - changes or refactors to defined classes that add, refine or modify features without breaking functionality from previous releases. A minor release may also occur if there are significant improvements testing, documentation or other use support features. 
patch - improvements to testing, documentation, or other user support features.  

### Testing

Tests are stored in the "tests" directory and test configurations can be found in the pyproject.toml file. See [Using Hatch for Developing](https://www.pyopensci.org/python-package-guide/tutorials/develop-python-package-hatch.html) for more info.

To run tests locally:
```
hatch run test:run_local
```
