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
  fairproxy-api:
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
  fairproxy-api:
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
  fairproxy-api:
    image: dartfx/fairproxy-api:latest
    ports:
      - "8000:8000"
    environment:
      - FAIRPROXY_SERVERS_CONFIG=/etc/custom/servers.yaml
    volumes:
      - ./my-custom-servers.yaml:/etc/custom/servers.yaml:ro
```

## Caching Configuration

To optimize performance and reduce downstream requests to data platforms, the API implements caching of external HTTP requests via `requests-cache`. You can configure the caching strategy using the following environment variables:

| Environment Variable | Description | Default |
| --- | --- | --- |
| `REQUEST_CACHE_BACKEND` | Cache backend: `memory`, `sqlite`, or `sqlalchemy` (Postgres) | `memory` |
| `REQUEST_CACHE_CONNECTION` | Connection URI for `sqlalchemy`, or file path for `sqlite` | *Optional* |
| `REQUEST_CACHE_EXPIRE` | Cache expiration time in seconds | `3600` (1 hour) |

### Memory Backend (Default)
In-memory caching stores requests in the running container's RAM. No extra configuration is needed:
```yaml
environment:
  - REQUEST_CACHE_BACKEND=memory
```

### SQLite Backend
Stores the cache in a local database file. To persist it across container rebuilds/restarts, bind-mount a host directory to `/app/cache`:
```yaml
services:
  fairproxy-api:
    image: dartfx/fairproxy-api:latest
    environment:
      - REQUEST_CACHE_BACKEND=sqlite
      # File path defaults to /app/cache/http_cache.sqlite if not specified
    volumes:
      # Bind-mount a local directory on your host to persist the cache database
      - ./api_cache:/app/cache
```

> [!IMPORTANT]
> **Directory Permissions (UID 10001)**
> Since the container runs as a non-root user (`appuser` with UID `10001`), the host directory must be writable by UID `10001`. Create the directory and set ownership before starting the container:
> ```bash
> mkdir -p api_cache
> sudo chown -R 10001:10001 api_cache
> ```

### PostgreSQL Backend
To share the cache across multiple container replicas or Gunicorn workers, use your existing PostgreSQL database:
```yaml
environment:
  - REQUEST_CACHE_BACKEND=sqlalchemy
  - REQUEST_CACHE_CONNECTION=postgresql+psycopg://user:password@postgres-host:5432/cache_db
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
