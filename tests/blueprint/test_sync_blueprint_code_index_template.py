# [A_test] module_id: MOD-TEST_sync_blueprint_code_index_template | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py | §
# [MODULE] tests.blueprint.test_sync_blueprint_code_index_template
# [INVARIANTS] 蓝图 AUTOGEN 模板不得含失效 AGENTS 编号引用（AGENTS.md §N 形态）；重建幂等；中断安全
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/blueprint/test_sync_blueprint_code_index_template.py -q
# [TTL] permanent
"""GW-C 蓝图模板治本防复发钉（2026-09-16，st-bptmpl-20260916）。

病根：sync_blueprint_code_index.py 模板行曾写死 "AGENTS.md §6.1"——L0 宪法
2026-09-12 替换后 §编号全部失效，人工修复即被下次重建回填。
本测试以正则钉扎模板真源（生成器源码 + 生成产物），并断言重建幂等与中断安全。
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

SYNCER_PATH = (
    REPO_ROOT
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "syncers"
    / "sync_blueprint_code_index.py"
)
PANORAMA_PATH = (
    REPO_ROOT
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "generators"
    / "generate_blueprint_panorama.py"
)

# 失效引用形态钉：AGENTS.md 后跟 §编号（L0 宪法 2026-09-12 起禁写死 §编号，稳定锚=规则名 RULE-XXX）
STALE_AGENTS_NUMBERED_REF = re.compile(r"AGENTS\.md\s*§\s*\d")

OLD_TEMPLATE_LINE = (
    "> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。"
)

# 旧模板行样例（含全部四类固定行 + 空表），用于模拟"已被旧模板污染"的存量蓝图
_STALE_SECTION_TEMPLATE = """## 2. 已实现代码完整路径索引

{old_line}
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 人工备注行：本模块测试先行。

### 2.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 2.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §2（本节）→ 知道「哪些已实现、在哪里」
"""

_BP_HEAD = """---
title: 测试模块蓝图
module_id: MOD-TEST-NOSUCH-0001
version: "0.0.1"
---

## 1. 概述

测试用最小蓝图。

"""


def _load_syncer_module():
    """以独立模块名加载 syncer 脚本（其自身完成 _shared sys.path bootstrap）。"""
    spec = importlib.util.spec_from_file_location(
        "_sync_blueprint_code_index_under_test", SYNCER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def syncer():
    return _load_syncer_module()


class TestTemplateNoStaleAgentsRefs:
    """T4 钉扎①：模板真源（生成器源码与生成产物）不含失效 AGENTS §编号引用。"""

    def test_syncer_source_has_no_stale_numbered_refs(self):
        text = SYNCER_PATH.read_text(encoding="utf-8")
        matches = STALE_AGENTS_NUMBERED_REF.findall(text)
        assert not matches, f"生成器源码含失效 AGENTS §编号引用: {matches}"

    def test_panorama_source_has_no_stale_numbered_refs(self):
        text = PANORAMA_PATH.read_text(encoding="utf-8")
        matches = STALE_AGENTS_NUMBERED_REF.findall(text)
        assert not matches, f"全景生成器源码含失效 AGENTS §编号引用: {matches}"

    def test_generated_section_has_no_stale_refs_and_keeps_stable_anchors(self, syncer):
        section = syncer._generate_path_index_section(9, "_master-blueprint")
        assert not STALE_AGENTS_NUMBERED_REF.search(section), "生成产物含失效 §编号引用"
        # 稳定锚点在位：规则名（不写死 §编号）+ 同步短语（匹配器依赖）
        assert "RULE-DEPGRAPH" in section
        assert "RULE-PANORAMA" in section
        assert "蓝图-代码同步强制约定" in section

    def test_autogen_note_has_no_stale_refs(self, syncer):
        assert not STALE_AGENTS_NUMBERED_REF.search(syncer._AUTOGEN_NOTE)


class TestMarkerMatcherCoversOldAndNew:
    """T4 钉扎②：note 提取匹配器同时识别新旧模板行（迁移期重建不误吞人工 note）。"""

    def _extract_note_from(self, syncer, fixed_line: str) -> str:
        section = _STALE_SECTION_TEMPLATE.format(old_line=fixed_line)
        return syncer._extract_note(section)

    def test_old_template_line_recognized(self, syncer):
        assert self._extract_note_from(syncer, OLD_TEMPLATE_LINE) == "人工备注行：本模块测试先行。"

    def test_new_template_line_recognized(self, syncer):
        new_line = (
            "> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；"
            "验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。"
        )
        assert self._extract_note_from(syncer, new_line) == "人工备注行：本模块测试先行。"


class TestRebuildIdempotentAndInterruptSafe:
    """T4 钉扎③：旧模板蓝图重建后新文案落地、重跑零漂移、中断不损文件。"""

    def _write_stale_blueprint(self, bp: Path) -> None:
        stale_section = _STALE_SECTION_TEMPLATE.format(old_line=OLD_TEMPLATE_LINE)
        bp.write_text(_BP_HEAD + stale_section, encoding="utf-8", newline="\n")

    def test_rebuild_replaces_stale_line_then_converges(self, syncer, tmp_path):
        bp = tmp_path / "some_module" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        self._write_stale_blueprint(bp)

        changed_first, _ = syncer._process_blueprint(bp)
        assert changed_first is True
        rebuilt = bp.read_text(encoding="utf-8")
        assert not STALE_AGENTS_NUMBERED_REF.search(rebuilt), "重建后仍残留失效 §编号引用"
        assert "蓝图-代码同步强制约定" in rebuilt
        assert "人工备注行：本模块测试先行。" in rebuilt, "人工 note 被重建吞掉"
        assert 'version: "0.0.2"' in rebuilt, "实际改动未触发 version patch+1"

        changed_second, _ = syncer._process_blueprint(bp)
        assert changed_second is False, "第二遍重建仍报变更——幂等破坏"
        assert bp.read_text(encoding="utf-8") == rebuilt, "第二遍重跑产生 diff——幂等破坏"

    def test_interrupted_rebuild_leaves_file_intact(self, syncer, tmp_path, monkeypatch):
        bp = tmp_path / "some_module" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        self._write_stale_blueprint(bp)
        before = bp.read_text(encoding="utf-8")

        def _boom(*_args, **_kwargs):
            raise RuntimeError("模拟重建中断（写盘前崩溃）")

        monkeypatch.setattr(syncer, "atomic_write_safe", _boom)
        with pytest.raises(RuntimeError):
            syncer._process_blueprint(bp)
        assert bp.read_text(encoding="utf-8") == before, "中断后文件被半写破坏"

        # 中断恢复：解除故障后重跑收敛
        monkeypatch.undo()
        changed, _ = syncer._process_blueprint(bp)
        assert changed is True
        assert not STALE_AGENTS_NUMBERED_REF.search(bp.read_text(encoding="utf-8"))

    def test_empty_blueprint_skipped_without_crash(self, syncer, tmp_path):
        bp = tmp_path / "unknown_module" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        bp.write_text("# 仅有一个标题，无 frontmatter 无章节\n", encoding="utf-8", newline="\n")
        changed, actions = syncer._process_blueprint(bp)
        assert changed is False
        assert any("跳过" in a for a in actions)
        assert bp.read_text(encoding="utf-8").startswith("# 仅有一个标题")

    def test_malformed_injected_section_repaired_and_converges(self, syncer, tmp_path):
        """红蓝：被注入畸形表格/伪造路径/截断行的 AUTOGEN 段，重建治愈且重跑收敛。"""
        bp = tmp_path / "some_module" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        injected = (
            _BP_HEAD
            + "## 2. 已实现代码完整路径索引\n\n"
            + OLD_TEMPLATE_LINE
            + "\n> 蓝图声称的文件必须与磁盘实际一致。\n"
            + "> **AUTOGEN**：本表由 sync_blueprint_code_index.py 单向派生，禁止手写。\n"
            + "| `../../etc/passwd | 破行 | `src/nonexistent_injected_path.py` | ✅ 伪造 | 不闭合\n"
            + "| `|` 竖线注入 | | | \n"
            + "### 2.1 源码文件\n\n被截断的表格行 |||\n"
        )
        bp.write_text(injected, encoding="utf-8", newline="\n")

        changed_first, _ = syncer._process_blueprint(bp)
        assert changed_first is True
        repaired = bp.read_text(encoding="utf-8")
        assert "passwd" not in repaired and "伪造" not in repaired, "注入内容未被重建清除"
        assert repaired.count("## 2. 已实现代码完整路径索引") == 1, "章节被重建重复插入"
        assert not STALE_AGENTS_NUMBERED_REF.search(repaired)

        changed_second, _ = syncer._process_blueprint(bp)
        assert changed_second is False, "治愈后重跑仍报变更"
        assert bp.read_text(encoding="utf-8") == repaired
