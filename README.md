# missouri

[![version](https://img.shields.io/pypi/v/missouri?style=flat-square)][pypi]
[![python version](https://img.shields.io/pypi/pyversions/missouri?style=flat-square)][pypi]
[![license](https://img.shields.io/pypi/missouri/vg?style=flat-square)][pypi]
[![](https://img.shields.io/badge/coverage-100%25-brightgreen.svg?style=flat-square)][coverage]

Read and write JSON files in one line.

[pypi]: https://pypi.org/project/missouri/
[coverage]: https://github.com/metabolize/missouri/blob/main/.coveragerc

## Features

- Read and write 
- Automatically serialize and deserialize NumPy arrays.
- Uses simplejson.
- Future: Automatically round nested data structures.


## Usage

Dump:

```py
from missouri import json

json.dump({"foo": 123}, "example.json")
```

Load:

```py
from missouri import json

data = json.load("example.json")
```


## Development

First, [install Poetry][].

After cloning the repo, run `./bootstrap.zsh` to initialize a virtual
environment with the project's dependencies.

Subsequently, run `./dev.py install` to update the dependencies.

[install poetry]: https://python-poetry.org/docs/#installation


## Acknowledgements

This friendly API was developed at Body Labs for an library called
[baiji-serialization][] which provided one-line reading and writing of objects
to JSON and YAML files and S3 keys on top of [baiji][] (may it rest in peace).
These were likely based on code written by [alex weiss][].

[alex weiss]: https://github.com/algrs
[baiji-serialization]: https://github.com/bodylabs/baiji-serialization
[baiji]: https://github.com/bodylabs/baiji

## Naming

baiji is a river dolphin of the Yangtze; boto is a river dolphin of the Amazon.
This library is not named after a dolphin, but it is named after a different big
river.


## License

The project is licensed under the Apache License, Version 2.0.
