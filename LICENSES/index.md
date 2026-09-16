# Third-Party Licenses

This project is released under the [MIT](./../LICENSE) License.

This project includes the following third-party software components, licensed under their respective licenses:

---

## Third-Party Software Components

| Name                    | Version  | License                         | Repository Link                                                                | Where it is used                    | Reasons                                            |
|-------------------------|----------|---------------------------------|------------------------------------------------------------------------------- |-------------------------------------|----------------------------------------------------|
| markdown                | 3.10.2   | BSD 3-Clause License            | [Markdown](https://github.com/Python-Markdown/markdown)                        | `core.markdown`                     | Parses Markdown text into HTML                     |
| pyyaml                  | 6.0.3    | MIT License                     | [pyyaml](https://github.com/yaml/pyyaml)                                       | `core.api` & `core.global_config_manager` | Read configuration file                      |
| aiofiles                | 25.1.0   | Apache Software License         | [aiofiles](https://github.com/Tinche/aiofiles)                                 | `core.data_manager`                 | Asynchronous file support                          |
| environs                | 14.5.0   | MIT License                     | [environs](https://github.com/sloria/environs)                                 | *Entire Project*                    | Support for environment variables                  |
| fastapi                 | 0.129.0  | MIT License                     | [fastapi](https://github.com/fastapi/fastapi)                                  | `core.api`                          | Build API                                          |
| httpx                   | 0.28.1   | BSD License                     | [httpx](https://github.com/encode/httpx)                                       | *Entire Project*                    | Asynchronous HTTP client                           |
| loguru                  | 0.7.3    | MIT License                     | [loguru](https://github.com/Delgan/loguru)                                     | *Entire Project*                    | Logging                                            |
| openai                  | 2.21.0   | Apache Software License         | [openai](https://github.com/openai/openai-python)                              | `core.call_api`                     | Call the OpenAI API                                |
| orjson                  | 3.11.7   | MPL-2.0 AND (Apache-2.0 OR MIT) | [orjson](https://github.com/ijl/orjson)                                        | `core.DataManager` & `API`          | High-performance JSON resolution                   |
| pydantic                | 2.11.7   | MIT License                     | [pydantic](https://github.com/pydantic/pydantic)                               | *Entire Project*                    | Simple and convenient data validation              |
| python-multipart        | 0.0.22   | Apache-2.0                      | [python-multipart](https://github.com/Kludex/python-multipart)                 | `core.data_manager` & `core.api`    | Support for form data                              |
| uvicorn                 | 0.40.0   | BSD License                     | [uvicorn](https://github.com/Kludex/uvicorn)                                   | `run_repeater.py`                   | Run FastAPI                                        |
| numpy                   | 2.4.2    | BSD License                     | [numpy](https://github.com/numpy/numpy)                                        | *Entire Project*                    | Speed up batch computing of data                   |
| python-box              | 7.3.2    | MIT License                     | [python-box](https://github.com/cdgriffith/Box/)                               | `core.global_config_manager`        | Mixed configuration files                          |
| jinja2                  | 3.1.6    | BSD-3-Clause license            | [jinja2](https://github.com/pallets/jinja)                                     | `core.text_template_processer`      | Render text templates                              |
| tzdata                  | 2025.3   | Apache-2.0                      | [tzdata](https://github.com/python/tzdata)                                     | `core.text_template_processer`      | Get timezone information                           |
| yarl                    | 1.23.0   | MIT License                     | [yarl](https://github.com/aio-libs/yarl)                                       | *Entire Project*                    | URL parsing                                        |
| bleach                  | 6.3.0    | Apache-2.0                      | [bleach](https://github.com/mozilla/bleach)                                    | `core.markdown_render`              | Clean HTML                                         |
| asteval                 | 1.0.8    | MIT License                     | [asteval](https://github.com/newville/asteval)                                 | `core.model_requester.tools`        | Assist AI in performing mathematical calculations. |
| pip-requirements-parser | 32.0.1   | MIT License                     | [pip-requirements-parser](https://github.com/jazzband/pip-requirements-parser) | `core.requirements_version_checker` | Parse requirements.txt files.                      |
| jsonpatch               | 1.33     | BSD-3-Clause license            | [jsonpatch](https://github.com/stefankoegl/python-json-patch)                  | `core.data_manager`                 | JSON Diff & Patch                                  |
| pythonping              | 1.1.4    | MIT License                     | [pythonping](https://github.com/alessandromaggio/pythonping)                   | `core.api`                          | Checking network connectivity                      |
| cachetools              | 7.1.4    | MIT License                     | [cachetools](https://github.com/tkem/cachetools)                               | *Entire Project*                    | Cachetools is a caching library for Python         |
| packaging               | 26.1     | Apache-2.0 AND BSD-3-Clause     | [packaging](https://github.com/pypa/packaging)                                 | `core.requirements_version_checker` | Format the Something pypi standard package name.   |
| starlark                | 0.6.0    | Apache-2.0                      | [starlark](https://github.com/dbohdan/starlark-python)                         | `core.model_requester.tools`        | Starlark is a language for configuration.          |
| sloves_starter          | 0.5.0    | MIT License                     | [sloves_starter](https://github.com/qeggs-dev/Sloves_Starter)                  | `run.py`                            | Starter for Repeater                               |

---

## License Copy

- [Python Markdown](./markdown/index.md)
- [PyYaml](./pyyaml/index.md)
- [Aiofiles](./aiofiles/index.md)
- [Environs](./environs/index.md)
- [FastAPI](./fastapi/index.md)
- [Httpx](./httpx/index.md)
- [Jinja2](./jinja2/index.md)
- [Loguru](./loguru/index.md)
- [Orjson](./orjson/index.md)
- [OpenAI](./openai/index.md)
- [Pydantic](./pydantic/index.md)
- [Python Multipart](./python-multipart/index.md)
- [Uvicorn](./uvicorn/index.md)
- [Numpy](./numpy/index.md)
- [Python-Box](./python-box/index.md)
- [Tzdata](./tzdata/index.md)
- [Yarl](./yarl/index.md)
- [Bleach](./bleach/index.md)
- [Asteval](./asteval/index.md)
- [Pip-requirements-parser](./pip-requirements-parser/index.md)
- [JSONPatch](./jsonpatch/index.md)
- [PythonPing](./pythonping/index.md)
- [Cachetools](./cachetools/index.md)
- [Packaging](./packaging/index.md)
- [Starlark](./starlark/index.md)
- [Sloves_Starter](./sloves_starter/index.md)