
from ._main_user_data_manager import UserDataManager as UserDataManager
from ...global_config_manager import ConfigManager, DataTypes

class ContextManager(UserDataManager[list]):
    def __init__(self):
        configs = ConfigManager.get_configs()
        super().__init__(
            "Context_UserData",
            cache_metadata = (
                bool(configs.user_data.cache_medadata.context)
                if isinstance(configs.user_data.cache_medadata, DataTypes)
                else configs.user_data.cache_medadata
            ),
            cache_data = (
                bool(configs.user_data.cache_data.context)
                if isinstance(configs.user_data.cache_data, DataTypes)
                else configs.user_data.cache_data
            ),
            branches_dir_name = configs.user_data.branches_dir_name,
            default_factory = list
        )

class PromptManager(UserDataManager[str]):
    def __init__(self):
        configs = ConfigManager.get_configs()
        super().__init__(
            "Prompt_UserData",
            cache_metadata = (
                bool(configs.user_data.cache_medadata.prompt)
                if isinstance(configs.user_data.cache_medadata, DataTypes)
                else configs.user_data.cache_medadata
            ),
            cache_data = (
                bool(configs.user_data.cache_data.prompt)
                if isinstance(configs.user_data.cache_data, DataTypes)
                else configs.user_data.cache_data
            ),
            branches_dir_name = configs.user_data.branches_dir_name,
            default_factory = lambda: ""
        )

class UserConfigManager(UserDataManager[dict]):
    def __init__(self):
        configs = ConfigManager.get_configs()
        super().__init__(
            "UserConfig_UserData",
            cache_metadata = (
                bool(configs.user_data.cache_medadata.config)
                if isinstance(configs.user_data.cache_medadata, DataTypes)
                else configs.user_data.cache_medadata
            ),
            cache_data = (
                bool(configs.user_data.cache_data.config)
                if isinstance(configs.user_data.cache_data, DataTypes)
                else configs.user_data.cache_data
            ),
            branches_dir_name = configs.user_data.branches_dir_name,
            default_factory = lambda: {}
        )

class ProgramDataManager(UserDataManager[dict]):
    def __init__(self):
        configs = ConfigManager.get_configs()
        super().__init__(
            "ProgramData_UserData",
            cache_metadata = (
                bool(configs.user_data.cache_medadata.program)
                if isinstance(configs.user_data.cache_medadata, DataTypes)
                else configs.user_data.cache_medadata
            ),
            cache_data = (
                bool(configs.user_data.cache_data.program)
                if isinstance(configs.user_data.cache_data, DataTypes)
                else configs.user_data.cache_data
            ),
            branches_dir_name = configs.user_data.branches_dir_name, 
            default_factory = lambda: {}
        )