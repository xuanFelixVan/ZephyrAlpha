# [A_test] module_id: MOD-GOV_module_translation_loader_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SH-MODULE_TRANSLATION-001 | scripts/governance/_shared/module_translation_loader.py
# [MODULE] tests.governance.test_module_translation_loader
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_module_translation_loader.py — 翻译真源加载器直测（W4d 施工安全网）。

补齐 st-vocabconsol-20260918 W1b 发现的"10 个消费方公共入口零直测"缺口，
并锚定裁定#335 结论7 的 loader 治本：entries 段同 module_path 重复条目
在加载时检测+去重（信息量仲裁、平分后写优先=维持既有消费可见语义），
且 stderr 打印一条可观测警告（组数+账实计数+样例路径），不静默。

测试隔离：全部用 tmp_path 迷你注册表 monkeypatch _REGISTRY_YAML，禁写生产路径。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_GOV_DIR = str(_PROJECT_ROOT / "scripts" / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared import module_translation_loader as mtl  # noqa: E402


def _mini_registry(tmp_path: Path, entries_text: str) -> Path:
    """构造 tmp 迷你注册表（含 entries 段 + 一个顶层尾段，验证 loader 只读 entries）。"""
    f = tmp_path / "module_translation_registry.yaml"
    text = (
        "version: 0.0.0-test\n"
        "unique_key: [module_path]\n"
        "entries:\n"
        f"{entries_text}"
        "\nbattle_map_steps:\n- step_id: BM-T-01\n  name_zh: \"应被忽略\"\n"
    )
    f.write_text(text, encoding="utf-8", newline="\n")
    return f


@pytest.fixture()
def loader_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """重置 loader 模块级缓存 + 指向 tmp 注册表的工厂。"""

    def _point_to(path_file: Path) -> Path:
        monkeypatch.setattr(mtl, "_REGISTRY_YAML", path_file)
        monkeypatch.setattr(mtl, "_PATH_CACHE", None)
        monkeypatch.setattr(mtl, "_PATH_CACHE_MTIME", None)
        return path_file

    yield _point_to
    monkeypatch.setattr(mtl, "_PATH_CACHE", None)
    monkeypatch.setattr(mtl, "_PATH_CACHE_MTIME", None)


_ENTRY_A = """\
- module_path: src/zephyr/aaa.py
  domain_id: D_TEST
  name_zh: "陈旧占位"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "占位"
"""

_ENTRY_A_CURATED = """\
- module_path: src/zephyr/aaa.py
  domain_id: D_TEST
  name_zh: "curated名"
  name_en: "Curated"
  desc_zh: "实质技术简介"
  desc_en: "real desc"
  plain_zh: "实质大白话简介内容"
"""

_ENTRY_B = """\
- module_path: src/zephyr/bbb.py
  domain_id: D_TEST
  name_zh: "B模块"
  name_en: "Bee"
  desc_zh: "B简介"
  desc_en: ""
  plain_zh: "B的大白话简介内容"
"""


class TestDuplicateDetection:
    """同 module_path 重复条目：检测+去重+可观测警告。"""

    def test_curated_wins_regardless_of_list_order(self, loader_tmp, tmp_path) -> None:
        """信息更全的条目胜出——即使 curated 在前、陈旧占位在最后（旧"后写覆盖"盲区）。"""
        f = loader_tmp(_mini_registry(tmp_path, _ENTRY_A_CURATED + _ENTRY_A + _ENTRY_B))
        cache = mtl.preload()
        assert cache["src/zephyr/aaa.py"]["name_zh"] == "curated名"
        assert cache["src/zephyr/aaa.py"]["desc_zh"] == "实质技术简介"
        assert f.exists()

    def test_curated_wins_when_listed_later(self, loader_tmp, tmp_path) -> None:
        """curated 靠后（真实注册表 30 组的既有形态）：胜出结果与旧折叠语义一致。"""
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A + _ENTRY_A_CURATED + _ENTRY_B))
        cache = mtl.preload()
        assert cache["src/zephyr/aaa.py"]["name_zh"] == "curated名"

    def test_tie_later_wins(self, loader_tmp, tmp_path) -> None:
        """信息量平分 → 后登记者优先（维持旧 dict 折叠的消费可见语义，零回归）。"""
        dup2 = _ENTRY_A.replace("陈旧占位", "后来的占位")
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A + dup2))
        cache = mtl.preload()
        assert cache["src/zephyr/aaa.py"]["name_zh"] == "后来的占位"

    def test_declared_vs_visible_counts(self, loader_tmp, tmp_path) -> None:
        """账实收敛：4 条声明（含 1 组重复）→ 2 个可见键。"""
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A + _ENTRY_A_CURATED + _ENTRY_B + _ENTRY_A))
        cache = mtl.preload()
        assert len(cache) == 2

    def test_warning_emitted_to_stderr_once_with_counts(
        self, loader_tmp, tmp_path, capsys
    ) -> None:
        """重复存在时必须打印一条 stderr 警告（组数+样例路径），不得静默。"""
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A + _ENTRY_A_CURATED + _ENTRY_B + _ENTRY_A))
        mtl.preload()
        err = capsys.readouterr().err
        assert "WARNING" in err
        assert "1 组重复" in err  # 两个重复组同一路径 → 组数=1，额外占用=2
        assert "src/zephyr/aaa.py" in err
        assert "声明 4 条" in err and "可见 2 键" in err

    def test_no_warning_when_unique(self, loader_tmp, tmp_path, capsys) -> None:
        """无重复 → 零警告（正常路径不产生噪声）。"""
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A_CURATED + _ENTRY_B))
        mtl.preload()
        err = capsys.readouterr().err
        assert "module_translation_loader" not in err


class TestLoaderContractPreserved:
    """既有对外契约零回归（10 个消费方依赖）。"""

    def test_missing_file_returns_empty(self, loader_tmp, tmp_path) -> None:
        f = tmp_path / "not_exists.yaml"
        loader_tmp(f)
        assert mtl.preload() == {}
        assert mtl.get_module_translation("src/zephyr/aaa.py") is None

    def test_broken_yaml_degrades_silently_empty(self, loader_tmp, tmp_path) -> None:
        f = tmp_path / "broken.yaml"
        f.write_text("entries: [ {", encoding="utf-8", newline="\n")
        loader_tmp(f)
        assert mtl.preload() == {}

    def test_get_module_name_bilingual_end_to_end(self, loader_tmp, tmp_path) -> None:
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A + _ENTRY_A_CURATED + _ENTRY_B))
        assert mtl.get_module_name_bilingual("src\\zephyr\\aaa.py") == "curated名 / Curated"
        assert mtl.get_module_plain("src/zephyr/aaa.py") == "实质大白话简介内容"

    def test_backslash_path_normalized(self, loader_tmp, tmp_path) -> None:
        loader_tmp(_mini_registry(tmp_path, _ENTRY_B))
        assert mtl.get_module_translation("src\\zephyr\\bbb.py") is not None


# 裁定#335 结论⑥（W4b）：写手落的派生层字段必须能被消费侧读到
_ENTRY_WITH_LAYER = """\
- module_path: src/zephyr/layered.py
  domain_id: D_TEST
  name_zh: "带层模块"
  name_en: "Layered"
  desc_zh: ""
  desc_en: ""
  plain_zh: "带层模块的大白话简介内容"
  responsibility_layer: governance
"""


class TestResponsibilityLayerPassthrough:
    """投影白名单透传 responsibility_layer，且不干扰重复仲裁口径。"""

    def test_layer_passed_through(self, loader_tmp, tmp_path) -> None:
        loader_tmp(_mini_registry(tmp_path, _ENTRY_WITH_LAYER))
        assert mtl.get_module_translation("src/zephyr/layered.py")["responsibility_layer"] == "governance"

    def test_absent_layer_projects_empty_string(self, loader_tmp, tmp_path) -> None:
        loader_tmp(_mini_registry(tmp_path, _ENTRY_B))
        assert mtl.get_module_translation("src/zephyr/bbb.py")["responsibility_layer"] == ""

    def test_layer_excluded_from_duplicate_info_score(self, loader_tmp, tmp_path) -> None:
        """低信息但带层段的重复条目不得凭派生字段反超信息更全的 curated 条目。"""
        weaker_with_layer = (
            _ENTRY_A_CURATED.replace('name_en: "Curated"', 'name_en: ""').rstrip("\n")
            + "\n  responsibility_layer: governance\n"
        )
        loader_tmp(_mini_registry(tmp_path, _ENTRY_A_CURATED + weaker_with_layer))
        hit = mtl.preload()["src/zephyr/aaa.py"]
        assert hit["name_en"] == "Curated"  # 翻译 5 字段口径：curated 仍胜出


# ============================================================================
# R-002 merge 治本回归面（总包裁定，全流通战役 st-ff-vocabM-20260918）：
# 六对 extract 级克隆合并为泛型访问器 _lookup_entry_text/_bilingual_field/
# _is_shared_template 后，module 族与 step 族薄封装的行为契约必须零回归。
# ============================================================================

_STEP_FULL = """\
- step_id: BM-T-02
  flow_stage: 测试阶段
  name_zh: "环节中文名"
  name_en: "Step Name"
  plain_zh: "环节大白话一句话"
  mechanism_zh: "环节机制说明多行文案"
  indicators_zh: "环节指标人读文案"
"""

_STEP_ZH_ONLY = """\
- step_id: BM-T-03
  flow_stage: 测试阶段
  name_zh: "仅中文环节"
  name_en: ""
  plain_zh: "仅中文环节大白话"
  mechanism_zh: ""
  indicators_zh: ""
"""

_ENTRY_SHARED_PLAIN_1 = """\
- module_path: src/zephyr/shared1.py
  domain_id: D_TEST
  name_zh: "共享模板一"
  name_en: ""
  desc_zh: "独有简介一"
  desc_en: ""
  plain_zh: "提供包入口和模块加载功能"
"""

_ENTRY_SHARED_PLAIN_2 = """\
- module_path: src/zephyr/shared2.py
  domain_id: D_TEST
  name_zh: "共享模板二"
  name_en: ""
  desc_zh: "独有简介二"
  desc_en: ""
  plain_zh: "提供包入口和模块加载功能"
"""


def _mini_registry_with_steps(tmp_path: Path, entries_text: str, steps_text: str) -> Path:
    """构造含 entries + battle_map_steps 双段的 tmp 迷你注册表。"""
    f = tmp_path / "module_translation_registry.yaml"
    f.write_text(
        "version: 0.0.0-test\nentries:\n" + entries_text + "\nbattle_map_steps:\n" + steps_text,
        encoding="utf-8",
        newline="\n",
    )
    return f


_ALL_CACHES = (
    "_PATH_CACHE",
    "_PATH_CACHE_MTIME",
    "_STEP_CACHE",
    "_GENERIC_PLAIN_CACHE",
    "_GENERIC_DESC_CACHE",
    "_GENERIC_SUFFIX_CACHE",
)


@pytest.fixture()
def loader_full(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """重置全部模块级缓存（含 step/泛型简介缓存）+ 指向 tmp 注册表。"""

    def _point_to(path_file: Path) -> Path:
        monkeypatch.setattr(mtl, "_REGISTRY_YAML", path_file)
        for name in _ALL_CACHES:
            monkeypatch.setattr(mtl, name, None)
        return path_file

    yield _point_to
    for name in _ALL_CACHES:
        monkeypatch.setattr(mtl, name, None)


class TestMergedAccessorsR002:
    """六对克隆合并后的行为契约（module 族 + step 族薄封装零回归）。"""

    def test_step_text_fields(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL))
        assert mtl.get_step_plain("BM-T-02") == "环节大白话一句话"
        assert mtl.get_step_mechanism("BM-T-02") == "环节机制说明多行文案"
        assert mtl.get_step_indicators_zh("BM-T-02") == "环节指标人读文案"

    def test_step_text_fields_missing_step_empty(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL))
        assert mtl.get_step_plain("BM-NOPE") == ""
        assert mtl.get_step_mechanism("BM-NOPE") == ""
        assert mtl.get_step_indicators_zh("BM-NOPE") == ""

    def test_module_plain_still_works(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_A_CURATED, _STEP_FULL))
        assert mtl.get_module_plain("src/zephyr/aaa.py") == "实质大白话简介内容"
        assert mtl.get_module_plain("src/zephyr/missing.py") == ""

    def test_step_name_bilingual_both(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL + _STEP_ZH_ONLY))
        assert mtl.get_step_name_bilingual("BM-T-02") == "环节中文名 / Step Name"

    def test_step_name_bilingual_zh_only(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL + _STEP_ZH_ONLY))
        assert mtl.get_step_name_bilingual("BM-T-03") == "仅中文环节"

    def test_step_name_bilingual_missing_empty(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL))
        assert mtl.get_step_name_bilingual("BM-NOPE") == ""

    def test_module_desc_bilingual_both(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_A_CURATED, _STEP_FULL))
        assert mtl.get_module_desc_bilingual("src/zephyr/aaa.py") == "实质技术简介 / real desc"

    def test_module_desc_bilingual_zh_only(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL))
        assert mtl.get_module_desc_bilingual("src/zephyr/bbb.py") == "B简介"
        assert mtl.get_module_desc_bilingual("src/zephyr/missing.py") == ""

    def test_preload_battle_map_steps(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL + _STEP_ZH_ONLY))
        cache = mtl.preload_battle_map_steps()
        assert set(cache.keys()) == {"BM-T-02", "BM-T-03"}
        assert cache["BM-T-02"]["name_zh"] == "环节中文名"

    def test_preload_battle_map_steps_missing_file_empty(self, loader_full, tmp_path) -> None:
        loader_full(tmp_path / "not_exists.yaml")
        assert mtl.preload_battle_map_steps() == {}

    def test_is_generic_plain_vs_desc_sets_distinct(self, loader_full, tmp_path) -> None:
        """plain 集与 desc 集必须各查各的（防 _is_shared_template 下标互换变异）。"""
        loader_full(
            _mini_registry_with_steps(tmp_path, _ENTRY_SHARED_PLAIN_1 + _ENTRY_SHARED_PLAIN_2, _STEP_FULL)
        )
        # plain_zh 被 2 模块共用 → 通用
        assert mtl.is_generic_plain_zh("提供包入口和模块加载功能") is True
        # desc_zh 各自独有 → 非通用（若下标互换，此处会误查 plain 集）
        assert mtl.is_generic_desc_zh("独有简介一") is False
        assert mtl.is_generic_plain_zh("独有简介一") is False

    def test_is_generic_desc_shared(self, loader_full, tmp_path) -> None:
        dup_desc = _ENTRY_SHARED_PLAIN_1.replace("独有简介一", "共用简介").replace("shared1", "shared3")
        dup_desc2 = _ENTRY_SHARED_PLAIN_1.replace("独有简介一", "共用简介").replace("shared1", "shared4")
        loader_full(_mini_registry_with_steps(tmp_path, dup_desc + dup_desc2, _STEP_FULL))
        assert mtl.is_generic_desc_zh("共用简介") is True

    def test_is_generic_empty_text_false(self, loader_full, tmp_path) -> None:
        loader_full(_mini_registry_with_steps(tmp_path, _ENTRY_B, _STEP_FULL))
        assert mtl.is_generic_plain_zh("") is False
        assert mtl.is_generic_desc_zh("") is False
