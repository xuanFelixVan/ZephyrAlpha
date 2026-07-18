#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §4.3
# [MODULE] scripts.backup.minio_tcp_relay
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] stdlib only (socket, threading); spawn path from config/.env.ch_backup RELAY_SCRIPT
# [CONSUMERS] scripts/backup/backup.ps1 (CH stage), scripts/backup/restore.ps1 (ch)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] MinIO binds localhost only (Windows Firewall auto-blocks minio.exe; python.exe has Public-allow) | dumb byte-pipe, no protocol parsing | listens 0.0.0.0:9100 -> 127.0.0.1:9101 | on-demand, killed after each backup/restore
# [MODIFY-GUARD] gate_id="MINIO-TCP-RELAY"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] per-connection OSError swallowed after socket shutdown; upstream connect failure closes client
# [TESTS] manual e2e via backup.ps1 CH stage (BACKUP TO S3 streams through this relay)
# [TTL] task_bound
"""TCP relay: expose localhost-only MinIO to the CH VM via firewall-allowed python.

Spawned on-demand by backup.ps1 CH stage and restore.ps1 ch; killed right after the
backup/restore completes (task-bound, not a resident service)."""
import socket
import threading

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 9100
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9101
BUF = 1024 * 1024  # 1 MiB chunks: 315 GiB backup throughput needs large buffers


def _pipe(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(BUF)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _handle(client: socket.socket) -> None:
    try:
        upstream = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=10)
    except OSError:
        client.close()
        return
    threading.Thread(target=_pipe, args=(upstream, client), daemon=True).start()
    _pipe(client, upstream)


def main() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((LISTEN_HOST, LISTEN_PORT))
    srv.listen(128)
    while True:
        client, _ = srv.accept()
        threading.Thread(target=_handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
