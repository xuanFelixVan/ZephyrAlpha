# [A_test] module_id: MOD-GOV_ALGO_FLOW_TRANSLATION_SYNC | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ALGO_FLOW_TRANSLATION_SYNC | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §B7-segment-surgery
# [MODULE] tests.scripts.test_algo_flow_translation_sync
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_ALGO_FLOW_TRANSLATION_SYNC | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_algo_flow_translation_sync.py — B7 治本（2026-08-19）段级文本替换单测

事故背景：原实现整文件 safe_load→safe_dump 重序列化，人工维护段落（引号/空串/折行）
被 PyYAML 规范化，两次未登记纯格式漂移（drift watchdog 快照在案）。治本=段级文本
替换（人工段字节级原样，仅派生段重写）+ 段级字段回填 + 写前 YAML 校验 + 运行审计。

覆盖（纯合成数据，tmp_path 隔离）：
1. _replace_top_level_section：人工段字节级保留 + 目标段重写 + 幂等（重跑零 diff）
2. 段不存在时追加
3. _fill_factor_fields_textual：空字段就地回填、非空字段不覆盖、其余字节不动
4. _validated_write：YAML 损坏→抛异常不写文件（ERROR_CONTRACT）
5. _sync_mtr_algo_submodules 端到端（monkeypatch _MTR）：人工段零漂移
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SHARED = _PROJECT_ROOT / "scripts" / "governance" / "_shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from algo_flow_translation_sync import (  # noqa: E402
    _fill_factor_fields_textual,
    _replace_top_level_section,
    _sync_mtr_algo_submodules,
    _validated_write,
)

_SYNTHETIC_MTR = """module_id: REG-MODULE-TRANSLATION-001
version: 1.0.0
entries:
- module_path: src/zephyr/foo.py
  name_zh: "带引号人工条目"
  desc_zh: ""
  plain_zh: "人工排版——这段一个字节都不许动"
  long_field: '人工折行第一段
    折行续行保留'
- module_path: src/zephyr/bar.py
  name_zh: 无引号条目
  desc_zh: ''
battle_map_steps:
- step: 1
algo_submodules:
- module_path: src/zephyr/old.py
  module_id: MOD-OLD
  node_id: A1
  name_zh: 旧节点
  name_en: old_node
  plain_zh: 旧解释
"""


class TestReplaceTopLevelSection:
    """段级文本替换原语。"""

    def test_handcrafted_sections_byte_preserved(self) -> None:
        """entries/battle_map 等人工段字节级原样，仅 algo_submodules 段被替换。"""
        import yaml

        new_section = yaml.safe_dump(
            {"algo_submodules": [{"module_path": "src/zephyr/new.py", "module_id": "MOD-NEW",
                                  "node_id": "A1", "name_zh": "新节点", "name_en": "new_node",
                                  "plain_zh": "新解释"}]},
            allow_unicode=True, sort_keys=False, width=120,
        )
        out = _replace_top_level_section(_SYNTHETIC_MTR, "algo_submodules", new_section)
        head = out.split("algo_submodules:", 1)[0]
        assert head == _SYNTHETIC_MTR.split("algo_submodules:", 1)[0], (
            "人工段（含引号/空串/折行）必须字节级原样"
        )
        assert "MOD-NEW" in out and "MOD-OLD" not in out
        yaml.safe_load(out)  # 产物可解析

    def test_idempotent_second_run_zero_diff(self) -> None:
        """幂等：同内容二次替换零 diff（dump 同参数确定性）。"""
        import yaml

        entries = [{"module_path": "a.py", "module_id": "M", "node_id": "A1",
                    "name_zh": "甲", "name_en": "a", "plain_zh": "乙"}]
        section = yaml.safe_dump({"algo_submodules": entries},
                                 allow_unicode=True, sort_keys=False, width=120)
        once = _replace_top_level_section(_SYNTHETIC_MTR, "algo_submodules", section)
        twice = _replace_top_level_section(once, "algo_submodules", section)
        assert once == twice

    def test_missing_section_appended(self) -> None:
        """段不存在 → 追加到文件尾。"""
        import yaml

        base = "module_id: R\nentries: []\n"
        section = yaml.safe_dump({"algo_submodules": []}, allow_unicode=True, sort_keys=False)
        out = _replace_top_level_section(base, "algo_submodules", section)
        assert out.startswith(base) and "algo_submodules: []" in out


class TestFillFactorFieldsTextual:
    """factor_registry 段级字段回填。"""

    _REG = """registry_id: REG-F
factors:
- factor_id: "FCT-TEST-001"
  name_zh: ""
  alpha_source: ''
  other: 不动我
- factor_id: "FCT-TEST-002"
  name_zh: "已有中文名"
  alpha_source: ""
"""

    def test_fill_empty_only(self) -> None:
        """空字段就地回填；已有值不覆盖（只填空铁律）；其余行字节不动。"""
        new_text, counts = _fill_factor_fields_textual(
            self._REG,
            {("FCT-TEST-001", "name_zh"): "新名字",
             ("FCT-TEST-001", "alpha_source"): "新来源",
             ("FCT-TEST-002", "name_zh"): "不应覆盖"},
        )
        assert counts == {"name_zh": 1, "alpha_source": 1}
        assert 'name_zh: 新名字' in new_text
        assert 'alpha_source: 新来源' in new_text
        assert '"已有中文名"' in new_text, "非空字段不得覆盖"
        assert "  other: 不动我\n" in new_text
        # 未触及行字节级原样
        assert new_text.splitlines()[0] == "registry_id: REG-F"

    def test_missing_field_line_inserted(self) -> None:
        """字段行缺失 → 条目块内插入。"""
        reg = "factors:\n- factor_id: \"FCT-X-001\"\n  weight: 1\n"
        new_text, counts = _fill_factor_fields_textual(reg, {("FCT-X-001", "name_zh"): "插入名"})
        assert counts == {"name_zh": 1}
        assert '- factor_id: "FCT-X-001"\n  name_zh: 插入名\n' in new_text

    def test_unknown_factor_skipped(self) -> None:
        """条目不存在 → 跳过不计数，文本零变化。"""
        new_text, counts = _fill_factor_fields_textual(
            self._REG, {("FCT-NOPE-999", "name_zh"): "x"}
        )
        assert counts == {} and new_text == self._REG


class TestValidatedWrite:
    """ERROR_CONTRACT：YAML 损坏→报错不部分写入。"""

    def test_broken_yaml_rejected(self, tmp_path: Path) -> None:
        target = tmp_path / "r.yaml"
        target.write_text("ok: 1\n", encoding="utf-8")
        with pytest.raises(Exception):
            _validated_write(target, "a: [unclosed\n  - : :\n")
        assert target.read_text(encoding="utf-8") == "ok: 1\n", "损坏写入必须被拦截"


class TestSyncMtrEndToEnd:
    """_sync_mtr_algo_submodules 端到端（monkeypatch _MTR 到 tmp 合成注册表）。"""

    def test_handcrafted_entries_zero_drift(self, tmp_path: Path, monkeypatch) -> None:
        import algo_flow_translation_sync as m

        mtr = tmp_path / "mtr.yaml"
        mtr.write_text(_SYNTHETIC_MTR, encoding="utf-8")
        monkeypatch.setattr(m, "_MTR", mtr)
        r = m._sync_mtr_algo_submodules([{
            "module_path": "src/zephyr/new.py", "module_id": "MOD-NEW", "node_id": "A9",
            "name_zh": "新节点", "name_en": "new_node", "intro": "新解释",
        }])
        assert r == {"algo_submodules": 1}
        out = mtr.read_text(encoding="utf-8")
        assert out.split("algo_submodules:", 1)[0] == _SYNTHETIC_MTR.split("algo_submodules:", 1)[0], (
            "人工段零漂移（B7 核心验收）"
        )
        assert "MOD-NEW" in out and "MOD-OLD" not in out
