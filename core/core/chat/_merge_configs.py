from box import Box
from ...user_data_managers.user_config_manager import UserConfigs

def merge_configs(base: UserConfigs, other: UserConfigs) -> UserConfigs:
    base_box = Box(base.model_dump())
    other_box = Box(other.model_dump(exclude_none=True))
    base_box.merge_update(other_box)
    return UserConfigs.model_validate(base_box.to_dict())