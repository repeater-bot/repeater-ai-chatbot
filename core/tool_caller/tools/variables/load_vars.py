import orjson
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class LoadVariables(ToolPackage):
    class Params(BaseModel):
        pass

    name = "load_variable"
    description = "Load variables from user's persisting datas."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data = await global_runtime.program_data_manager.load(user_id = runtime.user_id)
        variables_str = data.variables

        if not variables_str:
            # A user that never dumped anything still has the empty default here;
            # that is an empty variable table, not a broken record.
            variables = {}
        else:
            try:
                variables = orjson.loads(variables_str)
            except orjson.JSONDecodeError:
                return "Invalid variables string."

            # Anything but a JSON object would poison the in memory table for this
            # user: `set_variable` would fail on the next write.
            if not isinstance(variables, dict):
                return "Variables must be a JSON object."

        async with ToolsCaller.variable_lock:
            ToolsCaller.variables[runtime.user_id] = variables

        return "Variable loaded."