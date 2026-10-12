"""
The tool calling module.

Importing this package registers every tool of `tool_caller.tools` in
`ToolsCaller`, which is what makes them available to `ToolsCaller.to_request`
and `ToolsCaller.call_tools`.
"""

from .framework import *
from .framework import __all__ as _framework_all

def _delayed_import():
    from ..lifespan import register_post_init
    @register_post_init
    def post_init():
        from . import tools

_delayed_import()