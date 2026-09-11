# [BLUEPRINT] MOD-GOV_GATE_CACHE_PREFLIGHT | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.rule_bridge.gate_cache_preflight
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] stdlib（hashlib/json/os/time）；zephyr.shared.infra.process_pool（无）
# [CONSUMERS] git_commit_gateway（P2⑦ 预跑采信）；commit_gate_registry.check_all（P2⑧ 缓存查/存）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 白名单默认保守=纯 staged 内容扫描型 gate（无注册表/引擎/运行态输入）；只缓存 passed=True（降级态与失败一律不缓存——fail-open 不被缓存放大）；key=gate_id×own_scope×staged 树指纹×HEAD_sha×flags mtime（任一变化=全失效）；TTL 10min；两 flag（gate_result_cache/gate_preflight）出厂默认 OFF，启用属 Owner 窗口（宪章 B-007）
# [MODIFY-GUARD] 2026-09-10 提交通道性能优化方案 §2.2-A3 / §2.3 方案A / §2.6 分级清单（等价性红线：信号型永不缓存/预跑；指纹含 gate 输入清单 sha）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 指纹/缓存设施任何异常=回退全量现算（fail-safe to current behavior，调用方无感知）
# [TESTS] tests/git/test_gate_cache_preflight.py
# [TTL] permanent
"""gate_cache_preflight — P2⑧ 门禁结果持久缓存 + P2⑦ 锁外预跑指纹采信的共享基座。

等价性设计（方案 §2.2-A3 失效正确性 + §2.3 方案A 安全边界，逐条落实）：
- **staged 内容变化全失效**：key 含 ``git write-tree`` 树指纹（对 index 逐字节敏感）。
- **HEAD 移动全失效**：HEAD_sha 进 key（部分 gate 以 HEAD 为 diff 基线）。
- **配置变更失效**：config/flags.yaml mtime 进 key。
- **own-scope 组合**：own_scope_set_hash 进 key（同文件换 claim 范围不误命中）。
- **白名单准入**：默认只收"纯 staged 内容扫描型"（§2.6 内容扫描类中无注册表/引擎
  依赖者；TTL-METADATA/DIRECTORY-CONTRACT 等触发式结构校验读全局注册表，其输入
  超出 staged∪HEAD，未做逐 gate 输入面分析前**不准入**——保守空集原则）。
- **降级态**：准入 gate 均为无外部引擎依赖的纯扫描器，不存在降级路径；仍仅缓存
  passed=True（双保险）。
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.utils.time_utils import now_utc  # RULE-SCHEMA-TZ：时间 SSoT（src 禁裸 time.time()）

#: P2⑧/P2⑦ 共享白名单：纯 staged 内容扫描型（§2.6 实测分级总表"内容扫描"类中
#: 排除 CloneGuard 引擎依赖（CAPABILITY-OVERLAP，有 degraded 语义）与跨文件/注册表
#: 读取者）。白名单准入须逐 gate 输入面分析后追加——默认保守。
CONTENT_SCAN_CACHE_WHITELIST: frozenset[str] = frozenset(
    {
        "ENCODING-SAFETY",  # 5.37s（§0.1 实测最大收益点）
        "NO-BARE-SQL",
        "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS",
        "RELATIVE-PATH-LITERAL",
        "NO-IMPORT-SIDE-EFFECT",
        "ASYNCIO-RUN-IN-CONTEXT",
        "BARE-SUBPROCESS",
        "NO-LONG-PARAM-LIST",
        "NO-UPWARD-IMPORT",
        "UNSAFE-DICT-SPREAD",
    }
)

_CACHE_DIR = ".runtime/gate_cache"
_TTL_SECONDS = 600.0  # 方案 §2.2-A3：TTL 10min

_RESULT_FLAG = "gate_result_cache"
_PREFLIGHT_FLAG = "gate_preflight"


def flag_enabled(flag_name: str) -> bool:
    """flag 读取唯一点（fail-closed OFF；与 _commit_queue_serializer_enabled 同款语义）。"""
    try:
        from zephyr.shared.foundation.flags import (  # noqa: PLC0415
            ensure_global_flags_loaded,
            global_flag_registry,
        )

        ensure_global_flags_loaded()
        return global_flag_registry.is_enabled(flag_name, default=False)
    except Exception:  # noqa: BLE001 — 设施异常 fail-closed OFF
        return False


def result_cache_enabled() -> bool:
    return flag_enabled(_RESULT_FLAG)


def preflight_enabled() -> bool:
    return flag_enabled(_PREFLIGHT_FLAG)


@dataclass(frozen=True)
class Fingerprint:
    """预跑/缓存共享指纹（方案 §2.3 F 四元组的本实现收敛形态）。

    staged_tree_sha=git write-tree（index 逐字节敏感）；head_sha=diff 基线；
    flags_mtime=配置变更失效；own_scope 由各 gate key 分量自带。
    gate_inputs_manifest_sha：保守白名单的输入面=staged∪HEAD，已被前两项覆盖
    （注册表读取类未准入；未来准入时 MUST 在此追加其输入文件 sha 清单）。
    """

    staged_tree_sha: str
    head_sha: str
    flags_mtime: float

    def matches(self, other: "Fingerprint") -> bool:
        return (
            self.staged_tree_sha == other.staged_tree_sha
            and self.head_sha == other.head_sha
            and self.flags_mtime == other.flags_mtime
        )


def compute_fingerprint(gateway) -> Fingerprint | None:
    """计算当前 staged 树/HEAD 指纹；任何 git 异常返回 None（调用方回退全量现算）。"""
    try:
        tree = gateway.run_git(["git", "write-tree"])
        if tree.returncode != 0:
            return None
        head = gateway.run_git(["git", "rev-parse", "HEAD"])
        if head.returncode != 0:
            return None
        flags_yaml = Path(gateway.project_root) / "config" / "flags.yaml"
        try:
            mtime = os.path.getmtime(flags_yaml)
        except OSError:
            mtime = 0.0
        return Fingerprint(
            staged_tree_sha=tree.stdout.strip(),
            head_sha=head.stdout.strip(),
            flags_mtime=mtime,
        )
    except Exception:  # noqa: BLE001 — 指纹失败=回退全量现算（绝不阻断）
        return None


def own_scope_hash(gateway, files: list[str]) -> str:
    """own_scope 集合指纹（files∪session held_files；与 _diff_helpers._build_own_scope 同源语义）。"""
    try:
        from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope

        scope = _build_own_scope(gateway, files)
    except Exception:  # noqa: BLE001 — own_scope 不可得=退化用 files 本身
        scope = list(files)
    return hashlib.sha256("\n".join(sorted(scope)).encode("utf-8", "replace")).hexdigest()


class GateResultCache:
    """P2⑧ 持久结果缓存（.runtime/gate_cache/，TTL 10min，只存 passed=True）。"""

    def __init__(self, gateway, files: list[str]) -> None:
        self._gateway = gateway
        self._own_scope_hash = own_scope_hash(gateway, files)
        self._fp = compute_fingerprint(gateway)
        root = Path(gateway.project_root) / _CACHE_DIR
        self._dir: Path | None = root if self._fp is not None else None

    @property
    def usable(self) -> bool:
        return self._dir is not None

    def _path(self, gate_id: str, own_scope: str) -> Path:
        key = hashlib.sha256(
            f"{gate_id}\x1e{own_scope}\x1e{self._fp.staged_tree_sha}\x1e{self._fp.head_sha}\x1e{self._fp.flags_mtime}".encode()
        ).hexdigest()
        return self._dir / f"{key}.json"  # type: ignore[union-attr]

    def lookup(self, gate_id: str, own_scope: str) -> str | None:
        """命中返回缓存 detail（passed=True）；未命中/过期/异常返回 None。"""
        if not self.usable:
            return None
        p = self._path(gate_id, own_scope)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if now_utc().timestamp() - float(data["ts"]) > _TTL_SECONDS:
                return None
            if data.get("head_sha") != self._fp.head_sha:  # type: ignore[union-attr]
                return None
            return str(data["detail"])
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def store(self, gate_id: str, own_scope: str, detail: str) -> None:
        if not self.usable:
            return
        p = self._path(gate_id, own_scope)
        try:
            self._dir.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
            p.write_text(
                json.dumps(
                    {"gate_id": gate_id, "detail": detail, "ts": now_utc().timestamp(), "head_sha": self._fp.head_sha},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # 缓存写失败永不影响主链路
