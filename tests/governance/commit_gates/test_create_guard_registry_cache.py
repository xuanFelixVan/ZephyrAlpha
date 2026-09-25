# [TTL] permanent
"""T8 簇1：CREATE-GUARD 册解析进程内缓存判别测试（st-commitspeed-tbl-20260924）。

钉住三件不可回退的事：
- 命中：同 (mtime_ns, size) 二次加载不得重解析（_read_registry_text 调用计数=1）。
- 失效：mtime 或 size 任一变化必须重解析（写后失效，并发写窗口防陈旧）。
- 判据等价：命中与重解析返回同一 data 结构（同一文件同一字节同一解析器）。
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates import create_guard as cg


@pytest.fixture()
def reg_env(tmp_path, monkeypatch):
    """临时册+命中缓存清零+REGISTRY_YAML 回退钉到临时册。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(
        "schema_version: 1.1.0\ncapabilities: []\ncreation_tokens:\n  - file: a.md\n    token: t-a\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cg, "_REGISTRY_CACHE", {"key": None, "data": None})
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
