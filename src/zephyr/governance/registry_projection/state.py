# [MODULE] zephyr.governance.registry_projection.state
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text, content_sha256)
# [CONSUMERS] zephyr.governance.registry_projection.generator；REGISTRY-YAML-PARSE 执法扩展（只读）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 投影状态文件是漂移判别的本地真源（判别真源放本地=PG 宕机照样抓私改）；
#   双指纹=content_sha256+ledger_revision；写走 safe_write_text CAS；位于
#   .runtime/projection/ 子目录（宪法 §9.4 禁 .runtime 根直写，丙号文路径语义不变收编）
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] load_state 损坏/缺失返回 None（fail-open，执法层降级放行）；save_state CAS 失败 raise
# [TESTS] tests/governance/registry_projection/test_projection_state.py
"""state.py — 投影状态文件与四象限判别。

四象限（R=render(快照) 哈希，S=状态文件哈希，D=盘上文件哈希）：
- 干净     D==S==R          通过
- 私改     S==R 且 D!=S     PG wins 自动再生成+证据留档
- 陈旧     D==S 且 R!=S     静默再生成（主路径常态）
- 双向冲突 D!=S 且 R!=S     再生成后复检，仍不等→死信
快照不可达（PG 宕机）时只比 D vs S：私改照样现形，检测能力不随 PG 存活死亡。


# [ALGO_FLOW]
层: 读写
- 读: 加载 .runtime 投影状态文件（content_sha256+ledger_revision）
- 写: safe_write_text CAS 原子更新（渲染成功后）"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from zephyr.shared.io.file_utils import content_sha256, safe_write_text

__all__: Final = ["ProjectionState", "QUADRANT_PG_UNREACHABLE", "classify", "load_state", "save_state", "state_path"]

STATE_REL = ".runtime/projection/registry_projection_state.json"

QUADRANT_CLEAN = "clean"
QUADRANT_PRIVATE_EDIT = "private_edit"
QUADRANT_STALE = "stale"
QUADRANT_CONFLICT = "conflict"
QUADRANT_PG_UNREACHABLE = "pg_unreachable"


def state_path(project_root: str | Path) -> Path:
    return Path(project_root) / STATE_REL


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


def load_state(project_root: str | Path) -> ProjectionState | None:
    """读状态文件；缺失/损坏 → None（fail-open：执法层降级放行，daemon 兜底）。"""
    path = state_path(project_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ProjectionState(
            content_sha256=str(data["content_sha256"]),
            ledger_revision=int(data["ledger_revision"]),
            registry_path=str(data["registry_path"]),
            entry_counts=dict(data.get("entry_counts") or {}),
            generated_at=str(data.get("generated_at") or ""),
        )
    except Exception:  # noqa: BLE001 — 缺失/损坏一律按未武装处理
        return None


def save_state(project_root: str | Path, state: ProjectionState) -> None:
    payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path = state_path(project_root)
    expected_base = content_sha256(path.read_text(encoding="utf-8")) if path.exists() else None
    safe_write_text(path, payload, expected_base_sha256=expected_base, repo_root=project_root, newline="\n")


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
