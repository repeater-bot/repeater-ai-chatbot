from pydantic import BaseModel

from .....runtime_container import RuntimeContainer
from ....framework import ToolsCaller, ToolPackage, RuntimePackage


@ToolsCaller.register
class SQLiteList(ToolPackage):
    class Params(BaseModel):
        pass

    name = "workspace_sqlite_list"
    description = "List every SQLite database currently open on DataServer."

    async def call(self, args: Params, runtime: RuntimePackage):
        client = RuntimeContainer.get_runtime().data_client
        return [
            item.model_dump()
            for item in await client.list_sqlite()
        ]
