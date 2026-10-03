# Third-Party Licenses

This project is released under the [MIT](./../LICENSE) License.

This project includes the following third-party software components, licensed under their respective licenses:

> Version numbers are intentionally not listed in this document. The authoritative dependency versions are declared in the dependency configuration files (`pyproject.toml` and `poetry.lock`).

---

## Third-Party Software Components

| Name                    | License                         | Repository Link                                                                | Where it is used                    | Reasons                                            |
|-------------------------|---------------------------------|------------------------------------------------------------------------------- |-------------------------------------|----------------------------------------------------|
| markdown                | BSD 3-Clause License            | [Markdown](https://github.com/Python-Markdown/markdown)                        | `core.markdown`                     | Parses Markdown text into HTML                     |
| pyyaml                  | MIT License                     | [pyyaml](https://github.com/yaml/pyyaml)                                       | `core.api` & `core.global_config_manager` | Read configuration file                      |
| aiofiles                | Apache Software License         | [aiofiles](https://github.com/Tinche/aiofiles)                                 | `core.data_manager`                 | Asynchronous file support                          |
| environs                | MIT License                     | [environs](https://github.com/sloria/environs)                                 | *Entire Project*                    | Support for environment variables                  |
| fastapi                 | MIT License                     | [fastapi](https://github.com/fastapi/fastapi)                                  | `core.api`                          | Build API                                          |
| httpx                   | BSD License                     | [httpx](https://github.com/encode/httpx)                                       | *Entire Project*                    | Asynchronous HTTP client                           |
| loguru                  | MIT License                     | [loguru](https://github.com/Delgan/loguru)                                     | *Entire Project*                    | Logging                                            |
| openai                  | Apache Software License         | [openai](https://github.com/openai/openai-python)                              | `core.call_api`                     | Call the OpenAI API                                |
| orjson                  | MPL-2.0 AND (Apache-2.0 OR MIT) | [orjson](https://github.com/ijl/orjson)                                        | `core.DataManager` & `API`          | High-performance JSON resolution                   |
| pydantic                | MIT License                     | [pydantic](https://github.com/pydantic/pydantic)                               | *Entire Project*                    | Simple and convenient data validation              |
| python-multipart        | Apache-2.0                      | [python-multipart](https://github.com/Kludex/python-multipart)                 | `core.data_manager` & `core.api`    | Support for form data                              |
| uvicorn                 | BSD License                     | [uvicorn](https://github.com/Kludex/uvicorn)                                   | `run_repeater.py`                   | Run FastAPI                                        |
| numpy                   | BSD License                     | [numpy](https://github.com/numpy/numpy)                                        | *Entire Project*                    | Speed up batch computing of data                   |
| python-box              | MIT License                     | [python-box](https://github.com/cdgriffith/Box/)                               | `core.global_config_manager`        | Mixed configuration files                          |
| jinja2                  | BSD-3-Clause license            | [jinja2](https://github.com/pallets/jinja)                                     | `core.text_template_processer`      | Render text templates                              |
| tzdata                  | Apache-2.0                      | [tzdata](https://github.com/python/tzdata)                                     | `core.text_template_processer`      | Get timezone information                           |
| yarl                    | MIT License                     | [yarl](https://github.com/aio-libs/yarl)                                       | *Entire Project*                    | URL parsing                                        |
| bleach                  | Apache-2.0                      | [bleach](https://github.com/mozilla/bleach)                                    | `core.markdown_render`              | Clean HTML                                         |
| asteval                 | MIT License                     | [asteval](https://github.com/newville/asteval)                                 | `core.model_requester.tools`        | Assist AI in performing mathematical calculations. |
| jsonpatch               | BSD-3-Clause license            | [jsonpatch](https://github.com/stefankoegl/python-json-patch)                  | `core.data_manager`                 | JSON Diff & Patch                                  |
| pythonping              | MIT License                     | [pythonping](https://github.com/alessandromaggio/pythonping)                   | `core.api`                          | Checking network connectivity                      |
| cachetools              | MIT License                     | [cachetools](https://github.com/tkem/cachetools)                               | *Entire Project*                    | Cachetools is a caching library for Python         |
| starlark                | Apache-2.0                      | [starlark](https://github.com/dbohdan/starlark-python)                         | `core.model_requester.tools`        | Starlark is a language for configuration.          |
| sloves_starter          | MIT License                     | [sloves_starter](https://github.com/qeggs-dev/Sloves_Starter)                  | `run.py`                            | Starter for Repeater                               |

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
- [JSONPatch](./jsonpatch/index.md)
- [PythonPing](./pythonping/index.md)
- [Cachetools](./cachetools/index.md)
- [Starlark](./starlark/index.md)
- [Sloves_Starter](./sloves_starter/index.md)
