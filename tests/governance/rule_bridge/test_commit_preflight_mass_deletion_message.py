# [MODULE] tests.governance.rule_bridge.test_commit_preflight_mass_deletion_message
# [DOMAIN] D_GOV_SCRIPTS
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/rule_bridge/test_commit_preflight_mass_deletion_message.py
# [TTL] permanent
"""R6（W7 红蓝）——预检 message 输入面回归（治 2026-09-18 判据错位盲区）。

锁内权威链的 REGISTRY-MASS-DELETION 判据读 commit message 里的
[allow-mass-deletion:理由] 标记，而预检此前不传 message：带合法标记的净删批
被预检假红硬拦（rc=8），同一批落地侧却放行。治本=run_preflight 收
commit_message 并转发 gate.check(kwargs)。本钉防三件事复发：
1. message 不再转发（输入面重新失明）；
2. 缺省不为空串（判据漂移）；
3. 违规提示不含标记指引（假红后 AI 无出路）。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.gov_enforcement.rule_bridge.commit_preflight import (
    PREFLIGHT_GATES,
    _ESCAPE_HINTS,
    run_preflight,
)


@dataclass
class _MessageSpySpec:
    gate_id: str = "REGISTRY-MASS-DELETION"
    passed: bool = True
    detail: str = "净删 3 行 > 阈值"
    priority: int = 100
    seen: dict = field(default_factory=dict)

    def check(self, gateway, files, **kwargs):  # noqa: ANN001
        self.seen = dict(kwargs)
        return self.passed, self.detail


class _FakeGateway:
    def __init__(self, root: object) -> None:
        self.project_root = root


def test_mass_deletion_gate_in_preflight_whitelist():
    """REGISTRY-MASS-DELETION 必须在预检白名单——否则本回归失去意义。"""
    assert "REGISTRY-MASS-DELETION" in set(PREFLIGHT_GATES)


def test_preflight_forwards_commit_message_to_gate(tmp_path):
    """治本核心：run_preflight 必须把 commit_message 转发进 gate.check kwargs。"""
    spec = _MessageSpySpec()
    msg = "chore(registry): 去重 [allow-mass-deletion:整表重生成账实修正]"
    run_preflight(
        _FakeGateway(tmp_path), ["docs/_registry/catalogs/x.yaml"], "s1",
        specs=[spec], commit_message=msg,
    )
    assert spec.seen.get("commit_message") == msg


def test_preflight_default_message_is_empty_string(tmp_path):
    """缺省调用=空串入参（无标记→标记豁免型 gate 应判红，不得读到 None 而短路）。"""
    spec = _MessageSpySpec()
    run_preflight(_FakeGateway(tmp_path), ["a.yaml"], "s1", specs=[spec])
    assert spec.seen.get("commit_message") == ""


def test_violation_report_teaches_marker_escape(tmp_path):
    """预检红的报告必须含 [allow-mass-deletion: 标记指引（防假红困死）。"""
    spec = _MessageSpySpec(passed=False)
    result = run_preflight(
        _FakeGateway(tmp_path), ["a.yaml"], "s1", specs=[spec], commit_message="oops 无标记",
    )
    assert result.blocking
    report = result.render_report("s1")
    assert "[allow-mass-deletion:" in report
    assert "预检已可读 message" in _ESCAPE_HINTS["REGISTRY-MASS-DELETION"]
