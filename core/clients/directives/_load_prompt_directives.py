from yarl import URL
from ...runtime_container import RuntimeContainer
from ...global_config_manager import ConfigManager

def directive_path(
    base_path: URL,
    base_type: str,
    directive_name: str
) -> URL:
    return base_path / base_type / directive_name

async def load_prompt_directive(
    base_type: str,
    directive_name: str
):
    runtime = RuntimeContainer.get_runtime()
    config = ConfigManager.get_configs()

    base_path = config.prompt.directive_base_path
    static_client = runtime.static_resources_client
    directive_file = f"{directive_name}.md"
    url = directive_path(
        URL(base_path),
        base_type,
        directive_file
    )
    
    directive_content = await static_client.get_text(url)

    return directive_content