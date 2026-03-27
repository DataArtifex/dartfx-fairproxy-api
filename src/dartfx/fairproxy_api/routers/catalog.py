from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from fairproxy_api.adapters.base import CatalogProvider
from fairproxy_api.dependencies import get_catalog_adapter
from fairproxy_api.models import ResourceInfo
from fairproxy_api.utils import get_rdf_format, resolve_resource

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/{uri:path}/dcat")
async def dcat(
    uri: str, request: Request, adapter: Annotated[CatalogProvider, Depends(get_catalog_adapter)]
) -> Response:
    """
    W3C DCAT metadata for this catalog.
    NOTE: In the context of the prototype, this mapped out all catalogs using dartfx generators
    across the Server/DCAT platforms. Because dartfx components are currently inaccessible across
    this workspace environment, this method yields the base dataset DCAT graph from the Mock adapter for testing.
    """
    try:
        resource_info = resolve_resource(uri)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to resolve URN '{uri}': {err}") from err

    if not resource_info or resource_info.type not in [ResourceInfo.Type.CATALOG, ResourceInfo.Type.SERVER]:
        raise HTTPException(status_code=400, detail=f"Resource {uri} is not a valid catalog or server.")

    # Depending on the resolved PlatformAdapter (MTNA vs Socrata), this would generate DCAT.
    # We call adapter.get_dcat_graph() which natively yields the mocked graph currently mapped in SocrataAdapter
    graph = await adapter.get_dcat_graph()

    format, mimetype = get_rdf_format(request)
    response_data = graph.serialize(format=format, indent=4)

    return Response(content=response_data, media_type=mimetype)


@router.get("/{uri:path}")
def hvdnet(uri: str) -> dict[str, Any]:
    """Returns the parsed HVD resource info structure."""
    try:
        resource_info = resolve_resource(uri)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to resolve URN '{uri}': {err}") from err

    if not resource_info:
        raise HTTPException(status_code=404, detail=f"Resource {uri} not found.")

    if resource_info.type != ResourceInfo.Type.CATALOG:
        raise HTTPException(status_code=400, detail=f"Resource {uri} is a {resource_info.type}, not a catalog.")

    return resource_info.model_dump(exclude_none=True)
