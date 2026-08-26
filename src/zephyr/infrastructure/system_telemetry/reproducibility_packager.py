# [BLUEPRINT] MOD-INF-081 | docs/03_modules/_domain_infrastructure_operations/reproducibility_packager/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.reproducibility_packager
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] 无（纯内存；包目录 root/时钟全注入，仅写注入 root 下 manifest.json，不触网）
# [CONSUMERS] 运行时装配批（实验跟踪回放装配 / 审计快照引用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] manifest sha256 确定性（canonical JSON，同输入必同输出）; 时钟注入; params 字典序无关; 非法输入/未知包 Fail-Closed; 仅写注入 root 内文件
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/reproducibility_packager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ReproPackagerError(占位 ZA-INF-UNREGISTERED-REPRO-PACKAGER)——空exp_id/空必填字段/非法params/未知包/manifest缺失或损坏/hash不符时抛
# [TESTS] tests/infrastructure/test_reproducibility_packager.py
# [A_module] module_id=MOD-INF-081 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ReproducibilityPackager — 实验可复现打包器（MOD-INF-081）。

B1-00401（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-001，C2）：
实验一键打包——代码 commit + 参数 + 数据快照指针 + 依赖锁哈希 → 可回放包
（manifest.json + sha256 校验），打包/校验/回放指针解析三接口，mlflow Projects
思想单机版。包目录经注入 root（默认 .runtime/repro_packages），不触网。

查重分工（蓝图 §0）：experiment_tracker=实验元数据登记（本件不登记元数据，
只产出可回放包清单）；archive 族=冷数据归档（本件为实验包快照，零交集）。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "PackageManifest",
    "ReproPackagerError",
    "ReproducibilityPackager",
    "manifest_digest",
]

#: 默认包根目录（可经构造注入覆盖，测试用 tmp_path）
_DEFAULT_ROOT: Final[str] = ".runtime/repro_packages"
_MANIFEST_FILE: Final[str] = "manifest.json"


class ReproPackagerError(Exception):
    """可复现打包输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-REPRO-PACKAGER。
    """


@dataclass(frozen=True)
class PackageManifest:
    """可回放包清单（frozen）。"""

    exp_id: str
    code_commit: str
    params: dict
    data_snapshot_ref: str
    dep_lock_hash: str
    created_at: datetime.datetime


def _canonical(payload: Mapping) -> str:
    """canonical JSON（键排序/紧凑分隔符/UTF-8），保证哈希确定性。"""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def manifest_digest(manifest: PackageManifest) -> str:
    """清单内容 sha256（不含 digest 本身；created_at 取 ISO 格式）。"""
    payload = {
        "exp_id": manifest.exp_id,
        "code_commit": manifest.code_commit,
        "params": manifest.params,
        "data_snapshot_ref": manifest.data_snapshot_ref,
        "dep_lock_hash": manifest.dep_lock_hash,
        "created_at": manifest.created_at.isoformat(),
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


class ReproducibilityPackager:
    """实验可复现打包器（打包/校验/回放指针解析三接口）。"""

    def __init__(
        self,
        root: str | Path = _DEFAULT_ROOT,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not str(root):
            raise ReproPackagerError("root 为空")
        self._root = Path(root)
        self._clock = clock or datetime.datetime.now

    @property
    def root(self) -> Path:
        """包根目录（注入值）。"""
        return self._root

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _check_field(name: str, value: str) -> None:
        if not isinstance(value, str) or not value:
            raise ReproPackagerError(f"{name} 为空或非法: {value!r}")

    def _read_payload(self, exp_id: str) -> dict:
        self._check_field("exp_id", exp_id)
        path = self._root / exp_id / _MANIFEST_FILE
        if not path.is_file():
            raise ReproPackagerError(f"未知包或 manifest 缺失: {exp_id!r} ({path})")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReproPackagerError(f"manifest 损坏: {exp_id!r} ({exc})") from exc
        if not isinstance(payload, dict):
            raise ReproPackagerError(f"manifest 结构非法: {exp_id!r}")
        return payload

    @staticmethod
    def _manifest_from_payload(exp_id: str, payload: Mapping) -> PackageManifest:
        required = ("code_commit", "params", "data_snapshot_ref", "dep_lock_hash", "created_at")
        missing = [k for k in required if k not in payload]
        if missing:
            raise ReproPackagerError(f"manifest 字段缺失 {missing}: {exp_id!r}")
        try:
            created_at = datetime.datetime.fromisoformat(str(payload["created_at"]))
        except ValueError as exc:
            raise ReproPackagerError(f"created_at 非法: {exp_id!r} ({exc})") from exc
        params = payload["params"]
        if not isinstance(params, dict):
            raise ReproPackagerError(f"params 非字典: {exp_id!r}")
        return PackageManifest(
            exp_id=exp_id,
            code_commit=str(payload["code_commit"]),
            params=dict(params),
            data_snapshot_ref=str(payload["data_snapshot_ref"]),
            dep_lock_hash=str(payload["dep_lock_hash"]),
            created_at=created_at,
        )

    # ── 打包 ─────────────────────────────────────────────────────────────

    def build_package(
        self,
        exp_id: str,
        *,
        code_commit: str,
        params: Mapping,
        data_snapshot_ref: str,
        dep_lock_hash: str,
    ) -> PackageManifest:
        """打包：构造清单 → sha256 → 写 manifest.json 到注入 root 下 exp 目录。"""
        self._check_field("exp_id", exp_id)
        self._check_field("code_commit", code_commit)
        self._check_field("data_snapshot_ref", data_snapshot_ref)
        self._check_field("dep_lock_hash", dep_lock_hash)
        if not isinstance(params, Mapping):
            raise ReproPackagerError(f"params 非字典: {type(params).__name__}")
        try:
            _canonical(params)
        except (TypeError, ValueError) as exc:
            raise ReproPackagerError(f"params 不可 JSON 序列化: {exc}") from exc

        manifest = PackageManifest(
            exp_id=exp_id,
            code_commit=code_commit,
            params=dict(params),
            data_snapshot_ref=data_snapshot_ref,
            dep_lock_hash=dep_lock_hash,
            created_at=self._clock(),
        )
        digest = manifest_digest(manifest)
        pkg_dir = self._root / exp_id
        pkg_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "exp_id": exp_id,
            "code_commit": code_commit,
            "params": dict(params),
            "data_snapshot_ref": data_snapshot_ref,
            "dep_lock_hash": dep_lock_hash,
            "created_at": manifest.created_at.isoformat(),
            "sha256": digest,
        }
        (pkg_dir / _MANIFEST_FILE).write_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        _log.info("可复现包已生成: %s sha256=%s", exp_id, digest[:12])
        return manifest

    # ── 校验 ─────────────────────────────────────────────────────────────

    def verify_package(self, exp_id: str) -> bool:
        """hash 校验：重算 sha256 与文件内记录比对（篡改 → False）。"""
        payload = self._read_payload(exp_id)
        manifest = self._manifest_from_payload(exp_id, payload)
        ok = manifest_digest(manifest) == payload.get("sha256")
        if not ok:
            _log.warning("可复现包 hash 不符: %s", exp_id)
        return ok

    # ── 回放指针 ──────────────────────────────────────────────────────────

    def resolve_replay_pointer(self, exp_id: str) -> str:
        """回放指针解析：repro://<exp_id>@sha256:<digest>（篡改 Fail-Closed）。"""
        payload = self._read_payload(exp_id)
        manifest = self._manifest_from_payload(exp_id, payload)
        digest = manifest_digest(manifest)
        if payload.get("sha256") != digest:
            raise ReproPackagerError(f"manifest hash 不符，拒绝解析回放指针: {exp_id!r}")
        return f"repro://{exp_id}@sha256:{digest}"
