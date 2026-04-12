#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
定向治理补全：PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md

目标：
- 清理重复/异常 YAML 头（保留最完整那段）
- 高置信度修复“汉字?”断裂（标题/字段/常用短语）
"""

from __future__ import annotations

import re
from pathlib import Path


FP = Path("docs/01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md")


def keep_last_frontmatter(text: str) -> str:
    """
    该文件存在多段 frontmatter，保留最后一段（module_id: PROFESSIONAL_IMPLEMENTATION_001）
    """
    marker = "\nmodule_id: PROFESSIONAL_IMPLEMENTATION_001"
    idx = text.find(marker)
    if idx == -1:
        return text
    # 回溯到最近的 '---\n' 起点
    start = text.rfind("---\n", 0, idx)
    if start == -1:
        return text
    return text[start:]


PAIRS: list[tuple[str, str]] = [
    ("owner: 首席架构?", "owner: 首席架构师"),
    ("> **最后更?*:", "> **最后更新**:"),
    ("> **实施周期**: 10个月?0周）", "> **实施周期**: 10个月（约40周）"),
    ("## 📊 一、系统现状诊?", "## 📊 一、系统现状诊断"),
    ("### 1.1 设计文档状态评?", "### 1.1 设计文档状态评估"),
    ("### 1.2 代码实现状态评?", "### 1.2 代码实现状态评估"),
    ("**评估结果：优秀?5%完整?*", "**评估结果：优秀（95%完整）**"),
    ("**评估结果：严重滞后（?0%实现?*", "**评估结果：严重滞后（0%实现）**"),
    ("单**?", "说明："),
    ("三级时间框架架构?28行）", "三级时间框架架构（928行）"),
    ("策略引擎核心?427行）", "策略引擎核心（1427行）"),
    ("策略选择系统?011行）", "策略选择系统（1011行）"),
    ("组合优化系统?057行）", "组合优化系统（1057行）"),
    ("| **策略注册?*", "| **策略注册**"),
    ("| **策略加载?*", "| **策略加载**"),
    ("| **中观策略?*", "| **中观策略**"),
    ("| **微观执行?*", "| **微观执行**"),
    ("**核心风险识别**?", "**核心风险识别**:"),
    ("- **P0级风?*：", "- **P0级风险**："),
    ("- **P2级风?*：", "- **P2级风险**："),
    ("尚未启?", "尚未启动"),
    ("### 2.1 架构选择：三级时间框架融合架?", "### 2.1 架构选择：三级时间框架融合架构"),
    ("**核心理念**：时间框架分离原?", "**核心理念**：时间框架分离原则"),
]


def main() -> int:
    text = FP.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = text

    text = keep_last_frontmatter(text)
    # 去掉可能残留的 BOM 字符
    text = text.lstrip("\ufeff")

    for a, b in PAIRS:
        text = text.replace(a, b)

    # 清理明显的孤立行（表格残片）
    text = re.sub(r"(?m)^\\?\\|\\s*$", "", text)
    text = re.sub(r"(?m)^\\?\\*\\s*\\|", "|", text)

    if text != orig:
        if not text.endswith("\n"):
            text += "\n"
        FP.write_bytes(text.encode("utf-8-sig"))
        print("UPDATED")
    else:
        print("NO_CHANGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

