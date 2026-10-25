import orjson
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class DumpVariables(ToolPackage):
    class Params(BaseModel):
        pass

    name = "dump_variable"
    description = "Dump variables to user's persisting datas."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        async with ToolsCaller.variable_lock:
            variables = ToolsCaller.variables.get(runtime.user_id)
            if variables is None:
                variables = {}
            try:
                variables_str = orjson.dumps(variables).decode("utf-8")
            except orjson.JSONEncodeError:
                return "Variables cannot be dumped."

        data = await global_runtime.program_data_manager.load(user_id = runtime.user_id)
        data.variables = variables_str
        await global_runtime.program_data_manager.save(user_id = runtime.user_id, data = data)

        return "Variable dumped."