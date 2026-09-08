from pydantic import BaseModel, ConfigDict

class UserInfo(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    username: str | None = None
    nickname: str | None = None
    age: int | float | None = None
    gender: str | None = None

    def display_username(self) -> str | None:
        return self.nickname or self.username