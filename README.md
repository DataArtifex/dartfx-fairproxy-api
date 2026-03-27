# fair-proxy-api

[![PyPI - Version](https://img.shields.io/pypi/v/fair-proxy-api.svg)](https://pypi.org/project/fair-proxy-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fair-proxy-api.svg)](https://pypi.org/project/fair-proxy-api)
[![CI](https://github.com/DataArtifex/fair-proxy-api/actions/workflows/test.yml/badge.svg)](https://github.com/DataArtifex/fair-proxy-api/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/DataArtifex/fair-proxy-api.svg)](https://github.com/DataArtifex/fair-proxy-api/blob/main/LICENSE.txt)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/DataArtifex/fair-proxy-api)

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
