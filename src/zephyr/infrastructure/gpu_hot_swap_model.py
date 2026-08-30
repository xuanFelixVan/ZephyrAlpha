# [BLUEPRINT] MOD-INF-069 | docs/03_modules/_domain_infrastructure_operations/gpu_hot_swap_model/blueprint.md | §
# [MODULE] zephyr.infrastructure.gpu_hot_swap_model
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] zephyr.infrastructure.redis_state_layer_ssot
# [CONSUMERS] P4 运维进程（GPU 调度决策消费契约）；P5 盘后训练进程（上岗画像）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 两档上岗画像唯一真源=A9 运维架构 §0.3（盘中 8-10GB/盘后 16-18GB）；显存预算校验 Fail-Closed；热备恢复目标 <5s；gpu:allocation 状态草稿结构唯一真源=MOD-INF-063 gpu 命名空间（引用不重复建）；本模块只产出契约/校验/草稿文本，系统级显存操作属 Owner 窗口
# [MODIFY-GUARD] tests/infrastructure/test_gpu_hot_swap_model.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GpuHotSwapContractError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_gpu_hot_swap_model.py
# [A_module] module_id=MOD-INF-069 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
GPU 上岗热交换模型（MOD-INF-069）——横切层四件套 GPU 件契约收口。

真源：A9 运维架构 §0.3（docs/_working/架构图/运维架构.md）+ CAND-INFRAOPS-001（B14-04517，
AUD-DRAFT-001 裁定=做 P0）。

四件套分工（不重复建，只收口引用）：
  - Redis 共享状态层：MOD-INF-063 redis_state_layer_ssot（13 命名空间/TTL/持久化，W2b 已建成）；
  - GPU 上岗热交换：本模块（两档显存画像+热交换契约+gpu:allocation 状态草稿）；
  - 监控（RED+USE+SLO/4 级告警）：MOD-INF-015 system_telemetry（既有）；
  - 灾备（3-2-1-1-0）：MOD-INF-043 disaster_recovery_backup（既有）。

职责边界：本模块是 GPU 调度平面的**参数与契约真源**——两档上岗画像
（盘中推理 8-10GB / 盘后训练 16-18GB）、热交换步骤协议、热备恢复 <5s 目标、
gpu:allocation Hash 字段草稿（命名空间契约引用 MOD-INF-063，不重复建 Redis SSOT）。
采集归 trading/gpu_monitor.py（nvidia-smi 快照）；系统级显存分配/进程重启属 Owner 窗口。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gpu_hot_swap_model.py
# 层: 算法
# - id: A1
#   name_zh: ① GpuHotSwapModel
#   name_en: GpuHotSwapModel
#   intro: GPU 上岗热交换模型——契约校验与状态草稿产出（纯声明，零系统级执行）。
#   desc: GPU 上岗热交换模型——契约校验与状态草稿产出（纯声明，零系统级执行）。；公共方法（定义序）: validate_allocation, plan_swap, render_gpu_allocation_state,…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: GpuHotSwapModel
#   downstream: P4 运维进程（GPU 调度决策消费契约）；P5 盘后训练进程（上岗画像）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from zephyr.infrastructure.redis_state_layer_ssot import get_namespace

__all__: Final = [
    "CROSS_CUTTING_CONTRACT",
    "GPU_DUTY_PROFILES",
    "HOT_SWAP_CONTRACT",
    "GpuDutyProfile",
    "GpuHotSwapContractError",
    "GpuHotSwapModel",
    "HotSwapContract",
    "PieceOwner",
    "SwapPlan",
    "SwapStep",
]


class GpuHotSwapContractError(RuntimeError):
    """GPU 上岗热交换契约校验失败（未知会话/超显存预算/非法热交换，Fail-Closed）。"""


# ============================================================================
# 两档上岗画像（A9 §0.3 唯一真源：盘中推理 8-10GB / 盘后训练 16-18GB）
# ============================================================================

SESSION_INTRADAY_INFERENCE: Final[str] = "intraday_inference"  # 盘中推理档
SESSION_POSTMARKET_TRAINING: Final[str] = "postmarket_training"  # 盘后训练档


@dataclass(frozen=True)
class GpuDutyProfile:
    """单档 GPU 上岗画像（显存预算硬边界）。"""

    session: str  # 上岗会话标识
    vram_budget_min_gb: int  # 显存预算下限（GB）
    vram_budget_max_gb: int  # 显存预算上限（GB）
    duty_window: str  # 上岗时段（声明）
    workload: str  # 负载类型（声明）


GPU_DUTY_PROFILES: Final[dict[str, GpuDutyProfile]] = {
    SESSION_INTRADAY_INFERENCE: GpuDutyProfile(
        session=SESSION_INTRADAY_INFERENCE,
        vram_budget_min_gb=8,
        vram_budget_max_gb=10,
        duty_window="交易时段 09:15-15:00",
        workload="盘中推理（信号/风控前向计算）",
    ),
    SESSION_POSTMARKET_TRAINING: GpuDutyProfile(
        session=SESSION_POSTMARKET_TRAINING,
        vram_budget_min_gb=16,
        vram_budget_max_gb=18,
        duty_window="盘后 15:30-次日 08:30",
        workload="盘后训练（模型拟合/回测加速）",
    ),
}


@dataclass(frozen=True)
class HotSwapContract:
    """热交换契约参数（A9 §0.3：热备恢复 <5s）。"""

    standby_restore_target_seconds: float  # 热备恢复目标秒数（<5s）
    drain_timeout_seconds: float  # 旧画像显存排空超时
    verify_retry_limit: int  # 切换后校验重试上限


HOT_SWAP_CONTRACT: Final[HotSwapContract] = HotSwapContract(
    standby_restore_target_seconds=4.0,  # 目标 <5s，留 1s 余量
    drain_timeout_seconds=30.0,
    verify_retry_limit=3,
)


@dataclass(frozen=True)
class SwapStep:
    """热交换单步声明。"""

    kind: str  # release / load / verify
    detail: str


@dataclass(frozen=True)
class SwapPlan:
    """热交换计划（步骤有序：release → load → verify）。"""

    source_session: str
    target_profile: GpuDutyProfile
    steps: tuple[SwapStep, ...]


# ============================================================================
# 四件套收口映射（各件 SSOT 归属，引用不重复建）
# ============================================================================


@dataclass(frozen=True)
class PieceOwner:
    """四件套单件的 SSOT 归属声明。"""

    owner_module_id: str  # 归属模块 blueprint_id
    anchor_path: str  # 真源锚点文件（存在性校验用）


CROSS_CUTTING_CONTRACT: Final[dict[str, PieceOwner]] = {
    "redis_state": PieceOwner(
        owner_module_id="MOD-INF-063",
        anchor_path="src/zephyr/infrastructure/redis_state_layer_ssot.py",
    ),
    "gpu_duty": PieceOwner(
        owner_module_id="MOD-INF-069",
        anchor_path="src/zephyr/infrastructure/gpu_hot_swap_model.py",
    ),
    "monitoring": PieceOwner(
        owner_module_id="MOD-INF-015",
        anchor_path="src/zephyr/infrastructure/system_telemetry/facade.py",
    ),
    "disaster_recovery": PieceOwner(
        owner_module_id="MOD-INF-043",
        anchor_path="docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md",
    ),
}


class GpuHotSwapModel:
    """GPU 上岗热交换模型——契约校验与状态草稿产出（纯声明，零系统级执行）。"""

    def validate_allocation(self, requested_gb: float, session: str) -> None:
        """校验显存申请是否落在当档画像预算内（Fail-Closed）。

        Raises
        ------
        GpuHotSwapContractError
            未知上岗会话 / 申请超出显存预算上限。
        """
        profile = GPU_DUTY_PROFILES.get(session)
        if profile is None:
            raise GpuHotSwapContractError(f"未知上岗会话: {session!r}（合法={sorted(GPU_DUTY_PROFILES)}）")
        if requested_gb > profile.vram_budget_max_gb:
            raise GpuHotSwapContractError(
                f"显存预算越界: 申请 {requested_gb}GB > {session} 上限 {profile.vram_budget_max_gb}GB（A9 §0.3 硬边界）"
            )

    def plan_swap(self, source_session: str, target_session: str) -> SwapPlan:
        """产出热交换计划（release → load → verify，热备恢复目标 <5s）。"""
        if source_session == target_session:
            raise GpuHotSwapContractError(f"同会话无需热交换: {source_session!r}")
        target = GPU_DUTY_PROFILES.get(target_session)
        if target is None:
            raise GpuHotSwapContractError(f"未知上岗会话: {target_session!r}")
        if source_session not in GPU_DUTY_PROFILES:
            raise GpuHotSwapContractError(f"未知上岗会话: {source_session!r}")
        steps = (
            SwapStep(
                kind="release",
                detail=f"排空 {source_session} 画像显存（drain 超时 {HOT_SWAP_CONTRACT.drain_timeout_seconds}s）",
            ),
            SwapStep(
                kind="load",
                detail=(
                    f"加载 {target.session} 画像（预算 {target.vram_budget_min_gb}-"
                    f"{target.vram_budget_max_gb}GB，{target.workload}）"
                ),
            ),
            SwapStep(
                kind="verify",
                detail=(
                    f"校验新画像就绪（重试上限 {HOT_SWAP_CONTRACT.verify_retry_limit}，"
                    f"热备恢复目标 <{HOT_SWAP_CONTRACT.standby_restore_target_seconds}s）"
                ),
            ),
        )
        return SwapPlan(source_session=source_session, target_profile=target, steps=steps)

    def render_gpu_allocation_state(self, session: str, allocated_gb: float) -> dict[str, object]:
        """产出 gpu:allocation Hash 状态草稿（字段文本，不写 Redis）。

        命名空间契约（key/structure/TTL）引用 MOD-INF-063 SSOT——禁止重复建。
        """
        self.validate_allocation(allocated_gb, session)
        ns = get_namespace("gpu")  # MOD-INF-063 既有 SSOT（ops_control 层）
        return {
            "key": ns.key_pattern,  # gpu:allocation
            "structure": ns.structure,  # Hash
            "ttl_seconds": ns.ttl_seconds,  # None（永不过期）
            "fields": {
                "session": session,
                "allocated_gb": str(allocated_gb),
                "budget_max_gb": str(GPU_DUTY_PROFILES[session].vram_budget_max_gb),
            },
        }

    def check_four_piece_closure(self) -> dict[str, object]:
        """四件套收口自检：四件各有 SSOT 锚点（文件存在性，Fail-Closed 缺件）。"""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[3]
        pieces = {name: (repo_root / owner.anchor_path).exists() for name, owner in CROSS_CUTTING_CONTRACT.items()}
        return {"closed": all(pieces.values()), "pieces": pieces}
