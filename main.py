from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from proxmox import get_proxmox_nodes
from docker_client import get_docker_containers

app = FastAPI(title="InfraMap API")

# CORS erlauben damit das React Frontend zugreifen kann
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite Dev Server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "InfraMap API läuft"}


@app.get("/api/topology")
def get_topology():
    """
    Hauptendpoint: gibt die gesamte Infrastruktur als JSON zurück.
    Kombiniert Proxmox-Daten und Docker-Daten.
    """
    nodes = get_proxmox_nodes()
    containers = get_docker_containers()

    return {
        "nodes": nodes,
        "docker_containers": containers,
    }


@app.get("/api/proxmox/nodes")
def proxmox_nodes():
    """Alle Proxmox Nodes, VMs und LXCs"""
    return get_proxmox_nodes()


@app.get("/api/docker/containers")
def docker_containers():
    """Alle laufenden Docker Container"""
    return get_docker_containers()
