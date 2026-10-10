from ._load_prompt_directives import load_prompt_directive
from ...user_data_managers.user_config_manager import UserConfigs
from ...global_config_manager import GlobalConfigs
from typing import AsyncGenerator, Generator, Iterable

def match_directive_type(
    base_type: Iterable[str],
    prompt_directives: dict[str, list[str]]
) -> Generator[tuple[str, str], None, None]:
    for directive_type in base_type:
        if directive_type in prompt_directives:
            for directive in prompt_directives[directive_type]:
                yield directive_type, directive

def prompt_directive_from_config(
    base_type: Iterable[str],
    user_configs: UserConfigs,
    global_configs: GlobalConfigs
) -> Generator[tuple[str, str], None, None]:
    if user_configs.prompt_directives is None:
        prompt_directives = global_configs.prompt.prompt_directives
    else:
        prompt_directives = user_configs.prompt_directives

    yield from match_directive_type(base_type, prompt_directives)
    
    force_load_directives = global_configs.prompt.force_load_directives

    yield from match_directive_type(base_type, force_load_directives)

async def load_prompt_directive_from_config(
    base_type: Iterable[str],
    user_configs: UserConfigs,
    global_configs: GlobalConfigs
) -> AsyncGenerator[str, None]:
    for directive_type, directive_name in prompt_directive_from_config(base_type, user_configs, global_configs):
        yield await load_prompt_directive(
            directive_type,
            directive_name
        )