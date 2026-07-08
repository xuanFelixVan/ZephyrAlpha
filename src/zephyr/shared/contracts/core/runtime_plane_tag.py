# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.runtime_plane_tag
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_runtime_plane_tag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — shared/contracts/runtime_plane_tag.py

Runtime Plane 契约预留（Orthogonal View Runtime Plane Tag Contract）。

🔒 **契约预留（Reserved Contract）**：本文件定义 `runtime_planes.md` 正交视图所用的
运行平面枚举 + 模块标注协议。**当前阶段 ZephyrAlpha 处于 Warm Path only，本契约仅定义类型
与 docstring 规范，不作为运行时强制校验**——只在模块 metadata / 文档 / 架构静态分析脚本里使用。

═══════════════════════════════════════════════════════════════════════
【用途】
═══════════════════════════════════════════════════════════════════════
1. 为每个 D_DATA~实验 + shared + frontend + scripts 模块声明所属 **Runtime Plane**
   （Hot / Warm / Cold），作为 `runtime_planes.md` 正交视图的机器可读元数据。
2. 未来 Hot Path 激活时（T1 真实资金或 T-ENDGAME 顶级对标触发），本契约升级为
   **运行时强制校验**（PR lint + CI gate + 架构一致性扫描脚本消费）。
3. 当前（Warm Path only）本契约仅作为**文档级标注**，等价于一个"加强版的 module docstring"。

═══════════════════════════════════════════════════════════════════════
【三档 Runtime Plane 定义】（与 runtime_planes.md §2 对齐）
═══════════════════════════════════════════════════════════════════════
- **HOT**（Hot Path）:
    * 延迟预算：< 10ms 端到端（tick-to-trade 硬实时）
    * 技术栈：C++ / Rust / kernel-bypass (DPDK, io_uring, Solarflare OpenOnload)
    * 可中断性：**不可中断**（不得调用 GC 语言 / 不得阻塞 IO / 不得 async await）
    * 典型场景：做市报价、交易所订单网关、行情推送直连
    * **当前状态**：**NOT ACTIVATED**（T-ENDGAME 顶级机构对标阶段才激活）

- **WARM**（Warm Path）:
    * 延迟预算：10ms - 1s（近实时，人机交互 + 业务决策）
    * 技术栈：Python 3.12 + asyncio + uvloop / FastAPI + TanStack Query 前端
    * 可中断性：可中断（协程调度、IO-bound 任务）
    * 典型场景：因子计算、策略推理、风控校验、API 请求响应、前端交互
    * **当前状态**：**唯一激活平面**（ZephyrAlpha 2.0 Warm Path only 阶段）

- **COLD**（Cold Path）:
    * 延迟预算：> 1s（批处理，离线训练，报表）
    * 技术栈：Spark / Dask / Airflow / Ray cluster + Python 批处理
    * 可中断性：完全可中断（任务级别重试、容错、checkpointing）
    * 典型场景：历史回测、模型训练、特征工程批计算、合规报表生成、SSR 导出
    * **当前状态**：PARTIAL ACTIVATED（少量 cron + 回测作业已在 Warm Path 内以
      同步阻塞方式跑，未来分离到真正的 Cold Path cluster）

═══════════════════════════════════════════════════════════════════════
【使用示范】（当前文档级标注用法）
═══════════════════════════════════════════════════════════════════════
在模块 `__init__.py` 或 `<module>.py` 顶部声明：

    from zephyr.shared.contracts.core.runtime_plane_tag import RuntimePlane

    __runtime_plane__ = RuntimePlane.WARM
    __runtime_plane_rationale__ = (
        "factor computation in D_FACTOR factor_engine runs in async pipeline, "
        "latency budget 100ms per factor, Python async + numpy vectorization"
    )

或在模块 docstring 里声明：

    \"\"\"
    Module: zephyr.factor.momentum

    Runtime Plane: WARM (10ms-1s async Python path)
    Rationale: factor computation, async pipeline, numpy vectorization
    \"\"\"

═══════════════════════════════════════════════════════════════════════
【Hot-adjacent 特殊说明】
═══════════════════════════════════════════════════════════════════════
**Hot-adjacent**（热邻接）不是独立平面，而是 WARM 平面下的一类特殊子类——模块本身
运行在 Warm Path，但 **对接** Hot Path 的下游数据（例如前端 WebSocket 订阅行情、
D_FRONTEND api_gateway 的订单提交端点）。Hot-adjacent 模块在 Warm Path 标注的基础上，
应通过 `__runtime_plane_adjacency__ = ("HOT",)` 附加声明。

═══════════════════════════════════════════════════════════════════════
【与 runtime_planes.md 的关系】
═══════════════════════════════════════════════════════════════════════
- runtime_planes.md 是架构视图，定义平面划分方法论、业务归属矩阵、通信协议、激活触发器
- 本文件（runtime_plane_tag.py）是**契约载体**，定义枚举 + 标注协议 + 常量
- 改动本文件枚举值 / 标注协议 -> 必须先改 runtime-planes 视图 + ADR-0011 升级 -> 再改本文件
- 当前本文件版本 v1.0.0 对齐 runtime-planes v1.0.0 + ADR-0011 v1.0.0

参见：
  - architecture_model/cross_cutting/runtime_planes.yaml
  - adr/adr-0011-runtime-planes-orthogonal-view.md
  - OQ-083（已 closed，本批次拍板）
═══════════════════════════════════════════════════════════════════════
"""

from enum import Enum
from typing import Final


class RuntimePlane(str, Enum):
    """
    Runtime Plane 三档枚举（正交视图 runtime-planes 的规范类型）。

    继承 str 以便 JSON 序列化 / YAML dump / OpenAPI schema 直接输出字符串值，
    避免 `RuntimePlane.WARM` 在 jsonify 时出现 `{"__enum__": "..."}` 脏痕。
    """

    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


HOT_PATH_LATENCY_BUDGET_MS: Final[float] = 10.0
"""Hot Path 延迟硬预算上限（毫秒，tick-to-trade 端到端）。"""

WARM_PATH_LATENCY_BUDGET_MS: Final[float] = 1000.0
"""Warm Path 延迟硬预算上限（毫秒，人机交互 + 业务决策）。"""

COLD_PATH_LATENCY_BUDGET_MS: Final[float] = float("inf")
"""Cold Path 无硬上限（批处理作业），但 SLA 建议按作业类型分档（秒/分钟/小时）。"""

HOT_PATH_ACTIVATED: Final[bool] = False
"""
Hot Path 全局激活开关。

**当前 False**：ZephyrAlpha 2.0 处于 Warm Path only 阶段。

激活条件（满足任一即触发 ADR 升级本常量到 True）：
  1. T1 真实资金接入且交易频率 > 100 笔/天
  2. T-ENDGAME 顶级机构对标阶段启动（做市 / HFT 场景）
  3. 低延迟基础设施（C++/Rust + kernel-bypass）PoC 验证通过

**禁止**在本常量为 False 时调用任何自称 Hot Path 的代码路径——违反即 CI gate 驳回。
"""

COLD_PATH_PARTIAL_ACTIVATED: Final[bool] = True
"""
Cold Path 部分激活开关。

**当前 True**：少量 cron + 回测作业已落地（仍在 Warm Path 进程内同步阻塞跑，未来分离到
独立 Cold Path cluster）。Cold Path 作业在 Warm 进程内跑时，**必须**标注为
`RuntimePlane.COLD` 并通过 shield pattern 隔离（避免阻塞 Warm 主事件循环）。
"""

__all__ = [
    "COLD_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "HOT_PATH_ACTIVATED",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "RuntimePlane",
]
