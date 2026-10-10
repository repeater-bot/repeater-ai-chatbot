from ...user_data_managers.context import ContentUnit, ContentRole, ContentBlock, TextBlock
    
def create_tool_content_unit(
        tool_call_id: str,
        content: str | list[ContentBlock],
        loop_times: int | None = None,
        max_loop_times: int | None = None
    ) -> ContentUnit:

    if loop_times is None:
        return ContentUnit(
            role = ContentRole.TOOL,
            tool_call_id = tool_call_id,
            content = content
        )
    else:
        if isinstance(content, str):
            tool_response_length = len(content)
            buffer = [
                "<tool_response>",
                "  <info>",
                f"    <tool_call_id>{tool_call_id}</tool_call_id>",
                f"    <tool_response_length>{tool_response_length}</tool_response_length>",
                f"    <loop_times>{loop_times}/{max_loop_times}</loop_times>",
                "  </info>",
                "  <content>",
                "  " + content.replace("\n", "\n  "),
                "  </content>",
                "</tool_response>"
            ]
            return ContentUnit(
                role = ContentRole.TOOL,
                tool_call_id = tool_call_id,
                content = "\n".join(buffer)
            )
        elif isinstance(content, list):
            prefix_buffer = [
                "<tool_response>",
                "  <info>",
                f"    <tool_call_id>{tool_call_id}</tool_call_id>",
                f"    <tool_response_length>{len(content)}</tool_response_length>",
                f"    <loop_times>{loop_times}/{max_loop_times}</loop_times>",
                "  </info>",
                "  <content>"
            ]
            suffix_buffer = [
                "  </content>",
                "</tool_response>"
            ]
            return ContentUnit(
                role = ContentRole.TOOL,
                tool_call_id = tool_call_id,
                content = [
                    TextBlock(text = "\n".join(prefix_buffer)),
                    *content,
                    TextBlock(text = "\n".join(suffix_buffer))
                ]
            )
        else:
            raise ValueError(f"Unexpected content type: {type(content).__name__}")