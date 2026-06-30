import re

import uritools
from fastapi import HTTPException, Request

from .models import Platform, ResourceInfo


def get_rdf_format(request: Request) -> tuple[str, str]:
    """Get RDF serialization format from an HTTP request (content negotiation)."""

    format = "json-ld"
    mimetype = "application/ld+json"

    # In FastAPI, headers are accessed like a dict
    accept_header = request.headers.get("Accept")
    format_param = request.query_params.get("format")

    if format_param:
        format_param = format_param.lower()
        if format_param in ["json", "json-ld"]:
            format = "json-ld"
            mimetype = "application/ld+json"
        elif format_param in ["turtle", "ttl"]:
            format = "turtle"
            mimetype = "text/turtle"
        elif format_param in ["ntriples", "nt"]:
            format = "ntriples"
            mimetype = "text/plain"
        elif format_param == "pretty-xml":
            format = "pretty-xml"
            mimetype = "application/xml"
        elif format_param == "n3":
            format = "n3"
            mimetype = "text/n3"
        elif format_param == "trig":
            format = "trig"
            mimetype = "application/trig"
        elif format_param == "xml":
            format = "xml"
            mimetype = "application/xml"
        else:
            raise HTTPException(
                status_code=406,
                detail=(
                    "Format parameter must be 'json', 'json-ld', 'n3', 'ntriples', 'nt', "
                    "'pretty-xml', 'trig', 'turtle', 'ttl', 'xml'"
                ),
            )
    elif accept_header:
        accept_header = accept_header.lower()
        if "text/turtle" in accept_header:
            format = "turtle"
            mimetype = "text/turtle"
        elif "application/rdf+xml" in accept_header:
            format = "xml"
            mimetype = "application/xml"
    return format, mimetype


def resolve_resource(uri: str) -> ResourceInfo:
    """Infers resources identify and information based on URI"""
    resource_info = ResourceInfo(uri=uri)
    if re.match(r"^https?://.*", uri):
        # URL
        uritools.urisplit(uri)
        raise NotImplementedError("URLs based URI not supported at this time...")
    else:
        # URN
        tokens = uri.split(":")
        if tokens:
            if tokens[0].casefold() == "urn":
                tokens.pop(0)

            try:
                platform_id = tokens.pop(0)
                platform = Platform[platform_id.upper()]
                resource_info.platform = platform
            except KeyError:
                raise ValueError(f"Unknown platform ID: {platform_id}") from None

            resource_info.host = tokens.pop(0)
            if resource_info.platform == Platform.SOCRATA:
                if len(tokens) == 0:
                    resource_info.type = ResourceInfo.Type.CATALOG
                elif len(tokens) == 1:
                    resource_info.type = ResourceInfo.Type.DATASET
                    resource_info.host_resource_id = tokens[0]
                else:
                    raise ValueError(f"Malformed Socrata URI {uri}")
            elif resource_info.platform == Platform.MTNARDS:
                if len(tokens) == 0:
                    resource_info.type = ResourceInfo.Type.SERVER
                elif len(tokens) == 1:
                    resource_info.type = ResourceInfo.Type.CATALOG
                    resource_info.host_resource_id = tokens[0]
                elif len(tokens) == 2:
                    resource_info.type = ResourceInfo.Type.DATASET
                    resource_info.host_resource_id = ":".join(tokens)
            elif resource_info.platform == Platform.USCENSUS:
                if len(tokens) == 0:
                    resource_info.type = ResourceInfo.Type.CATALOG
                    resource_info.host_resource_id = tokens[0]
                elif len(tokens) == 1:
                    resource_info.type = ResourceInfo.Type.DATASET
                    resource_info.host_resource_id = ":".join(tokens)
            else:
                resource_info.host_resource_id = ":".join(tokens)
        else:
            pass
    return resource_info
