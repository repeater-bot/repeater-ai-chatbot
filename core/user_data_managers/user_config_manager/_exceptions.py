class ConfigManagerException(Exception):
    """Base class for exceptions in this module."""
    pass

class UnintelligibleConfigFormat(ConfigManagerException):
    """Raised when the config file is not in a supported format."""
    pass

class KeyNotFoundError(ConfigManagerException):
    """Raised when a key is not found."""
    pass

class ConfigFieldError(ConfigManagerException):
    """Raised when a config field is not in the correct format."""
    pass