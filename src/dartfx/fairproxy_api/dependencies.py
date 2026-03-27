from functools import lru_cache
from typing import Any

from fastapi import HTTPException

from fairproxy_api.adapters.base import CatalogProvider, DatasetProvider
from fairproxy_api.models import Platform
from fairproxy_api.repositories.server import ServerRepository
from fairproxy_api.repositories.yaml_server import YamlServerRepository
from fairproxy_api.utils import resolve_resource


@lru_cache(maxsize=1)
def get_server_repository() -> ServerRepository:
    return YamlServerRepository()


@lru_cache(maxsize=128)
def get_socrata_server(host: str) -> Any:
    from fairproxy_api.adapters.socrata import create_socrata_server

    return create_socrata_server(host)


def get_platform_adapter(uri: str) -> DatasetProvider:
    """
    FastAPI Dependency to parse a URI string and return the corresponding initialized PlatformAdapter.
    Currently only supports Socrata based on current build status.
    """

    try:
        resource_info = resolve_resource(uri)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to resolve URN '{uri}': {err}") from err

    if not resource_info or not resource_info.platform:
        raise HTTPException(status_code=400, detail=f"Resource {uri} is not supported or malformed.")

    if resource_info.platform == Platform.SOCRATA:
        # Avoid circular import, delay import of adapters
        from fairproxy_api.adapters.socrata import SocrataAdapter

        # Leverage our SocrataServer lru cache
        server = get_socrata_server(resource_info.host)
        if resource_info.host_resource_id is None:
            raise HTTPException(status_code=400, detail=f"No dataset ID found in URI '{uri}'.")
        return SocrataAdapter(server, resource_info.host_resource_id)

    elif resource_info.platform == Platform.MTNARDS:
        raise HTTPException(status_code=501, detail="MTNA RDS integration is experimental and currently disabled.")

    elif resource_info.platform == Platform.USCENSUS:
        raise HTTPException(status_code=501, detail="US Census integration is experimental and currently disabled.")

    else:
        raise HTTPException(
            status_code=501, detail=f"Adapter for platform {resource_info.platform.value.name} is not implemented."
        )


def get_catalog_adapter(uri: str) -> CatalogProvider:
    """
    FastAPI Dependency to parse a URI string and return the corresponding initialized catalog-level adapter.
    """

    try:
        resource_info = resolve_resource(uri)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to resolve URN '{uri}': {err}") from err

    if not resource_info or not resource_info.platform:
        raise HTTPException(status_code=400, detail=f"Resource {uri} is not supported or malformed.")

    if resource_info.platform == Platform.SOCRATA:
        from fairproxy_api.adapters.socrata import SocrataCatalogAdapter

        server = get_socrata_server(resource_info.host)
        return SocrataCatalogAdapter(server)

    elif resource_info.platform == Platform.MTNARDS:
        raise HTTPException(status_code=501, detail="MTNA RDS catalog integration is experimental and currently disabled.")

    elif resource_info.platform == Platform.USCENSUS:
        raise HTTPException(status_code=501, detail="US Census catalog integration is experimental and currently disabled.")

    else:
        raise HTTPException(
            status_code=501, detail=f"Catalog adapter for platform {resource_info.platform.value.name} is not implemented."
        )
