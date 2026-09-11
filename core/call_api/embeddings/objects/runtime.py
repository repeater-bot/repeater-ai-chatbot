from dataclasses import dataclass, field
from ....pools.openai_pool import OpenAIPool

@dataclass
class EmbeddingsRuntime:
    client_pool: OpenAIPool = field(default_factory=OpenAIPool)