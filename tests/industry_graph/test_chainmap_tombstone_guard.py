# -*- coding: utf-8 -*-
"""chainmap 墓碑节点过滤守卫测试（Owner 2026-09-10："整个产业链全景图都不要再出现这种情况"）。

事故：cluster/search/catalyst 端点漏过滤墓碑节点（'（已并入'=已合并历史快照，落位已迁空），
显示层剥离长名后墓碑卡与实体卡无法分辨（军工簇实测"航空发动机×6"实为 2 实体+4 墓碑）。
守卫：api_server.py 中所有 `FROM ig_node` 查询必须伴随墓碑过滤串——源码级机械扫描，
新增查询漏过滤 = commit 红（对标 NO-BARE-SQL 的源码模式门禁）。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
API = REPO / "src" / "zephyr" / "frontend" / "dashboard" / "api_server.py"
TOMB = "已并入"


def test_all_ig_node_queries_filter_tombstones():
    src = API.read_text(encoding="utf-8")
    # 逐行扫描 FROM ig_node 的查询行；SQL 常量与内联 execute 同检。
    # 允许的过滤形态：NOT LIKE '%（已并入%'（直写或 %% 转义两种）
    lines = src.splitlines()
    offenders = []
    for i, ln in enumerate(lines, 1):
        if not re.search(r"FROM ig_node", ln):
            continue
        # 该行或其后 2 行（多行 SQL 字符串拼接）内须含墓碑过滤
        window = "\n".join(lines[i - 1 : i + 2])
        if TOMB not in window:
            offenders.append(f"L{i}: {ln.strip()[:110]}")
    assert not offenders, (
        "ig_node 查询缺墓碑过滤（查询侧纪律：墓碑=已合并历史快照，S8/S21/S24/api 同口径过滤）:\n"
        + "\n".join(offenders)
    )


def test_tombstone_filter_uses_escaped_percent():
    """psycopg2 参数化里 LIKE 通配符必须写 %%（裸 % = 占位符冲突，tuple index out of range 事故）。"""
    src = API.read_text(encoding="utf-8")
    for i, ln in enumerate(lines := src.splitlines(), 1):
        # 裸 '%（已并入%'（单 %）= 违规；'%%（已并入%%'（双 %）= 合规
        if re.search(r"(?<!%)'%（已并入", ln) or re.search(r"已并入%(?!%)'", ln):
            assert False, f"L{i} LIKE 通配符未转义（须 %%）: {ln.strip()[:110]}"
    assert lines  # 非空读入防呆
