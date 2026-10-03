# [MODULE] zephyr.governance.registry_projection.state
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text, content_sha256)
# [CONSUMERS] zephyr.governance.registry_projection.generator；REGISTRY-YAML-PARSE 执法扩展（只读原始 JSON）；commit_belt_daemon 漂移探针
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 投影状态文件是漂移判别的本地真源（判别真源放本地=PG 宕机照样抓私改）；
#   双指纹=content_sha256+ledger_revision；写走 safe_write_text CAS；位于
#   .runtime/projection/ 子目录（宪法 §9.4 禁 .runtime 根直写，丙号文路径语义不变收编）；
#   v2 map 形态（2026-10-03 PD-1 方案①）：多册并挂按 registry_path 键控（单槽形态退役），
#   旧 v1 单册平铺文件兼容读（首写即迁移为 v2）；并发异册写靠 CAS 重读重试保他册条目
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）；v2 map 化 2026-10-03 st-commitmap-chief-20261003（B3 前置 PD-1，净零申报=替代单槽形态）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] load_all 整文件缺失/损坏返回 {}（fail-open：执法层降级放行，daemon 兜底），
#   单条目损坏只跳过该册（损失半径=该册 fail-open）；load_state 未命中或缺省参且多册返回 None；
#   save_state CAS 冲突重读重试 3 次仍败 raise
# [TESTS] tests/governance/registry_projection/test_projection_generator.py；tests/governance/registry_projection/test_state_v2.py
"""state.py — 投影状态文件与四象限判别（v2 多册 map）。

四象限（R=render(快照) 哈希，S=状态文件哈希，D=盘上文件哈希）：
- 干净     D==S==R          通过
- 私改     S==R 且 D!=S     PG wins 自动再生成+证据留档
- 陈旧     D==S 且 R!=S     静默再生成（主路径常态）
- 双向冲突 D!=S 且 R!=S     再生成后复检，仍不等→死信
快照不可达（PG 宕机）时只比 D vs S：私改照样现形，检测能力不随 PG 存活死亡。

状态文件形态（v2，一次可挂多册）::

    {"version": 2, "registries": {"<registry_path>": {"content_sha256": ...,
      "ledger_revision": ..., "registry_path": ..., "entry_counts": {...},
      "generated_at": ...}}}

旧 v1 单册平铺形态兼容读：load 时折为单条映射，save 时即迁移为 v2。

# [ALGO_FLOW]
层: 读写
- 读: load_all 全量映射；load_state 按册取条目（缺省参=唯一条目，多册/空=None）
- 写: save_state 按 registry_path upsert 入映射；safe_write_text CAS 原子更新
  （冲突=他册并发写先落，重读新基座重试，3 轮仍败 raise）"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from zephyr.shared.io.file_utils import content_sha256, safe_write_text

__all__: Final = [
    "ProjectionState",
    "QUADRANT_PG_UNREACHABLE",
    "STATE_VERSION",
    "classify",
    "load_all",
    "load_state",
    "save_state",
    "state_path",
]

STATE_REL = ".runtime/projection/registry_projection_state.json"
STATE_VERSION: Final = 2
_SAVE_RETRIES: Final = 3

QUADRANT_CLEAN = "clean"
QUADRANT_PRIVATE_EDIT = "private_edit"
QUADRANT_STALE = "stale"
QUADRANT_CONFLICT = "conflict"
QUADRANT_PG_UNREACHABLE = "pg_unreachable"


def state_path(project_root: str | Path) -> Path:
    return Path(project_root) / STATE_REL


def _canon(path: str) -> str:
    """路径键归一（posix 斜杠；Path 构造顺带吃掉 './' 前缀与反斜杠差异）。"""
    return Path(path).as_posix()


@dataclass
class ProjectionState:
    content_sha256: str
    ledger_revision: int
    registry_path: str
    entry_counts: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "content_sha256": self.content_sha256,
            "ledger_revision": self.ledger_revision,
            "registry_path": self.registry_path,
            "entry_counts": self.entry_counts or {},
            "generated_at": self.generated_at,
        }


def _entry_from(value: object, key_hint: str) -> ProjectionState | None:
    """单条目解析；损坏返回 None（损失半径=该册 fail-open）。"""
    if not isinstance(value, dict):
        return None
    try:
        return ProjectionState(
            content_sha256=str(value["content_sha256"]),
            ledger_revision=int(value["ledger_revision"]),
            registry_path=str(value.get("registry_path") or key_hint),
            entry_counts={str(k): int(v) for k, v in (value.get("entry_counts") or {}).items()},
            generated_at=str(value.get("generated_at") or ""),
        )
    except Exception:  # noqa: BLE001 — 单条损坏跳过该册
        return None


def load_all(project_root: str | Path) -> dict[str, ProjectionState]:
    """读全量映射；缺失/损坏返回 {}（fail-open），v1 单册形态折为单条映射。"""
    path = state_path(project_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 缺失/损坏一律按未武装处理
        return {}
    if not isinstance(data, dict):
        return {}
    registries = data.get("registries")
    if isinstance(registries, dict):
        out: dict[str, ProjectionState] = {}
        for key, value in registries.items():
            entry = _entry_from(value, str(key))
            if entry is not None:
                out[_canon(str(key))] = entry
        return out
    legacy = _entry_from(data, str(data.get("registry_path", "")))
    return {_canon(legacy.registry_path): legacy} if legacy and legacy.registry_path else {}


def load_state(project_root: str | Path, registry_path: str | None = None) -> ProjectionState | None:
    """按册取条目；registry_path 缺省=唯一条目（多册/空 → None，v1 兼容语义）。"""
    entries = load_all(project_root)
    if registry_path is not None:
        wanted = _canon(registry_path)
        state = entries.get(wanted)
        if state is not None:
            return state
        for entry in entries.values():  # 键形差异兜底（反斜杠/前缀已归一，此处防手写键）
            if _canon(entry.registry_path) == wanted:
                return entry
        return None
    if len(entries) == 1:
        return next(iter(entries.values()))
    return None


def save_state(project_root: str | Path, state: ProjectionState) -> None:
    """按 registry_path upsert 入 v2 映射并 CAS 写盘；冲突=他册并发先落，重读重试。"""
    raw = state.registry_path.strip().replace("\\", "/")
    if not raw or raw == ".":
        raise ValueError("registry_path 不能为空（v2 键控；Path('').as_posix() 会折成 '.'）")
    key = _canon(raw)
    last_exc: Exception | None = None
    for attempt in range(_SAVE_RETRIES):
        path = state_path(project_root)
        current: dict[str, object] = {}
        expected_base: str | None = None
        if path.exists():
            text = path.read_text(encoding="utf-8")
            expected_base = content_sha256(text)
            try:
                data = json.loads(text)
            except Exception:  # noqa: BLE001 — 基座损坏按空映射重建（唯一写者纪律：本册条目为准）
                data = None
            if isinstance(data, dict):
                registries = data.get("registries")
                if isinstance(registries, dict):
                    current = {str(k): v for k, v in registries.items() if isinstance(v, dict)}
                else:
                    legacy = _entry_from(data, str(data.get("registry_path", "")))
                    if legacy is not None and legacy.registry_path:
                        current = {_canon(legacy.registry_path): legacy.to_dict()}
        current[key] = state.to_dict()
        payload = (
            json.dumps({"version": STATE_VERSION, "registries": current}, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        )
        try:
            result = safe_write_text(
                path, payload, expected_base_sha256=expected_base, repo_root=project_root, newline="\n"
            )
            if getattr(result, "written", False):
                return
            last_exc = RuntimeError("safe_write_text written=False（CAS 未生效）")
        except Exception as exc:  # noqa: BLE001 — CAS 冲突进重试；3 轮仍败按 ERROR_CONTRACT raise
            last_exc = exc
        if attempt == _SAVE_RETRIES - 1:
            break
    raise last_exc if last_exc else RuntimeError("save_state 重试耗尽")


def classify(disk_sha: str, state_sha: str, render_sha: str | None) -> str:
    """四象限判别；render_sha=None（PG 宕机）时降级只比 D vs S（私改照样现形）。"""
    if render_sha is None:
        return QUADRANT_CLEAN if disk_sha == state_sha else QUADRANT_PRIVATE_EDIT
    if disk_sha == state_sha == render_sha:
        return QUADRANT_CLEAN
    if state_sha == render_sha and disk_sha != state_sha:
        return QUADRANT_PRIVATE_EDIT
    if disk_sha == state_sha and render_sha != state_sha:
        return QUADRANT_STALE
    return QUADRANT_CONFLICT
