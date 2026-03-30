import docker


def get_docker_containers() -> list[dict]:
    """
    Liest alle laufenden Docker Container über den Docker Socket aus.
    Der Socket muss im docker-compose.yml als Volume eingebunden sein.
    """
    try:
        client = docker.from_env()
        result = []

        for container in client.containers.list(all=True):
            # Ports: Docker gibt ein Dict zurück, wir vereinfachen es
            ports = []
            for container_port, host_bindings in (container.ports or {}).items():
                if host_bindings:
                    for binding in host_bindings:
                        ports.append(f"{binding['HostPort']}→{container_port}")
                else:
                    ports.append(container_port)

            # Netzwerke
            networks = list(container.attrs.get("NetworkSettings", {}).get("Networks", {}).keys())

            # Labels – interessant für Traefik und eigene infra.* Labels
            labels = container.labels or {}
            depends_on = labels.get("infra.depends-on", "")
            depends_on_list = [d.strip() for d in depends_on.split(",")] if depends_on else []

            result.append({
                "id": container.short_id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "status": container.status,         # running, exited, paused, ...
                "ports": ports,
                "networks": networks,
                "depends_on": depends_on_list,      # aus infra.depends-on Label
                "labels": {
                    k: v for k, v in labels.items()
                    if k.startswith("infra.") or k.startswith("traefik.")
                },
            })

        return result

    except Exception as e:
        return [{"error": str(e), "hint": "Docker Socket nicht erreichbar – läuft das Backend in Docker?"}]
