from ......repeater_main import RepeaterMain
from .._router import prompt_router
from fastapi import Query
from fastapi.responses import (
    PlainTextResponse
)
from loguru import logger

@prompt_router.get("/get/{user_id}")
@prompt_router.get("/get/{user_id}.md")
async def get_prompt(
    user_id: str,
    branch_id: str | None = Query(None)
):
    """
    Endpoint for setting prompt

    Args:
        user_id (str): User ID
        branch_id (str, optional): Branch ID. Defaults to None.
    
    Returns:
        PlainTextResponse: User's prompt
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    # 获取用户ID为user_id的提示词
    prompt = await runtime.prompt_manager.load(user_id = user_id, branch_id = branch_id)

    if branch_id is None:
        logger.info("Get active prompt", user_id = user_id)
    else:
        logger.info("Get prompt {branch_id}", user_id = user_id, branch_id = branch_id)

    # 返回提示词内容
    return PlainTextResponse(prompt)