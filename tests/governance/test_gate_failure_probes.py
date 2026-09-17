# [BLUEPRINT] MOD-GATE_ENGINE | tests/governance/test_gate_failure_probes.py
# [MODULE] tests.governance.test_gate_failure_probes
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate; zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate; zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate; zephyr.gov_enforcement.commit_gates._diff_helpers
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] S12-E8 门禁失效探针（S4-F7 收口）：
#   探针1 注入 git diff 故障（run_git rc≠0/抛异常）→ 内容扫描型门禁 fail-open
#         且必须 warn 留痕（红=故障注入后无任何 warn 记录=静默失效）；
#   探针2 注入 YAML 破损 → REGISTRY-YAML-PARSE 只拦该表、不连坐（S18 R-09 判据）。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败（xfail strict 件=已发现真红，修复后必须摘除标记）
# [TESTS] pytest tests/governance/test_gate_failure_probes.py
# [TTL] permanent
"""S12-E8 门禁失效探针。fake gateway 不落真仓库（project_root=tmp_path，审计写隔离）。"""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from zephyr.gov_enforcement.commit_gates import _diff_helpers
from zephyr.gov_enforcement.commit_gates import registry_yaml_parse_gate as ryp
from zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate import (
    make_datetime_now_forbidden_gate,
)
from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
    make_registry_yaml_parse_gate,
)
from zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate import (
    make_unsafe_dict_spread_gate,
)

_WATCH_CAP = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_WATCH_DAT = "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"


class _FakeGateway:
    """最小 gateway 替身：run_git 可注入 rc≠0/异常；审计面指向 tmp_path（隔离生产 .runtime）。"""

    def __init__(self, project_root, *, rc: int = 0, stdout: str = "", exc: Exception | None = None):
        self.project_root = str(project_root)
        self._rc = rc
        self._stdout = stdout
        self._exc = exc
        self._registry = None  # own-scope 退化为 files-only（fail-open 红线语义）

    def run_git(self, args):
        if self._exc is not None:
            raise self._exc
        return SimpleNamespace(returncode=self._rc, stdout=self._stdout, stderr="git injected failure")


# ── 探针 1：git diff 故障注入 → fail-open + warn 留痕 ────────────────────────


def test_probe_diff_helpers_warns_on_git_rc_nonzero(caplog, tmp_path):
    """内容扫描型 gate 共享入口 _get_staged_py_files：rc≠0 → 空集 + WARNING 留痕。"""
    gw = _FakeGateway(tmp_path, rc=128)
    with caplog.at_level(logging.WARNING, logger="_diff_helpers"):
        out = _diff_helpers._get_staged_py_files(gw, gate_name="PROBE")
    assert out == []  # fail-open 契约
    assert any("fail-open" in r.message and "PROBE" in r.message for r in caplog.records), (
        "git rc≠0 后无任何 warn 记录=静默失效（红）"
    )


@pytest.mark.parametrize("make_gate", [make_datetime_now_forbidden_gate, make_unsafe_dict_spread_gate])
def test_probe_content_scan_gates_warn_on_git_failure(make_gate, caplog, tmp_path):
    """内容扫描型门禁本体：git 故障 → (True,'') fail-open 且 WARNING 留痕。"""
    spec = make_gate()
    gw = _FakeGateway(tmp_path, rc=1)
    with caplog.at_level(logging.WARNING):
        passed, msg = spec.check(gw, ["src/zephyr/x.py"], session_id=None)
    assert (passed, msg) == (True, ""), "fail-open 红线契约漂移"
    assert any(r.levelno >= logging.WARNING for r in caplog.records), (
        f"{spec.gate_id}: git 故障注入后无 warn 记录=静默失效（红）"
    )


def test_probe_registry_yaml_parse_warns_on_git_exception(caplog, tmp_path):
    """REGISTRY-YAML-PARSE 异常分支有 warning 留痕（钉住既有健康面）。"""
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, exc=RuntimeError("injected git boom"))
    with caplog.at_level(logging.WARNING):
        passed, _msg = spec.check(gw, [], session_id=None)
    assert passed is True
    assert any("fail-open" in r.message for r in caplog.records)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "S12-E8 真红发现：REGISTRY-YAML-PARSE 的 git rc≠0 分支静默放行"
        "（registry_yaml_parse_gate.py:184 `return True, ''` 无 logger.warning，"
        "同文件仅异常分支留痕）——修复=rc≠0 分支补 warning 后本件 XPASS(strict) 强制摘除"
    ),
)
def test_probe_registry_yaml_parse_rc_nonzero_must_warn(caplog, tmp_path):
    """注入反例：git diff rc≠0 → REGISTRY-YAML-PARSE 必须 warn 留痕。

    红=静默失效。当前现状=静默（见 xfail reason）——本件是"注入反例必须变红"
    纪律的实证锚：它若绿，说明静默通路已修。
    """
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, rc=1)
    with caplog.at_level(logging.WARNING):
        passed, _msg = spec.check(gw, [], session_id=None)
    assert passed is True  # fail-open 设计契约不变
    assert any(r.levelno >= logging.WARNING for r in caplog.records), (
        "REGISTRY-YAML-PARSE git rc≠0 静默放行——S4-F7 静默失效通路实证"
    )


# ── 探针 2：YAML 破损注入 → 只拦该表、不连坐 ─────────────────────────────────

_BROKEN_YAML = "schema_version: [1,\n  bad_indent: : :\n"  # safe_load 必炸
_VALID_CAP_YAML = (
    "schema_version: 1\ncapabilities: []\ncreation_tokens: []\ndi_seam_exemptions: []\n"
)


def test_probe_broken_yaml_blocks_only_that_registry(monkeypatch, tmp_path):
    """破损 YAML 注入 watched 注册表 → 阻断且报错只点名该表（不连坐另一张 watch 表）。"""
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, rc=0, stdout=_WATCH_CAP + "\n")
    monkeypatch.setattr(ryp, "_read_staged_file", lambda _gw, _f: _BROKEN_YAML)
    passed, msg = spec.check(gw, [_WATCH_CAP], session_id=None)
    assert passed is False, "破损 YAML 未拦截=门禁失效（红）"
    assert "REGISTRY-YAML-PARSE" in msg and _WATCH_CAP in msg
    assert _WATCH_DAT not in msg, "另一张 watch 表被点名=连坐"


def test_probe_broken_yaml_in_nonwatched_file_not_blocked(monkeypatch, tmp_path):
    """非 watch 表的 YAML 破损 → 不拦（紧范围不加宽，连坐防护钉）。"""
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, rc=0, stdout="docs/_working/some_random.yaml\n")
    monkeypatch.setattr(ryp, "_read_staged_file", lambda _gw, _f: _BROKEN_YAML)
    passed, msg = spec.check(gw, ["docs/_working/some_random.yaml"], session_id=None)
    assert (passed, msg) == (True, ""), "非 watch 表破损被拦=连坐（红）"


def test_probe_duplicate_root_keys_detected(monkeypatch, tmp_path):
    """根键重复注入（PyYAML 静默取后者盲区）→ data_asset 档阻断。"""
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, rc=0, stdout=_WATCH_DAT + "\n")
    monkeypatch.setattr(ryp, "_read_staged_file", lambda _gw, _f: "datasets: []\ndatasets:\n  - a\n")
    passed, msg = spec.check(gw, [_WATCH_DAT], session_id=None)
    assert passed is False and "根键重复" in msg


def test_probe_valid_capability_registry_passes(monkeypatch, tmp_path):
    """阳性对照：结构合法的 capability 注册表 staged → 放行（防探针全盘误红）。"""
    spec = make_registry_yaml_parse_gate()
    gw = _FakeGateway(tmp_path, rc=0, stdout=_WATCH_CAP + "\n")
    monkeypatch.setattr(ryp, "_read_staged_file", lambda _gw, _f: _VALID_CAP_YAML)
    passed, msg = spec.check(gw, [_WATCH_CAP], session_id=None)
    assert (passed, msg) == (True, "")
