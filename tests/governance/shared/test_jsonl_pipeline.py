# [A_test] module_id: MOD-GOV_jsonl_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-292 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_jsonl_pipeline
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-292 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""端到端验证 JSONL 管道 — BaseAuditScript → stdout → run_all 解析"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

GOV_DIR = REPO_ROOT / "scripts" / "governance"


def _test_script_path() -> Path:
    return GOV_DIR / "_test_jsonl_verify.py"


def setup_module():
    content = '''"""临时验证脚本 — 继承 BaseAuditScript 输出 JSONL"""
from __future__ import annotations
import sys
from pathlib import Path
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.base import BaseAuditScript
try:
    from zephyr.infrastructure.script_system.finding import Dimension, Severity
except ImportError:
    class Dimension: D7 = "D7"; label = "测试"
    class Severity: MEDIUM = "MEDIUM"

class TestChecker(BaseAuditScript):
    def check(self) -> None:
        self.add_finding(
            dimension=Dimension.D7,
            severity=Severity.MEDIUM,
            target_file="tests/governance/test_jsonl_pipeline.py",
            description="测试 Finding Schema 管道",
            category="Phase1 验证",
        )

if __name__ == "__main__":
    TestChecker().run()
'''
    _test_script_path().write_text(content, encoding="utf-8")


def teardown_module():
    p = _test_script_path()
    if p.exists():
        p.unlink()


def test_base_script_outputs_jsonl():
    r = subprocess.run(
        [sys.executable, str(_test_script_path()), "--warn-only", "--jsonl"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"exit={r.returncode}, stderr={r.stderr[:200]}"
    assert r.stdout.strip(), "JSONL 输出为空"

    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    assert len(lines) == 1, f"应有 1 条 Finding，实际 {len(lines)}"

    data = json.loads(lines[0])
    assert data["description"] == "测试 Finding Schema 管道"
    assert data["severity"] == "MEDIUM"
    assert "finding_id" in data


def test_run_all_imports_jsonl_parser():
    sys.path.insert(0, str(GOV_DIR))
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from run_all import _parse_jsonl_to_findings, _try_jsonl_run

    assert callable(_parse_jsonl_to_findings)
    assert callable(_try_jsonl_run)
    print("  run_all.py JSONL API 导入正常")


def test_jsonl_parse_roundtrip():
    sys.path.insert(0, str(GOV_DIR))
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from run_all import Dimension, _parse_jsonl_to_findings

    sample = json.dumps(
        {
            "finding_id": "FIND-D7-20260504-test1234",
            "dimension": "D7",
            "severity": "HIGH",
            "category": "代码质量",
            "target": {"file_path": "src/test.py", "line_range": "10-20"},
            "description": "测试解析",
            "evidence": "raw line",
            "remediation": {"priority": "P1"},
            "timestamp": "2026-05-04T00:00:00Z",
        },
        ensure_ascii=False,
    )

    parsed = _parse_jsonl_to_findings(sample + "\n", [Dimension.D7], "test.py")
    assert len(parsed) == 1, f"解析结果为空，sample={sample[:100]}"
    assert parsed[0].description == "测试解析"
    assert parsed[0].severity.value == "HIGH"
    assert parsed[0].finding_id == "FIND-D7-20260504-test1234"


def test_jsonl_fallback_on_invalid():
    sys.path.insert(0, str(GOV_DIR))
    from run_all import Dimension, _parse_jsonl_to_findings

    parsed = _parse_jsonl_to_findings("不是 JSON\n", [Dimension.D7], "test.py")
    assert len(parsed) == 0

    parsed = _parse_jsonl_to_findings("", [Dimension.D7], "test.py")
    assert len(parsed) == 0
