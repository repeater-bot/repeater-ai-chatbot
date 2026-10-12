from .._requests import RenderRequest
from .....global_config_manager import ConfigManager
from .....markdown_to_html import Styles
from .....user_data_managers.user_config_manager import UserConfigs
from .....clients.static_resources_client import StaticResourcesClient

async def get_style(request: RenderRequest, user_configs: UserConfigs, static_resources_client: StaticResourcesClient):
    """
    获取用户配置的样式文件

    :param request: 请求参数
    :param user_configs: 用户配置
    :return: 样式文件内容(样式名称，样式文件内容)
    """
    style_path = ConfigManager.get_configs().render.markdown.styles_base_path
    styles = Styles(
        static_resources_client = static_resources_client,
        style_base_path = style_path
    )
    
    if request.style:
        style_name = request.style
        style_url = styles.get_style_full_url(style_name)
    else:
        # 获取配置中的默认图片渲染风格
        if user_configs.render_style:
            style_name = user_configs.render_style
        else:
            style_name = ConfigManager.get_configs().render.markdown.default_style
        
        style_url = styles.get_style_full_url(style_name)
    
    return style_name, style_url