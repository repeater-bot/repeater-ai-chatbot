import uuid
from dataclasses import dataclass, field
from fastapi import Request
from ....user_data_managers.user_config_manager import UserConfigs
from ....global_config_manager import GlobalConfigs

@dataclass
class RuntimePackage:
    """
    This class represents a runtime package.
    """
    user_id: str
    task_id: uuid.UUID
    tool_call_id: str
    raw_argument: str
    user_configs: UserConfigs
    global_configs: GlobalConfigs
    fastapi_request: Request
    loop_times: int | None = None
    max_loop_times: int | None = None