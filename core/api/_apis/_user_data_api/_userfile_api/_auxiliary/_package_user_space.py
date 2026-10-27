import yaml
import orjson
import zipfile
import asyncio

from typing import BinaryIO
from ......user_data_managers.user_config_manager import (
    ConfigManager,
    UserConfigs
)
from ......user_data_managers.context import (
    ContextLoader,
    Context
)
from ......user_data_managers.program_data_manager import (
    ProgramDataManager,
    ProgramData
)
from ......data_manager import (
    PromptManager
)
from ._readable_context import readable_context

def package_to_zip(
    file: BinaryIO,
    contexts: dict[str, Context],
    prompts: dict[str, str],
    user_configs: dict[str, UserConfigs],
    program_datas: dict[str, ProgramData]
):
    with zipfile.ZipFile(file, "w") as zipf:
        for branch_id, context in contexts.items():
            zipf.writestr(
                f"raw/contexts/{branch_id}.json",
                orjson.dumps(
                    context.to_context()
                )
            )
            zipf.writestr(
                f"readable/contexts/{branch_id}.txt",
                readable_context(context)
            )
        for branch_id, prompt in prompts.items():
            zipf.writestr(
                f"raw/prompts/{branch_id}.json",
                orjson.dumps(
                    prompt
                )
            )
            zipf.writestr(
                f"readable/prompts/{branch_id}.txt",
                prompt
            )
        for branch_id, config in user_configs.items():
            zipf.writestr(
                f"raw/configs/{branch_id}.json",
                orjson.dumps(
                    config.model_dump(
                        exclude_none=True
                    ),
                )
            )
            zipf.writestr(
                f"readable/configs/{branch_id}.yaml",
                yaml.safe_dump(
                    config.model_dump(
                        exclude_none=True
                    ),
                    allow_unicode = True
                )
            )
        for branch_id, program_data in program_datas.items():
            zipf.writestr(
                f"raw/program_data/{branch_id}.json",
                orjson.dumps(
                    program_data
                )
            )
            zipf.writestr(
                f"readable/program_data/{branch_id}.yaml",
                yaml.safe_dump(
                    program_data
                )
            )
    file.seek(0)

async def package_user_space(
    user_id: str,
    context_loader: ContextLoader,
    prompt_manager: PromptManager,
    config_manager: ConfigManager,
    program_data_manager: ProgramDataManager,
    file: BinaryIO
):
    contexts: dict[str, Context] = {}
    context_branchs = await context_loader.get_context_branchs(user_id)
    for context_branch in context_branchs:
        context = await context_loader.load_context(
            user_id = user_id,
            branch_id = context_branch,
        )
        contexts[context_branch] = context
    
    prompts: dict[str, str] = {}
    prompt_branchs = await prompt_manager.get_all_branch_id(user_id)
    for prompt_branch in prompt_branchs:
        prompt = await prompt_manager.load(
            user_id = user_id,
            branch_id = prompt_branch
        )
        prompts[prompt_branch] = prompt
    
    configs: dict[str, UserConfigs] = {}
    config_branchs = await config_manager.get_all_branch_id(user_id)
    for config_branch in config_branchs:
        config = await config_manager.load(
            user_id = user_id,
            branch_id = config_branch
        )
        configs[config_branch] = config

    program_datas: dict[str, ProgramData] = {}
    program_data_branchs = await program_data_manager.get_all_branch_id(user_id)
    for program_data_branch in program_data_branchs:
        program_data = await program_data_manager.load(
            user_id = user_id,
            branch_id = program_data_branch
        )
        program_datas[program_data_branch] = program_data
    
    await asyncio.to_thread(
        package_to_zip,
        file,
        contexts,
        prompts,
        configs,
        program_datas
    )
