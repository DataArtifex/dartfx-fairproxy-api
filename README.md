# fairproxy-api

[![Development Status](https://img.shields.io/badge/status-early%20release-orange.svg)](https://github.com/DataArtifex/dartfx-fairproxy-api)
[![Documentation](https://img.shields.io/badge/docs-blue)](https://www.dataartifex.org/dartfx-fairproxy-api/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/DataArtifex/dartfx-fairproxy-api)
[![Package Status](https://img.shields.io/badge/PyPI-not%20published-lightgrey)](https://github.com/DataArtifex/dartfx-fairproxy-api)
[![CI](https://github.com/DataArtifex/rdf-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/DataArtifex/dartfx-fairproxy-api/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![License](https://img.shields.io/github/license/DataArtifex/rdf-toolkit.svg)](https://github.com/DataArtifex/dartfx-fairproxy-api/blob/main/LICENSE.txt)

**This project is in its early development stages. Stability is not guaranteed, and documentation is limited. We welcome your feedback and contributions.**

## Overview

`fairproxy-api` is a FastAPI service that exposes FAIR-oriented metadata and native
payloads for heterogeneous data platforms behind a single API surface.

## Supported Platform

[Socrata](https://dev.socrata.com/) (a.k.a. Data Insights) is the only fully implemented platform at this time. Support for [MTNA Rich Data Services](https:/www.richdataservices.com) in under development.

### Socrata

Socrata (also known as Data Insights) is a cloud data publishing platform used by governments and organizations to host open data portals and dataset APIs.

Socrata datasets through both a unified FAIR URI route (`/datasets/{uri}`) and a
Socrata-specific route (`/socrata/{host}/{dataset_id}`).

## Supported Standards

- [Croissant](https://mlcommons.org/working-groups/data/croissant/) — MLCommons metadata format for machine learning datasets.
- [DCAT](https://www.w3.org/TR/vocab-dcat-3/) — W3C vocabulary for publishing data catalogs on the web.
- [DDI Codebook](https://ddialliance.org/create-a-codebook) — XML standard for documenting survey and social science datasets.
- [DDI-CDI](https://ddialliance.org/ddi-cdi) (via CDIF profile) — semantic model for structured data integration and interoperability.
- [Markdown](https://www.markdownguide.org/) — lightweight plain-text format for human-readable dataset summaries.
- [Postman Collection](https://schema.postman.com/) — machine-readable API request collection format for tooling and sharing.
- platform-native metadata via the common `/native` endpoint

## Installation

This project recommends using [uv](https://github.com/astral-sh/uv) for fast and reliable Python package management.

### Setup with uv

To set up the development environment with `uv`:

```bash
# Install dependencies and create virtual environment
uv sync
```

Run project tasks with `uv run`:

```bash
# Run tests
uv run pytest

# Build documentation
uv run sphinx-build -b html docs/source docs/build/html
```

### Optional: Hatch via uvx

You can also use [Hatch](https://hatch.pypa.io/) directly:

```bash
# Run tests
uvx hatch run test

# Enter the default shell
uvx hatch shell
```

## Configuration

The FAIRification API relies on a `servers.yaml` file to resolve and discover data servers. By default, the application uses an embedded `servers.yaml` file packaged with the source.

To customize or externalize this configuration (especially in containerized environments), you can configure the file path using the following lookup order:

1. **Environment Variable**: Set the `FAIRPROXY_SERVERS_CONFIG` environment variable to the absolute path of your custom YAML file.
2. **Container Config**: Mount your custom file to `/app/config/servers.yaml` (automatically detected inside Docker containers).
3. **System Config**: Place your custom file at `/etc/fairproxy/servers.yaml`.
4. **Embedded Default**: Fall back to the packaged `servers.yaml`.

### Docker Compose Configuration

To mount and use a custom servers configuration in Docker Compose, update your `docker-compose.yaml` service definition:

```yaml
services:
  fairproxy-api:
    # ...
    volumes:
      - ./my-custom-servers.yaml:/app/config/servers.yaml:ro
```

## Development

### Version Management

Versions are managed dynamically in `src/dartfx/fairproxy_api/__about__.py`.

### Secret Management

For local development, create a `.env` file in the root directory. This file is git-ignored and can be used to store local API keys or configuration. These are automatically loaded by the test suite.

### Run API Locally

From this project directory, install dependencies first:

```bash
uv sync
```

Start the API from this project directory:

```bash
uv run uvicorn --app-dir src/dartfx fairproxy_api.main:app --host 0.0.0.0 --port 8000 --reload
```

If you prefer to run it from the monorepo root, use the package-targeted form:

```bash
uv run --package dartfx-fairproxy-api uvicorn --app-dir dartfx-fairproxy-api/src/dartfx fairproxy_api.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternative using `PYTHONPATH`:

```bash
PYTHONPATH=src/dartfx uv run uvicorn fairproxy_api.main:app --host 0.0.0.0 --port 8000 --reload
```

Quick health check:

```bash
curl http://127.0.0.1:8000/status
```

Quick tests:

```bash
# get list of servers
curl http://127.0.0.1:8000/servers


# Get San Francisco 311 Dataset (Socrata)
curl http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/native
curl http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/ddi/codebook
curl http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/ddi/cdi
curl http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/dcat

# Get San Francisco 311 Dataset (Unified)
curl http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/markdown
curl http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/postman/collection

```

### Running with Docker

You can also run the application containerized using Docker and Docker Compose:

```bash
# Build the container image
docker compose build

# Start the service in the background
docker compose up -d

# Verify it is running
curl http://localhost:8000/status
```

To stop the container:

```bash
docker compose down
```

### Deployment Behind a Reverse Proxy (Nginx / Nginx Proxy Manager)

When exposing the API behind a reverse proxy under a subpath like `/fairproxy`, both the proxy and the application must be configured to handle the path prefix routing.

#### 1. FastAPI / Uvicorn Configuration

For FastAPI to generate correct URLs (e.g. for Swagger UI at `/fairproxy/docs` instead of `/docs`), it needs to know the subpath prefix. Configure this using the `UVICORN_ROOT_PATH` environment variable in your `docker-compose.yaml`:

```yaml
services:
  fairproxy-api:
    image: dartfx/fairproxy-api:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app/src/dartfx
      # Tell FastAPI it is hosted behind the /fairproxy subpath
      - UVICORN_ROOT_PATH=/fairproxy
```

#### 2. Nginx Configuration

In your Nginx site configuration, rewrite the incoming subpath and forward the headers:

```nginx
location /fairproxy/ {
    proxy_pass http://fairproxy-api:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /fairproxy;
}
```

> [!NOTE]
> Make sure the trailing slash `/` is present in both `location /fairproxy/` and `proxy_pass http://fairproxy-api:8000/;` so Nginx correctly strips the `/fairproxy` prefix before forwarding the request to the container.

#### 3. Nginx Proxy Manager Setup (Shared Host Configuration)

If you are using **Nginx Proxy Manager** (NPM) to route a single domain host (e.g., `api.highvaluedata.net`) to multiple backend APIs on the same Docker network, you can configure `fairproxy-api` as a **Custom Location** under that shared host:

1. In NPM, create or edit the **Proxy Host** for your domain (e.g., `api.highvaluedata.net`).
2. Go to the **Custom Locations** tab.
3. Click **Add Location** to register the `fairproxy` endpoint:
   - **Define Location**: `/fairproxy/`
   - **Scheme**: `http`
   - **Forward Host / IP**: `fairproxy-api` (resolves via the shared Docker network)
   - **Forward Port**: `8000`
4. Click the gear icon next to the location definition to insert the **Advanced** configuration:
   ```nginx
   rewrite ^/fairproxy$ / break;
   rewrite ^/fairproxy/(.*)$ /$1 break;
   proxy_set_header X-Forwarded-Prefix /fairproxy;
   ```

*(You can then repeat this pattern under the same Proxy Host to add other API endpoints under different location paths like `/anotherapi/`.)*

### Verifying and Publishing the Image

We provide helper scripts to verify and publish the Docker image:

1. **Verify**: Validate the built image locally to ensure the container starts up and responds to status checks:

   ```bash
   ./verify_images.sh
   ```

2. **Publish**: Build (if not present locally), verify, tag (with `latest` and the dynamic project version from `__about__.py`), and push the image to a container registry:

   ```bash
   # Build, verify, tag, and publish to Docker Hub (default namespace 'dartfx')
   ./publish_image.sh

   # Publish with a custom namespace or custom tag
   ./publish_image.sh --namespace custom-namespace --tag custom-tag
   ```

### Running Tests

```bash
uv run pytest
```

### Building Documentation

```bash
uv run sphinx-build -b html docs/source docs/build/html
```

## Usage

### Health Check

```bash
curl http://127.0.0.1:8000/status
```

### Current Top-Level Routes

- `/status` for health status
- `/servers` for configured data server discovery
- `/datasets/{uri}` for unified dataset metadata and native payloads
- `/socrata/{host}/{dataset_id}` for Socrata-specific dataset access

Generic routes like `/catalog`, `/resources`, and `/vocab` are intentionally not exposed in the current build.

### Socrata URI Format

The unified datasets endpoint expects Socrata URIs in this format:

`socrata:<server>:<dataset-id>`

Where:

- `socrata` is the platform identifier.
- `<server>` is the Socrata host (for example, `data.sfgov.org`).
- `<dataset-id>` is the Socrata dataset identifier (for example, `wg3w-h783`).

Example URI:

`socrata:data.sfgov.org:wg3w-h783`

### Example Socrata Metadata Endpoints

Unified dataset route using a FAIR URI:

```bash
curl "http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/ddi/codebook"
curl "http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/postman/collection"
curl "http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/markdown"
curl "http://127.0.0.1:8000/datasets/socrata:data.sfgov.org:wg3w-h783/native"
```

Socrata-native route using host and dataset id:

```bash
curl "http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/ddi/codebook"
curl "http://127.0.0.1:8000/socrata/data.sfgov.org/wg3w-h783/native"
```

### Notes

- `/datasets/{uri}/native` is the platform-agnostic native payload endpoint.
- `/socrata/{host}/{dataset_id}/native` exposes the same native payload through the Socrata-specific route.
- The older `/socrata` native suffix has been replaced by `/native`.

## Roadmap

- MTNA Rich Data Service (MTNA RDS) adapter support
- Additional platform adapters aligned with the common `DatasetProvider` interface

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines and information on how to get started.
