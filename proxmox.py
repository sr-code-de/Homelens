import os
from proxmoxer import ProxmoxAPI

# Konfiguration aus Umgebungsvariablen (sicherer als Passwort im Code)
PROXMOX_HOST     = os.getenv("PROXMOX_HOST", "192.168.1.10")
PROXMOX_USER     = os.getenv("PROXMOX_USER", "root@pam")
PROXMOX_PASSWORD = os.getenv("PROXMOX_PASSWORD", "")
PROXMOX_VERIFY_SSL = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"


def get_client() -> ProxmoxAPI:
    """Gibt einen authentifizierten Proxmox API Client zurück"""
    return ProxmoxAPI(
        PROXMOX_HOST,
        user=PROXMOX_USER,
        password=PROXMOX_PASSWORD,
        verify_ssl=PROXMOX_VERIFY_SSL,
    )


def get_proxmox_nodes() -> list[dict]:
    """
    Liest alle Nodes, VMs und LXCs aus Proxmox aus.
    Gibt eine strukturierte Liste zurück.
    """
    try:
        proxmox = get_client()
        result = []

        for node in proxmox.nodes.get():
            node_name = node["node"]

            node_data = {
                "name": node_name,
                "status": node.get("status", "unknown"),
                "cpu": round(node.get("cpu", 0) * 100, 1),       # in Prozent
                "mem_used_gb": round(node.get("mem", 0) / 1e9, 1),
                "mem_total_gb": round(node.get("maxmem", 0) / 1e9, 1),
                "uptime_hours": round(node.get("uptime", 0) / 3600, 1),
                "vms": [],
                "lxcs": [],
            }

            # VMs (QEMU)
            for vm in proxmox.nodes(node_name).qemu.get():
                node_data["vms"].append({
                    "id": vm.get("vmid"),
                    "name": vm.get("name", "unknown"),
                    "status": vm.get("status", "unknown"),
                    "cpu": round(vm.get("cpu", 0) * 100, 1),
                    "mem_used_gb": round(vm.get("mem", 0) / 1e9, 1),
                    "mem_total_gb": round(vm.get("maxmem", 0) / 1e9, 1),
                    "uptime_hours": round(vm.get("uptime", 0) / 3600, 1),
                    "type": "vm",
                })

            # LXC Container
            for lxc in proxmox.nodes(node_name).lxc.get():
                node_data["lxcs"].append({
                    "id": lxc.get("vmid"),
                    "name": lxc.get("name", "unknown"),
                    "status": lxc.get("status", "unknown"),
                    "cpu": round(lxc.get("cpu", 0) * 100, 1),
                    "mem_used_gb": round(lxc.get("mem", 0) / 1e9, 1),
                    "mem_total_gb": round(lxc.get("maxmem", 0) / 1e9, 1),
                    "uptime_hours": round(lxc.get("uptime", 0) / 3600, 1),
                    "type": "lxc",
                })

            result.append(node_data)

        return result

    except Exception as e:
        # Gibt Fehler zurück anstatt zu crashen – nützlich während der Entwicklung
        return [{"error": str(e), "hint": "Proxmox nicht erreichbar oder falsche Zugangsdaten"}]
