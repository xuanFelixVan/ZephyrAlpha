# [BLUEPRINT] MOD-CMP-009 | docs/03_modules/_domain_compliance/compliance_report_registry/blueprint.md
# [MODULE] zephyr.compliance.compliance_report_registry
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + pyyaml + zephyr.compliance.compliance_log
# [CONSUMERS] C-002 执行域（先报告后交易铁律：任一必报项 broker_ack 缺失 → 拒单，43 号 §7.4）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 先报告后交易（必报项 broker_ack 缺失=BLOCK）; 登记表不可读=Fail-Closed BLOCK; 报送动作为人工（券商渠道），系统管登记/确认位/门禁
# [MODIFY-GUARD] 43_compliance_discipline.md §7.4/§7.5
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceReportError(ZA-CMP-0006)
# [TESTS] tests/compliance/test_compliance_report_registry.py
# [TTL] permanent

"""



程序化交易报告 6 项义务登记 + 报送门禁（43_compliance_discipline §7.4）。

铁律：**先报告后交易**——报告未完成确认前，C-002 执行域拒绝发送任何订单
（steps JSON degradation 原样承继）。

6 项义务（§7.4 表格）：①账户基本信息 ②交易软件信息 ③策略类型（6 大类）
④最高申报速率（miniQMT 通道上限 10 笔/秒填报）⑤单日最高申报笔数
（MVP 2000 笔/日待校准）⑥重大变更（T+1 报送）。

报送动作本身为人工（券商渠道），系统管"登记、确认位、门禁"——本模块只读
校验；报送后由人工/AI 编辑 YAML 更新 reported_at/broker_ack 确认位。

50μs 订单停留时间锁（§7.5）：裁定不适用（个人低频），在登记表记录
``order_min_dwell_us: 50``（监管参考值，本系统天然满足）。

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 参数 registry_path（无注解）
#   code: compliance_report_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ComplianceReportRegistry
#   name_en: ComplianceReportRegistry
#   intro: 报告登记表（只读加载 + 门禁校验）。
#   desc: 报告登记表（只读加载 + 门禁校验）。；公共方法（定义序）: load_items, order_min_dwell_us；源码 L130-L165
#   inputs: registry_path
#   outputs: 返回值
# - id: A2
#   name_zh: ② ReportGate
#   name_en: ReportGate
#   intro: 报送门禁：任一必报项 broker_ack 缺失 → BLOCK（C-002 拒单）。
#   desc: 报送门禁：任一必报项 broker_ack 缺失 → BLOCK（C-002 拒单）。；公共方法（定义序）: check；源码 L168-L216
#   inputs: registry logger
#   outputs: 返回值
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: ComplianceReportRegistry, ReportGate
#   downstream: C-002 执行域（先报告后交易铁律：任一必报项 broker_ack 缺失 → 拒单，43 号 §7.4）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path

import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

DEFAULT_REGISTRY_PATH: Path = (
    REPO_ROOT  # git 版本化配置锚定当前检出（区别于治理观测库锚主仓）
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "compliance_report_registry.yaml"
)


class ComplianceReportError(ZephyrBaseError):
    """报告登记错误。"""

    error_code = "ZA-CMP-0006"


class ReportGateDecision(enum.Enum):
    """门禁结论。"""

    PASS = "PASS"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class ReportItem:
    """一条报告义务（§7.4）。"""

    item_id: str
    name: str
    content_source: str  # 内容真源
    timing: str  # 报送时机
    required: bool
    reported_at: str | None
    broker_ack: bool


@dataclass(frozen=True)
class ReportGateResult:
    """门禁校验结果（不可变）。"""

    decision: ReportGateDecision
    missing: tuple[str, ...]  # 未确认必报项 item_id
    detail: str


class ComplianceReportRegistry:
    """报告登记表（只读加载 + 门禁校验）。"""

    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path = registry_path or DEFAULT_REGISTRY_PATH

    def load_items(self) -> list[ReportItem]:
        """加载全部报告项；登记表不可读 → ComplianceReportError。"""
        if not self._registry_path.exists():
            raise ComplianceReportError(f"登记表不存在: {self._registry_path}")
        try:
            data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ComplianceReportError(f"登记表解析失败: {exc}") from exc
        items: list[ReportItem] = []
        for raw in data.get("report_items", []):
            items.append(
                ReportItem(
                    item_id=raw["item_id"],
                    name=str(raw.get("name", "")),
                    content_source=str(raw.get("content_source", "")),
                    timing=str(raw.get("timing", "")),
                    required=bool(raw.get("required", True)),
                    reported_at=raw.get("reported_at"),
                    broker_ack=bool(raw.get("broker_ack", False)),
                )
            )
        return items

    def order_min_dwell_us(self) -> int | None:
        """记录性参数：50μs 订单停留时间锁（§7.5 监管参考值，本系统天然满足）。"""
        if not self._registry_path.exists():
            return None
        data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        value = data.get("order_min_dwell_us")
        return int(value) if value is not None else None


class ReportGate:
    """报送门禁：任一必报项 broker_ack 缺失 → BLOCK（C-002 拒单）。"""

    def __init__(
        self,
        registry: ComplianceReportRegistry | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._registry = registry or ComplianceReportRegistry()
        self._logger = logger or ComplianceLogger()

    def check(self) -> ReportGateResult:
        """校验报送状态。登记表不可读 → Fail-Closed BLOCK。"""
        try:
            items = self._registry.load_items()
        except ComplianceReportError as exc:
            result = ReportGateResult(
                decision=ReportGateDecision.BLOCK,
                missing=(),
                detail=f"登记表不可读，Fail-Closed 拒单: {exc}",
            )
            self._log(result)
            return result
        missing = tuple(i.item_id for i in items if i.required and not i.broker_ack)
        if missing:
            result = ReportGateResult(
                decision=ReportGateDecision.BLOCK,
                missing=missing,
                detail=f"先报告后交易：{len(missing)} 项必报未确认（broker_ack 缺失）→ C-002 拒单",
            )
        else:
            result = ReportGateResult(
                decision=ReportGateDecision.PASS,
                missing=(),
                detail="全部必报项已确认",
            )
        self._log(result)
        return result

    def _log(self, result: ReportGateResult) -> None:
        self._logger.log(
            "REPORT_GATE_CHECK",
            "compliance_report_registry",
            {
                "decision": result.decision.value,
                "missing": list(result.missing),
                "detail": result.detail,
            },
        )
