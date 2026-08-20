# [A_test] module_id: MOD-GOV_add_module_translation_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.d3_metadata.test_add_module_translation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_add_module_translation.py — 模块翻译条目写入工具单测

权威依据：scripts/governance/d3_metadata/add_module_translation.py

测试组：
- TestValidatePlain: _validate_plain 合规校验
  - 合格 plain_zh → ok=True
  - 空 plain_zh → ok=False
  - CJK 不足 → ok=False
  - 通用模板 → ok=False（monkeypatch is_generic_plain_zh）
  - 通用后缀 → ok=False（monkeypatch is_generic_plain_suffix）
- TestYamlQuote: _yaml_quote 转义
  - 含冒号/引号/破折号 → 双引号包裹+转义
- TestUpsertEntry: _upsert_entry upsert 逻辑
  - 新增条目 → 追加到 entries 列表末尾
  - 更新已有条目 → 替换整块
- TestAddTranslationDryRun: add_translation dry-run 模式
  - 校验通过 → exit 0
  - 校验失败 → exit 1

测试隔离：monkeypatch is_generic_* / REGISTRY_YAML；tmp_path 构造临时 YAML。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from add_module_translation import (  # noqa: E402
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    _normalize_path,
    _split_entries_section,
    _upsert_entry,
    _validate_plain,
    _yaml_quote,
    add_translation,
)

# ---------------------------------------------------------------------------
# TestValidatePlain
# ---------------------------------------------------------------------------


class TestValidatePlain:
    """_validate_plain 合规校验。"""

    def test_valid_plain(self) -> None:
        """合格 plain_zh → ok=True。"""
        ok, reason = _validate_plain("这是一个合格的大白话简介用于测试覆盖", "测试模块")
        assert ok is True

    def test_empty_plain(self) -> None:
        """空 plain_zh → ok=False。"""
        ok, reason = _validate_plain("", "测试模块")
        assert ok is False
        assert "为空" in reason

    def test_short_plain(self) -> None:
        """CJK 不足 → ok=False。"""
        ok, reason = _validate_plain("太短", "测试模块")
        assert ok is False
        assert "CJK" in reason

    def test_generic_plain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """通用模板 → ok=False。"""
        import add_module_translation as mod

        monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: True)
        ok, reason = _validate_plain("这是一个通用模板的大白话简介测试", "测试模块")
        assert ok is False
        assert "通用模板" in reason

    def test_generic_suffix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """通用后缀 → ok=False。"""
        import add_module_translation as mod

        monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: False)
        monkeypatch.setattr(mod, "is_generic_plain_suffix", lambda s, n: True)
        ok, reason = _validate_plain("测试模块的实现相关功能", "测试模块")
        assert ok is False
        assert "is_generic_plain_suffix" in reason or "后缀" in reason


# ---------------------------------------------------------------------------
# TestYamlQuote
# ---------------------------------------------------------------------------


class TestYamlQuote:
    """_yaml_quote 转义。"""

    def test_simple_string(self) -> None:
        """简单字符串 → 双引号包裹。"""
        assert _yaml_quote("hello") == '"hello"'

    def test_colon_escaped(self) -> None:
        """含冒号 → 双引号包裹（YAML 不会误解析）。"""
        result = _yaml_quote("做什么: 解决什么")
        assert result.startswith('"')
        assert result.endswith('"')
        assert "做什么: 解决什么" in result

    def test_double_quote_escaped(self) -> None:
        """含双引号 → 转义。"""
        result = _yaml_quote('say "hi"')
        assert '\\"' in result
        assert result.startswith('"') and result.endswith('"')

    def test_backslash_escaped(self) -> None:
        """含反斜杠 → 双反斜杠。"""
        result = _yaml_quote("path\\to")
        assert "\\\\" in result


# ---------------------------------------------------------------------------
# TestUpsertEntry
# ---------------------------------------------------------------------------


class TestUpsertEntry:
    """_upsert_entry upsert 逻辑。"""

    _YAML_TEMPLATE = """\
header: value
entries:
- module_path: src/zephyr/existing.py
  domain_id: D_TEST
  name_zh: "已有模块"
  name_en: "Existing"
  desc_zh: "desc"
  desc_en: "desc"
  plain_zh: "已有模块的大白话简介"
"""

    def test_add_new_entry(self) -> None:
        """新增条目 → 追加到 entries 列表末尾。"""
        entry = {
            "module_path": "src/zephyr/new.py",
            "domain_id": "D_TEST",
            "name_zh": "新模块",
            "name_en": "New",
            "desc_zh": "desc",
            "desc_en": "desc",
            "plain_zh": "新模块的大白话简介内容",
        }
        new_text, is_new = _upsert_entry(self._YAML_TEMPLATE, entry)
        assert is_new is True
        assert "src/zephyr/new.py" in new_text
        assert "src/zephyr/existing.py" in new_text  # 原有条目保留

    def test_update_existing_entry(self) -> None:
        """更新已有条目 → 替换整块。"""
        entry = {
            "module_path": "src/zephyr/existing.py",
            "domain_id": "D_TEST",
            "name_zh": "更新模块",
            "name_en": "Updated",
            "desc_zh": "new desc",
            "desc_en": "new desc",
            "plain_zh": "更新后的大白话简介内容",
        }
        new_text, is_new = _upsert_entry(self._YAML_TEMPLATE, entry)
        assert is_new is False
        assert "更新后的大白话简介内容" in new_text
        assert "已有模块的大白话简介" not in new_text  # 旧值被替换

    def test_split_entries_section(self) -> None:
        """_split_entries_section 正确切分段落。"""
        yaml_text = 'header: value\nentries:\n- module_path: a.py\n  plain_zh: "aaa"\nbattle_map_steps:\n  step1: foo\n'
        preamble, body, tail = _split_entries_section(yaml_text)
        assert "entries:" in preamble
        assert "module_path: a.py" in body
        assert "battle_map_steps:" in tail


# ---------------------------------------------------------------------------
# TestAddTranslationDryRun
# ---------------------------------------------------------------------------


class TestAddTranslationDryRun:
    """add_translation dry-run 模式（不写盘）。"""

    def test_dry_run_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """校验通过 → exit 0（不写盘）。"""
        import add_module_translation as mod

        # is_generic 返回 False（合格简介）
        monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: False)
        monkeypatch.setattr(mod, "is_generic_plain_suffix", lambda s, n: False)

        entry = {
            "module_path": "src/zephyr/dry_run.py",
            "domain_id": "D_TEST",
            "name_zh": "测试模块",
            "name_en": "Test",
            "desc_zh": "desc",
            "desc_en": "desc",
            "plain_zh": "这是 dry-run 测试用的大白话简介",
        }
        code, msg = add_translation(entry, dry_run=True)
        assert code == EXIT_SUCCESS
        assert "dry-run" in msg

    def test_dry_run_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """校验失败（空 plain_zh）→ exit 1。"""
        entry = {
            "module_path": "src/zephyr/bad.py",
            "domain_id": "D_TEST",
            "name_zh": "测试模块",
            "name_en": "",
            "desc_zh": "",
            "desc_en": "",
            "plain_zh": "",
        }
        code, msg = add_translation(entry, dry_run=True)
        assert code == EXIT_VALIDATION
        assert "plain_zh" in msg or "字段缺失" in msg

    def test_normalize_path(self) -> None:
        """_normalize_path Windows 反斜杠归一化。"""
        assert _normalize_path("src\\zephyr\\foo.py") == "src/zephyr/foo.py"
        assert _normalize_path(" src/zephyr/foo.py ") == "src/zephyr/foo.py"
