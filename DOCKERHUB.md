# FAIRification Proxy API (`fairproxy-api`)

The `fairproxy-api` is a FastAPI service designed to expose FAIR-oriented metadata (such as DCAT, MLCommons Croissant, and DDI-CDIF graphs) and native payloads for heterogeneous data platforms behind a single unified API surface.

Currently, it provides out-of-the-box support for **Socrata** (Data Insights) open data portals, with experimental/under-development support for **MTNA Rich Data Services (RDS)** and **U.S. Census** APIs.

## Quick Start

You can run the `fairproxy-api` container using Docker or Docker Compose.

### Running with Docker

Run the container exposing port `8000`:

```bash
docker run -d \
  --name fairproxy-api \
  -p 8000:8000 \
  dartfx/fairproxy-api:latest
```

Once started, you can verify it is running by checking the status endpoint:

```bash
curl http://localhost:8000/status
```

### Running with Docker Compose

Create a `docker-compose.yaml` file:

```yaml
services:
  api:
    image: dartfx/fairproxy-api:latest
    ports:
      - "8000:8000"
    security_opt:
      - no-new-privileges:true
```

Start the service:

```bash
docker compose up -d
```

## Configuration & Externalizing Servers

The proxy relies on a server registry configuration (`servers.yaml`) to discover and resolve data hosts. By default, the image runs with a packaged set of embedded open data servers.

To override or customize this configuration in your Docker environment, you can use the following methods:

### Method 1: Mount configuration to the default container path

Mount your custom `servers.yaml` directly to `/app/config/servers.yaml` inside the container. The application automatically detects and loads the file from this path:

```yaml
services:
  api:
    image: dartfx/fairproxy-api:latest
    ports:
      - "8000:8000"
    volumes:
      - ./my-custom-servers.yaml:/app/config/servers.yaml:ro
```

### Method 2: Configure via environment variable

Mount your custom `servers.yaml` to any path in the container, and set the `FAIRPROXY_SERVERS_CONFIG` environment variable to point to it:

```yaml
services:
  api:
    image: dartfx/fairproxy-api:latest
    ports:
      - "8000:8000"
    environment:
      - FAIRPROXY_SERVERS_CONFIG=/etc/custom/servers.yaml
    volumes:
      - ./my-custom-servers.yaml:/etc/custom/servers.yaml:ro
```

## Example API Queries

Once the service is running, you can explore the following endpoints:

* **Health Check**:
  ```bash
  curl http://localhost:8000/status
  ```
* **List Registered Servers**:
  ```bash
  curl http://localhost:8000/servers
  ```
* **Retrieve DCAT Metadata (Socrata route)**:
  ```bash
  curl http://localhost:8000/socrata/data.sfgov.org/wg3w-h783/dcat
  ```
* **Retrieve DDI Codebook (Unified dataset route)**:
  ```bash
  curl http://localhost:8000/datasets/socrata:data.sfgov.org:wg3w-h783/ddi/codebook
  ```
