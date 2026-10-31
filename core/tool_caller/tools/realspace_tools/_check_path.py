import os
from ....auxiliary.path import validate_path

def check_path(
        path: str | os.PathLike,
        writelist: list[str | os.PathLike],
        embed: bool = True
    ):
    for wl_path in writelist:
        if not validate_path(base_path=path, new_path=wl_path, embed=embed):
            return False
    return True