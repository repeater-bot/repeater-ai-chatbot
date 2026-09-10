from ......context import (
    Context
)

def readable_context(context: Context) -> str:
    text_buffer: list[str] = []
    text_buffer.append("======== Context  ========")
    for index, item in enumerate(context.context_list):
        text_buffer.append(f"[{index + 1}(Pair: {(index // 2) + 1})] {item.role.name}:")
        if item.reasoning_content:
            text_buffer.append("Reasoning:")
            text_buffer.append(item.reasoning_content)
            text_buffer.append("")
        if item.content:
            text_buffer.append("Content:")
            text_buffer.append(item.content_to_string())
            text_buffer.append("")
        
        text_buffer.append("==========================")
        text_buffer.append("")
    return "\n".join(text_buffer)