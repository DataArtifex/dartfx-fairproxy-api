import os

import yaml
from fairproxy_api.models import Platform, ServerInfo
from fairproxy_api.repositories.server import ServerRepository


class YamlServerRepository(ServerRepository):
    """
    Local implementation of ServerRepository parsing the local YAML file.
    Legacy behavior ported from the hvdnet_api prototype.
    """

    def __init__(self, file_path: str | None = None):
        if file_path is None:
            # 1. Check for environment variable configuration override
            env_path = os.environ.get("FAIRPROXY_SERVERS_CONFIG")
            if env_path:
                self.file_path = env_path
            # 2. Check for container default config path
            elif os.path.exists("/app/config/servers.yaml"):
                self.file_path = "/app/config/servers.yaml"
            # 3. Check for system default config path
            elif os.path.exists("/etc/fairproxy/servers.yaml"):
                self.file_path = "/etc/fairproxy/servers.yaml"
            # 4. Fallback to package-embedded servers configuration
            else:
                module_dir = os.path.dirname(__file__)
                self.file_path = os.path.join(module_dir, "servers.yaml")
        else:
            self.file_path = file_path

        self._cache: list[ServerInfo] = []
        self._loaded = False

    def _load_if_needed(self) -> None:
        if self._loaded:
            return

        with open(self.file_path) as file:
            data = yaml.safe_load(file)

        servers_data = data.get("servers", {})
        for key, value in servers_data.items():
            server = ServerInfo(id=key, **value)
            self._cache.append(server)

        self._loaded = True

    def get_all(self, platform: Platform | None = None) -> list[ServerInfo]:
        self._load_if_needed()
        if platform:
            return [s for s in self._cache if s.platform == platform.value.id]
        return self._cache

    def get_by_id(self, server_id: str) -> ServerInfo | None:
        self._load_if_needed()
        for server in self._cache:
            if server.id == server_id:
                return server
        return None
