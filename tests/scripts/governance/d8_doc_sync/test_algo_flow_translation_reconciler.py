"""test_algo_flow_translation_reconciler.py — ALGO_FLOW 翻译漂移 reconciler 单测（#ARCH-69/70）。

覆盖 §4.16.4 两级引用语义：
- 整体引用：name_zh/intro 与 factor_registry 强对比，漂移进 findings
- 分量引用（registry 含"分量"/"component"标注）：只做存在性校验，文案差异不报
- 悬空引用（FCT 编号在注册表无条目）：存在性校验失败进 findings
- 无 FCT 编号节点（断点/未登记）：跳过不参与校验
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[4]
for _p in (
    str(_REPO_ROOT / "scripts" / "governance" / "d8_doc_sync"),
    str(_REPO_ROOT / "scripts" / "governance" / "_shared"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import algo_flow_translation_reconciler as rec  # noqa: E402
from code_algorithm_extractor import AlgoFlowData, AlgoFlowNode  # noqa: E402

_FCT_ENTRY = {
    "factor_id": "FCT-SENT-002",
    "name_zh": "炸板率+连板高度+涨停回封时间",
    "alpha_source": "三件套可量化",
}


def _make_feature_node(registry: str, name_zh: str = "连板高度评分", intro: str = "连板越多越强") -> AlgoFlowNode:
    return AlgoFlowNode(id="F1", layer="特征", name_zh=name_zh, intro=intro, registry=registry)


def _run_check(node: AlgoFlowNode, factors: dict) -> list[str]:
    """以构造节点跑 _check_module（mock 文件解析层），返回 findings。"""
    algo = AlgoFlowData(nodes=[node], edges=[])
    findings: list[str] = []
    with patch.object(rec, "_extract_algo_flow", return_value=(algo, "fake/module.py")):
        rec._check_module("fake/module.py", factors, {}, findings)
    return findings


class TestIsComponentRef:
    """分量引用标注判定。"""

    def test_component_zh_marker(self):
        assert rec._is_component_ref("factor_registry: 有FCT条目 FCT-SENT-002（分量：连板高度）")

    def test_component_en_marker(self):
        assert rec._is_component_ref("factor_registry: FCT-SENT-002 (component)")

    def test_full_ref_not_component(self):
        assert not rec._is_component_ref("factor_registry: 有FCT条目 FCT-SENT-002")

    def test_empty_or_none(self):
        assert not rec._is_component_ref("")
        assert not rec._is_component_ref(None)  # type: ignore[arg-type]


class TestTwoTierReference:
    """两级引用校验强度（§4.16.4）。"""

    def test_component_ref_skips_strong_compare(self):
        """分量引用：文案与 YAML 不同也不报（存在性校验已通过）。"""
        findings = _run_check(
            _make_feature_node("factor_registry: 有FCT条目 FCT-SENT-002（分量：连板高度）"),
            {"FCT-SENT-002": _FCT_ENTRY},
        )
        assert findings == []

    def test_full_ref_drift_reported(self):
        """整体引用：name_zh/intro 与 YAML 不一致 → 强对比报漂移（2 处）。"""
        findings = _run_check(
            _make_feature_node("factor_registry: 有FCT条目 FCT-SENT-002"),
            {"FCT-SENT-002": _FCT_ENTRY},
        )
        assert len(findings) == 2
        assert any("name_zh" in f for f in findings)
        assert any("alpha_source" in f for f in findings)

    def test_full_ref_consistent_is_clean(self):
        """整体引用且文案一致 → 无 findings。"""
        findings = _run_check(
            _make_feature_node(
                "factor_registry: 有FCT条目 FCT-SENT-002",
                name_zh="炸板率+连板高度+涨停回封时间",
                intro="三件套可量化",
            ),
            {"FCT-SENT-002": _FCT_ENTRY},
        )
        assert findings == []

    def test_dangling_fct_ref_reported(self):
        """FCT 编号无条目 → 悬空引用（整体/分量同级存在性校验）。"""
        findings = _run_check(
            _make_feature_node("factor_registry: 有FCT条目 FCT-SENT-999（分量：连板高度）"),
            {"FCT-SENT-002": _FCT_ENTRY},
        )
        assert len(findings) == 1
        assert "悬空引用" in findings[0]
        assert "FCT-SENT-999" in findings[0]

    def test_no_fct_marker_skipped(self):
        """registry 无 FCT 编号（断点节点"无FCT条目"）→ 跳过不参与校验。"""
        findings = _run_check(
            _make_feature_node("factor_registry: 无FCT条目"),
            {"FCT-SENT-002": _FCT_ENTRY},
        )
        assert findings == []


class TestFactoryPathReassign:
    """make_ 工厂 project_root 重设路径回归（2026-08-14 worker 环境导入失败实证）。

    病根：模块级 _GOV_SHARED_DIR 指向 scripts/governance/_shared（正确），
    但工厂重设分支漏改为 scripts/governance（旧值）——gateway/worker 环境
    必传 project_root → 重设覆盖 → extractor 导入失败 → reconcile 永远 warn。
    """

    def test_factory_reassign_keeps_shared_suffix(self):
        spec = rec.make_algo_flow_translation_reconciler(_REPO_ROOT)
        assert spec.gate_id == "GATE-ALGO-FLOW-TRANSLATION-DRIFT"
        assert rec._GOV_SHARED_DIR.name == "_shared", (
            f"工厂重设后 _GOV_SHARED_DIR 必须以 _shared 结尾，实际: {rec._GOV_SHARED_DIR}"
        )
        assert (rec._GOV_SHARED_DIR / "code_algorithm_extractor.py").exists()

    def test_extractor_importable_after_factory_reassign(self):
        """工厂重设后提取器必须可导入（worker/gateway 环境的真实路径）。"""
        rec.make_algo_flow_translation_reconciler(_REPO_ROOT)
        func = rec._get_extractor()
        assert callable(func)
