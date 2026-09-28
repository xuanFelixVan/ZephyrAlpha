# [A_test] module_id: MOD-TRADING-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TRADING-013 | docs/03_modules/_domain_trading/blueprint.md | §
# [MODULE] tests.trading.test_tdm_false_auto_census
# [DOMAIN] D_TRADING
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_tdm_false_auto_census.py — TDM「标 auto 但生产零调用方」普查器（M7-BF-1③ 的可复算腿）。

为什么不是直接把 `TDM-E-L4-13` 的 `ai_autonomy` 改成 `manual`（2026-09-26 实测）：
`ai_autonomy` 是**宪章 B-007 五档实盘治理阶梯**（shadow/paper/pilot/daily_review/auto，
见 docs/01_policies_and_standards/sop/trading_decision_map_sop/
trading_decision_map_layering_policy.md §2.2.1），词表真源在 `decision_map.py::_AI_AUTONOMY`。
把 `manual` 写进 YAML 后跑校验器实测＝**R15 硬错误 1 条**（基线 error=0，改后 error=1：
`ai_autonomy 非法: manual`），要落地必须同时扩档（代码常量＋SOP 阶梯表＋宪章 B-007 文本），
那是"词表/判据变更"＝Owner 门位，施工车道今夜不自裁（92 册 §1.5/§1.6）。

所以本件落的是**没有争议的半边**：让"谎标注"从背出来的口头说法变成机器可复算的普查结果，
并钉死两件事——
  1. `TDM-E-L4-13` 的 `auto` 目前**无生产执行者背书**（承载件 three_way_reconciliation.py
     在 src/+scripts/ 的非自身引用为 0），该事实必须持续可复算；
  2. 五档阶梯词表不得被悄悄扩档（谁动 `_AI_AUTONOMY`，必须与 SOP 表＋宪章同批，否则红）。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from zephyr.trading.decision_map import _AI_AUTONOMY, load_decision_map

# DEFECT-4（2026-09-28 st-zcloseout 收口，owner=域会话）：decision map 317MB +
# 每 auto 节点全量重扫 44MB 语料，本机实测 234.21s（3/3 PASSED，900s 预算下），
# 超全局 pytest-timeout 120s 默认预算必被杀。非无限挂、非断言红——具名 timeout
# 覆盖到 240s（治本方向：语料读一次共享/按文件懒扫，留待域会话另批）。
pytestmark = pytest.mark.timeout(240)

_ROOT = Path(__file__).resolve().parents[2]
_MAP_PATH = _ROOT / "config" / "trading_decision_map.yaml"

#: 宪章 B-007 / SOP §2.2.1 的五档阶梯（扩档=词表变更，须与宪章+SOP 同批，Owner 门位）
_CHARTER_LADDER = frozenset({"shadow", "paper", "pilot", "daily_review", "auto"})

#: 本案卷点名的假 auto 节点（MOD-TRADING-013 三方对账引擎）
_FALSE_AUTO_NODE = "TDM-E-L4-13"


def _scanned_sources() -> list[Path]:
    files: list[Path] = []
    for pkg in ("src", "scripts"):
        files.extend(p for p in (_ROOT / pkg).rglob("*.py") if "__pycache__" not in p.parts)
    return files


def _production_ref_count(dotted: str, texts: dict[Path, str], self_path: str) -> int:
    """src/+scripts/ 中对该模块的**非自身**引用数（import 或 dotted 字符串皆计入）。"""
    leaf = dotted.rsplit(".", 1)[-1]
    pat = re.compile(rf"\b{re.escape(leaf)}\b")
    hits = 0
    for path, text in texts.items():
        rel = path.relative_to(_ROOT).as_posix()
        if rel == self_path:
            continue
        if pat.search(text):
            hits += 1
    return hits


def _false_auto_nodes() -> dict[str, int]:
    dm = load_decision_map(_MAP_PATH)
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in _scanned_sources()}
    out: dict[str, int] = {}
    for node in dm.nodes:
        if node.ai_autonomy != "auto" or not node.module_ref:
            continue
        rel = node.module_ref.replace("\\", "/")
        if not rel.startswith("src/") and not rel.startswith("scripts/"):
            continue
        dotted = rel.removesuffix(".py").replace("/", ".")
        if dotted.startswith("src."):
            dotted = dotted[len("src.") :]
        refs = _production_ref_count(dotted, texts, rel)
        if refs == 0:
            out[node.node_id] = 0
    return out


class TestFalseAutoCensus:
    def test_charter_ladder_is_not_silently_extended(self):
        """五档阶梯词表＝宪章 B-007 真源的镜像；扩档必须与 SOP 表＋宪章同批。"""
        assert _AI_AUTONOMY == _CHARTER_LADDER, (
            f"ai_autonomy 词表已变更（实测={sorted(_AI_AUTONOMY)}）——"
            "同步 trading_decision_map_layering_policy.md §2.2.1 与宪章 B-007 后方可放行"
        )

    def test_named_node_has_unbacked_auto_label(self):
        """TDM-E-L4-13 标 auto 而承载件生产零引用＝该标注无执行者背书（本案卷主张的可复算版）。"""
        census = _false_auto_nodes()
        assert _FALSE_AUTO_NODE in census, f"{_FALSE_AUTO_NODE} 不在零调用方普查结果里：{sorted(census)}"

    def test_census_is_reportable_and_bounded(self):
        """普查器自身必须可复算且有界（清单失控=又一处"账面与世界的漂移"）。"""
        census = _false_auto_nodes()
        assert len(census) >= 1
        assert len(census) < 60, f"零调用方 auto 标注节点已达 {len(census)} 个，须重开环节普查"
