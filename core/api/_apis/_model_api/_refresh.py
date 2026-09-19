from ....repeater_main import RepeaterMain
from ._router import models_router
from fastapi.responses import ORJSONResponse
from ....special_exception import HTTPException

@models_router.get("/")
@models_router.get("/{provider_id:path}")
async def refresh(provider_id: str | None = None):
    server = RepeaterMain.get_now_server()
    response = await server.runtime.model_info_client.refresh(provider_id)

    if response:
        return ORJSONResponse(
            content = {
                "status": "success",
                "Message": "Models refreshed successfully"
            }
        )
    else:
        raise HTTPException(
            status_code = 500,
            detail = "Internal server error"
        )