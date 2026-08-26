# [BLUEPRINT] MOD-ML-021 | docs/03_modules/_domain_machine_learning_train/research_data_sandbox/blueprint.md
# [MODULE] zephyr.ml_train.research_data_sandbox
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（纯内存/DI；sandbox_root/production_root/production_files/clock 全注入；语义旁挂 governance.resilience_governance.engine_sandbox）
# [CONSUMERS] 运行时装配批（沙箱 root 绑定 / 生产只读视图绑定 / 评审人路由装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 沙箱/生产 root 注入且不得相同或嵌套; 生产数据只读(写入恒拦截 Fail-Closed); 路径禁止绝对/越界(..); 配额声明须为正且不超 max_quota; 产出回写强制评审状态机 PENDING→APPROVED|REJECTED 单次迁移; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/research_data_sandbox/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchSandboxError(占位 ZA-MLT-UNREGISTERED-RESEARCH-SANDBOX)——root 非法/配额越界/路径越界/生产写入/未知产出/重复评审时抛
# [TESTS] tests/ml_train/test_research_data_sandbox.py
# [A_module] module_id=MOD-ML-021 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchDataSandbox — 研究数据沙箱（MOD-ML-021）。

B13-04339（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-029，A3 D-RESEARCH-12）：
**独立工作目录**（注入 root，纯内存工作区）+ **生产数据只读视图**
（写入拦截 Fail-Closed）+ **资源配额声明校验**（CPU/内存预算）
+ **产出回写需评审**（回写队列 + PENDING→APPROVED|REJECTED 评审状态机）。

canonical 承接 WFO-005 归并。本件不触真实文件系统：root 仅为逻辑命名空间，
工作区/生产视图均为注入内存映射。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ResearchDataSandbox",
    "ResearchSandboxError",
    "ResourceQuota",
    "ReviewDecision",
    "ReviewStatus",
    "WritebackArtifact",
]


class ResearchSandboxError(Exception):
    """研究数据沙箱输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-RESEARCH-SANDBOX。
    """


class ReviewStatus(str, Enum):
    """回写评审状态机（PENDING→APPROVED|REJECTED 单次迁移）。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ResourceQuota:
    """资源配额声明（frozen；cpu_cores/memory_mb 须为正）。"""

    cpu_cores: float
    memory_mb: int


@dataclass(frozen=True)
class WritebackArtifact:
    """产出回写单（frozen；状态迁移经 replace 生成新实例）。"""

    artifact_id: str
    workspace_path: str
    submitted_by: str
    status: ReviewStatus
    submitted_at: datetime.datetime


@dataclass(frozen=True)
class ReviewDecision:
    """评审裁决（frozen，留痕）。"""

    artifact_id: str
    status: ReviewStatus
    reviewer: str
    reason: str
    decided_at: datetime.datetime


def _validate_rel_path(path: str) -> None:
    """相对路径校验：非空、禁绝对、禁空/./.. 段。"""
    if not isinstance(path, str) or not path:
        raise ResearchSandboxError("路径为空或非字符串")
    if path.startswith(("/", "\\")) or (len(path) > 1 and path[1] == ":"):
        raise ResearchSandboxError(f"禁止绝对路径: {path!r}")
    parts = path.replace("\\", "/").split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ResearchSandboxError(f"非法路径段（空/./.. 越界）: {path!r}")


def _validate_quota(quota: ResourceQuota, *, what: str = "quota") -> None:
    if not isinstance(quota, ResourceQuota):
        raise ResearchSandboxError(f"{what} 非 ResourceQuota")
    if quota.cpu_cores <= 0:
        raise ResearchSandboxError(f"{what}.cpu_cores 须为正: {quota.cpu_cores!r}")
    if quota.memory_mb <= 0:
        raise ResearchSandboxError(f"{what}.memory_mb 须为正: {quota.memory_mb!r}")


class ResearchDataSandbox:
    """轻量研究沙箱（独立工作目录 + 生产只读 + 配额校验 + 回写评审）。"""

    def __init__(
        self,
        *,
        sandbox_root: str,
        production_root: str,
        quota: ResourceQuota,
        max_quota: ResourceQuota | None = None,
        production_files: Mapping[str, str] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not sandbox_root:
            raise ResearchSandboxError("sandbox_root 为空（独立工作目录须注入 root）")
        if not production_root:
            raise ResearchSandboxError("production_root 为空")
        sb = sandbox_root.rstrip("/")
        prod = production_root.rstrip("/")
        if sb == prod:
            raise ResearchSandboxError("sandbox_root 与 production_root 不得相同")
        if sb.startswith(prod + "/") or prod.startswith(sb + "/"):
            raise ResearchSandboxError("sandbox_root 与 production_root 不得相互嵌套")
        _validate_quota(quota)
        if max_quota is not None:
            _validate_quota(max_quota, what="max_quota")
            if quota.cpu_cores > max_quota.cpu_cores or quota.memory_mb > max_quota.memory_mb:
                raise ResearchSandboxError(
                    f"配额声明超预算: cpu={quota.cpu_cores}/{max_quota.cpu_cores}, "
                    f"mem={quota.memory_mb}/{max_quota.memory_mb}"
                )
        self._sandbox_root = sb
        self._production_root = prod
        self._quota = quota
        self._clock = clock or datetime.datetime.now
        self._production: dict[str, str] = {}
        for path, content in (production_files or {}).items():
            _validate_rel_path(path)
            if not isinstance(content, str):
                raise ResearchSandboxError(f"生产视图内容非字符串: {path!r}")
            self._production[path] = content
        self._workspace: dict[str, str] = {}
        self._artifacts: dict[str, WritebackArtifact] = {}
        self._decisions: dict[str, ReviewDecision] = {}
        self._approved: dict[str, str] = {}

    # ── 生产数据只读视图（写入拦截 Fail-Closed） ───────────────────────────

    def read_production(self, rel_path: str) -> str:
        """生产数据只读读取（未知路径 Fail-Closed）。"""
        _validate_rel_path(rel_path)
        content = self._production.get(rel_path)
        if content is None:
            raise ResearchSandboxError(f"未知生产数据路径: {rel_path!r}")
        return content

    def list_production(self) -> tuple[str, ...]:
        """生产视图清单（字典序确定性）。"""
        return tuple(sorted(self._production))

    def write_production(self, rel_path: str, content: str) -> None:
        """生产数据写入——恒拦截（只读视图，Fail-Closed）。"""
        raise ResearchSandboxError(
            f"生产数据只读视图：写入拦截 {rel_path!r}（Fail-Closed）"
        )

    # ── 独立工作目录（纯内存工作区） ────────────────────────────────────────

    def write_workspace(self, rel_path: str, content: str) -> str:
        """工作区写入（返回沙箱全路径；覆盖写幂等于末次）。"""
        _validate_rel_path(rel_path)
        if not isinstance(content, str):
            raise ResearchSandboxError("工作区内容非字符串")
        self._workspace[rel_path] = content
        return f"{self._sandbox_root}/{rel_path}"

    def read_workspace(self, rel_path: str) -> str:
        """工作区读取（未知路径 Fail-Closed）。"""
        _validate_rel_path(rel_path)
        content = self._workspace.get(rel_path)
        if content is None:
            raise ResearchSandboxError(f"未知工作区路径: {rel_path!r}")
        return content

    def list_workspace(self) -> tuple[str, ...]:
        """工作区清单（字典序确定性）。"""
        return tuple(sorted(self._workspace))

    # ── 产出回写评审（状态机） ──────────────────────────────────────────────

    def submit_writeback(
        self, artifact_id: str, workspace_path: str, submitted_by: str
    ) -> WritebackArtifact:
        """产出回写申请：工作区产出入评审队列（PENDING）。"""
        if not artifact_id:
            raise ResearchSandboxError("artifact_id 为空")
        if artifact_id in self._artifacts:
            raise ResearchSandboxError(f"artifact_id 重复: {artifact_id!r}")
        _validate_rel_path(workspace_path)
        if workspace_path not in self._workspace:
            raise ResearchSandboxError(f"回写产出不存在于工作区: {workspace_path!r}")
        if not submitted_by:
            raise ResearchSandboxError("submitted_by 为空")
        art = WritebackArtifact(
            artifact_id=artifact_id,
            workspace_path=workspace_path,
            submitted_by=submitted_by,
            status=ReviewStatus.PENDING,
            submitted_at=self._clock(),
        )
        self._artifacts[artifact_id] = art
        _log.info("回写申请: %s <- %s", artifact_id, workspace_path)
        return art

    def review_writeback(
        self, artifact_id: str, approve: bool, reviewer: str, reason: str = ""
    ) -> ReviewDecision:
        """评审裁决：PENDING→APPROVED|REJECTED（单次迁移；通过才入回写存档）。"""
        art = self._artifacts.get(artifact_id)
        if art is None:
            raise ResearchSandboxError(f"未知回写单: {artifact_id!r}")
        if art.status is not ReviewStatus.PENDING:
            raise ResearchSandboxError(
                f"回写单 {artifact_id!r} 已评审（{art.status.value}），禁止重复裁决"
            )
        if not reviewer:
            raise ResearchSandboxError("reviewer 为空")
        status = ReviewStatus.APPROVED if approve else ReviewStatus.REJECTED
        decision = ReviewDecision(
            artifact_id=artifact_id,
            status=status,
            reviewer=reviewer,
            reason=reason,
            decided_at=self._clock(),
        )
        self._decisions[artifact_id] = decision
        self._artifacts[artifact_id] = replace(art, status=status)
        if approve:
            self._approved[artifact_id] = self._workspace[art.workspace_path]
        _log.info("回写评审: %s -> %s (%s)", artifact_id, status.value, reviewer)
        return decision

    def approved_content(self, artifact_id: str) -> str:
        """已批准回写内容（未批准/未知 Fail-Closed）。"""
        content = self._approved.get(artifact_id)
        if content is None:
            raise ResearchSandboxError(f"回写单 {artifact_id!r} 未获批准（无回写内容）")
        return content

    # ── 查询 ─────────────────────────────────────────────────────────────

    def review_status(self, artifact_id: str) -> ReviewStatus:
        """回写单状态（未知 Fail-Closed）。"""
        art = self._artifacts.get(artifact_id)
        if art is None:
            raise ResearchSandboxError(f"未知回写单: {artifact_id!r}")
        return art.status

    def writeback_queue(
        self, status: ReviewStatus | None = None
    ) -> tuple[WritebackArtifact, ...]:
        """回写队列（按 (submitted_at, artifact_id) 确定性排序；可按状态过滤）。"""
        if status is not None and not isinstance(status, ReviewStatus):
            raise ResearchSandboxError(f"非法评审状态: {status!r}")
        out = [
            a for a in self._artifacts.values() if status is None or a.status is status
        ]
        out.sort(key=lambda a: (a.submitted_at, a.artifact_id))
        return tuple(out)

    @property
    def quota(self) -> ResourceQuota:
        """配额声明（构造期已校验）。"""
        return self._quota

    @property
    def sandbox_root(self) -> str:
        return self._sandbox_root

    @property
    def production_root(self) -> str:
        return self._production_root
