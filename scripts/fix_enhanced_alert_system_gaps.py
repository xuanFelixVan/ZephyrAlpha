#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
对 ENHANCED_ALERT_SYSTEM_BLUEPRINT.md 做定向治理补全：
- 修复标题/表格/清单/代码注释中的“汉字?”断裂与孤立问号（高置信度）
- 允许修复 fenced code block 内的注释断裂（不改变量名）
"""

from __future__ import annotations

from pathlib import Path


FP = Path(
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/"
    "ENHANCED_ALERT_SYSTEM_BLUEPRINT.md"
)


PAIRS: list[tuple[str, str]] = [
    ("### 1.1 业务需?", "### 1.1 业务需求"),
    ("### 1.2 技术目?", "### 1.2 技术目标"),
    ("?告警渠道单一", "告警渠道单一"),
    ("?告警噪音?", "告警噪音"),
    ("?缺少告警聚合和抑?", "缺少告警聚合和抑制"),
    ("?多渠道告警（邮件、短信、Slack、Webhook?", "多渠道告警（邮件、短信、Slack、Webhook）"),
    ("?告警聚合和抑?", "告警聚合和抑制"),
    ("?告警趋势分析", "告警趋势分析"),
    ("| 指标 | 目指标| 说明 |", "| 指标 | 目标值 | 说明 |"),
    ("告警覆盖?*", "告警覆盖率"),
    ("告警聚合准确?*", "告警聚合准确率"),
    ("?5%", "95%"),
    ("?0%", "90%"),
    ("### 3.1 告警聚合?(AlertAggregator)", "### 3.1 告警聚合（AlertAggregator）"),
    ("\"\"\"告警聚合?\"\"", "\"\"\"告警聚合器\"\"\""),
    ("时间（秒?", "时间（秒）"),
    ("聚合间隔（秒?", "聚合间隔（秒）"),
    ("生成聚合?", "生成聚合键"),
    ("判断是否应该发送聚合告?", "判断是否应该发送聚合告警"),
    ("bool: 是否应该?", "bool: 是否应该发送"),
    ("时?        time_since_first", "        time_since_first"),
    ("检查聚合间?", "检查聚合间隔"),
    ("### 3.2 告警抑制?(AlertInhibitor)", "### 3.2 告警抑制（AlertInhibitor）"),
    ("\"\"\"告警抑制?\"\"", "\"\"\"告警抑制器\"\"\""),
    ("### 3.3 多渠道通知?(MultiChannelNotifier)", "### 3.3 多渠道通知（MultiChannelNotifier）"),
    ("\"\"\"多渠道通知?\"\"", "\"\"\"多渠道通知器\"\"\""),
    ("初始化多渠道通知?", "初始化多渠道通知器"),
    ("收件人列?", "收件人列表"),
    ("使用SMTP发送邮?", "使用 SMTP 发送邮件"),
    ("使用Twilio API发送短?", "使用 Twilio API 发送短信"),
    ("发送短信失?", "发送短信失败："),
    ("各渠道发送结?", "各渠道发送结果"),
    ("#### Day 1-2: 告警聚合和抑?", "#### Day 1-2: 告警聚合和抑制"),
    ("告警分析和优?", "告警分析和优化"),
    ("多渠道通知?2.", "多渠道通知器\n2."),
    ("| 验收?| 验收标准 | 验收方法 |", "| 验收项 | 验收标准 | 验收方法 |"),
    ("| **告警覆盖率 | 95% | 功能测试 |", "| **告警覆盖率** | 95% | 功能测试 |"),
    ("| **告警聚合准确率 | 90% | 功能测试 |", "| **告警聚合准确率** | 90% | 功能测试 |"),
    ("| **告警响应时间** | <1分钟 | 性能测试 |", "| **告警响应时间** | <1分钟 | 性能测试 |"),
    ("**?*: ?正式", "**状态**: 正式"),
    ("维护?*", "维护团队"),
    ("ZephyrAlpha技术团?", "ZephyrAlpha 技术团队"),
]


def main() -> int:
    t = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = t
    for a, b in PAIRS:
        t = t.replace(a, b)
    t = t.replace("\n?\n", "\n\n").replace("- ?", "- ")
    if t != orig:
        if not t.endswith("\n"):
            t += "\n"
        FP.write_bytes(t.encode("utf-8-sig"))
        print("UPDATED")
    else:
        print("NO_CHANGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

