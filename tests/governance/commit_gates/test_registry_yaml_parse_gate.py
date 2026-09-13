# -*- coding: utf-8 -*-
# [A_test] module_id: MOD-GOV_registry_yaml_parse_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_registry_yaml_parse_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_registry_yaml_parse_gate — capability 注册表结构硬化门禁单测

覆盖：
- 合法注册表（exemptions 末位+creation_tokens list）放行
- 尾追悬挂（exemptions 后跟条目）解析炸 → 阻断
- di_seam_exemptions 缺失 → 阻断
- di_seam_exemptions 非末位 → 阻断
- 触发范围外 YAML → 放行（不误伤）
- staged 读取失败 → fail-open 放行
"""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
    _WATCH_FILE,
    make_registry_yaml_parse_gate,
)

VALID_YAML = """schema_version: 1.1.0
capabilities:
- capability_id: demo_a
creation_tokens:
- file: a.md
  token: tok-a
di_seam_exemptions: []
"""

DANGLING_YAML = """schema_version: 1.1.0
creation_tokens:
- file: a.md
  token: tok-a
di_seam_exemptions: []
- file: b.md
  token: tok-b
"""

MISSING_EXEMPTIONS_YAML = """schema_version: 1.1.0
creation_tokens:
- file: a.md
  token: tok-a
"""


class _FakeGateway:
    def __init__(self, staged: list[str], staged_content: str | None):
        self.project_root = "."
        self._staged = staged
        self._staged_content = staged_content

    def run_git(self, cmd: list[str]):
        if cmd[:3] == ["git", "diff", "--cached"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self._staged))
        if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
            if self._staged_content is None:
                return SimpleNamespace(returncode=1, stdout="")
            return SimpleNamespace(returncode=0, stdout=self._staged_content)
        raise AssertionError(f"unexpected git cmd: {cmd}")


def _run(staged: list[str], content: str | None):
    gate = make_registry_yaml_parse_gate()
    return gate.check(_FakeGateway(staged, content), [], session_id=None)


def test_valid_registry_passes():
    ok, msg = _run([_WATCH_FILE], VALID_YAML)
    assert ok, msg


def test_dangling_after_exemptions_blocks():
    ok, msg = _run([_WATCH_FILE], DANGLING_YAML)
    assert not ok
    assert "解析失败" in msg or "di_seam_exemptions" in msg
    assert "creation_tokens 列表尾" in msg  # 教学信息必附


def test_missing_exemptions_blocks():
    ok, msg = _run([_WATCH_FILE], MISSING_EXEMPTIONS_YAML)
    assert not ok
    assert "缺失" in msg


def test_exemptions_not_last_blocks():
    reordered = VALID_YAML.replace("di_seam_exemptions: []\n", "").rstrip("\n") + "\ndi_seam_exemptions: []\n"
    # 构造 exemptions 非末位：把 capabilities 放到 exemptions 之后
    text = "schema_version: 1.1.0\ndi_seam_exemptions: []\ncapabilities:\n- capability_id: demo_a\n"
    ok, msg = _run([_WATCH_FILE], text)
    assert not ok
    assert "末位" in msg
    assert reordered  # 生成物使用避免 lint 噪音


def test_unrelated_yaml_passes():
    ok, msg = _run(["docs/01_policies_and_standards/_registry/catalogs/other_registry.yaml"], "broken: [yaml")
    assert ok, msg


def test_read_failure_fail_open():
    ok, msg = _run([_WATCH_FILE], None)
    assert ok, msg
