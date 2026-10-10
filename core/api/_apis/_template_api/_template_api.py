import asyncio

from ._router import template_router
from fastapi.responses import PlainTextResponse
from ....repeater_main import RepeaterMain
from ....global_config_manager import ConfigManager as Global_Config_Manager
from ....user_data_managers.user_config_manager import ConfigManager
from ._requests import ExpandVariableRequest
from jinja2 import TemplateError

@template_router.post("/render/{user_id}")
async def template(user_id: str, request: ExpandVariableRequest):
    """
    Endpoint for expanding variables
    """
    enable = Global_Config_Manager.get_configs().text_template.enable.api_template
    if not enable:
        return PlainTextResponse(
            "Text template is not enabled",
            status_code = 403
        )

    # 初始化加载器
    config_loader = ConfigManager()

    # 获取服务器实例
    server = RepeaterMain.get_now_server()

    # 获取用户配置
    config = await config_loader.load(user_id=user_id)

    template_parser = await server.core.get_template_parser(
        user_config = config,
        global_config = Global_Config_Manager.get_configs(),
    )

    # 调用PromptVP类处理文本
    try:
        output = await template_parser.render_ex(
            request.text,
            user_id = user_id,
            **request.extra_fields
        )
        # 返回结果
        return PlainTextResponse(output)
    except TemplateError as e:
        output = f"{e.__class__.__name__}: {e.message}"
        return PlainTextResponse(
            output,
            status_code = 400
        )
    except Exception as e:
        output = f"{e.__class__.__name__}: {str(e)}"
        return PlainTextResponse(
            output,
            status_code = 400
        )