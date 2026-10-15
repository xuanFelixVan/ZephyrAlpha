# [TTL] permanent
"""st-perfz2-20261015 P0-1：共册解析缓存文本喂入口 + REGISTRY-YAML-PARSE 结构序降 warn 判别测试。

钉住五件不可回退的事：
- 文本喂入口命中：CREATE-GUARD（盘面路径键）先解析后，REGISTRY-YAML-PARSE 喂同一字节
  的 staged 文本必须**零 yaml.safe_load** 命中（全链一次解析）。
- 失效：盘面 mtime/size 变化后文本喂入口必须重解析（键失配不命中）。
- 不串台：staged≠盘面时只返回不回填——后续盘面读者（CREATE-GUARD）读到的是盘面字节
  的解析，绝不被 staged 数据毒化。
- 失败不缓存：语法错的 staged 文本不缓存，修复后真读。
- 分级：REGISTRY-YAML-PARSE 仅 yaml.safe_load 语法错误 fail-closed；结构序四类
  （非 mapping/根键重复/exemptions 末位/creation_tokens 非 list）降 warn 放行+审计；
  preflight_merge_terminal 判据零变化（merge 通道仍全量阻断）。
"""

from __future__ import annotations

import json
import os
from types import SimpleNamespace

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates import _capability_registry_io as crio
from zephyr.gov_enforcement.commit_gates import create_guard as cg
from zephyr.gov_enforcement.commit_gates import registry_yaml_parse_gate as rg

_WATCH = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"

_GOOD = (
    "schema_version: 1.1.0\n"
    "capabilities:\n  - capability_id: cap-x\n"
    "creation_tokens:\n  - file: a.py\n    token: t1\n"
    "di_seam_exemptions: []\n"
)


@pytest.fixture()
def fresh_cache(monkeypatch):
    monkeypatch.setattr(crio, "_PARSE_CACHE", {"key": None, "data": None, "text_sha256": None})


@pytest.fixture()
def reg_repo(tmp_path):
    """tmp 仓根：盘面册 + gateway 垫片（staged=盘面字节）。"""
    reg = tmp_path / _WATCH
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(_GOOD, encoding="utf-8")
    gw = SimpleNamespace(project_root=tmp_path)

    def run_git(cmd, cwd=None):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        c = list(cmd)
        if c[1] == "diff" and "--name-only" in c:
            _R.stdout = _WATCH
        elif c[1] == "show" and c[2].startswith(":"):
            rel = c[2][1:]
            _R.stdout = (tmp_path / rel).read_text(encoding="utf-8") if (tmp_path / rel).exists() else ""
        elif c[1] == "show" and c[2].startswith("HEAD:"):
            _R.returncode = 1  # 无 HEAD → A-12 lag fail-open
        return _R()

    gw.run_git = run_git
    return tmp_path, gw


def test_text_feeded_hit_after_disk_parse(reg_repo, fresh_cache, monkeypatch):
    """CREATE-GUARD 盘面解析后，同字节 staged 文本喂入=零 safe_load 命中（全链一次解析）。"""
    tmp_path, gw = reg_repo
    reg = tmp_path / _WATCH
    calls = {"n": 0}
    real = yaml.safe_load

    def counting(data):
        calls["n"] += 1
        return real(data)

    monkeypatch.setattr(yaml, "safe_load", counting)
    d1, err1 = cg._load_capability_registry(gw)
    assert err1 == "" and d1 is not None
    n_after_guard = calls["n"]
    data, err = crio.parse_registry_text_cached(reg, _GOOD)
    assert err is None and data is not None
    assert data is d1, "同字节必须命中 CREATE-GUARD 已填的共享条目（同一对象）"
    assert calls["n"] == n_after_guard, "文本喂入口命中不得再 safe_load"


def test_text_cache_invalidated_by_mtime(reg_repo, fresh_cache):
    tmp_path, _gw = reg_repo
    reg = tmp_path / _WATCH
    d1, e1 = crio.parse_registry_text_cached(reg, _GOOD)
    assert e1 is None and d1 is not None
    os.utime(reg, ns=(reg.stat().st_mtime_ns + 1_000_000,) * 2)  # 仅 mtime 变
    d2, e2 = crio.parse_registry_text_cached(reg, _GOOD)
    assert e2 is None and d2 is not None
    assert d2 is not d1, "盘面 mtime 变化后必须重解析（键失配）"


def test_staged_not_equal_disk_never_stored(reg_repo, fresh_cache):
    """staged≠盘面：只返回不回填——盘面读者不被 staged 数据毒化（防串台正题）。"""
    tmp_path, _gw = reg_repo
    reg = tmp_path / _WATCH
    staged_text = _GOOD + "# staged-only tail\n"
    d1, e1 = crio.parse_registry_text_cached(reg, staged_text)
    assert e1 is None and d1 is not None
    # 若被毒化，盘面字节喂入会命中 staged 的 data（同一对象）——必须不命中且真读盘面
    d2, e2 = crio.parse_registry_text_cached(reg, _GOOD)
    assert e2 is None and d2 is not None
    assert d2 is not d1, "staged 数据不得以盘面键入缓存（毒化盘面读者）"
    d3, _ = crio.parse_registry_text_cached(reg, _GOOD)
    assert d3 is d2, "盘面字节第二次喂入应命中（回填的必须是盘面字节）"


def test_parse_failure_not_cached(reg_repo, fresh_cache):
    tmp_path, _gw = reg_repo
    reg = tmp_path / _WATCH
    bad = "creation_tokens: [oops\n"
    d1, e1 = crio.parse_registry_text_cached(reg, bad)
    assert d1 is None and e1 is not None
    ok_text = _GOOD
    os.utime(reg, ns=(reg.stat().st_mtime_ns + 2_000_000,) * 2)  # 换键，模拟"修复后"
    reg.write_text(ok_text, encoding="utf-8")
    d2, e2 = crio.parse_registry_text_cached(reg, ok_text)
    assert e2 is None and d2 is not None, "解析失败不得缓存（修复后真读）"


class _GateStub(SimpleNamespace):
    pass


def _make_gate_gw(tmp_path, staged_text: str, name_only: str = _WATCH) -> SimpleNamespace:
    gw = SimpleNamespace(project_root=tmp_path)

    def run_git(cmd, cwd=None):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        c = list(cmd)
        if c[1] == "diff" and "--name-only" in c:
            _R.stdout = name_only
        elif c[1] == "show" and c[2].startswith(":"):
            rel = c[2][1:]
            _R.stdout = staged_text
        elif c[1] == "show" and c[2].startswith("HEAD:"):
            _R.returncode = 1
        return _R()

    gw.run_git = run_git
    return gw


def test_gate_syntax_error_still_blocks(tmp_path, fresh_cache):
    gate = rg.make_registry_yaml_parse_gate()
    gw = _make_gate_gw(tmp_path, "creation_tokens: [oops\n")
    ok, detail = gate.check(gw, [], session_id=None)
    assert ok is False
    assert "yaml.safe_load 解析失败" in detail


def test_gate_structural_order_downgraded_to_warn(tmp_path, fresh_cache):
    """结构序违规（exemptions 非末位/缺失）→ warn 放行；审计带 warn_issues。"""
    gate = rg.make_registry_yaml_parse_gate()
    bad_order = (
        "schema_version: 1.1.0\n"
        "di_seam_exemptions: []\n"
        "creation_tokens:\n  - file: a.py\n    token: t1\n"  # exemptions 不在末位
    )
    (tmp_path / _WATCH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _WATCH).write_text(bad_order, encoding="utf-8")
    gw = _make_gate_gw(tmp_path, bad_order)
    ok, detail = gate.check(gw, [], session_id=None)
    assert ok is True, f"结构序降 warn 应放行，实际阻断: {detail}"
    assert "di_seam_exemptions" in detail and "warn" in detail
    audit = tmp_path / ".runtime" / "gate_audit" / "registry_yaml_parse.jsonl"
    rows = [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert rows and rows[-1]["action"] == "pass"
    assert rows[-1].get("warn_issues"), "warn 必须入审计（warn_issues 字段）"


def test_gate_duplicate_root_keys_downgraded_to_warn(tmp_path, fresh_cache):
    gate = rg.make_registry_yaml_parse_gate()
    dups = "datasets: []\nother: 1\ndatasets: [1]\n"
    (tmp_path / _WATCH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _WATCH).write_text(dups, encoding="utf-8")
    gw = _make_gate_gw(
        tmp_path, dups, name_only="docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"
    )
    ok, detail = gate.check(gw, [], session_id=None)
    assert ok is True, f"根键重复降 warn 应放行: {detail}"
    assert "顶层根键重复" in detail


def test_preflight_merge_terminal_unchanged_full_blocking():
    """A-14 merge 通道补检判据零变化：结构序违规在 merge 通道仍入阻断清单。"""
    tree = "deadbeef" * 5
    target = "base1234" * 5

    def run_git(cmd):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        if cmd[0] == "merge-tree":
            _R.stdout = f"{tree}\n"
        elif cmd[0] == "diff":
            _R.stdout = f"{_WATCH}\n"
        elif cmd[0] == "show":
            _R.stdout = "schema_version: 1\nunexpected_top: 1\n"  # 结构序问题（exemptions 缺失）
        return _R()

    issues, state = rg.preflight_merge_terminal(run_git, target, "other")
    assert state == "checked"
    assert issues, "merge 通道仍全量阻断（判据零变化）"
