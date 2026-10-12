class ContextException(Exception):
    pass

class ContextManagerException(ContextException):
    pass

class ContextObjectException(ContextException):
    pass

class ContextSyntaxError(ContextObjectException):
    pass

class ContextLoadingSyntaxError(ContextSyntaxError):
    pass

class ContextNecessaryFieldsMissingError(ContextLoadingSyntaxError):
    pass

class ContextFieldTypeError(ContextSyntaxError):
    pass

class ContextInvalidRoleError(ContextSyntaxError):
    pass

class InvalidPromptPathError(ContextManagerException):
    pass

class IndexOutOfRangeError(ContextObjectException):
    pass

class ContentUnitError(ContextObjectException):
    pass