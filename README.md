# 🐝 Bee Py

<div align="center">

| Feature       | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technology    | [![Python](https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org/) [![Ape](https://img.shields.io/badge/Built%20with-Ape-blue.svg)](https://github.com/ApeWorX/ape) [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white)](https://github.com/features/actions) [![Pytest](https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white)](https://github.com/alienrobotninja/bee-py/actions/workflows/tests.yml/badge.svg) [![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)                              |
| Linting       | [![Code style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/psf/black) ![Style Guide](https://img.shields.io/badge/Style%20Guide-Flake8-blue) [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)                                                                                                                                                                                                                                                                                                                                                                              |
| Type Checking | [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| CI/CD         | [![Tests](https://github.com/alienrobotninja/bee-py/actions/workflows/tests.yml/badge.svg)](https://github.com/alienrobotninja/bee-py/actions/workflows/tests.yml) [![Labeler](https://github.com/alienrobotninja/bee-py/actions/workflows/labeler.yml/badge.svg)](https://github.com/alienrobotninja/bee-py/actions/workflows/labeler.yml) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)                                                                                                                                                                                                            |
| Docs          | [![Read the Docs](https://img.shields.io/readthedocs/bee-py/latest.svg?label=Read%20the%20Docs)](https://bee-py.readthedocs.io/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Package       | [![PyPI - Version](https://img.shields.io/pypi/v/bee-py.svg)](https://pypi.org/project/bee-Py/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bee-Py)](https://pypi.org/project/bee-py/) [![PyPI - License](https://img.shields.io/pypi/l/bee-Py)](https://pypi.org/project/bee-py/)                                                                                                                                                                                                                                                                                                                                                                                                        |
| Meta          | [![GitHub license](https://img.shields.io/github/license/alienrobotninja/bee-py?style=flat&color=1573D5)](https://github.com/alienrobotninja/bee-py/blob/main/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/alienrobotninja/bee-py?style=flat&color=1573D5)](https://github.com/alienrobotninja/bee-py/commits/main) [![GitHub commit activity](https://img.shields.io/github/commit-activity/m/alienrobotninja/bee-py?style=flat&color=1573D5)](https://github.com/alienrobotninja/bee-py/graphs/commit-activity) [![GitHub top language](https://img.shields.io/github/languages/top/alienrobotninja/bee-py?style=flat&color=1573D5)](https://github.com/alienrobotninja/bee-py) |

</div>

## 📖 Table of Contents

- [🐝 Bee Py](#-bee-py)
  - [📖 Table of Contents](#-table-of-contents)
  - [🌐 Overview](#-overview)
  - [✨ Features](#-features)
  - [📋 Requirements](#-requirements)
    - [🚀 Testing Locally](#-testing-locally)
  - [🛠️ Installation](#️-installation)
  - [🚀 Usage](#-usage)
    - [🐝 Bee Endpoint](#-bee-endpoint)
    - [🚀 Bee Debug Endpoint](#-bee-debug-endpoint)
  - [👩‍💻 Development](#-development)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [🐞 Issues](#-issues)
  - [📚 Documentation](#-documentation)
  - [👏 Credits](#-credits)

## 🌐 Overview

This is the library for connecting to Bee decentralised storage using python.

## ✨ Features

- TODO

## 📋 Requirements

- `Python3.9+`

### 🚀 Testing Locally

- [npm](https://www.npmjs.com/package/npm)
- [Bee-factory](https://github.com/ethersphere/bee-factory)
- [Docker](https://docs.docker.com/desktop/)

## 🛠️ Installation

You can install `bee-py` via \[pip\] from \[PyPI\]:

```sh
pip install swarm-bee-py
```

## 🚀 Usage

### 🐝 Bee Endpoint

```py
from bee_py.bee import Bee

bee = Bee("https://18.134.10.41:1633")
# List Tags
all_tags = bee.get_all_tags({"limit": 1000})
print(all_tags) 
>>> [Tag(split=0, seen=0, stored=0, sent=0, synced=6, uid=2270760008, started_at='2023-12-27T19:00:24Z', total=6, processed=6),
 Tag(split=0, seen=0, stored=0, sent=0, synced=0, uid=2271272542, started_at='2023-12-09T13:22:52Z', total=0, processed=0),
 Tag(split=0, seen=0, stored=0, sent=0, synced=3, uid=2272654825, started_at='2023-12-26T22:15:30Z', total=3, processed=3),
 Tag(split=0, seen=0, stored=0, sent=0, synced=3, uid=2274652661, started_at='2023-12-19T20:27:27Z', total=3, processed=3),
 Tag(split=0, seen=0, stored=0, sent=0, synced=4, uid=2274680401, started_at='2024-01-05T20:03:17Z', total=4, processed=4),
 Tag(split=0, seen=0, stored=0, sent=0, synced=16, uid=2274738522, started_at='2023-12-27T00:12:46Z', total=16, processed=16),
 Tag(split=0, seen=0, stored=0, sent=0, synced=6, uid=2277789382, started_at='2024-01-05T19:30:39Z', total=6, processed=6),
 Tag(split=0, seen=0, stored=0, sent=0, synced=5, uid=2278169907, started_at='2023-12-27T00:44:34Z', total=5, processed=5),
 Tag(split=0, seen=0, stored=0, sent=0, synced=1, uid=2278428847, started_at='2023-12-19T01:29:06Z', total=1, processed=1),
 Tag(split=0, seen=0, stored=0, sent=0, synced=1, uid=2280360127, started_at='2023-12-27T16:18:04Z', total=1, processed=1)]

# Random Taken for example
batch_id = "eeba33ebe515c3ca9827a5e82e07987f813966fd39067126b120bcd6cd714ce9"
# Upload Data
upload_result = bee.upload_data(batch_id, "Bee is Awesome!")

print(upload_result)
>>> UploadResult(reference=Reference(value='b0d6b928d0f64fab1a50d37a965515cc6f152d3c27f58fbcefb6b8506f23b076'), tag_uid=None)

print(upload_result.reference)
>>> Reference(value='b0d6b928d0f64fab1a50d37a965515cc6f152d3c27f58fbcefb6b8506f23b076')

print(upload_result.reference.value)
>>> 'b0d6b928d0f64fab1a50d37a965515cc6f152d3c27f58fbcefb6b8506f23b076'

# Both can be done to obtain the reference value

print(str(upload_result.reference))
>>> 'b0d6b928d0f64fab1a50d37a965515cc6f152d3c27f58fbcefb6b8506f23b076'

data = bee.download_data(upload_result.reference.value)
print(data)
>>> Data(data=b'Bee is Awesome!')

# Data can be converted into json format, hex, bytes or plain-text
print(data.to_json())
>>> '{"data":"Bee is Awesome!"}'

print(data.text())
>>> 'Bee is Awesome!'

print(data.hex())
>>> '42656520697320417765736f6d6521'
```

### 🚀 Bee Debug Endpoint

```py
from bee_py.bee_debug import BeeDebug

bee_debug = BeeDebug("https://18.134.10.41:1635")

# Be aware, this creates on-chain transactions that spend Eth and BZZ!
# Get Postage
batch_id = bee_debug.create_postage_batch('2000', 20)
print(batch_id)
>>> "17cbeb913ff852e34ade49c6df75adc7ff6f263b86d59c1cb2c3b0388cfe9cf3"
```

## 👩‍💻 Development

This project is developed using [pdm](https://pdm-project.org/). So the quickest way to get started is using `pdm`. Install pdm using `pip`, `pipx` etc & then follow the following steps

```sh
git clone https://github.com/alienrobotninja/bee-py
cd bee-py
# To install all the dev & lint dependencies 
pdm install -G:all
```

That's it, you're environment is ready. Now install docker to run [bee-factory](https://github.com/ethersphere/bee-factory). Now to start the `bee-factory` do `bee-factory start --detach 1.15.0-rc2`. As of 7th January 2024 `1.15.0-rc2` is the latest release for `bee-factory` which uses a very outdated versions of bee.

## 🤝 Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## 📄 License

Distributed under the terms of the [GPL 3.0 license][license],
_Bee Py_ is free and open source software.

## 🐞 Issues

There are some know issues like:

- Some tests are perfomed on older versions of bee.
- Some tests are stuck for hours when using the latest Bee API(not `bee-py` issue).
- Some tests are skipped because of outdated libraries used by various `ethersphere` projects.

If you encounter any problems,
please \[file an issue\] along with a detailed description.

## 📚 Documentation

You can find the full documentation [here](https://bee-js.ethswarm.org/docs). The API reference documentation can be found [here](https://bee-js.ethswarm.org/docs/api).

## 👏 Credits

Developed by [@Aviksaikat](https://github.com/aviksaikat)

<!-- github-only -->

[contributor guide]: https://github.com/alienrobotninja/bee-py/blob/main/CONTRIBUTING.md
[license]: https://github.com/alienrobotninja/bee-py/blob/main/LICENSE
