import json
from importlib import import_module
from typing import Any, cast

from fairproxy_api.adapters.base import CatalogProvider, DatasetProvider
from fastapi import HTTPException
from lxml import etree
from rdflib import Graph

SOCRATA_MODULE = "dartfx.socrata"
DDI_MODULE = "dartfx.ddi.ddicodebook"
DDI_UTILS_MODULE = "dartfx.ddi.ddicodebook.utils"
POSTMAN_SOCRATA_MODULE = "dartfx.postman.socrata"


def _missing_dartfx_dependency_error(err: Exception) -> HTTPException:
    return HTTPException(
        status_code=501,
        detail=(
            "Socrata adapter dependencies are unavailable in this environment. "
            "Required modules include 'dartfx.socrata', 'dartfx.ddi.ddicodebook', "
            "and 'dartfx.postman.socrata'. "
            f"Original import error: {err}"
        ),
    )


def _import_socrata_server_class() -> Any:
    try:
        module = import_module(SOCRATA_MODULE)
        return module.SocrataServer
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def _import_socrata_dataset_class() -> Any:
    try:
        module = import_module(SOCRATA_MODULE)
        return module.SocrataDataset
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def _import_socrata_dcat_generator() -> Any:
    try:
        module = import_module(SOCRATA_MODULE)
        return module.DcatGenerator
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def _import_loadxmlstring() -> Any:
    try:
        module = import_module(DDI_MODULE)
        return module.loadxmlstring
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def _import_codebook_to_cdif_graph() -> Any:
    try:
        module = import_module(DDI_UTILS_MODULE)
        return module.codebook_to_cdif_graph
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def _import_socrata_postman_collection_generator() -> Any:
    try:
        module = import_module(POSTMAN_SOCRATA_MODULE)
        return module.SocrataPostmanCollectionGenerator
    except (ModuleNotFoundError, AttributeError) as err:
        raise _missing_dartfx_dependency_error(err) from err


def create_socrata_server(host: str) -> Any:
    socrata_server_class = _import_socrata_server_class()
    return socrata_server_class(host=host)


class SocrataAdapter(DatasetProvider):
    """
    Adapter implementing the DatasetProvider interface for Socrata datasets.
    Wraps the dartfx logic for Socrata into asynchronous FastAPI-compatible methods.
    """

    def __init__(self, server: Any, dataset_id: str):
        self.server = server
        self.dataset_id = dataset_id
        self._dataset: Any | None = None

    @property
    def dataset(self) -> Any:
        if self._dataset is None:
            try:
                socrata_dataset_class = _import_socrata_dataset_class()
                self._dataset = socrata_dataset_class(server=self.server, id=self.dataset_id)
            except HTTPException:
                raise
            except Exception as err:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Dataset {self.dataset_id} could not be initialized or found on "
                        f"Socrata host {self.server.host}. Error: {err}"
                    ),
                ) from err
        return self._dataset

    async def get_croissant(self) -> dict[str, Any]:
        try:
            croissant = self.dataset.get_croissant()
            if croissant is None:
                raise HTTPException(status_code=500, detail="Failed to generate Croissant metadata.")
            return cast(dict[str, Any], croissant.to_json())
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating Croissant: {err}") from err

    async def get_dcat_graph(self) -> Graph:
        try:
            dcat_generator_class = _import_socrata_dcat_generator()
            generator = dcat_generator_class(self.dataset.server)
            generator.add_dataset(self.dataset.id)
            return cast(Graph, generator.get_graph())
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating DCAT: {err}") from err

    async def get_ddi_cdif_graph(self, use_skos: bool = True, cdif_variable_count_limit: int = 100) -> Graph:
        try:
            if len(self.dataset.variables) > cdif_variable_count_limit:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        "This service does not support datasets with more than "
                        f"{cdif_variable_count_limit} variables due to size limitations."
                    ),
                )

            xml_content = self.dataset.get_ddi_codebook()
            loadxmlstring = _import_loadxmlstring()
            codebook_to_cdif_graph = _import_codebook_to_cdif_graph()
            codebook = loadxmlstring(xml_content)
            return cast(Graph, codebook_to_cdif_graph(codebook, use_skos=use_skos))
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating DDI-CDIF: {err}") from err

    async def get_ddi_codebook_xml(self, pretty: bool = False) -> str:
        try:
            xml_content = self.dataset.get_ddi_codebook()
            if not xml_content:
                raise HTTPException(status_code=500, detail="DDI Codebook XML is empty.")

            if pretty:
                try:
                    xml_content_bytes = xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content
                    root = etree.fromstring(xml_content_bytes)
                    etree.indent(root, space="  ")
                    return etree.tostring(root, encoding="utf-8").decode("utf-8")
                except etree.XMLSyntaxError:
                    # Fallback to raw if pretty printing fails
                    pass
            return cast(str, xml_content)
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating DDI Codebook: {err}") from err

    async def get_markdown(self) -> str:
        try:
            md_content = self.dataset.get_markdown()
            if md_content is None:
                raise HTTPException(status_code=500, detail="Markdown response is unexpectedly None.")
            return cast(str, md_content)
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating Markdown: {err}") from err

    async def get_postman_collection(self) -> dict[str, Any]:
        try:
            postman_generator_class = _import_socrata_postman_collection_generator()
            generator = postman_generator_class(dataset=self.dataset)
            collection = generator.generate()
            if collection is None:
                raise HTTPException(status_code=500, detail="Postman collection object is None after generation.")

            if hasattr(collection, "to_dict"):
                return cast(dict[str, Any], collection.to_dict())
            if hasattr(collection, "model_dump"):
                return cast(dict[str, Any], collection.model_dump(exclude_none=True))

            collection_json_str = json.dumps(collection, default=str)
            return cast(dict[str, Any], json.loads(collection_json_str))
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred generating Postman collection: {err}",
            ) from err

    async def get_native_socrata_data(self) -> dict[str, Any]:
        try:
            return cast(dict[str, Any], self.dataset.data)
        except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred retrieving Socrata native data: {err}",
            ) from err

    async def get_native_data(self) -> dict[str, Any]:
        return await self.get_native_socrata_data()

    async def get_code_snippet(self, environment: str) -> str:
        try:
            code = self.dataset.get_code(environment)
            if code is None:
                raise HTTPException(
                    status_code=501,
                    detail=(
                        f"Code snippet for environment '{environment}' is not available "
                        "or not implemented for this dataset."
                    ),
                )
            return cast(str, code)
        except ValueError as err:
            raise HTTPException(status_code=501, detail=str(err)) from err
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(
                status_code=500, detail=f"An error occurred getting code snippet for env '{environment}': {err}"
            ) from err


class SocrataCatalogAdapter(CatalogProvider):
    """
    Adapter implementing the CatalogProvider interface for Socrata catalog/server metadata.
    """

    def __init__(self, server: Any):
        self.server = server

    async def get_dcat_graph(self) -> Graph:
        try:
            dcat_generator_class = _import_socrata_dcat_generator()
            generator = dcat_generator_class(self.server)
            return cast(Graph, generator.get_graph())
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred generating catalog DCAT: {err}") from err
