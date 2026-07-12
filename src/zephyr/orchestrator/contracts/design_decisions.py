from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.contracts.design_decisions
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_design_decisions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
设计决策注册表（Design Decisions — DD-1~DD-14）

依据：MOD-MASTER-002 蓝图 §九 设计决策集中表
记录 14 条关键设计决策，含替代方案、选择理由、重评条件。

注：蓝图 §九 声明"当前10条"但实际列出14行，DD9/DD10出现两次（编号重复）。
本文件以14条决策为准。
"""

from enum import Enum

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    ACTIVE = "active"
    RE_EVALUATED = "re_evaluated"
    SUPERSEDED = "superseded"


class DesignDecision(BaseModel):
    dd_id: str
    title: str
    content: str
    alternatives: list[str] = Field(default_factory=list)
    rationale: str = ""
    re_evaluate_when: str = ""
    impact_scope: str = ""
    status: DecisionStatus = DecisionStatus.ACTIVE


DECISIONS: Final[dict[str, DesignDecision]] = {
    "DD-1": DesignDecision(
        dd_id="DD-1",
        title="总蓝图只定义'之间'不管'内部'",
        content="本蓝图仅定义 12 系统间的集成契约（CT-*），不干预各模块内部实现细节",
        alternatives=["每个模块蓝图各自定义集成规则 -> 碎片化、无全局视角"],
        rationale="保持职责单一——模块蓝图管内部，本蓝图管跨系统",
        re_evaluate_when="出现需要跨系统管控模块内部行为的强需求时",
        impact_scope="全部 54 条 CT-* 契约",
    ),
    "DD-2": DesignDecision(
        dd_id="DD-2",
        title="YAML 结构化契约",
        content="所有 CT-* 契约使用 YAML 格式定义，包含 trigger/schema/telemetry/ai_prompt 结构化字段",
        alternatives=["纯 Markdown 表格 -> 难以机器解析", "JSON Schema -> 过于冗长"],
        rationale="YAML 兼顾人类可读性和机器解析，与 architecture_model 格式一致",
        re_evaluate_when="出现大量 YAML 解析性能瓶颈时",
        impact_scope="契约定义格式",
    ),
    "DD-3": DesignDecision(
        dd_id="DD-3",
        title="fail-closed 优先于 availability",
        content="集成调用失败时默认拒绝（fail-closed），而非降级放行（fail-open）",
        alternatives=["fail-open：失败时允许降级 -> 安全风险"],
        rationale="ZephyrAlpha 为金融量化系统，安全优先于可用性",
        re_evaluate_when="出现因过度保守导致的严重可用性问题",
        impact_scope="所有 CT-* 调用失败处理",
    ),
    "DD-4": DesignDecision(
        dd_id="DD-4",
        title="circuit_breaker 每条 CT-* 独立配置",
        content="每条 CT-* 契约的熔断器参数（阈值/冷却时间/半开探测）独立配置",
        alternatives=["全局统一熔断器 -> 粒度太粗"],
        rationale="不同契约的调用频率和影响范围差异大，独立配置更精确",
        re_evaluate_when="12 条 circuit_breaker 管理成本超出收益时",
        impact_scope="熔断器架构",
    ),
    "DD-5": DesignDecision(
        dd_id="DD-5",
        title="FLE 无异常也记录",
        content="FLE 即使未检测到异常也定期记录系统状态快照",
        alternatives=["仅异常时记录 -> 缺少基线对比数据"],
        rationale="需要正常状态基线才能准确检测异常",
        re_evaluate_when="存储成本显著增长时",
        impact_scope="FLE 数据采集策略",
    ),
    "DD-6": DesignDecision(
        dd_id="DD-6",
        title="KE 更新 -> 新 embedding 非覆写",
        content="知识条目更新时创建新 embedding 版本而非覆写旧版本",
        alternatives=["覆写旧 embedding -> 丢失版本历史"],
        rationale="需保留知识演化轨迹，支持回退到历史版本",
        re_evaluate_when="embedding 存储成本成为瓶颈",
        impact_scope="VMS 写入策略",
    ),
    "DD-7": DesignDecision(
        dd_id="DD-7",
        title="故障传播方向内->外",
        content="系统故障传播方向为从内部向外围，内层故障不应影响外围",
        alternatives=["全局广播式故障通知 -> 可能导致雪崩"],
        rationale="Bulkhead 隔舱原则——故障应被隔离在最小范围",
        re_evaluate_when="出现因故障未传播导致的级联问题时",
        impact_scope="故障传播架构",
    ),
    "DD-8": DesignDecision(
        dd_id="DD-8",
        title="M1-M11 双 zone 不交叉",
        content="Pipeline 的 A区（生产）和 B区（审计）管线不交叉，数据仅通过 Artifact 传递",
        alternatives=["单区管线 -> 审计不独立"],
        rationale="生产与审计职责分离，确保审计管线不受生产影响",
        re_evaluate_when="双区维护成本超过收益时",
        impact_scope="Pipeline 架构",
    ),
    "DD-9": DesignDecision(
        dd_id="DD-9",
        title="三态 HealthCheck",
        content="12 系统标准化三态健康探针：healthy / degraded / unhealthy",
        alternatives=["二态 healthy/unhealthy -> 粒度不足", "四态 -> 过度复杂"],
        rationale="三态平衡了可操作性和简洁性",
        re_evaluate_when="出现需要更细粒度健康状态的场景",
        impact_scope="健康探针协议 CT-HEALTH-001",
    ),
    "DD-10": DesignDecision(
        dd_id="DD-10",
        title="DLQ 用 SQLite",
        content="死信队列使用 SQLite 持久化，而非专用消息队列中间件",
        alternatives=["Kafka DLQ -> 过度重量", "Redis DLQ -> 不持久"],
        rationale="1人+AI维护模式下优先简洁，SQLite 满足持久化需求",
        re_evaluate_when="DLQ 吞吐量超过 SQLite 能力时",
        impact_scope="DLQ 实现 CT-DLQ",
    ),
    "DD-11": DesignDecision(
        dd_id="DD-11",
        title="CDC 用本地 SQLite 简化版",
        content="消费者驱动契约验证使用本地 SQLite 实现，而非专用 CDC 工具",
        alternatives=["Debezium -> 过度重量", "手动脚本 -> 不可靠"],
        rationale="对齐 DD-10 的简洁原则，SQLite 可满足 1人+AI 模式",
        re_evaluate_when="CDC 验证需求复杂化时",
        impact_scope="CDC 实现 CT-CDC",
    ),
    "DD-12": DesignDecision(
        dd_id="DD-12",
        title="Telemetry push 模式",
        content="各系统主动 push metrics 到 Telemetry，而非 Telemetry 拉取",
        alternatives=["pull 模式 -> 需要 Telemetry 感知所有系统端点"],
        rationale="push 模式降低 Telemetry 耦合度，系统自主控制上报频率",
        re_evaluate_when="push 模式出现采集延迟或丢失问题时",
        impact_scope="可观测性架构",
    ),
    "DD-13": DesignDecision(
        dd_id="DD-13",
        title="stub/mock 必须在契约文件内定义",
        content="所有 stub 和 mock 行为必须在对应的 CT-* 契约 YAML 文件中声明",
        alternatives=["独立 mock 配置文件 -> 契约与 mock 分离"],
        rationale="契约即文档，mock 行为是契约语义的一部分",
        re_evaluate_when="契约文件因 mock 定义而膨胀严重时",
        impact_scope="mock 策略管理",
    ),
    "DD-14": DesignDecision(
        dd_id="DD-14",
        title="契约编号 CT-{A}-{B} 固定",
        content="契约编号格式 CT-{A}-{B} 不可变，A 为生产者系统缩写，B 为消费者系统缩写",
        alternatives=["UUID -> 不可读", "自增编号 -> 无语义"],
        rationale="编号即语义——从编号即可知道集成方向",
        re_evaluate_when="系统命名发生重大变更时",
        impact_scope="契约命名规范",
    ),
}


class DecisionRegistry:
    def get(self, dd_id: str) -> DesignDecision | None:
        return DECISIONS.get(dd_id)

    def list_all(self) -> list[DesignDecision]:
        return list(DECISIONS.values())

    def list_active(self) -> list[DesignDecision]:
        return [d for d in DECISIONS.values() if d.status == DecisionStatus.ACTIVE]

    def get_by_impact(self, keyword: str) -> list[DesignDecision]:
        return [d for d in DECISIONS.values() if keyword.lower() in d.impact_scope.lower()]

    def check_re_evaluate(self, dd_id: str, condition_met: bool) -> bool:
        decision = DECISIONS.get(dd_id)
        if decision is None:
            return False
        return condition_met
