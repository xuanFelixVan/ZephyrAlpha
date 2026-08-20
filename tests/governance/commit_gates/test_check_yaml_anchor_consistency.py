# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_check_yaml_anchor_consistency
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d7_code.check_yaml_anchor_consistency
# [CONSUMERS] CI governance.yml; pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] smoke test 验证 check_yaml_anchor_consistency.py 能正确检测 P1/P2/P3 问题
# [MODIFY-GUARD] check_yaml_anchor_consistency.py（被测对象真源）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0=pass; 1=fail
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_check_yaml_anchor_consistency.py — YAML 治理锚定一致性扫描 smoke test.

验证 check_yaml_anchor_consistency.py 能正确检测四类问题：
  P1_LEGACY_A_CONFIG / P2_ANCHOR_BODY_MISMATCH / P3_MISSING_ANCHOR_BLOCK / P4_MISSING_BLUEPRINT
以及豁免第三方配置（grafana/prometheus/docker-compose）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "d7_code" / "check_yaml_anchor_consistency.py"


def _load_module():
    """动态加载脚本（避免包导入路径问题）."""
    spec = importlib.util.spec_from_file_location("check_yaml_anchor_consistency", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_yaml_anchor_consistency"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_classify_p1_legacy_a_config(tmp_path):
    """P1: 检测 [A_config] 遗留行."""
    mod = _load_module()
    f = tmp_path / "test.yaml"
    f.write_text(
        "# [A_config] module_id=CFG-test | layer=config | stability=stable\n"
        "# --- 治理锚定 ---\n"
        "# blueprint: CFG-test | x | §\n"
        "# module_id: CFG-test\n"
        "# stability: stable\n"
        "# safety_level: L\n"
        "# ai_autonomy: ai_modifiable\n"
        "# ttl: permanent\n"
        "# --- 治理锚定结束 ---\n"
        "module_id: CFG-test\n",
        encoding="utf-8",
    )
    result = mod.scan_file(f)
    problems = mod.classify(result)
    assert "P1_LEGACY_A_CONFIG" in problems


def test_classify_p2_anchor_body_mismatch(tmp_path):
    """P2: 检测锚定块与 body module_id 不一致."""
    mod = _load_module()
    f = tmp_path / "test.yaml"
    f.write_text(
        "# --- 治理锚定 ---\n"
        "# blueprint: MOD-A | x | §\n"
        "# module_id: MOD-A\n"
        "# stability: stable\n"
        "# safety_level: L\n"
        "# ai_autonomy: ai_modifiable\n"
        "# ttl: permanent\n"
        "# --- 治理锚定结束 ---\n"
        "module_id: MOD-B\n",
        encoding="utf-8",
    )
    result = mod.scan_file(f)
    problems = mod.classify(result)
    assert "P2_ANCHOR_BODY_MISMATCH" in problems


def test_classify_p3_missing_anchor_block(tmp_path):
    """P3: 检测有 body module_id 但缺锚定块."""
    mod = _load_module()
    f = tmp_path / "test.yaml"
    f.write_text("module_id: MOD-X\n", encoding="utf-8")
    result = mod.scan_file(f)
    problems = mod.classify(result)
    assert "P3_MISSING_ANCHOR_BLOCK" in problems


def test_classify_p4_missing_blueprint(tmp_path):
    """P4: 检测锚定块缺 blueprint 字段."""
    mod = _load_module()
    f = tmp_path / "test.yaml"
    f.write_text(
        "# --- 治理锚定 ---\n"
        "# module_id: MOD-Y\n"
        "# stability: stable\n"
        "# safety_level: L\n"
        "# ai_autonomy: ai_modifiable\n"
        "# ttl: permanent\n"
        "# --- 治理锚定结束 ---\n"
        "module_id: MOD-Y\n",
        encoding="utf-8",
    )
    result = mod.scan_file(f)
    problems = mod.classify(result)
    assert "P4_MISSING_BLUEPRINT" in problems


def test_classify_clean_file(tmp_path):
    """合规文件无问题."""
    mod = _load_module()
    f = tmp_path / "test.yaml"
    f.write_text(
        "# --- 治理锚定 ---\n"
        "# blueprint: MOD-Z | x | §\n"
        "# module_id: MOD-Z\n"
        "# stability: stable\n"
        "# safety_level: L\n"
        "# ai_autonomy: ai_modifiable\n"
        "# ttl: permanent\n"
        "# --- 治理锚定结束 ---\n"
        "module_id: MOD-Z\n",
        encoding="utf-8",
    )
    result = mod.scan_file(f)
    problems = mod.classify(result)
    assert problems == []


def test_exempt_grafana():
    """grafana 配置豁免."""
    mod = _load_module()
    assert mod._is_exempt("config/infra/grafana/dashboards/provider.yml")
    assert mod._is_exempt("config/infra/prometheus/prometheus.yml")
    assert mod._is_exempt("config/infra/docker-compose.override.example.yml")
    assert not mod._is_exempt("config/alert_rules.yaml")
