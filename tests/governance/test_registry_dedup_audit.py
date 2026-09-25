# [A_test] module_id: QCURE-HYGIENE-1-test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_registry_dedup_audit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest；PyYAML；scripts.governance.registry_dedup_audit（importlib 文件加载）
# [CONSUMERS] pytest 自动发现；QMine A2G 施工线验收回归尺
# [STARTUP] python -m pytest tests/governance/test_registry_dedup_audit.py -q
# [MATURITY] testing
# [INVARIANTS] 全 tmp_path 隔离（fixture 册全部落 tmp_path，绝不写生产 catalogs；生产册只读断言）；
#              四类报告（精确重复/真冲突/枚举违规/字段漂移）×身份键三形态（list/点分/dict）矩阵覆盖；
#              heal 核验失败必拒写；severity 精确映射表在此断言存证（P0→P0致命/P1→P1高/P2→P2中/P3→P3低）
# [MODIFY-GUARD] QCURE-HYGIENE-1 回归尺：身份键口径/heal 只删全等后至者/枚举胶连污染豁免任一漂移即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] task_bound
"""registry_dedup_audit 回归尺：四类报告 × heal-equal 净删语义的 tmp 隔离验证。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROD_ARCH_ISSUE = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"

# severity 精确映射表（QMine A2G 批次 D3 修复口径，存证于断言）
SEVERITY_MAP = {"P0": "P0致命", "P1": "P1高", "P2": "P2中", "P3": "P3低"}


def _load():
    spec = importlib.util.spec_from_file_location(
        "_registry_dedup_audit", REPO_ROOT / "scripts/governance/registry_dedup_audit.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def aud():
    return _load()


def _scan(aud, tmp_path: Path, name: str, text: str) -> dict:
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return aud.scan_catalog(f)


def _mk(catalogs: Path, name: str, text: str) -> Path:
    catalogs.mkdir(parents=True, exist_ok=True)
    f = catalogs / name
    f.write_text(text, encoding="utf-8")
    return f


BASE = """module_id: MOD-X
unique_key:
- id
entry_schema:
  status: str   # active/deprecated
entries:
- id: A
  status: active
- id: B
  status: deprecated
"""


class TestFourReports:
    def test_exact_dup_detected(self, aud, tmp_path):
        rpt = _scan(aud, tmp_path, "r.yaml", BASE + "- id: A\n  status: active\n")
        assert len(rpt["exact_dup"]) == 1
        assert rpt["exact_dup"][0]["count"] == 2 and rpt["conflicts"] == []

    def test_conflict_dumped_not_dup(self, aud, tmp_path):
        rpt = _scan(aud, tmp_path, "r.yaml", BASE + "- id: A\n  status: deprecated\n")
        assert rpt["exact_dup"] == [] and len(rpt["conflicts"]) == 1
        assert len(rpt["conflicts"][0]["entries"]) == 2  # 双条 dump

    def test_parse_fail_reported(self, aud, tmp_path):
        bad = BASE + "- id: G:" + chr(8) + "ackup\n"  # 0x08 脏字节（D1 同型）
        rpt = _scan(aud, tmp_path, "bad.yaml", bad)
        assert rpt["parse_fail"] and "unacceptable character" in rpt["parse_fail"]

    def test_enum_violation_and_glue_skip(self, aud, tmp_path):
        text = """module_id: MOD-E
entry_schema:
  status: str   # active/deprecated
  algorithm_status: str   # quantized已量化/pending_backtest待回测
entries:
- id: A
  status: paused
  algorithm_status: quantized
"""
        rpt = _scan(aud, tmp_path, "e.yaml", text)
        assert rpt["enum_violations"] == {"entries.status": {"paused": 1}}  # 胶连字段豁免
        assert rpt["enum_violations"].get("entries.algorithm_status") is None

    def test_drift_pair_detected(self, aud, tmp_path):
        text = """module_id: MOD-D
entries:
- id: A
  created: '2026-01-01'
  created_at: '2026-01-02'
"""
        rpt = _scan(aud, tmp_path, "d.yaml", text)
        assert any(p["fields"] == ["created", "created_at"] for p in rpt["drift_pairs"])

    def test_identity_key_three_forms(self, aud, tmp_path):
        dotted = """module_id: M
unique_key:
- files.path
files:
- path: a
- path: a
"""
        dicted = """module_id: M
unique_key:
  files: [path]
files:
- path: a
- path: a
"""
        for i, text in enumerate((dotted, dicted)):
            rpt = _scan(aud, tmp_path, f"k{i}.yaml", text)
            assert len(rpt["exact_dup"]) == 1, f"form {i} 应按声明键识别重复"

    def test_scalar_container_dup(self, aud, tmp_path):
        text = "exempt_module_ids:\n- MOD-GOV_AUDIT\n- MOD-OTHER\n- MOD-GOV_AUDIT\n"
        rpt = _scan(aud, tmp_path, "s.yaml", text)
        assert rpt["exact_dup"] == [{"container": "exempt_module_ids", "key": ["MOD-GOV_AUDIT"], "count": 2}]


class TestHealEqual:
    def test_heal_removes_later_equal_block_only(self, aud, tmp_path):
        f = _mk(tmp_path, "h.yaml", BASE + "- id: A\n  status: active\n")
        ok, n = aud.heal_equal(f)
        assert ok and n == 1
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert [e["id"] for e in doc["entries"]] == ["A", "B"]  # 保留首条
        assert aud.scan_catalog(f)["exact_dup"] == []  # 复扫干净

    def test_heal_scalar_container(self, aud, tmp_path):
        f = _mk(tmp_path, "s.yaml", "exempt_module_ids:\n- MOD-A\n- MOD-A\n- MOD-A\n")
        ok, n = aud.heal_equal(f)
        assert ok and n == 2
        assert yaml.safe_load(f.read_text(encoding="utf-8"))["exempt_module_ids"] == ["MOD-A"]

    def test_heal_refuses_conflict_and_unparsable(self, aud, tmp_path):
        fc = _mk(tmp_path, "c.yaml", BASE + "- id: A\n  status: deprecated\n")
        assert aud.heal_equal(fc) == (False, 0)  # 真冲突不碰（撞号归 Owner 裁定）
        assert "status: deprecated" in fc.read_text(encoding="utf-8")  # 原文未动
        fb = _mk(tmp_path, "b.yaml", BASE + "- id: G:" + chr(8) + "ackup\n")
        assert aud.heal_equal(fb) == (False, 0)  # 解析失败册不 heal

    def test_cli_heal_end_to_end(self, aud, tmp_path, capsys):
        _mk(tmp_path, "h.yaml", BASE + "- id: A\n  status: active\n")
        assert aud.main(["--catalogs", str(tmp_path), "--heal-equal"]) == 0
        assert "HEALED" in capsys.readouterr().out

    def test_cli_missing_dir_exit_1(self, aud, tmp_path):
        assert aud.main(["--catalogs", str(tmp_path / "nope")]) == 1


class TestProductionDataReadOnly:
    """生产册只读断言（A2G 批次修复口径的回归尺；绝不写生产路径）。"""

    def test_severity_map_documented(self):
        assert SEVERITY_MAP == {"P0": "P0致命", "P1": "P1高", "P2": "P2中", "P3": "P3低"}

    @pytest.mark.skipif(not PROD_ARCH_ISSUE.exists(), reason="生产册不在仓")
    def test_no_bare_severity_left(self):
        doc = yaml.safe_load(PROD_ARCH_ISSUE.read_text(encoding="utf-8"))
        sevs = [e.get("severity") for e in doc["entries"]]
        assert not [s for s in sevs if s in SEVERITY_MAP], "裸 P0/P1/P2/P3 应已全部精确映射"

    @pytest.mark.skipif(not PROD_ARCH_ISSUE.exists(), reason="生产册不在仓")
    def test_ssot_drift_issue_registered(self):
        doc = yaml.safe_load(PROD_ARCH_ISSUE.read_text(encoding="utf-8"))
        hits = [e for e in doc["entries"] if e.get("issue_id") == "#ARCH-AGENTS-SSOT-DRIFT-001"]
        assert len(hits) == 1
        e = hits[0]
        assert e["severity"] == "P2中" and e["status"] == "in_progress"
        assert e["created"] == e["last_updated"] == "2026-09-25"
        assert e["owner"] == "st-qmine-20260925 总包授权" and e["impact"] == ["AGENTS.md"]
