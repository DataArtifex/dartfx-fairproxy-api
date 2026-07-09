from fairproxy_api.dependencies import get_server_repository
from fairproxy_api.main import app
from fairproxy_api.repositories.yaml_server import YamlServerRepository
from fastapi.testclient import TestClient

client = TestClient(app)


def test_status_endpoint() -> None:
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pass"
    assert data["version"] == "0.1.0"
    assert "releaseId" in data
    assert data["releaseId"] == "development"


def test_root_endpoint_landing_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FAIRification Proxy API" in response.text


def test_socrata_dcat() -> None:
    response = client.get("/socrata/data.cityofnewyork.us/uvpi-gqnh/dcat")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/ld+json"


def test_socrata_unified_dcat() -> None:
    response = client.get("/datasets/urn:socrata:data.cityofnewyork.us:uvpi-gqnh/dcat")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/ld+json"


def test_unsupported_unified_platform() -> None:
    response = client.get("/datasets/urn:mtnards:rds.highvalueata.net:catalog:dataset/dcat")
    assert response.status_code == 501
    assert "experimental" in response.json()["detail"]


def test_resources_endpoint_removed() -> None:
    response = client.get("/resources/")
    assert response.status_code == 404


def test_vocab_endpoint_removed() -> None:
    response = client.get("/vocab/")
    assert response.status_code == 404


# Servers Route Tests
def override_get_server_repository() -> YamlServerRepository:
    return YamlServerRepository()


app.dependency_overrides[get_server_repository] = override_get_server_repository


def test_servers_get_all() -> None:
    response = client.get("/servers/")
    assert response.status_code == 200
    servers = response.json()
    assert isinstance(servers, list)
    assert len(servers) > 0  # servers.yaml has multiple entries


def test_servers_get_by_id() -> None:
    response = client.get("/servers/data.cityofchicago.org")
    assert response.status_code == 200
    server = response.json()
    assert server["id"] == "data.cityofchicago.org"
    assert server["platform"] == "socrata"


def test_servers_get_by_id_missing() -> None:
    response = client.get("/servers/does_not_exist_at_all")
    assert response.status_code == 404


# Catalog Route Tests
def test_catalog_endpoint_removed() -> None:
    response = client.get("/catalog/urn:socrata:data.cityofnewyork.us/dcat")
    assert response.status_code == 404


def test_yaml_server_repository_path_resolution(tmp_path) -> None:
    import os
    from unittest.mock import patch

    # Create a temporary yaml configuration file
    temp_yaml = tmp_path / "custom_servers.yaml"
    temp_yaml.write_text("""
servers:
  custom.server.org:
    platform: socrata
    name: Custom Test Server
""")

    # 1. Test environment variable override
    with patch.dict(os.environ, {"FAIRPROXY_SERVERS_CONFIG": str(temp_yaml)}):
        repo = YamlServerRepository()
        assert repo.file_path == str(temp_yaml)
        servers = repo.get_all()
        assert len(servers) == 1
        assert servers[0].id == "custom.server.org"
        assert servers[0].name == "Custom Test Server"

    # 2. Test fallback check paths using mock of os.path.exists
    with patch("os.path.exists") as mock_exists:
        # Mock /app/config/servers.yaml exists
        mock_exists.side_effect = lambda p: p == "/app/config/servers.yaml"
        repo = YamlServerRepository()
        assert repo.file_path == "/app/config/servers.yaml"

        # Mock /etc/fairproxy/servers.yaml exists
        mock_exists.side_effect = lambda p: p == "/etc/fairproxy/servers.yaml"
        repo = YamlServerRepository()
        assert repo.file_path == "/etc/fairproxy/servers.yaml"
