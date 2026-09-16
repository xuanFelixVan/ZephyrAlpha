# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.governance.commit_gates.test_repo_state_observation
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_repo_state_observation.py — 裁定#279 同盲区门禁家族清偿的机证测试（2026-09-17）

门禁要判的命题是"本 commit 之后的仓库态"，不是"本机磁盘上碰巧有什么"。
本文件为家族四门各钉一组 post-commit 仓库态判定场景：

- SCHEMA-FILE-EXISTS：磁盘陈旧/他会话在途删除不误伤（存在面=index/HEAD）；
  存量悬空（HEAD 已有）不阻断本次提交人；真新增悬空仍硬拦。
- DOC-REF-BROKEN：链接目标只在 index（staged 未落盘）不误报断链；真断链仍拦。
- CAP-CONSISTENCY：他人落地批的存量欠账（HEAD 已在）不连坐后续触碰该 provider
  的批次（§8.14 实证形态）；本次新增违规仍硬拦。
- CONSUMERS-ACCURACY：warn-only 豁免钉——phantom 假警（磁盘陈旧场景）只出警告
  永不阻断（passed=True 恒成立）。

git 桩契约：``run_git(cmd)`` 按命令形态分发——``git show :path`` 返回 staged 内容、
``git show HEAD:path`` 返回 HEAD 内容、``git ls-files --cached -- path`` /
``git ls-tree HEAD -- path`` 返回存在性（输出行数布尔）。磁盘一律用空 tmp_path
模拟"目标不在本机磁盘"。
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.capability_consistency_gate import (  # noqa: E402
    make_capability_consistency_gate,
)
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import (  # noqa: E402
    make_doc_ref_broken_gate,
)
from zephyr.gov_enforcement.commit_gates.schema_file_exists_gate import (  # noqa: E402
    _YAML_REL,
    make_schema_file_exists_gate,
)

_YAML = "docs/03_modules/_cross_layer/database/business_data_categories.yaml"


class _R:
    def __init__(self, rc: int = 0, out: str = "") -> None:
        self.returncode = rc
        self.stdout = out


def _make_gateway(
    staged: dict[str, str] | None = None,
    head: dict[str, str] | None = None,
    index_has: set[str] | None = None,
    head_has: set[str] | None = None,
    project_root: Path | None = None,
):
    """构造仓库态 git 桩。index_has/head_has=存在的文件相对路径集合（磁盘上均不存在）。"""
    staged = staged or {}
    head = head or {}
    index_has = index_has or set()
    head_has = head_has or set()

    def _run_git(cmd):
        if cmd[:2] == ["git", "show"]:
            spec = cmd[2]
            if spec.startswith(":") and not spec.startswith("::"):
                rel = spec[1:]
                return _R(0, staged[rel]) if rel in staged else _R(1, "")
            if spec.startswith("HEAD:"):
                rel = spec[5:]
                return _R(0, head[rel]) if rel in head else _R(1, "")
        if cmd[:2] == ["git", "ls-files"]:
            rel = cmd[-1]
            return _R(0, f"{rel}\n" if rel in index_has else "")
        if cmd[:2] == ["git", "ls-tree"]:
            rel = cmd[-1]
            return _R(0, f"blob x\t{rel}\n" if rel in head_has else "")
        if cmd[:3] == ["git", "diff", "--cached"]:
            return _R(0, "\n".join(sorted(staged)) + ("\n" if staged else ""))
        return _R(1, "")

    gw = type("GW", (), {})()
    gw.run_git = _run_git
    gw.project_root = str(project_root)
    return gw


# ───────────────────────── SCHEMA-FILE-EXISTS ─────────────────────────

_CAT_OK = "- category_id: a\n  schema_file: schemas/in_index.py\n"
_CAT_DANGLING = "- category_id: b\n  schema_file: schemas/nowhere.py\n"
_YAML_HEAD_ONLY_OK = "- category_id: legacy\n  schema_file: schemas/legacy_missing.py\n"


def test_schema_target_absent_on_disk_but_in_index_passes(tmp_path):
    """磁盘陈旧场景：schema 文件只 staged 未 checkout（落地 worktree 形态）→ 不误伤。"""
    yaml_text = _CAT_OK
    gw = _make_gateway(
        staged={_YAML: yaml_text},
        head={_YAML: yaml_text},
        index_has={"schemas/in_index.py"},
        head_has={"schemas/in_index.py"},
        project_root=tmp_path,
    )
    ok, detail = make_schema_file_exists_gate().check(gw, [_YAML])
    assert ok is True, detail


def test_schema_in_flight_deletion_on_disk_does_not_block(tmp_path):
    """他会话在途删除场景：文件磁盘已没、index/HEAD 还在 → 仓库态存在，不阻断。"""
    gw = _make_gateway(
        staged={_YAML: _CAT_OK},
        index_has={"schemas/in_index.py"},
        head_has={"schemas/in_index.py"},
        project_root=tmp_path,
    )
    ok, detail = make_schema_file_exists_gate().check(gw, [_YAML])
    assert ok is True, detail


def test_schema_genuinely_new_dangling_ref_blocks(tmp_path):
    """真违规不放过：本次新增条目引用仓库态（index+HEAD+磁盘）都不存在的文件 → 拦。"""
    gw = _make_gateway(
        staged={_YAML: _CAT_OK + _CAT_DANGLING},
        head={_YAML: _CAT_OK},
        index_has={"schemas/in_index.py"},
        head_has={"schemas/in_index.py"},
        project_root=tmp_path,
    )
    ok, detail = make_schema_file_exists_gate().check(gw, [_YAML])
    assert ok is False
    assert "nowhere.py" in detail


def test_schema_preexisting_dangling_in_head_warns_not_blocks(tmp_path):
    """存量连坐治本：悬空引用 HEAD 里早已有（他人欠账）→ 不阻断本次提交人。"""
    yaml_text = _CAT_OK + _CAT_DANGLING
    gw = _make_gateway(
        staged={_YAML: yaml_text},
        head={_YAML: yaml_text},
        index_has={"schemas/in_index.py"},
        head_has={"schemas/in_index.py"},
        project_root=tmp_path,
    )
    ok, detail = make_schema_file_exists_gate().check(gw, [_YAML])
    assert ok is True, detail


# ───────────────────────── DOC-REF-BROKEN ─────────────────────────

_MD_REL = "docs/guide/new_page.md"
_MD_STAGED = textwrap.dedent(
    """\
    # 新页
    [同批新增目标](./staged_target.md)
    """
)
_MD_WITH_BROKEN = textwrap.dedent(
    """\
    # 新页
    [真断链](./missing_everywhere.md)
    """
)


def test_doc_link_target_staged_only_not_broken(tmp_path):
    """磁盘陈旧场景：链接目标同批 staged 但未落盘 → 仓库态存在，不误报断链。"""
    md_dir = (_MD_REL.rsplit("/", 1))[0]
    target_rel = f"{md_dir}/staged_target.md"
    gw = _make_gateway(
        staged={_MD_REL: _MD_STAGED, target_rel: "# t\n"},
        index_has={target_rel},
        project_root=tmp_path,
    )
    ok, detail = make_doc_ref_broken_gate().check(gw, [_MD_REL])
    assert ok is True, detail


def test_doc_genuinely_missing_link_still_blocks(tmp_path):
    """真断链不放过：目标在 index/HEAD/磁盘全都不存在 → 拦。"""
    gw = _make_gateway(
        staged={_MD_REL: _MD_WITH_BROKEN},
        project_root=tmp_path,
    )
    ok, detail = make_doc_ref_broken_gate().check(gw, [_MD_REL])
    assert ok is False
    assert "missing_everywhere.md" in detail


# ───────────────────────── CAP-CONSISTENCY ─────────────────────────

_PROVIDER_REL = "src/zephyr/data/implementations/fake_provider.py"


def _provider(routes: set[str], meta: set[str]) -> str:
    routes_txt = ", ".join(f'"{r}": "_fetch_{r}"' for r in sorted(routes))
    meta_txt = ", ".join(f'"{m}"' for m in sorted(meta))
    return textwrap.dedent(
        f"""\
        _ROUTES = {{{routes_txt}}}

        class P:
            meta: IngestProviderMeta = IngestProviderMeta(
                name="p", display_name="t", auth_type="anonymous",
                requires_process=False, thread_safety="shared", rate_limit_default=0,
                capabilities=[{meta_txt}],
            )
        """
    )


def test_cap_inherited_debt_from_head_does_not_block(tmp_path):
    """§8.14 连坐形态治本钉：他人落地批漏声明的存量欠账（HEAD 已在）+本次内容
    未新增违规 → 不阻断后续任何触碰该 provider 的批次（含队列整文件重放）。"""
    head_text = _provider({"cap_old", "cap_shared"}, {"cap_old"})
    # staged=HEAD 原样重放（队列 serializer 场景）+ 顺手修掉旧欠账之外零改动
    gw = _make_gateway(
        staged={_PROVIDER_REL: head_text},
        head={_PROVIDER_REL: head_text},
        project_root=tmp_path,
    )
    ok, detail = make_capability_consistency_gate().check(gw, [_PROVIDER_REL], session_id=None)
    assert ok is True, detail


def test_cap_new_violation_still_blocks(tmp_path):
    """本次新增违规（死声明）仍硬拦。"""
    head_text = _provider({"cap_old", "cap_shared"}, {"cap_old"})
    staged_text = _provider({"cap_old", "cap_shared"}, {"cap_old", "cap_new"})
    gw = _make_gateway(
        staged={_PROVIDER_REL: staged_text},
        head={_PROVIDER_REL: head_text},
        project_root=tmp_path,
    )
    ok, detail = make_capability_consistency_gate().check(gw, [_PROVIDER_REL], session_id=None)
    assert ok is False
    assert "cap_new" in detail


# ───────────────────────── CONSUMERS-ACCURACY（warn-only 豁免钉）─────────────────────────

def test_consumers_accuracy_never_blocks_even_on_phantom(tmp_path, monkeypatch):
    """warn-only 豁免钉（裁定#279 家族清偿 2026-09-17）：磁盘陈旧场景出 phantom
    假警也只 warn，passed=True 恒成立——无阻断权即无连坐。"""
    from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import (
        make_consumers_accuracy_gate,
    )

    rel = "scripts/governance/fake_mod.py"
    content = textwrap.dedent(
        """\
        # [CONSUMERS] scripts/gone_with_the_wind.py（ghost_fn）
        def real_fn():
            return 1
        """
    )
    gw = _make_gateway(
        staged={rel: content},
        index_has={rel},
        project_root=tmp_path,
    )
    monkeypatch.setattr(
        "zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate._SCAN_PREFIXES",
        ("scripts/governance/",),
    )
    ok, detail = make_consumers_accuracy_gate().check(gw, [rel])
    assert ok is True  # warn-only：无论检出什么都放行
    assert isinstance(detail, str)
