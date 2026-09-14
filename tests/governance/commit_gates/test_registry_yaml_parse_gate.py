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
"""test_registry_yaml_parse_gate — 注册表结构硬化门禁单测

覆盖：
- 合法注册表（exemptions 末位+creation_tokens list）放行
- 尾追悬挂（exemptions 后跟条目）解析炸 → 阻断
- di_seam_exemptions 缺失 / 非末位 → 阻断
- 顶层根键重复（双 datasets 事故族，2026-09-15 件3 扩面）→ 阻断
- data_asset_registry watch 档（parse+根键唯一，无 exemptions 断言）
- 触发范围外 YAML → 放行（不误伤）
- staged 读取失败 → fail-open 放行
"""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
    _WATCH_FILES,
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


# ---------------------------------------------------------------------------
# 2026-09-15 件3 扩面：根键唯一断言 + data_asset_registry watch 档
# ---------------------------------------------------------------------------

_DATA_ASSET_FILE = "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"

_VALID_DATA_ASSET_YAML = """schema_version: '2.0'
registry_id: REG-DATA-001
datasets:
- dataset_id: DS-001
  entity_name: market_data.tick
jobs:
- job_id: JOB-001
"""

_DOUBLE_ROOT_YAML = """schema_version: '2.0'
registry_id: REG-DATA-001
datasets:
jobs:
- job_id: JOB-000
datasets:
- dataset_id: DS-001
  entity_name: market_data.tick
"""


def test_watch_table_contains_data_asset_registry():
    assert _DATA_ASSET_FILE in _WATCH_FILES
    assert _WATCH_FILES[_DATA_ASSET_FILE] == "data_asset_registry"
    assert _WATCH_FILES[_WATCH_FILE] == "capability_registry"


def test_duplicate_root_key_blocks_capability_registry():
    """双 creation_tokens 根键 → 阻断（PyYAML 静默取后者，节点树判重才抓得住）。"""
    dup = VALID_YAML + "creation_tokens:\n- file: z.md\n  token: tok-z\n"
    ok, msg = _run([_WATCH_FILE], dup)
    assert not ok
    assert "顶层根键重复" in msg
    assert "creation_tokens" in msg


def test_duplicate_root_key_blocks_data_asset_registry():
    """双 datasets 根键（L752/755 事故原样复现）→ 阻断。"""
    ok, msg = _run([_DATA_ASSET_FILE], _DOUBLE_ROOT_YAML)
    assert not ok
    assert "顶层根键重复" in msg
    assert "datasets" in msg


def test_valid_data_asset_registry_passes():
    ok, msg = _run([_DATA_ASSET_FILE], _VALID_DATA_ASSET_YAML)
    assert ok, msg  # 无 exemptions/creation_tokens 结构要求——该档只查 parse+根键唯一


def test_broken_data_asset_registry_blocks():
    ok, msg = _run([_DATA_ASSET_FILE], "datasets:\n  - [broken\n")
    assert not ok
    assert "解析失败" in msg


def test_both_watched_files_checked_in_one_pass():
    """同批 staged 两个 watch 文件各有问题 → 逐文件问题全列出（不短路）。"""
    ok, msg = _run([_WATCH_FILE, _DATA_ASSET_FILE], _DOUBLE_ROOT_YAML)
    assert not ok
    # _FakeGateway 单内容桩：两个文件读同一 staged 内容 → 双双命中根键重复
    assert msg.count("顶层根键重复") == 2
