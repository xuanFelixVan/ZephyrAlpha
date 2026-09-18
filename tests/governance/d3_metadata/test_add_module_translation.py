# [BLUEPRINT] MOD-INF-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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
- W4e（裁定#335 结论7）: TestPreserveExtensionFields / TestUpsertSelfHealDuplicates /
  TestCASWrite（safe_write_text：base 陈旧拒写 + LF 行尾）/ TestDedupeRegistry（--dedupe）
- W4b（裁定#335 结论⑥）: TestUpsertAutoFillLayer（按 domain 自动填层/缺域 WARNING 留空/
  真源覆写调用方值/派生字段不从旧块复活）/ TestSyncLayerRegistry（--sync-layer 写入+幂等/
  dry-run 零写/映射删行→字段移除/无 domain 跳过/真源不可用拒跑/行级编辑保字节）/
  TestSyncLayerCli / TestLayerMapLoaderFailFast（受控词表越界=fail-fast）

测试隔离：monkeypatch is_generic_* / REGISTRY_YAML / RESPONSIBILITY_LAYER_MAP_YAML；
tmp_path 构造临时 YAML 与临时映射真源（不读真仓 registry 写路径）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from add_module_translation import (  # noqa: E402
    EXIT_IO,
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    _format_entry_block,
    _normalize_path,
    _set_layer_line,
    _split_entries_section,
    _upsert_entry,
    _validate_plain,
    _write_registry,
    _yaml_quote,
    add_translation,
    dedupe_registry,
    sync_layer_registry,
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


# ---------------------------------------------------------------------------
# W4e 治本（裁定#335 结论7）夹具
# ---------------------------------------------------------------------------

_EXT_YAML = """\
header: v
entries:
- module_path: src/zephyr/with_extras.py
  module_id: MOD-TEST
  domain_id: D_TEST
  name_zh: "旧名"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "旧的大白话简介测试用"
  build_status: dormant
- module_path: src/zephyr/other.py
  domain_id: D_TEST
  name_zh: "旁观者"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "旁观者的大白话简介内容"

battle_map_steps:
- step_id: BM-T-01
  name_zh: "x"
"""


def _entry(path: str, name_zh: str, plain_zh: str, **extra: str) -> dict:
    base = {
        "module_path": path,
        "domain_id": "D_TEST",
        "name_zh": name_zh,
        "name_en": "",
        "desc_zh": "",
        "desc_en": "",
        "plain_zh": plain_zh,
    }
    base.update(extra)
    return base


# ---------------------------------------------------------------------------
# W4e-A: 扩展字段保留 + upsert 全文件查重自愈
# ---------------------------------------------------------------------------


class TestPreserveExtensionFields:
    """整块重写保留未知扩展字段（module_id/build_status/domain），round-trip 安全。"""

    def test_upsert_keeps_module_id_and_build_status(self) -> None:
        """更新条目后 module_id/build_status 仍在，且解析回读同值。"""
        entry = _entry("src/zephyr/with_extras.py", "更新名", "更新后的大白话简介内容")
        new_text, is_new = _upsert_entry(_EXT_YAML, entry)
        assert is_new is False
        data = yaml.safe_load(new_text)
        hit = [e for e in data["entries"] if e["module_path"] == "src/zephyr/with_extras.py"]
        assert len(hit) == 1
        assert hit[0]["name_zh"] == "更新名"
        assert hit[0]["module_id"] == "MOD-TEST"
        assert hit[0]["build_status"] == "dormant"

    def test_bare_identifier_style_preserved(self) -> None:
        """扩展字段安全标识符值裸写（匹配存量条目字节风格，不加引号漂移）。"""
        entry = _entry("src/zephyr/with_extras.py", "更新名", "更新后的大白话简介内容")
        new_text, _ = _upsert_entry(_EXT_YAML, entry)
        assert "  module_id: MOD-TEST" in new_text
        assert "  build_status: dormant" in new_text
        assert '  module_id: "MOD-TEST"' not in new_text

    def test_format_entry_block_unknown_field_roundtrip(self) -> None:
        """_format_entry_block 输出的扩展字段 safe_load 读回同值（round-trip 安全）。"""
        entry = _entry("src/zephyr/m.py", "名", "大白话简介内容测试用", layer="governance", flag=True)
        block = _format_entry_block(entry)
        parsed = yaml.safe_load(block)[0]
        assert parsed["layer"] == "governance"
        assert parsed["flag"] is True


class TestUpsertSelfHealDuplicates:
    """upsert 命中多个同 module_path 块 → 全部收敛为一条（重复自愈）。"""

    _DUP_YAML = _EXT_YAML.replace(
        "- module_path: src/zephyr/other.py",
        """- module_path: src/zephyr/with_extras.py
  domain_id: D_TEST
  name_zh: "占位重复段"
  name_en: "Dup"
  desc_zh: ""
  desc_en: ""
  plain_zh: "占位重复段的大白话简介"
  domain: D_EXTRA
- module_path: src/zephyr/other.py""",
    )

    def test_duplicates_collapse_to_one(self) -> None:
        entry = _entry("src/zephyr/with_extras.py", "最终名", "最终的大白话简介内容")
        new_text, is_new = _upsert_entry(self._DUP_YAML, entry)
        assert is_new is False
        assert new_text.count("- module_path: src/zephyr/with_extras.py") == 1
        data = yaml.safe_load(new_text)
        assert len(data["entries"]) == 2  # 3 块 → 2 条
        hit = data["entries"][0]
        # 两组重复块的扩展字段全部并入（module_id 来自块1、domain 来自块2）
        assert hit["module_id"] == "MOD-TEST"
        assert hit["build_status"] == "dormant"
        assert hit["domain"] == "D_EXTRA"
        assert hit["name_zh"] == "最终名"

    def test_untouched_entries_bytes_preserved(self) -> None:
        """区间级编辑：未命中条目与 tail 段落字节原样（禁整文件重序列化漂移）。"""
        entry = _entry("src/zephyr/with_extras.py", "最终名", "最终的大白话简介内容")
        new_text, _ = _upsert_entry(_EXT_YAML, entry)
        other_block = """- module_path: src/zephyr/other.py
  domain_id: D_TEST
  name_zh: "旁观者"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "旁观者的大白话简介内容"
"""
        assert other_block in new_text
        assert new_text.endswith("  name_zh: \"x\"\n")


# ---------------------------------------------------------------------------
# W4e-A: 热文件 CAS 写入（safe_write_text，AGENTS 硬规则 13）
# ---------------------------------------------------------------------------


class TestCASWrite:
    """写盘必须走 safe_write_text：base 陈旧拒写、成功路径 LF 行尾。"""

    def _mini(self, tmp_path: Path) -> Path:
        f = tmp_path / "module_translation_registry.yaml"
        f.write_text(_EXT_YAML, encoding="utf-8", newline="\n")
        return f

    def test_stale_base_refused(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """base 与磁盘不符（他会话已推进）→ StaleWriteRefused 拒写不落盘。"""
        from zephyr.shared.io.file_utils import StaleWriteRefused

        import add_module_translation as mod

        f = self._mini(tmp_path)
        monkeypatch.setattr(mod, "REGISTRY_YAML", f)
        with pytest.raises(StaleWriteRefused):
            mod._write_registry("new: content\n", base_text="陈旧快照内容")
        # 拒写后文件未被部分写入
        assert f.read_text(encoding="utf-8") == _EXT_YAML

    def test_add_translation_writes_lf_bytes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """正常写盘走 CAS 且保 LF 行尾（.gitattributes eol=lf 约定，写手不再翻转 CRLF）。"""
        import add_module_translation as mod

        f = self._mini(tmp_path)
        monkeypatch.setattr(mod, "REGISTRY_YAML", f)
        monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: False)
        monkeypatch.setattr(mod, "is_generic_plain_suffix", lambda s, n: False)
        entry = _entry("src/zephyr/with_extras.py", "写手更新", "写手更新的大白话简介内容")
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        assert b"\r" not in f.read_bytes()
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        hit = [e for e in data["entries"] if e["module_path"] == "src/zephyr/with_extras.py"]
        assert len(hit) == 1 and hit[0]["module_id"] == "MOD-TEST"

    def test_concurrent_modification_maps_to_exit_io(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """读到写之间磁盘被推进 → add_translation 返回 EXIT_IO（不吞并发改）。"""
        import add_module_translation as mod

        f = self._mini(tmp_path)
        monkeypatch.setattr(mod, "REGISTRY_YAML", f)
        monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: False)
        monkeypatch.setattr(mod, "is_generic_plain_suffix", lambda s, n: False)
        real_write = mod._write_registry

        def racing_write(new_text: str, base_text: str) -> None:
            # 模拟并发改：add_translation 读完之后、写盘之前，他会话推进磁盘
            cur = f.read_text(encoding="utf-8")
            f.write_text(cur + "# 他会话追加\n", encoding="utf-8", newline="\n")
            real_write(new_text, base_text)

        monkeypatch.setattr(mod, "_write_registry", racing_write)
        entry = _entry("src/zephyr/with_extras.py", "写手更新", "写手更新的大白话简介内容")
        code, msg = add_translation(entry)
        assert code == EXIT_IO
        assert "CAS" in msg or "Stale" in msg or "写入翻译真源失败" in msg


# ---------------------------------------------------------------------------
# W4e-C: --dedupe 整表去重
# ---------------------------------------------------------------------------


class TestDedupeRegistry:
    """--dedupe：重复组保留信息最全条目+合并扩展字段；幂等；dry-run 不写盘。"""

    _DUP_YAML = TestUpsertSelfHealDuplicates._DUP_YAML

    def _patch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str) -> Path:
        import add_module_translation as mod

        f = tmp_path / "module_translation_registry.yaml"
        f.write_text(text, encoding="utf-8", newline="\n")
        monkeypatch.setattr(mod, "REGISTRY_YAML", f)
        return f

    def test_dry_run_does_not_write(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        f = self._patch(tmp_path, monkeypatch, self._DUP_YAML)
        before = f.read_bytes()
        code, msg = dedupe_registry(dry_run=True)
        assert code == EXIT_SUCCESS
        assert "1 组" in msg and "dry-run" in msg
        assert f.read_bytes() == before  # 零写盘

    def test_dedupe_keeps_richest_and_merges_extras(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        f = self._patch(tmp_path, monkeypatch, self._DUP_YAML)
        code, msg = dedupe_registry()
        assert code == EXIT_SUCCESS, msg
        assert "1 组" in msg and "删除 1 条" in msg
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 2
        hit = data["entries"][0]
        # curated（非空字段更多的占位段 name_en=Dup/domain=D_EXTRA vs 块1 module_id/build_status）
        # 双方扩展字段都被合并
        assert hit["module_id"] == "MOD-TEST" and hit["domain"] == "D_EXTRA"
        assert hit["build_status"] == "dormant" and hit["name_en"] == "Dup"
        # 胜出内容=信息最全段（curated 占位段有 name_en+domain+plain 四项非空）
        assert hit["name_zh"] == "占位重复段"

    def test_idempotent_second_run(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        f = self._patch(tmp_path, monkeypatch, self._DUP_YAML)
        assert dedupe_registry()[0] == EXIT_SUCCESS
        after_first = f.read_bytes()
        code, msg = dedupe_registry()
        assert code == EXIT_SUCCESS and "0 组" in msg
        assert f.read_bytes() == after_first  # 幂等：第二次运行零改动

    def test_unique_registry_untouched(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        f = self._patch(tmp_path, monkeypatch, _EXT_YAML)
        before = f.read_bytes()
        code, msg = dedupe_registry()
        assert code == EXIT_SUCCESS and "0 组" in msg
        assert f.read_bytes() == before

    def test_cli_dispatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """main：--dedupe 可脱离 upsert 必填参数运行；混用/缺参 → exit 1。"""
        import add_module_translation as mod

        f = self._patch(tmp_path, monkeypatch, self._DUP_YAML)
        assert mod.main(["--dedupe"]) == EXIT_SUCCESS
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 2
        assert mod.main(["--dedupe", "--dry-run", "--path", "x"]) == EXIT_VALIDATION
        assert mod.main([]) == EXIT_VALIDATION


# ---------------------------------------------------------------------------
# W4b: responsibility_layer 派生（裁定#335 结论⑥——唯一真源=域→层映射 YAML）
# ---------------------------------------------------------------------------

# tmp 假映射（不读真仓 catalogs；受控词表也自带，验证加载器读真源自述而非硬编码）
_FAKE_MAP = """\
module_id: REG-TEST-LAYER-MAP
responsibility_layer_values:
  governance: "测试治理层"
  business: "测试业务层"
entries:
- domain: D_TEST
  responsibility_layer: governance
  reason: "测试域"
- domain: D_BIZ
  responsibility_layer: business
  reason: "测试业务域"
"""

# 映射被删掉 D_TEST 行后的形态（验证"映射删行→字段移除/不复活"）
_FAKE_MAP_WITHOUT_D_TEST = """\
module_id: REG-TEST-LAYER-MAP
responsibility_layer_values:
  governance: "测试治理层"
  business: "测试业务层"
entries:
- domain: D_BIZ
  responsibility_layer: business
  reason: "测试业务域"
"""

# 裸写风格 + 扩展字段 + 尾随顶层段：验证层同步只动目标行，其余字节原样
_BARE_YAML = """\
header: v
entries:
- module_path: src/zephyr/bare_a.py
  domain_id: D_TEST
  name_zh: 裸写中文名
  name_en: Bare A
  desc_zh: ""
  desc_en: ""
  plain_zh: 裸写条目的大白话简介内容
- module_path: src/zephyr/bare_b.py
  domain_id: D_BIZ
  name_zh: 另一个裸写名
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: 另一个条目的大白话简介
  module_id: MOD-BARE-B
- module_path: src/zephyr/no_domain.py
  domain_id: ""
  name_zh: 无域条目
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: 无域条目的大白话简介
  responsibility_layer: governance

battle_map_steps:
- step_id: BM-T-01
  name_zh: "层同步必须整段忽略这里"
"""

# 已带层字段（且层行位于扩展字段之前）——验证行级改值不重排、映射删行能移除
_LAYERED_YAML = """\
header: v
entries:
- module_path: src/zephyr/layered.py
  domain_id: D_TEST
  name_zh: "已派生条目"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "已派生条目的大白话简介"
  responsibility_layer: governance
  module_id: MOD-LAYERED
- module_path: src/zephyr/other_domain.py
  domain_id: D_BIZ
  name_zh: "他域条目"
  name_en: ""
  desc_zh: ""
  desc_en: ""
  plain_zh: "他域条目的大白话简介内容"
"""


def _w4b_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    registry_text: str = _EXT_YAML,
    map_text: str | None = _FAKE_MAP,
) -> Path:
    """写手注入：REGISTRY_YAML + 映射真源都指向 tmp（禁碰真仓 registry 写路径）。"""
    import add_module_translation as mod

    reg = tmp_path / "module_translation_registry.yaml"
    reg.write_text(registry_text, encoding="utf-8", newline="\n")
    monkeypatch.setattr(mod, "REGISTRY_YAML", reg)
    if map_text is None:
        monkeypatch.setattr(mod, "RESPONSIBILITY_LAYER_MAP_YAML", tmp_path / "absent_map.yaml")
    else:
        m = tmp_path / "domain_responsibility_layer_mapping.yaml"
        m.write_text(map_text, encoding="utf-8", newline="\n")
        monkeypatch.setattr(mod, "RESPONSIBILITY_LAYER_MAP_YAML", m)
    monkeypatch.setattr(mod, "is_generic_plain_zh", lambda s: False)
    monkeypatch.setattr(mod, "is_generic_plain_suffix", lambda s, n: False)
    return reg


def _entry_by_path(path: Path, module_path: str) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    hits = [e for e in data["entries"] if e["module_path"] == module_path]
    assert len(hits) == 1, f"{module_path} 命中 {len(hits)} 条"
    return hits[0]


class TestUpsertAutoFillLayer:
    """新条目 upsert 按 --domain 自动填 responsibility_layer（映射真源是唯一通道）。"""

    def test_autofill_writes_bare_layer(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """映射命中 → 落派生层，且标识符值裸写（与 --sync-layer 同字面风格）。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        entry = _entry("src/zephyr/new_mod.py", "新模块", "新模块的大白话简介内容")
        entry["domain_id"] = "D_TEST"
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        hit = _entry_by_path(reg, "src/zephyr/new_mod.py")
        assert hit["responsibility_layer"] == "governance"
        assert "  responsibility_layer: governance" in reg.read_text(encoding="utf-8")
        assert 'responsibility_layer: "governance"' not in reg.read_text(encoding="utf-8")

    def test_mapping_missing_domain_warns_and_leaves_blank(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """映射缺该域 → stderr WARNING + 字段留空（键不存在），写入本身不阻断。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        entry = _entry("src/zephyr/orphan.py", "孤儿模块", "孤儿模块的大白话简介内容")
        entry["domain_id"] = "D_NOT_IN_MAP"
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        assert "responsibility_layer" not in _entry_by_path(reg, "src/zephyr/orphan.py")
        err = capsys.readouterr().err
        assert "WARNING" in err and "D_NOT_IN_MAP" in err

    def test_map_wins_over_caller_supplied_value(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """调用方手塞的层与映射不一致 → 以真源为准覆盖并告警（禁直推旁路）。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        entry = _entry("src/zephyr/lying.py", "谎报模块", "谎报模块的大白话简介内容")
        entry["domain_id"] = "D_TEST"
        entry["responsibility_layer"] = "business"
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        assert _entry_by_path(reg, "src/zephyr/lying.py")["responsibility_layer"] == "governance"
        assert "真源" in capsys.readouterr().err

    def test_stale_layer_not_resurrected_from_old_block(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """映射删行后 upsert 旧条目：扩展字段合并通道不得继承旧块的陈旧层（派生字段例外）。"""
        reg = _w4b_env(tmp_path, monkeypatch, _LAYERED_YAML, map_text=_FAKE_MAP_WITHOUT_D_TEST)
        assert _entry_by_path(reg, "src/zephyr/layered.py")["responsibility_layer"] == "governance"
        entry = _entry("src/zephyr/layered.py", "改名后", "改名后的大白话简介内容")
        entry["domain_id"] = "D_TEST"
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        hit = _entry_by_path(reg, "src/zephyr/layered.py")
        assert "responsibility_layer" not in hit  # 未复活
        assert hit["module_id"] == "MOD-LAYERED"  # 非派生扩展字段照旧保留


class TestSyncLayerRegistry:
    """--sync-layer：整表按 domain_id 重算/覆盖，幂等 + dry-run 零写 + 删行移除。"""

    def test_writes_every_mapped_entry_and_is_idempotent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        code, msg = sync_layer_registry()
        assert code == EXIT_SUCCESS, msg
        assert "写入 2" in msg and "无 domain 跳过 1" in msg
        assert _entry_by_path(reg, "src/zephyr/bare_a.py")["responsibility_layer"] == "governance"
        assert _entry_by_path(reg, "src/zephyr/bare_b.py")["responsibility_layer"] == "business"

        after_first = reg.read_bytes()
        code2, msg2 = sync_layer_registry()
        assert code2 == EXIT_SUCCESS, msg2
        assert "未变 2" in msg2 and "写入 0" in msg2 and "已幂等收敛" in msg2
        assert reg.read_bytes() == after_first  # 第二次运行零改动

    def test_dry_run_zero_write(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        before = reg.read_bytes()
        code, msg = sync_layer_registry(dry_run=True)
        assert code == EXIT_SUCCESS, msg
        assert "dry-run" in msg and "拟改 2 块" in msg
        assert reg.read_bytes() == before  # 零写盘

    def test_mapping_row_deleted_removes_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """条目已写层但映射已删该域 → 移除字段；他域条目照常重算。"""
        reg = _w4b_env(tmp_path, monkeypatch, _LAYERED_YAML, map_text=_FAKE_MAP_WITHOUT_D_TEST)
        code, msg = sync_layer_registry()
        assert code == EXIT_SUCCESS, msg
        assert "移除 1" in msg and "写入 1" in msg
        hit = _entry_by_path(reg, "src/zephyr/layered.py")
        assert "responsibility_layer" not in hit
        assert hit["module_id"] == "MOD-LAYERED"  # 移除的是单行，扩展字段未受累
        assert _entry_by_path(reg, "src/zephyr/other_domain.py")["responsibility_layer"] == "business"

    def test_entry_without_domain_is_skipped_not_cleared(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """domain 为 None/空 → 该条目不写此字段（也不误删既有值，等补域后再放量）。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        assert sync_layer_registry()[0] == EXIT_SUCCESS
        assert _entry_by_path(reg, "src/zephyr/no_domain.py")["responsibility_layer"] == "governance"

    def test_refuses_when_mapping_source_unavailable(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """映射真源读不到 → EXIT_IO 拒跑（空映射放行会把全表字段抹成未派生）。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML, map_text=None)
        before = reg.read_bytes()
        code, msg = sync_layer_registry()
        assert code == EXIT_IO
        assert "映射真源不可用" in msg
        assert reg.read_bytes() == before

    def test_surgical_edit_preserves_other_bytes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """行级编辑：裸写文本字段不加引号、既有扩展字段不重排、尾随顶层段字节不动。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        code, msg = sync_layer_registry()
        assert code == EXIT_SUCCESS, msg
        text = reg.read_text(encoding="utf-8")
        assert "  name_zh: 裸写中文名" in text  # 未被整块格式化翻成带引号形态
        assert '  name_zh: "裸写中文名"' not in text
        assert "  module_id: MOD-BARE-B\n  responsibility_layer: business" in text
        assert text.endswith('  name_zh: "层同步必须整段忽略这里"\n')  # tail 段零漂移
        # 无 domain 条目整块字节原样（层行原位保留、未被改动）
        assert "  plain_zh: 无域条目的大白话简介\n  responsibility_layer: governance\n" in text

    def test_set_layer_line_three_postures(self) -> None:
        """_set_layer_line 单元语义：无则加 / 有则改 / None 则删（含块尾空行保留）。"""
        block = '- module_path: a.py\n  plain_zh: "x"\n\n'
        added = _set_layer_line(block, "governance")
        assert added == '- module_path: a.py\n  plain_zh: "x"\n  responsibility_layer: governance\n\n'
        changed = _set_layer_line(added, "business")
        assert "responsibility_layer: business" in changed and "governance" not in changed
        assert _set_layer_line(changed, None) == block  # 删回到原字节


class TestSyncLayerCli:
    """main() 派发：--sync-layer 免 upsert 必填参数，且与 --dedupe/单条目参数互斥。"""

    def test_cli_dispatch_and_exclusion(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import add_module_translation as mod

        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML)
        assert mod.main(["--sync-layer", "--dry-run"]) == EXIT_SUCCESS
        before = reg.read_bytes()
        assert mod.main(["--sync-layer"]) == EXIT_SUCCESS
        assert reg.read_bytes() != before
        assert mod.main(["--sync-layer", "--path", "src/zephyr/x.py"]) == EXIT_VALIDATION
        assert mod.main(["--sync-layer", "--dedupe"]) == EXIT_VALIDATION


# 越出真源自述受控词表的映射（加载器 fail-fast 语义）
_FAKE_MAP_BAD_VALUE = """\
responsibility_layer_values:
  governance: "测试治理层"
entries:
- domain: D_TEST
  responsibility_layer: governancex
  reason: "拼错的层名不得被复制到全表"
"""


class TestLayerMapLoaderFailFast:
    """映射真源结构异常：同步拒跑（禁按坏映射抹表），单条写入只降级不填。"""

    def test_sync_refuses_bad_controlled_value(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML, map_text=_FAKE_MAP_BAD_VALUE)
        before = reg.read_bytes()
        code, msg = sync_layer_registry()
        assert code == EXIT_IO
        assert "映射真源不可用" in msg and "受控词表" in msg
        assert reg.read_bytes() == before

    def test_upsert_degrades_with_warning(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """同源的映射故障在 upsert 通道不连坐：翻译照写、层留空、stderr 有 WARNING。"""
        reg = _w4b_env(tmp_path, monkeypatch, _BARE_YAML, map_text=_FAKE_MAP_BAD_VALUE)
        entry = _entry("src/zephyr/degraded.py", "降级模块", "降级模块的大白话简介内容")
        entry["domain_id"] = "D_TEST"
        code, msg = add_translation(entry)
        assert code == EXIT_SUCCESS, msg
        assert "responsibility_layer" not in _entry_by_path(reg, "src/zephyr/degraded.py")
