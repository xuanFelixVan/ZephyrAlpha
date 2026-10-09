# [TTL] permanent
"""T8 簇1：capability 册共享解析缓存判别测试（st-commitspeed-pkg8-20260925）。

钉住四件不可回退的事：
- 命中：同 (normcase 路径, mtime_ns, size) 二次加载不重读文件、返回同一对象。
- 失效：mtime/size 任一变化必须重解析；不同路径同 (mtime,size) 不得串台。
- 失败不缓存：reader 抛错→(None, exc)，修复后下次真读。
- 共享：CREATE-GUARD 与 SSOT-REDEFINITION 经同一容器——整链一次 yaml.safe_load。
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from zephyr.gov_enforcement.commit_gates import _capability_registry_io as crio
from zephyr.gov_enforcement.commit_gates import create_guard as cg
from zephyr.gov_enforcement.commit_gates import ssot_redefinition_gate as ssot

_REG_TEXT = "schema_version: 1.1.0\ncapabilities:\n  - capability_id: cap-x\n    aliases: [CapX]\n"


@pytest.fixture()
def fresh_cache(monkeypatch):
    """共享缓存容器复位（进程级单条，测试间零串台）。"""
    monkeypatch.setattr(crio, "_PARSE_CACHE", {"key": None, "data": None})


@pytest.fixture()
def reg_file(tmp_path):
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_TEXT, encoding="utf-8")
    return reg


def _counting_reader(store: dict):
    real = crio._default_reader

    def _read(p):
        store["n"] = store.get("n", 0) + 1
        return real(p)

    return _read


def test_hit_same_key_no_reread_same_object(reg_file, fresh_cache):
    store: dict = {}
    reader = _counting_reader(store)
    d1, e1 = crio.parse_capability_registry_cached(reg_file, reader=reader)
    assert e1 is None and d1 is not None
    d2, e2 = crio.parse_capability_registry_cached(reg_file, reader=reader)
    assert e2 is None
    assert d2 is d1, "同 normcase 路径+mtime+size 必须命中缓存（同一对象）"
    assert store["n"] == 1, "命中不得重读文件"


def test_invalidate_on_mtime_or_size(reg_file, fresh_cache):
    store: dict = {}
    reader = _counting_reader(store)
    crio.parse_capability_registry_cached(reg_file, reader=reader)
    reg_file.write_text(_REG_TEXT + "# tail\n", encoding="utf-8")  # size 变
    crio.parse_capability_registry_cached(reg_file, reader=reader)
    assert store["n"] == 2, "size 变化必须重解析"
    with open(reg_file, "ab") as fh:
        fh.write(b"")
    os.utime(reg_file, ns=(reg_file.stat().st_mtime_ns + 1_000_000,) * 2)  # 仅 mtime 变
    crio.parse_capability_registry_cached(reg_file, reader=reader)
    assert store["n"] == 3, "mtime 变化必须重解析"


def test_no_cross_path_false_hit(tmp_path, fresh_cache):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("x: 1\n", encoding="utf-8")
    b.write_text("x: 1\n", encoding="utf-8")
    os.utime(b, ns=(a.stat().st_mtime_ns, a.stat().st_mtime_ns))  # 强造同 mtime+size
    d1, _ = crio.parse_capability_registry_cached(a)
    d2, _ = crio.parse_capability_registry_cached(b)
    assert d1 == d2 == {"x": 1}
    assert d1 is not d2, "不同路径同 (mtime,size) 不得串台（键含 normcase 路径）"


def test_parse_failure_not_cached(reg_file, fresh_cache):
    def bad_reader(_p):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad")

    d1, e1 = crio.parse_capability_registry_cached(reg_file, reader=bad_reader)
    assert d1 is None and isinstance(e1, UnicodeDecodeError)
    d2, e2 = crio.parse_capability_registry_cached(reg_file)  # 换回默认 reader：必须真读
    assert e2 is None and d2 is not None, "解析失败不得缓存（下次真读）"


def test_create_guard_and_ssot_share_one_parse(tmp_path, fresh_cache, monkeypatch):
    """簇1 判别面：CREATE-GUARD 与 SSOT-REDEFINITION 同读一册只解析一次。"""
    import zephyr.governance.capability_lookup as cl

    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_TEXT, encoding="utf-8")
    monkeypatch.setattr(cl, "REGISTRY_YAML", reg)

    store: dict = {}
    real_read = cg._read_registry_text

    def counting_read(p):
        store["n"] = store.get("n", 0) + 1
        return real_read(p)

    monkeypatch.setattr(cg, "_read_registry_text", counting_read)
    gw = SimpleNamespace(project_root=tmp_path)

    d_cg, err_cg = cg._load_capability_registry(gw)
    assert err_cg == "" and d_cg is not None
    assert store["n"] == 1

    d_ssot, early = ssot._load_registry_yaml(gw, [])
    assert early is None and d_ssot is not None
    assert store["n"] == 1, "SSOT 必须命中 CREATE-GUARD 已填的共享缓存（全链一次解析）"
    assert d_ssot is d_cg
