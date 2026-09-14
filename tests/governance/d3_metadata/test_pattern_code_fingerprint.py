# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §pattern_code_fingerprint 测试
# [MODULE] tests.governance.d3_metadata.test_pattern_code_fingerprint
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.d3_metadata.pattern_code_fingerprint
# [CONSUMERS] 指纹扫描器质量守卫（门禁A/B/回滚/幂等）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp 副本（monkeypatch _REGISTRY，不碰生产注册表）
# [MODIFY-GUARD] 与 pattern_code_fingerprint.py 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pattern_code_fingerprint 扫描器测试（#ARCH-BREG-002 门禁A/B）。

含 2026-09-15 实弹回归：stale 偏移切片版 apply 在写后校验网兜住回滚（exit 1），
单趟块重建治本——回滚路径用例 + 多条目全落位用例固定该防线。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.pattern_code_fingerprint as pcf

_IMPL_V1 = '"""impl"""\n\n\ndef scan_candles(x):\n    return x\n'
_IMPL_V2 = '"""impl"""\n\n\ndef scan_candles(x):\n    return x * 2\n'

_REG_BODY = """ttl: permanent
entry_count: 2
chart_patterns:
  - pattern_id: "PAT-T-001"
    name: "Alpha"
    code_path: "impl/scanner.py"
    code_symbol: "impl/scanner.py::scan_candles"
    code_fingerprint: null
  - pattern_id: "PAT-T-002"
    name: "Beta"
    code_path: "impl/scanner.py"
    code_symbol: "impl/scanner.py::scan_candles"
    code_fingerprint: null
"""


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    reg = tmp_path / "chart_pattern_registry.yaml"
    impl_dir = tmp_path / "impl"
    impl_dir.mkdir()
    impl = impl_dir / "scanner.py"
    impl.write_text(_IMPL_V1, encoding="utf-8")
    monkeypatch.setattr(pcf, "_REGISTRY", reg)
    monkeypatch.setattr(pcf, "_REPO", tmp_path)
    reg.write_text(_REG_BODY, encoding="utf-8")
    return reg, impl


def test_module_fingerprint_stable_and_sensitive(lab):
    reg, impl = lab
    fp1 = pcf.module_fingerprint(impl)
    assert fp1.startswith("sha256:") and len(fp1) == len("sha256:") + 16
    impl.write_text(_IMPL_V2, encoding="utf-8")
    assert pcf.module_fingerprint(impl) != fp1, "实现改动必须改变指纹（门禁B 语义）"


def test_symbol_exists_gate_a(lab):
    reg, impl = lab
    assert pcf.symbol_exists(impl, "scan_candles")
    assert not pcf.symbol_exists(impl, "no_such_fn")


def test_parse_code_symbol_invalid(lab):
    with pytest.raises(ValueError):
        pcf.parse_code_symbol("no-anchor-path.py")


def test_scan_reports_unfilled(lab):
    findings, wanted = pcf.scan()
    assert len(wanted) == 2
    assert all("未回填" in f for f in findings)


def test_apply_backfills_all_and_idempotent(lab):
    reg, impl = lab
    assert pcf.apply_fingerprints() == 0
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    fps = {e["pattern_id"]: e["code_fingerprint"] for e in data["chart_patterns"]}
    assert all(v and v.startswith("sha256:") for v in fps.values())
    assert len(set(fps.values())) == 1  # 同锚点同指纹
    # 幂等：再跑零回填
    findings, wanted = pcf.scan()
    assert not findings
    assert pcf.apply_fingerprints() == 0


def test_apply_detects_drift_after_impl_change(lab):
    reg, impl = lab
    assert pcf.apply_fingerprints() == 0
    impl.write_text(_IMPL_V2, encoding="utf-8")  # 实现演进未回写指纹
    findings, wanted = pcf.scan()
    assert wanted and all("漂移" in f for f in findings)


def test_apply_rollback_on_partial_landing(lab, monkeypatch):
    """写后校验失败 → 回滚写前字节（实弹回归：stale 偏移事故防线固定）。"""
    reg, impl = lab
    pre = reg.read_bytes()
    # 让写后 parse 层面必败：monkeypatch scan 返回一个不存在于注册表的 pid
    monkeypatch.setattr(
        pcf, "scan", lambda: (["f"], {"PAT-GHOST-999": "sha256:deadbeefdeadbeef"})
    )
    assert pcf.apply_fingerprints() == 1
    assert reg.read_bytes() == pre, "自检失败必须回滚到写前字节"
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert data["entry_count"] == 2  # 结构未破坏
