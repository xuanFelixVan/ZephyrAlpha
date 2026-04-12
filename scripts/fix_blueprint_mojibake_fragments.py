#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""定向修复 01_BLUEPRINTS 中 UTF-8 断裂产生的残缺片段（保持 utf-8-sig）。"""

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")

MODULE_SECTION_2 = """## 二、核心模块职责边界

本节用四组典型模块对说明职责如何划分，避免重复实现与能力遗漏；实现细节以各模块蓝图为准。

### 2.1 情景分析器（ScenarioAnalyzer）与压力测试报告器（StressTestReporter）

#### 对比摘要

| 维度 | ScenarioAnalyzer | StressTestReporter |
|------|------------------|-------------------|
| **核心职责** | 历史/假设情景定义与回放 | 压力情景执行与报告产出 |
| **主要输出** | 情景分析报告、冲击结果 | 压力测试报告、监管口径材料 |
| **典型节奏** | 按需 / 周度 | 月度 / 季度 |
| **典型场景** | 危机回放、参数敏感性 | 统一压力模板、限额联动 |

#### ScenarioAnalyzer 职责范围

**包含**：情景库与模板管理；资产在给定情景下的损益与风险指标；情景分析报告。

**不包含**：以监管报送为目的的定型压力测试流水线（与 StressTestReporter 的边界在集成设计中另行约定）。

#### StressTestReporter 职责范围

**包含**：压力测试任务编排、极值与生存能力类指标、合规报送格式报告。

**不包含**：一般性的策略级情景探索（偏研究向时由 ScenarioAnalyzer 侧重承担）。

---

### 2.2 实时风险报告（RealTimeRiskReporter）与风险控制（risk_manager.py）

| 维度 | RealTimeRiskReporter | risk_manager.py |
|------|---------------------|-----------------|
| **核心职责** | 风险计量与报告 | 限额、指令与管控动作 |
| **输出** | 报告、告警、可视化素材 | 控制指令、限额变更记录 |
| **调用频率** | 实时（秒级） | 事件驱动 / 按需 |
| **典型场景** | 盘中监控大屏 | 触发减仓、对冲或暂停交易 |

**划分原则**：计量与展示归报告侧；对头寸的硬控制归 risk_manager 侧。

---

### 2.3 多周期报告融合（MultiTimeframeReportFusion）与经济范式报告（EconomicRegimeReporter）

| 维度 | MultiTimeframeReportFusion | EconomicRegimeReporter |
|------|---------------------------|----------------------|
| **核心职责** | 多频报告对齐与融合叙事 | 宏观范式识别与解释 |
| **输出** | 融合报告 | 范式/周期类专题报告 |
| **调用频率** | 日度 | 季度 / 月度 |
| **典型场景** | 日盘与周盘一致性校验 | 衰退/复苏阶段标签 |

---

### 2.4 常规报告（Daily/MonthlyReporter）与专题报告器

| 维度 | DailyReporter / MonthlyReporter | 专题报告器 |
|------|--------------------------------|-----------|
| **核心职责** | 综合性定期披露 | 单一主题的深度分析 |
| **输出** | 综合报告 | 专题报告 |
| **调用频率** | 日度 / 月度 | 按需 |
| **典型场景** | 管理层仪表盘 | 单一风险事件复盘 |

---
"""


def rewrite_module_responsibility(text: str) -> str:
    text = text.replace("layer: Layer 5 (策略执行层)---", "layer: Layer 5 (策略执行层)\n---")
    start = text.find("## 二、核心模块职责边")
    end = text.find("## 三、模块间接口定义")
    if start != -1 and end != -1 and end > start:
        text = text[:start] + MODULE_SECTION_2 + "\n\n" + text[end:]
    return text


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fill_empty_applicable_scope(text: str) -> str:
    if not re.search(r"^applicable_scope:\s*$", text, flags=re.M):
        return text
    m = re.search(r"^layer:\s*(.+)$", text, flags=re.M)
    if not m:
        return text
    val = m.group(1).strip()
    return re.sub(r"^applicable_scope:\s*$", f"applicable_scope: {val}", text, count=1, flags=re.M)


def fix_applicable_scope(text: str) -> str:
    if "applicable_scope: å" not in text:
        return text
    m = re.search(
        r"^applicable_scope:\s*å\s*$(?:\r?\n)(?:^[^\n]*$\n)*?^layer:\s*(.+)$",
        text,
        re.M,
    )
    if not m:
        return text
    layer_val = m.group(1).strip()
    return re.sub(r"^applicable_scope:\s*å\s*$", f"applicable_scope: {layer_val}", text, count=1, flags=re.M)


def apply_subs(text: str) -> str:
    subs: list[tuple[str, str]] = [
        ("å®?", "合规"),
        ("**Staræ?*:", "**GitHub Stars**:"),
        ("S3å\n", "S3 兼容 API\n"),
        ("| å\n存占用", "| 内存占用"),
        ("100mså\n", "100ms内\n"),
        ("10mså\n", "10ms内\n"),
        ("7. **yfinance** - é\n虎财经数据接口", "7. **yfinance** - 雅虎财经数据接口"),
        ("### 5.3 YAMLé\n", "### 5.3 YAML 配置示例\n"),
        ("**Docker Composeé\n", "**Docker Compose 配置**\n"),
        ("**Deploymenté\n", "**Deployment 流程**\n"),
        (
            "| **PostgreSQL** | 15+ | å\n| **Redis**",
            "| **PostgreSQL** | 15+ | 关系型数据库 | [官方文档](https://www.postgresql.org/) |\n| **Redis**",
        ),
        (
            "| **Unified Data Infrastructure** | å\n\n### 1.3 版本管理",
            "| **Unified Data Infrastructure** | 统一数据基础设施编排与治理 | 与数据湖、管道类蓝图衔接 |\n\n### 1.3 版本管理",
        ),
        ("## å\n\n### 6.1 开发阶段划?", "## 六、实施路线图\n\n### 6.1 开发阶段划分"),
        ("### 6.2 å\n\n| 里程?", "### 6.2 里程碑与交付物\n\n| 里程碑"),
        ("## å\n\n\n，支持灵活组合", "## 八、总结与展望\n\n，支持灵活组合"),
        ("- **é\n- **测试验证**", "- **参数与配置调优**\n- **测试验证**"),
        ("CointegrationResult: å\n", "CointegrationResult: 协整检验结果\n"),
        ("TradingSignal: å\n", "TradingSignal: 交易信号\n"),
        ("PortfolioAllocation: å\n", "PortfolioAllocation: 组合配置结果\n"),
        ("AllocationResult: é\n", "AllocationResult: 配置结果\n"),
        ("Black-Littermané\n", "Black-Litterman 视图融合\n"),
        ("### 3.4 é\n", "### 3.4 性能与成本\n"),
        ("### 3.6 é\n", "### 3.6 扩展阅读\n"),
        ("### 5.1 é\n", "### 5.1 集成要点\n"),
        ("### 5.2 é\n", "### 5.2 配置说明\n"),
        ("### 7.1 Phase 1: é\n", "### 7.1 Phase 1: 基础能力\n"),
        ("### 8.1 å\n", "### 8.1 运维要点\n"),
        ("### 6.1 å\n", "### 6.1 集成清单\n"),
        ("- [ ] é\n", "- [ ] 集成验收项（待补充）\n"),
        ("¥é\n", "  # 示例配置\n"),
    ]
    for a, b in subs:
        text = text.replace(a, b)
    return text


def fix_table_ending_å(text: str) -> str:
    text = re.sub(
        r"(\| \*\*[^*|]+\*\* \|) å\s*\n(\s*\n)(?=### |\n## |\Z)",
        r"\1 核心能力摘要（见正文） |\2",
        text,
    )
    text = re.sub(r"(\| \*\*[^*|]+\*\* \|) å\s*$", r"\1 核心能力摘要（见正文） |", text, flags=re.M)
    return text


def fix_lone_heading_å(text: str) -> str:
    text = re.sub(r"^## å\s*$", "## 相关说明（待补充）", text, flags=re.M)
    text = re.sub(r"^### å\s*$", "### 子章节（待补充）", text, flags=re.M)
    text = re.sub(r"^### 4\.4 å\s*$", "### 4.4 其他说明", text, flags=re.M)
    text = re.sub(r"^### 10\. å\s*$", "### 10. 附录", text, flags=re.M)
    return text


def fix_scenario_file(text: str) -> str:
    text = re.sub(r"scenario_name: æ\n", "scenario_name: 情景名称\n", text)
    text = re.sub(r"scenario_dates: æ\n", "scenario_dates: 情景日期范围\n", text)
    text = re.sub(r"(?m)^\s*æ\n景", "情景", text)
    text = re.sub(r"Returns:\s*\n\s*æ\n景", "Returns:\n            情景", text)
    text = re.sub(r"scenario_results: æ\n", "scenario_results: 情景", text)
    text = re.sub(r"\| æ\n景类型", "| 情景类型", text)
    text = re.sub(r'"""æ\n景分析API"""', '"""情景分析 API"""', text)
    text = re.sub(r"^-\s*æ\n", "- 情景", text, flags=re.M)
    return text


def fix_broken_memory_rows(text: str) -> str:
    text = re.sub(r"\|\s*\n存占用", "| 内存占用", text)
    text = text.replace("存占用** |", "内存占用** |")
    return text


def process_file(fp: pathlib.Path) -> bool:
    raw = fp.read_bytes()
    text = normalize_newlines(raw.decode("utf-8-sig", errors="strict"))
    orig = text

    if fp.name == "MODULE_RESPONSIBILITY_BOUNDARIES_BLUEPRINT.md":
        text = rewrite_module_responsibility(text)

    text = fill_empty_applicable_scope(text)
    text = fix_applicable_scope(text)
    text = apply_subs(text)
    text = fix_table_ending_å(text)
    text = fix_lone_heading_å(text)

    if fp.name == "PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md":
        text = fix_scenario_file(text)

    text = fix_broken_memory_rows(text)

    if text != orig:
        fp.write_bytes(text.encode("utf-8-sig"))
        return True
    return False


def main() -> int:
    n = 0
    for fp in sorted(ROOT.glob("*.md")):
        if process_file(fp):
            n += 1
            print("fixed", fp.as_posix())
    print("ChangedFiles=", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
