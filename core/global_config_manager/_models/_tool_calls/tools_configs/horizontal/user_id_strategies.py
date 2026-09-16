from enum import StrEnum

class UserIdStrategies(StrEnum):
    """用户ID策略"""

    LOCAL_INSTANCE = "local_instance"
    """
    本地实例

    仅传递本机 user_id
    """

    SEPARATE = "separate"
    """
    独立

    每个访客传递不同的 user_id
    """

    USERS = "users"
    """
    混合用户

    使用访客的 user_id
    """