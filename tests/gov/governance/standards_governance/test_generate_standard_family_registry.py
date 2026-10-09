# [TEST] tests/governance/standards_governance/test_generate_standard_family_registry.py
# [COVERS] scripts.governance.standards_governance.generate_standard_family_registry（三要素+幂等+错误契约）
# [TTL] permanent
"""标准族派生册生成器的验收钉（req_tdchainJ_02 三要素机械可检化）。

三要素逐条钉死：
  ① 落点=scripts/governance/standards_governance/ 子包（ARCH-031）——本文件路径即证据；
  ② 条目来源=standards.yaml + governance_family_vocabulary.yaml + ruling_registry 提及计数，
     禁手工维护 → 钉"盘上册 == 再生册"（漂移即红）；
  ③ 计数字段 total_families/total_standards 由生成器**现算** → 与独立重算的真源计数比对。

全部只读 + tmp_path（测试隔离铁律：禁写 data/ 与 docs/ 生产路径）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from zephyr.shared.io.paths import REPO_ROOT  # SSOT（禁在本文件重定义仓根）

_SCRIPT = REPO_ROOT / "scripts" / "governance" / "standards_governance" / "generate_standard_family_registry.py"


@pytest.fixture(scope="module")
def gen() -> ModuleType:
    """按文件路径加载生成器（scripts/ 非包，对标 tests/governance 既有 importlib 先例）。"""
    spec = importlib.util.spec_from_file_location("gen_std_family_under_test", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _std_ids() -> list[str]:
    doc = yaml.safe_load((REPO_ROOT / "config" / "standards.yaml").read_text(encoding="utf-8")) or {}
    return [str(i.get("std_id")) for i in (doc.get("standards") or []) if i.get("std_id")]


def _vocab_values() -> list[str]:
    vocab = yaml.safe_load(
        (
            REPO_ROOT
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "vocabularies"
            / "governance_family_vocabulary.yaml"
        ).read_text(encoding="utf-8")
    )
    return [str(v.get("value")) for v in (vocab.get("values") or []) if v.get("value")]


def test_counts_are_computed_not_hardcoded(gen: ModuleType) -> None:
    """要素③：计数字段与独立重算的真源条数相等（写死数字必红）。"""
    reg = gen.build_registry()
    assert reg["total_standards"] == len(_std_ids())
    assert reg["total_families"] == len(_vocab_values())
    assert len(reg["entries"]) == reg["total_standards"]


def test_entries_are_derived_from_registered_sources(gen: ModuleType) -> None:
    """要素②：在册条目 == config/standards.yaml 的 std_id 集合（多一条/少一条都红）。"""
    reg = gen.build_registry()
    assert sorted(e["std_id"] for e in reg["entries"]) == sorted(_std_ids())
    # 未声明族的条目必须显式记缺口，禁臆造归属（诚实条款）
    for e in reg["entries"]:
        if e["family"] is None:
            assert e["family_source"] == "undeclared"
            assert e["std_id"] in reg["family_unassigned_std_ids"]
    assert reg["family_unassigned"] == len(reg["family_unassigned_std_ids"])


def test_render_is_deterministic(gen: ModuleType) -> None:
    """幂等：同输入两次渲染逐字节相等（无时间戳/无随机序）。"""
    assert gen.render(gen.build_registry()) == gen.render(gen.build_registry())


def test_catalog_on_disk_matches_regeneration(gen: ModuleType, tmp_path: Path) -> None:
    """要素②（禁手工维护的机械判据）：盘上派生册必须等于再生字节。"""
    text = gen.render(gen.build_registry())
    assert gen.check_freshness(text) is True, "盘上 standard_family_registry.yaml 与再生结果漂移——须再生而非手改"
    # 反向：漂移必红（把册指到 tmp 的改动副本上，--check 口径必须判 STALE）
    drifted = tmp_path / "drifted.yaml"
    drifted.write_text(text + "# 手工塞一行\n", encoding="utf-8")
    monkey = tmp_path / "clean.yaml"
    monkey.write_text(text, encoding="utf-8")
    assert gen.check_freshness(text) is True
    original = gen.OUTPUT
    try:
        gen.OUTPUT = drifted
        assert gen.check_freshness(text) is False, "漂移未被检出=判据失效"
        gen.OUTPUT = monkey
        assert gen.check_freshness(text) is True
    finally:
        gen.OUTPUT = original


def test_missing_source_fails_loudly_with_details(
    gen: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """错误契约：真源缺失→抛错且定位信息在 details 通道（消息面不留路径）。"""
    absent = tmp_path / "not_here.yaml"
    with pytest.raises(FileNotFoundError) as ei:
        gen._load_yaml(absent)
    assert "真源缺失" in str(ei.value)
    assert "not_here.yaml" not in str(ei.value)  # 路径不入消息面（MSG-EXPOSURE 口径）
    assert ei.value.details["path"].endswith("not_here.yaml")  # type: ignore[attr-defined]
    # build_registry 必须把缺失传真源升级成异常，禁静默产出空册冒充"已建"
    monkeypatch.setattr(gen, "STD_SOURCE", absent)
    with pytest.raises(FileNotFoundError):
        gen.build_registry()


def test_non_mapping_source_rejected(gen: ModuleType, tmp_path: Path) -> None:
    """错误契约：真源结构非 mapping → ValueError（禁 None/空 dict 冒充合法）。"""
    bad = tmp_path / "bad.yaml"
    bad.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ValueError) as ei:
        gen._load_yaml(bad)
    assert "mapping" in str(ei.value)
