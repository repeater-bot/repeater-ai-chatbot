from ....runtime_container import RuntimeContainer
from ....clients.data_client import DataClient


def get_data_client() -> DataClient:
    """Return the shared DataClient held by the running server."""
    return RuntimeContainer.get_runtime().data_client
