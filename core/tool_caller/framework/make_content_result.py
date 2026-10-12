from ...user_data_managers.context import ContentUnit, ContentRole, ContentBlock, TextBlock
    
def create_tool_content_unit(
        tool_call_id: str,
        content: str | list[ContentBlock],
        loop_times: int | None = None,
        max_loop_times: int | None = None
    ) -> ContentUnit:

    return ContentUnit(
        role = ContentRole.TOOL,
        tool_call_id = tool_call_id,
        content = content
    )