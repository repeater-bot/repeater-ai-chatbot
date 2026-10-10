from typing import BinaryIO
from ......user_data_managers.user_config_manager import (
    UserConfigs
)
from ......user_data_managers.context import (
    Context
)
import zipfile
import orjson
from ._readable_context import readable_context
import yaml

def make_user_file(file: BinaryIO, context: Context, prompt: str, user_configs: UserConfigs) -> None:
    with zipfile.ZipFile(file, "w") as zipf:
        zipf.writestr(
            "raw/context.json",
            orjson.dumps(
                context.to_context()
            )
        )
        zipf.writestr(
            "readable/context.txt",
            readable_context(
                context
            )
        )
        zipf.writestr(
            "raw/prompt.json",
            orjson.dumps(
                prompt
            )
        )
        zipf.writestr(
            "readable/prompt.txt",
            prompt
        )
        zipf.writestr(
            "raw/user_configs.json",
            orjson.dumps(
                user_configs.model_dump(
                    exclude_defaults=True
                )
            )
        )
        zipf.writestr(
            "readable/user_configs.yaml",
            (
                yaml.dump(
                    user_configs.model_dump(
                        exclude_defaults=True
                    ),
                    indent = 2,
                    allow_unicode = True
                )
            )
        )
    file.seek(0)