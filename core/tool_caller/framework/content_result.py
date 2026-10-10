"""
The `ContentResult` re-export of the tool calling framework.

`ContentResult` used to be declared twice — once here and once in
`core.context.objects.function_calling._content_result` — which meant a tool and
the framework could hold two different classes with the same name and silently
fail every `isinstance` check. The framework now re-exports the single class
from `context`; when the old `FunctionCaller` layer is removed, move the
definition back in here instead of adding a second copy.
"""

from ...context import ContentResult, ContentBlock

__all__ = [
    "ContentResult",
    "ContentBlock",
]
