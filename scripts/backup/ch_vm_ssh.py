# [BLUEPRINT] MOD-INF-043 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""SSH helper for ClickHouse VM operations (VHDX backup scheme).

Usage from PowerShell / Python:
    python ch_vm_ssh.py --cmd "rm -f /mnt/chbackup_local/market.zip"
    python ch_vm_ssh.py --cmd "ls -la /mnt/chbackup_local/market.zip" --json
    python ch_vm_ssh.py --delete-backup market.zip
    python ch_vm_ssh.py --stat-backup market.zip --json

Credentials read from config/.env.ch_backup (CH_VM_HOST, CH_VM_USER, CH_VM_PASSWORD, CH_VM_KEY_PATH).
Exit code 0 = success, 1 = failure. Output to stdout.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import paramiko

# Resolve project root from script location (scripts/backup/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "config" / ".env.ch_backup"


def load_env() -> dict:
    """Load VM credentials from .env.ch_backup.

    Auth precedence: CH_VM_KEY_PATH (SSH key, recommended) > CH_VM_PASSWORD (legacy).
    At least one must be set. When key auth is used, password is optional and
    only needed for sudo fallback (or configure NOPASSWD sudo on the VM).
    """
    creds = {"host": "172.24.30.100", "user": "ubuntu", "password": "", "key_path": ""}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key == "CH_VM_HOST":
                creds["host"] = val
            elif key == "CH_VM_USER":
                creds["user"] = val
            elif key == "CH_VM_PASSWORD":
                creds["password"] = val
            elif key == "CH_VM_KEY_PATH":
                creds["key_path"] = val
    if not creds["password"] and not creds["key_path"]:
        print("ERROR: set CH_VM_KEY_PATH (recommended) or CH_VM_PASSWORD in config/.env.ch_backup", file=sys.stderr)
        sys.exit(1)
    return creds


def ssh_run(cmd: str, timeout: int = 120, use_sudo: bool = False) -> dict:
    """Run a command on the CH VM via SSH. Returns dict with exit_code, stdout, stderr."""
    creds = load_env()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connect_kwargs = dict(
        hostname=creds["host"],
        username=creds["user"],
        timeout=15,
        allow_agent=False,
        look_for_keys=False,
    )
    if creds["key_path"]:
        connect_kwargs["key_filename"] = creds["key_path"]
    else:
        connect_kwargs["password"] = creds["password"]
    client.connect(**connect_kwargs)
    try:
        if use_sudo:
            if not creds["password"]:
                return {
                    "exit_code": 1,
                    "stdout": "",
                    "stderr": "sudo requires CH_VM_PASSWORD (or configure NOPASSWD sudo on VM for key-only auth)",
                }
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout, get_pty=True)
            stdin.write(creds["password"] + "\n")
            stdin.flush()
        else:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        return {"exit_code": exit_code, "stdout": out.strip(), "stderr": err.strip()}
    finally:
        client.close()


def stat_backup(filename: str) -> dict:
    """Get file stats for a backup file on the VHDX disk. Returns dict or None."""
    path = f"/mnt/chbackup_local/{filename}"
    # stat -c '%s %Y' gives size (bytes) and mtime (epoch)
    result = ssh_run(f"stat -c '%s %Y' {path} 2>/dev/null", timeout=15)
    if result["exit_code"] != 0 or not result["stdout"]:
        return {"exists": False, "path": path, "bytes": 0}
    parts = result["stdout"].split()
    return {
        "exists": True,
        "path": path,
        "bytes": int(parts[0]),
        "mtime_epoch": int(parts[1]),
    }


def delete_backup(filename: str) -> dict:
    """Delete a backup file from the VHDX disk (requires sudo - clickhouse owns the files)."""
    path = f"/mnt/chbackup_local/{filename}"
    result = ssh_run(f"sudo rm -f {path} && echo DELETED", timeout=30, use_sudo=True)
    return result


def sync_config(dest_dir: str) -> dict:
    """Sync CH config files from VM to local directory (single SSH round-trip).

    Copies: config.xml, users.xml, config.d/backup_disk.xml, /etc/fstab.
    Small text files critical for DR. Uses sudo (backup_disk.xml is clickhouse-group-only).
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    cmd = (
        "sudo sh -c '"
        'echo "=CFG=config.xml="; cat /etc/clickhouse-server/config.xml; '
        'echo "=CFG=users.xml="; cat /etc/clickhouse-server/users.xml; '
        'echo "=CFG=backup_disk.xml="; cat /etc/clickhouse-server/config.d/backup_disk.xml; '
        'echo "=CFG=fstab="; cat /etc/fstab'
        "'"
    )
    result = ssh_run(cmd, timeout=30, use_sudo=True)
    files_written = []
    if result["exit_code"] == 0:
        out = result["stdout"]
        # With get_pty=True (sudo), output has \r\n line endings AND may echo the
        # command itself. Find the first =CFG= that starts a line (actual echo
        # output), skipping any =CFG= embedded in the command-echo line.
        # Match =CFG= at start of a line (after \n or start of string)
        marker_match = re.search(r"(?:^|\n)=CFG=", out)
        if marker_match:
            out = out[marker_match.start() :]
        for part in out.split("=CFG=")[1:]:
            # Normalize \r\n to \n first (get_pty adds \r)
            part = part.replace("\r\n", "\n").replace("\r", "\n")
            lines = part.split("\n", 1)
            # strip() FIRST (removes \r), THEN rstrip("=") (removes trailing =)
            fname = lines[0].strip().rstrip("=").strip()
            content = lines[1] if len(lines) > 1 else ""
            if not fname:
                continue  # skip empty parts (e.g., from command echo)
            fpath = dest / fname
            fpath.write_text(content, encoding="utf-8")
            files_written.append(str(fpath))
    return {"exit_code": result["exit_code"], "files": files_written, "stderr": result.get("stderr", "")}


def main():
    parser = argparse.ArgumentParser(description="SSH helper for CH VM (VHDX backup)")
    parser.add_argument("--cmd", help="Arbitrary command to run on VM")
    parser.add_argument("--sudo", action="store_true", help="Run with sudo")
    parser.add_argument("--delete-backup", metavar="FILENAME", help="Delete a backup file from VHDX disk")
    parser.add_argument("--stat-backup", metavar="FILENAME", help="Get stats for a backup file")
    parser.add_argument("--sync-config", metavar="DEST_DIR", help="Sync CH config files from VM to local dir")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--timeout", type=int, default=120, help="SSH timeout in seconds")
    args = parser.parse_args()

    if args.delete_backup:
        result = delete_backup(args.delete_backup)
        if args.json:
            print(json.dumps(result))
        else:
            print(result["stdout"] or result["stderr"])
        sys.exit(0 if result["exit_code"] == 0 else 1)

    if args.stat_backup:
        result = stat_backup(args.stat_backup)
        if args.json:
            print(json.dumps(result))
        else:
            if result["exists"]:
                print(f"exists=True bytes={result['bytes']}")
            else:
                print("exists=False")
        sys.exit(0)

    if args.sync_config:
        result = sync_config(args.sync_config)
        print(json.dumps(result))
        sys.exit(0 if result["exit_code"] == 0 else 1)

    if args.cmd:
        result = ssh_run(args.cmd, timeout=args.timeout, use_sudo=args.sudo)
        if args.json:
            print(json.dumps(result))
        else:
            if result["stdout"]:
                print(result["stdout"])
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr)
        sys.exit(0 if result["exit_code"] == 0 else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
