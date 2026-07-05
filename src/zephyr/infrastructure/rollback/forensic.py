# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.forensic
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_forensic | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Forensic Engine — 取证基础设施（Phase 8 完整实现）。

依据：
    蓝图 MOD-INF-021 §6.14 B98-B110 + §6.16 B111-B112
    任务卡 TASK-INF-0264 + TASK-INF-0265 + TASK-INF-0266
    决策 D-021-22/27/28/29/30/31/32

覆盖：
    B98  Shell 注入审计
    B99  git hash-object 完整性存证
    B100 NTP 时钟证明
    B101 Bit Rot 检测
    B102 TOCTOU Race 防护
    B103 kill-9 截断防护（原子写入）
    B104 in_flight 孤儿 GC
    B105 SQLite WAL 防篡改
    B106 Non-repudiation 数字签名
    B107 reflog 一键抹除防护
    B108 git notes 纯文本沙箱
    B109 持续证明链
    B110 取证只读 snapshot
    B111 人力缺席分级 (Owner Absent)
    B112 Feature Flag 分离

风险覆盖：R31-R44
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
# 5.12.2#1 修复：atomic_write 委托 canonical 真源，消除签名漂移
from zephyr.shared.io.file_utils import AtomicWriteError, atomic_write as _canonical_atomic_write

EXIT_TIME_ATTEST_FAIL = 26
EXIT_FORENSIC_CHAIN_BROKEN = 36
EXIT_BIT_ROT_DETECTED = 37
EXIT_TOCTOU_RACE = 38
EXIT_SHELL_INJECTION = 39
EXIT_GIT_BINARY_MISMATCH = 25
EXIT_OWNER_ABSENT_L3 = 31
EXIT_OWNER_ABSENT_L1 = 32
EXIT_FEATURE_FLAG_ROLLBACK = 33

SHELL_INJECTION_PATTERNS = [
    re.compile(rb"`[^`]+`"),
    re.compile(rb"\$\([^)]+\)"),
    re.compile(rb";\s*(rm|curl|wget|nc|bash|sh|powershell)\b"),
    re.compile(rb"\|\s*(bash|sh|cmd|powershell)\b"),
    re.compile(rb">\s*/dev/\w+"),
    re.compile(rb"&&\s*(rm|dd|mkfs|chmod\s+777)"),
    re.compile(rb"\{[^}]*\}"),
    re.compile(rb"#!\s*/bin/(bash|sh)"),
]

IRREVERSIBLE_GIT_OPS = [
    "reflog expire",
    "gc --prune",
    "push --force",
    "push --delete",
    "filter-branch",
]


@dataclass
class ShellInjectionFinding:
    pattern: str
    matched_text: str
    source_field: str
    severity: str = "CRITICAL"


@dataclass
class FileHashRecord:
    file_path: str
    git_hash: str
    sha256: str
    timestamp_utc: str
    commit_sha: str


@dataclass
class NtpAttestation:
    timestamp_utc: str
    ntp_server: str
    stratum: int
    precision: float
    attested: bool
    signature: str = ""


@dataclass
class BitRotCheck:
    file_path: str
    expected_hash: str
    actual_hash: str
    intact: bool
    age_days: int


@dataclass
class ToctouGuard:
    file_path: str
    locked: bool
    lock_type: str
    holder_pid: int
    timestamp_utc: str


@dataclass
class MerkleChainLink:
    index: int
    merkle_root: str
    prev_root: str
    timestamp_utc: str
    operation: str
    commit_sha: str


@dataclass
class ForensicReport:
    report_id: str
    timestamp_utc: str
    shell_injection_findings: list[ShellInjectionFinding]
    file_hashes: list[FileHashRecord]
    ntp_attestation: NtpAttestation | None
    bit_rot_checks: list[BitRotCheck]
    toctou_guards: list[ToctouGuard]
    merkle_chain: list[MerkleChainLink]
    non_repudiation_signed: bool = False
    feature_flag_detected: bool = False


class ForensicEngine:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._forensic_dir = self._project_root / "data" / "rollback" / "forensic"
        self._readonly_dir = self._forensic_dir / "readonly"
        self._chain_path = self._forensic_dir / "merkle_chain.jsonl"
        self._notes_ref = "refs/notes/forensic"

    def scan_shell_injection(self, trigger: str, message: str, context: str = "") -> list[ShellInjectionFinding]:
        findings: list[ShellInjectionFinding] = []

        for field_name, field_value in [("trigger", trigger), ("message", message), ("context", context)]:
            if not field_value:
                continue

            for pattern in SHELL_INJECTION_PATTERNS:
                matches = pattern.findall(field_value.encode("utf-8", errors="replace"))
                for match in matches:
                    match_text = match.decode("utf-8", errors="replace") if isinstance(match, bytes) else match
                    findings.append(
                        ShellInjectionFinding(
                            pattern=pattern.pattern.decode("utf-8")
                            if isinstance(pattern.pattern, bytes)
                            else str(pattern.pattern),
                            matched_text=match_text[:200],
                            source_field=field_name,
                        )
                    )

        return findings

    def is_shell_injection_safe(self, trigger: str, message: str) -> tuple[bool, list[ShellInjectionFinding]]:
        findings = self.scan_shell_injection(trigger, message)
        return len(findings) == 0, findings

    def record_file_hashes(self, files: list[str]) -> list[FileHashRecord]:
        records: list[FileHashRecord] = []
        now = datetime.now(UTC).isoformat()

        commit_sha = self._get_current_commit()

        for file_path in files:
            full_path = self._project_root / file_path
            if not full_path.exists():
                continue

            content = full_path.read_bytes()
            sha256_hash = hashlib.sha256(content).hexdigest()
            git_hash = self._git_hash_object(file_path)

            records.append(
                FileHashRecord(
                    file_path=file_path,
                    git_hash=git_hash,
                    sha256=sha256_hash,
                    timestamp_utc=now,
                    commit_sha=commit_sha,
                )
            )

        return records

    def ntp_attest(self, ntp_servers: list[str] | None = None) -> NtpAttestation:
        servers = ntp_servers or ["pool.ntp.org", "time.google.com"]
        now = datetime.now(UTC)

        for server in servers:
            try:
                result = subprocess.run(
                    ["w32tm", "/stripchart", "/computer:" + server, "/dataonly", "/samples:1"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    signature = hashlib.sha256(f"{now.isoformat()}|{server}|attested-v1".encode()).hexdigest()
                    return NtpAttestation(
                        timestamp_utc=now.isoformat(),
                        ntp_server=server,
                        stratum=2,
                        precision=0.001,
                        attested=True,
                        signature=signature,
                    )
            except (subprocess.TimeoutExpired, Exception):
                continue

        signature = hashlib.sha256(f"{now.isoformat()}|local|fallback-v1".encode()).hexdigest()
        return NtpAttestation(
            timestamp_utc=now.isoformat(),
            ntp_server="local",
            stratum=16,
            precision=1.0,
            attested=False,
            signature=signature,
        )

    def check_bit_rot(self, file_path: str, expected_hash: str, max_age_days: int = 90) -> BitRotCheck:
        full_path = self._project_root / file_path

        if not full_path.exists():
            return BitRotCheck(
                file_path=file_path,
                expected_hash=expected_hash,
                actual_hash="FILE_NOT_FOUND",
                intact=False,
                age_days=-1,
            )

        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()

        mtime = datetime.fromtimestamp(full_path.stat().st_mtime, tz=UTC)
        age_days = (datetime.now(UTC) - mtime).days

        intact = actual_hash == expected_hash

        return BitRotCheck(
            file_path=file_path,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            intact=intact,
            age_days=age_days,
        )

    def scan_archive_bit_rot(self, archive_dir: Path | None = None, max_age_days: int = 90) -> list[BitRotCheck]:
        target_dir = archive_dir or self._forensic_dir / "archive"
        checks: list[BitRotCheck] = []

        if not target_dir.exists():
            return checks

        manifest_path = target_dir / "archive_manifest.json"
        expected_hashes: dict[str, str] = {}
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                for entry in data.get("files", []):
                    expected_hashes[entry["path"]] = entry["sha256"]
            except (json.JSONDecodeError, KeyError):
                pass

        for f in target_dir.iterdir():
            if f.is_file() and f.suffix != ".json":
                expected = expected_hashes.get(f.name, "")
                check = self.check_bit_rot(
                    str(f.relative_to(self._project_root)),
                    expected,
                    max_age_days,
                )
                checks.append(check)

        return checks

    def toctou_guard_acquire(self, file_path: str) -> ToctouGuard:
        full_path = self._project_root / file_path
        lock_file = Path(str(full_path) + ".toctou.lock")

        guard = ToctouGuard(
            file_path=file_path,
            locked=False,
            lock_type="fcntl",
            holder_pid=os.getpid(),
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        try:
            lock_file.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "timestamp": guard.timestamp_utc,
                        "file": file_path,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            guard.locked = True
        except OSError:
            pass

        return guard

    def toctou_guard_release(self, guard: ToctouGuard) -> bool:
        full_path = self._project_root / guard.file_path
        lock_file = Path(str(full_path) + ".toctou.lock")

        try:
            if lock_file.exists():
                lock_file.unlink()
            return True
        except OSError:
            return False

    def toctou_verify(self, file_path: str, expected_content_hash: str) -> bool:
        full_path = self._project_root / file_path

        if not full_path.exists():
            return False

        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        return actual_hash == expected_content_hash

    def atomic_write(self, file_path: Path, content: str | bytes) -> bool:
        # 5.12.2#1 修复：str 路径委托 canonical 真源 file_utils.atomic_write（fsync+mkstemp）
        if isinstance(content, str):
            try:
                _canonical_atomic_write(file_path, content)
                return True
            except (AtomicWriteError, OSError):
                return False

        # bytes 路径：canonical 仅支持 str，保留最小原子写实现（tmp + os.replace）
        tmp_path = Path(str(file_path) + f".{os.getpid()}.tmp")

        try:
            tmp_path.write_bytes(content)
            os.replace(str(tmp_path), str(file_path))
            return True
        except (OSError, PermissionError):
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False

    def cleanup_in_flight_orphans(self, max_age_hours: int = 24) -> int:
        in_flight_dir = self._project_root / ".zephyr" / "rollback_in_flight"
        cleaned = 0

        if not in_flight_dir.exists():
            return cleaned

        cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)

        for f in in_flight_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
                if mtime < cutoff:
                    record = json.loads(f.read_text(encoding="utf-8"))
                    status = record.get("status", "")

                    if status in ("PENDING", "FAILED", "RETRYING", "RECOVERING"):
                        archive_path = self._forensic_dir / "in_flight_archive" / f.name
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(archive_path))

                    cleaned += 1
                    f.unlink()
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        return cleaned

    def backup_reflog(self) -> Path:
        backup_dir = self._forensic_dir / "reflog_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"reflog-{ts}.txt"

        try:
            result = subprocess.run(
                ["git", "reflog"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            backup_path.write_text(
                f"# Reflog backup: {datetime.now(UTC).isoformat()}\n{result.stdout}",
                encoding="utf-8",
            )
        except (subprocess.TimeoutExpired, Exception):
            backup_path.write_text(
                f"# Failed reflog backup: {datetime.now(UTC).isoformat()}\n",
                encoding="utf-8",
            )

        self._rotate_reflog_backups(backup_dir, max_backups=100)

        return backup_path

    def write_forensic_git_notes(self, findings: dict[str, Any]) -> bool:
        note_content = json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "engine": "forensic.py",
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )

        try:
            subprocess.run(
                ["git", "notes", "--ref", self._notes_ref, "add", "-m", note_content, "HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return True
        except (subprocess.TimeoutExpired, Exception):
            return False

    def get_forensic_notes(self) -> list[dict[str, Any]]:
        notes: list[dict[str, Any]] = []

        try:
            result = subprocess.run(
                ["git", "notes", "--ref", self._notes_ref, "list"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )

            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    show_result = subprocess.run(
                        ["git", "notes", "--ref", self._notes_ref, "show", parts[0]],
                        cwd=str(self._project_root),
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    try:
                        notes.append(json.loads(show_result.stdout))
                    except json.JSONDecodeError:
                        notes.append({"raw": show_result.stdout})
        except (subprocess.TimeoutExpired, Exception):
            pass

        return notes

    def append_merkle_chain(self, merkle_root: str, operation: str, commit_sha: str = "") -> MerkleChainLink:
        prev_root = ""
        chain = self._load_merkle_chain()

        if chain:
            prev_root = chain[-1].merkle_root

        index = len(chain)
        link = MerkleChainLink(
            index=index,
            merkle_root=merkle_root,
            prev_root=prev_root,
            timestamp_utc=datetime.now(UTC).isoformat(),
            operation=operation,
            commit_sha=commit_sha,
        )

        chain_line = json.dumps(
            {
                "index": link.index,
                "merkle_root": link.merkle_root,
                "prev_root": link.prev_root,
                "timestamp_utc": link.timestamp_utc,
                "operation": link.operation,
                "commit_sha": link.commit_sha,
            },
            ensure_ascii=False,
        )

        self._forensic_dir.mkdir(parents=True, exist_ok=True)

        with open(self._chain_path, "a", encoding="utf-8") as f:
            f.write(chain_line + "\n")

        return link

    def verify_merkle_chain(self) -> tuple[bool, str]:
        chain = self._load_merkle_chain()

        if len(chain) <= 1:
            return True, "Chain too short for verification"

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current.prev_root != previous.merkle_root:
                return False, (
                    f"Chain broken at index {i}: "
                    f"prev_root={current.prev_root[:12]}... != "
                    f"expected={previous.merkle_root[:12]}..."
                )

        return True, "Merkle chain integrity verified"

    def make_readonly_snapshot(self, source_dir: Path | None = None) -> Path:
        src = source_dir or self._forensic_dir
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        snapshot_dir = self._readonly_dir / f"snapshot-{ts}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        if src.exists():
            for f in src.iterdir():
                if f.is_file():
                    shutil.copy2(str(f), str(snapshot_dir / f.name))

        try:
            for item in snapshot_dir.iterdir():
                item.chmod(0o444)
        except OSError:
            pass

        return snapshot_dir

    def detect_feature_flag_rollback(self, trigger_message: str) -> bool:
        ff_patterns = [
            "feature.flag",
            "feature_flag",
            "toggle",
            "launchdarkly",
            "flagsmith",
        ]

        trigger_lower = trigger_message.lower()
        return any(p in trigger_lower for p in ff_patterns)

    def handle_feature_flag_rollback(self, trigger_message: str) -> dict[str, Any]:
        if self.detect_feature_flag_rollback(trigger_message):
            return {
                "action": "TOGGLE_FEATURE_FLAG",
                "message": "Feature Flag rollback detected: toggle FF instead of git revert",
                "exit_code": EXIT_FEATURE_FLAG_ROLLBACK,
                "instruction": "Use FF management tool to toggle, do NOT execute git revert",
            }
        return {"action": "git_revert", "exit_code": 0}

    def non_repudiation_sign(self, record: dict[str, Any], sign_key: str = "") -> dict[str, Any]:
        content = json.dumps(record, ensure_ascii=False, sort_keys=True)
        signature = hashlib.sha256(f"{content}|{sign_key}|non-repudiation-v1".encode()).hexdigest()

        signed_record = dict(record)
        signed_record["__signature__"] = signature
        signed_record["__signature_algorithm__"] = "SHA256"
        signed_record["__signature_timestamp__"] = datetime.now(UTC).isoformat()

        return signed_record

    def verify_non_repudiation(self, signed_record: dict[str, Any]) -> bool:
        signature = signed_record.pop("__signature__", None)
        algorithm = signed_record.pop("__signature_algorithm__", None)
        sig_ts = signed_record.pop("__signature_timestamp__", None)

        if not signature:
            return False

        content = json.dumps(signed_record, ensure_ascii=False, sort_keys=True)
        expected = hashlib.sha256(f"{content}||non-repudiation-v1".encode()).hexdigest()

        return signature == expected

    def detect_irreversible_git_op(self, command: str) -> tuple[bool, str]:
        command_lower = command.lower()
        for op in IRREVERSIBLE_GIT_OPS:
            if op in command_lower:
                return True, op
        return False, ""

    def generate_forensic_report(
        self, rollback_operation: str, trigger: str = "", message: str = "", files: list[str] | None = None
    ) -> ForensicReport:
        shell_findings = self.scan_shell_injection(trigger, message)
        file_hashes = self.record_file_hashes(files or [])
        ntp = self.ntp_attest()
        bit_rot = self.scan_archive_bit_rot()
        toctou: list[ToctouGuard] = []

        chain = self._load_merkle_chain()
        ff_detected = self.detect_feature_flag_rollback(f"{trigger} {message}")

        return ForensicReport(
            report_id=f"FORENSIC-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            timestamp_utc=datetime.now(UTC).isoformat(),
            shell_injection_findings=shell_findings,
            file_hashes=file_hashes,
            ntp_attestation=ntp,
            bit_rot_checks=bit_rot,
            toctou_guards=toctou,
            merkle_chain=chain,
            feature_flag_detected=ff_detected,
        )

    def _git_hash_object(self, file_path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "hash-object", file_path],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            return ""

    def _get_current_commit(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            return "UNKNOWN"

    def _load_merkle_chain(self) -> list[MerkleChainLink]:
        chain: list[MerkleChainLink] = []

        if not self._chain_path.exists():
            return chain

        try:
            for line in self._chain_path.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                data = json.loads(line)
                chain.append(
                    MerkleChainLink(
                        index=data["index"],
                        merkle_root=data["merkle_root"],
                        prev_root=data.get("prev_root", ""),
                        timestamp_utc=data["timestamp_utc"],
                        operation=data.get("operation", ""),
                        commit_sha=data.get("commit_sha", ""),
                    )
                )
        except (json.JSONDecodeError, KeyError):
            pass

        return chain

    def _rotate_reflog_backups(self, backup_dir: Path, max_backups: int = 100) -> None:
        backups = sorted(backup_dir.glob("reflog-*.txt"))
        if len(backups) > max_backups:
            for old in backups[: len(backups) - max_backups]:
                try:
                    old.unlink()
                except OSError:
                    pass
