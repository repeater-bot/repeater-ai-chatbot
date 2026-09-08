import aiofiles
import environs
import pydantic
import fastapi
import python_multipart
import loguru
import openai
import orjson
import uvicorn
import markdown
import httpx
import numpy
import yaml
import box
import tzdata
import jinja2
import yarl
import bleach
import asteval
import pip_requirements_parser
import jsonpatch
import pythonping
import cachetools
import packaging
import starlark

modules_list = [
    aiofiles,
    environs,
    pydantic,
    fastapi,
    python_multipart,
    loguru,
    openai,
    orjson,
    uvicorn,
    markdown,
    httpx,
    numpy,
    yaml,
    box,
    tzdata,
    jinja2,
    yarl,
    bleach,
    asteval,
    pip_requirements_parser,
    jsonpatch,
    pythonping,
    cachetools,
    packaging,
    starlark,
]

from types import ModuleType
from packaging.utils import canonicalize_name
name_map: dict[str, ModuleType] = {
    canonicalize_name(module.__name__): module for module in modules_list
}
name_map["python-box"] = box
name_map["pyyaml"] = yaml