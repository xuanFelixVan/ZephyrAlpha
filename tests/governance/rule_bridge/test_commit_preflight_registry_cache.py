# [BLUEPRINT] MOD-TEST-001 | tests/governance/rule_bridge/test_commit_preflight_registry_cache.py | §
# [MODULE] tests.governance.rule_bridge.test_commit_preflight_registry_cache
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_preflight
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯单元测试（fake gateway stub + 模块级缓存清空 fixture，测试不写生产路径、零真 git 调用）；验证 QMine M5 矿③ blob sha 内容寻址 memo：同(rel,sha) 第二次起零 git show（解析省 ≈6.5s/件）、sha 变更必重解析、不可读面照旧抛错不缓存假数据
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试永不抛未捕获异常
# [TESTS] self
# [A_module] module_id=MOD-TEST-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_commit_preflight_registry_cache.py — HEAD 注册表解析 memo 单元测试（QMine M5 矿③）。

覆盖：
1. 缓存命中：同 (rel, blob sha) 第二次调用零 `git show`（只剩 ls-tree），返回同一 dict 对象
2. 键正确性：rel 归一（Windows normcase+posix）、sha 变更 → miss 重解析
3. 守恒语义：ls-tree 非 blob / git show 失败 → RuntimeError 且不写缓存（不假绿）
4. 容量护栏：超 _CACHE_CAP 整体清空，正确性不受影响
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from zephyr.gov_enforcement.rule_bridge import commit_preflight as cp

_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_SHA1 = "0123456789abcdef0123456789abcdef01234567"
_SHA2 = "fedcba9876543210fedcba9876543210fedcba98"


@dataclass
class _Out:
    returncode: int = 0
    stdout: str | bytes = ""
    stderr: str = ""


@dataclass
class _FakeGateway:
    """run_git stub：ls-tree 按 (rel→sha) 应答，show 按 (rel→yaml text) 应答；全调用留痕。"""

    tree: dict[str, str] = field(default_factory=dict)  # rel → blob sha
    blobs: dict[str, str] = field(default_factory=dict)  # rel → yaml text
    calls: list[list[str]] = field(default_factory=list)

    def run_git(self, cmd: list[str]):
        self.calls.append(list(cmd))
        if cmd[:3] == ["git", "ls-tree", "HEAD"]:
            sha = self._lookup(self.tree, cmd[-1])
            if sha is None:
                return _Out(returncode=0, stdout="")
            return _Out(returncode=0, stdout=f"100644 blob {sha}\t{cmd[-1]}\n")
        if cmd[:2] == ["git", "show"]:
            text = self._lookup(self.blobs, cmd[2].split(":", 1)[1])
            if text is None:
                return _Out(returncode=1, stderr="not found")
            return _Out(returncode=0, stdout=text.encode("utf-8"))
        raise AssertionError(f"unexpected git cmd: {cmd}")

    @staticmethod
    def _lookup(store: dict[str, str], rel: str) -> str | None:
        """仿真 git on Windows（core.ignorecase）：pathspec/HEAD:path 大小写与分隔符不敏感。"""
        key = rel.replace("\\", "/").lower()
        return next((v for k, v in store.items() if k.replace("\\", "/").lower() == key), None)

    def show_calls(self) -> int:
        return sum(1 for c in self.calls if c[:2] == ["git", "show"])


@pytest.fixture(autouse=True)
def _clean_cache():
    """模块级 memo 是跨测试共享的可变单例——每测清空（生产键=内容寻址，无此问题）。"""
    cp._HEAD_REGISTRY_PARSE_CACHE.clear()
    yield
    cp._HEAD_REGISTRY_PARSE_CACHE.clear()


class TestCacheHit:
    """缓存命中=省解析面（生产实测 6.5s/件的收取点）。"""

    def test_second_call_skips_git_show(self) -> None:
        gw = _FakeGateway(tree={_REL: _SHA1}, blobs={_REL: "entries: [a, b]\n"})
        d1 = cp._head_registry_yaml_data(gw, _REL)
        assert d1 == {"entries": ["a", "b"]}
        assert gw.show_calls() == 1
        d2 = cp._head_registry_yaml_data(gw, _REL)
        assert d2 == d1
        assert gw.show_calls() == 1  # 第二件起零 show（只剩 ls-tree 取 sha）
        assert d2 is d1  # 命中返回缓存本体（消费方均只读投影）

    def test_both_registries_cached_independently(self) -> None:
        rel2 = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"
        gw = _FakeGateway(tree={_REL: _SHA1, rel2: _SHA2}, blobs={_REL: "a: 1\n", rel2: "b: 2\n"})
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 1}
        assert cp._head_registry_yaml_data(gw, rel2) == {"b": 2}
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 1}
        assert gw.show_calls() == 2  # 两册各解析一次

    def test_rel_path_key_normalized_windows(self) -> None:
        """Windows 路径键归一：反斜杠/大小写差异不产生第二缓存项。"""
        gw = _FakeGateway(tree={_REL: _SHA1}, blobs={_REL: "a: 1\n"})
        cp._head_registry_yaml_data(gw, _REL.replace("/", "\\").upper())
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 1}
        assert gw.show_calls() == 1

    def test_sha_change_forces_reparse(self) -> None:
        """blob sha 变更（HEAD 前进/内容变化）→ miss 重解析（内容寻址零失效窗口的另一面）。"""
        gw = _FakeGateway(tree={_REL: _SHA1}, blobs={_REL: "a: 1\n"})
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 1}
        gw.tree[_REL] = _SHA2
        gw.blobs[_REL] = "a: 2\n"
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 2}
        assert gw.show_calls() == 2


class TestConservationSemantics:
    """不可读面照旧抛错（ERROR_CONTRACT 同构），且绝不缓存失败态。"""

    def test_non_blob_ls_tree_raises(self) -> None:
        gw = _FakeGateway(tree={}, blobs={})  # 路径不在 HEAD → 空输出 → 非 blob
        with pytest.raises(RuntimeError, match="HEAD 注册表不可读"):
            cp._head_registry_yaml_data(gw, _REL)
        assert not cp._HEAD_REGISTRY_PARSE_CACHE

    def test_show_failure_raises_and_not_cached(self) -> None:
        gw = _FakeGateway(tree={_REL: _SHA1}, blobs={})
        with pytest.raises(RuntimeError, match="HEAD 注册表不可读"):
            cp._head_registry_yaml_data(gw, _REL)
        assert not cp._HEAD_REGISTRY_PARSE_CACHE
        gw.blobs[_REL] = "a: 1\n"
        assert cp._head_registry_yaml_data(gw, _REL) == {"a": 1}  # 失败后成功可入缓存

    def test_non_dict_root_raises(self) -> None:
        gw = _FakeGateway(tree={_REL: _SHA1}, blobs={_REL: "- just\n- list\n"})
        with pytest.raises(RuntimeError, match="顶层非 dict"):
            cp._head_registry_yaml_data(gw, _REL)

    def test_capacity_guard_clears_and_stays_correct(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """超容量整体清空（护栏），清空后同键重解析结果仍正确。"""
        monkeypatch.setattr(cp, "_CACHE_CAP", 2)
        gw = _FakeGateway(blobs={"r1.yaml": "a: 1\n", "r2.yaml": "a: 2\n", "r3.yaml": "a: 3\n"})
        gw.tree = {"r1.yaml": _SHA1, "r2.yaml": _SHA1, "r3.yaml": _SHA1}
        cp._head_registry_yaml_data(gw, "r1.yaml")
        cp._head_registry_yaml_data(gw, "r2.yaml")
        cp._head_registry_yaml_data(gw, "r3.yaml")
        assert len(cp._HEAD_REGISTRY_PARSE_CACHE) == 1  # 第三件触发清空后只留 r3
        cp._head_registry_yaml_data(gw, "r1.yaml")
        assert cp._head_registry_yaml_data(gw, "r1.yaml") == {"a": 1}
