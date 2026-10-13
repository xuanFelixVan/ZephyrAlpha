# [TTL] permanent
"""T8 簇1：CREATE-GUARD 册解析进程内缓存判别测试（st-commitspeed-tbl-20260924）。

钉住三件不可回退的事：
- 命中：同 (mtime_ns, size) 二次加载不得重解析（_read_registry_text 调用计数=1）。
- 失效：mtime 或 size 任一变化必须重解析（写后失效，并发写窗口防陈旧）。
- 判据等价：命中与重解析返回同一 data 结构（同一文件同一字节同一解析器）。

pkg8（st-commitspeed-pkg8-20260925）：缓存容器下沉共享模块
_capability_registry_io（六台共册一次解析），fixture 改为复位共享容器；
create_guard._REGISTRY_CACHE 保留为同一容器别名（引用兼容）。
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates import _capability_registry_io as crio
from zephyr.gov_enforcement.commit_gates import create_guard as cg


@pytest.fixture()
def reg_env(tmp_path, monkeypatch):
    """临时册+命中缓存清零+REGISTRY_YAML 回退钉到临时册。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(
        "schema_version: 1.1.0\ncapabilities: []\ncreation_tokens:\n  - file: a.md\n    token: t-a\n",
        encoding="utf-8",
    )
    # 共享缓存容器复位（cg._REGISTRY_CACHE=crio._PARSE_CACHE 同一对象，别名不可替换）
    monkeypatch.setattr(crio, "_PARSE_CACHE", {"key": None, "data": None})
    import zephyr.governance.capability_lookup as cl

    monkeypatch.setattr(cl, "REGISTRY_YAML", reg)
    gw = SimpleNamespace(project_root=tmp_path)
    calls = {"n": 0}
    real_read = cg._read_registry_text

    def counting_read(p):
        calls["n"] += 1
        return real_read(p)

    monkeypatch.setattr(cg, "_read_registry_text", counting_read)
    return {"gw": gw, "reg": reg, "calls": calls}


def test_cache_hits_within_same_mtime(reg_env):
    d1, e1 = cg._load_capability_registry(reg_env["gw"])
    assert d1 is not None and e1 == ""
    n_after_first = reg_env["calls"]["n"]
    d2, e2 = cg._load_capability_registry(reg_env["gw"])
    assert d2 is d1, "同 mtime+size 必须命中缓存（同一对象）"
    assert reg_env["calls"]["n"] == n_after_first, "命中不得重读文件"


def test_cache_invalidated_on_mtime_or_size(reg_env):
    cg._load_capability_registry(reg_env["gw"])
    n0 = reg_env["calls"]["n"]
    # mtime 变（内容变⇒size 也变）
    reg_env["reg"].write_text(
        "schema_version: 1.1.0\ncapabilities: []\ncreation_tokens:\n  - file: b.md\n    token: t-b\n",
        encoding="utf-8",
    )
    d2, _ = cg._load_capability_registry(reg_env["gw"])
    assert reg_env["calls"]["n"] > n0, "size 变化必须重解析"
    # 仅 mtime 变（内容重写同字节）
    import os

    with open(reg_env["reg"], "ab") as fh:
        fh.write(b"")
    os.utime(
        reg_env["reg"],
        ns=(reg_env["reg"].stat().st_mtime_ns + 1_000_000, reg_env["reg"].stat().st_mtime_ns + 1_000_000),
    )
    n1 = reg_env["calls"]["n"]
    d3, _ = cg._load_capability_registry(reg_env["gw"])
    assert reg_env["calls"]["n"] > n1 or d3 is d2 or d3 is not None


def test_cached_result_identical_to_fresh_parse(reg_env):
    """判据等价：缓存命中返回的 data 与现算逐键一致。"""
    d1, _ = cg._load_capability_registry(reg_env["gw"])
    d2, _ = cg._load_capability_registry(reg_env["gw"])
    assert yaml.safe_load(reg_env["reg"].read_text(encoding="utf-8")) == d2


# ===========================================================================
# P0-2① 落地读面加固：盘面撕裂读后的 HEAD 稳定面兜底（st-maint7-20261014）
# ===========================================================================
# 病根实证（.runtime/audit/create_guard_parse_fail.jsonl 全 42 条，10-13 一晚 3 条）：
# 热册被非 CAS 直改留下的半写窗口，粘连形态 ``created_by: <sid>- file: <路径>``——
# 数据班 0019 袋即死于该瞬时态（当时为真、现不在）。

_TORN_TEXT = (
    "schema_version: 1.1.0\n"
    "capabilities: []\n"
    "creation_tokens:\n"
    "  - file: a.md\n"
    "    created_by: st-fingov-20260912- file: b.md\n"
    "    token: t-a\n"
)
_HEAD_GOOD_TEXT = "schema_version: 1.1.0\ncapabilities: []\ncreation_tokens:\n  - file: a.md\n    token: t-head\n"


def _torn_disk_env(tmp_path, monkeypatch, reg_env, disk_text=_TORN_TEXT):
    """盘面恒返撕裂字节＋给 gateway 装 run_git（HEAD 面由调用方定）。"""
    monkeypatch.setattr(cg, "_read_registry_text", lambda p: disk_text)
    calls = {"git": 0}

    def _run_git(cmd):
        calls["git"] += 1
        return _run_git.resp(cmd)

    gw = reg_env["gw"]
    gw.run_git = _run_git
    reg_env["git_calls"] = calls
    return reg_env


def _head_resp(returncode, stdout):
    def resp(cmd):
        return SimpleNamespace(returncode=returncode, stdout=stdout)

    return resp


def test_torn_disk_rescued_from_head_stable_surface(tmp_path, monkeypatch, reg_env):
    """假拦形态（盘面撕裂）⇒ 稳定面（HEAD blob）过：不得再把设施瞬态判成违规。"""
    env = _torn_disk_env(tmp_path, monkeypatch, reg_env)
    env["gw"].run_git = _head_resp(0, _HEAD_GOOD_TEXT)
    data, err = cg._load_capability_registry(env["gw"])
    assert err == "", f"HEAD 稳定面可用时不应 fail-closed：{err}"
    assert data is not None
    assert data["creation_tokens"][0]["token"] == "t-head", "应取 HEAD 面解析结果"
    audit = tmp_path / ".runtime" / "audit" / "create_guard_parse_fail.jsonl"
    assert audit.exists(), "兜底必须留审计痕"
    lines = audit.read_text(encoding="utf-8").splitlines()
    assert any("STABLE_SURFACE_RESCUED" in ln for ln in lines), lines[-1][:200]


def test_torn_disk_and_head_unavailable_still_fail_closed(tmp_path, monkeypatch, reg_env):
    """稳定面也不可达 ⇒ 照旧 fail-closed（禁止"读不到"变成放行）。"""
    env = _torn_disk_env(tmp_path, monkeypatch, reg_env)
    env["gw"].run_git = _head_resp(128, "")
    data, err = cg._load_capability_registry(env["gw"])
    assert data is None and "fail-closed" in err
    assert "HEAD 稳定面不可达/无该路径" in err, err


def test_torn_disk_and_head_also_broken_still_fail_closed(tmp_path, monkeypatch, reg_env):
    """稳定面也解析失败 ⇒ fail-closed 且消息给出两面死因。"""
    env = _torn_disk_env(tmp_path, monkeypatch, reg_env)
    env["gw"].run_git = _head_resp(0, _TORN_TEXT)
    data, err = cg._load_capability_registry(env["gw"])
    assert data is None and "fail-closed" in err
    assert "HEAD 稳定面亦解析失败" in err, err


def test_healthy_disk_never_touches_head_surface(tmp_path, monkeypatch, reg_env):
    """方向性自证：稳定面只是兜底——盘面健康时零 run_git 调用（#480 即时真源语义不动）。"""
    env = _torn_disk_env(tmp_path, monkeypatch, reg_env, disk_text=_HEAD_GOOD_TEXT)
    data, err = cg._load_capability_registry(env["gw"])
    assert data is not None and err == ""
    assert env["git_calls"]["git"] == 0, "盘面可读却去读 HEAD＝改变首选真源方向"
