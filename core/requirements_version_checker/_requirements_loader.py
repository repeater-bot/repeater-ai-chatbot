from ..global_config_manager import ConfigManager
from pip_requirements_parser import RequirementsFile
from pathlib import Path

def load_requirements() -> RequirementsFile:
    path = ConfigManager().get_configs().requirements.requirements_file
    # 此处本来是使用 RequirementsFile.from_string() 的，但是因为 pip_requirements_parser 的问题，
    # 这个方法调用后会抛 `NameError: name 'Path' is not defined` 的异常
    return RequirementsFile.from_file(path)