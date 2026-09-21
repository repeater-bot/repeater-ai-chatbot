from enum import StrEnum
from ....repeater_main import RepeaterMain
from ....data_manager import UserDataManager

class UserDataType(StrEnum):
    CONTEXT = "context"
    PROMPT = "prompt"
    CONFIG = "config"
    PROGRAM = "program"

def get_manager(data_type: UserDataType) -> UserDataManager:
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    match data_type:
        case UserDataType.CONTEXT:
            return runtime.context_manager
        case UserDataType.PROMPT:
            return runtime.prompt_manager
        case UserDataType.CONFIG:
            return runtime.user_config_manager
        case UserDataType.PROGRAM:
            return runtime.program_data_manager
    
    raise ValueError(f"Invalid data type: {data_type}")