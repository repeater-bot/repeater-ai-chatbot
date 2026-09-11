from ....global_config_manager import UserIdStrategies

def get_user_id(strategy: UserIdStrategies, local_id: str, user_id: str) -> str:
    match strategy:
        case UserIdStrategies.LOCAL_INSTANCE:
            return f"{local_id}"
        case UserIdStrategies.USERS:
            return f"{user_id}"
        case UserIdStrategies.SEPARATE:
            return f"{user_id}_{local_id}"
        case _:
            raise ValueError(f"Invalid user_id strategy: {strategy}")