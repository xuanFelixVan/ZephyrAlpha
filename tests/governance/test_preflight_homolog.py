"""M2.1/M2.3 预检落地同源化单测（st-qcure-20260925 施工线B）。

核心回归=CREATE-GUARD 23 笔 no-token 死因的精确复现：新文件 token 只登记在会话
盘面册、注册表不在袋内 → 落地面=HEAD 册（token 缺）→ 预检必须 BLOCK（改前读盘面
册假绿放行、落地侧冤杀）。TRANSLATION-COVERAGE 内联适配同构三例。零真仓依赖：
run_git 面由 _HeadGateway 仿真（ls-tree + git show 两点契约），项目根=tmp_path
（测试隔离，不写生产路径）。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_preflight import (
    _ESCAPE_HINTS,
    _INLINE_PREFLIGHT_CHECKS,
    run_preflight,
)

_CAP_REG = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_TRANS_REG = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"

# 15 字段合规头（trae_047 a_full.required）——PASS 用例须过 _check_field_header
_FIELD_NAMES = (
    "BLUEPRINT",
    "MODULE",
    "DOMAIN",
    "DEPENDENCIES",
    "CONSUMERS",
    "STARTUP",
    "MATURITY",
    "INVARIANTS",
    "MODIFY-GUARD",
    "STABILITY",
    "SAFETY",
    "AI_AUTONOMY",
    "ERROR_CONTRACT",
    "TESTS",
    "TTL",
)
_COMPLIANT_PY = "\n".join(f"# [{n}] qcure-fixture" for n in _FIELD_NAMES) + "\nVALUE = 1\n"
_PLAIN_ZH = "这个门禁负责拦截未登记大白话简介的新建能力模块文件"


@dataclass
class _GitResult:
    """text 模式 CompletedProcess 最小投影（对齐 run_git 文本契约）。"""

    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


class _HeadGateway:
    """run_git/project_root 两点契约：HEAD 面由 head_files 仿真（落地仿真态 git 面）。

    2026-09-30 契约补齐：QMine M5 矿③给 _head_registry_yaml_data 挂内容寻址 memo 后，
    预检读 HEAD 册先走单路径 `git ls-tree HEAD -- <rel>` 取 blob sha（缓存键）——
    本仿真此前只实现 `ls-tree -r` 递归形态，单路径形态落 unsupported → 两内联 gate
    全体 degraded=假阴性（M2.1 死因复现用例失去判别力）。补齐单路径 blob 契约。
    """

    def __init__(self, root: Path, head_files: dict[str, str] | None = None) -> None:
        self.project_root = root
        self._head = dict(head_files or {})

    def run_git(self, cmd: list[str]) -> _GitResult:
        if cmd[:3] == ["git", "ls-tree", "-r"]:
            return _GitResult(stdout="\n".join(sorted(self._head)))
        if cmd[:2] == ["git", "ls-tree"] and len(cmd) >= 5 and cmd[2] == "HEAD" and cmd[3] == "--":
            import hashlib

            rel = cmd[4]
            if rel in self._head:
                sha = hashlib.sha1(self._head[rel].encode("utf-8")).hexdigest()
                return _GitResult(stdout=f"100644 blob {sha}\t{rel}")
            return _GitResult(returncode=1, stderr=f"fatal: path '{rel}' does not exist in 'HEAD'")
        if cmd[:2] == ["git", "show"] and len(cmd) >= 3:
            rel = cmd[2].split(":", 1)[1]
            if rel in self._head:
                return _GitResult(stdout=self._head[rel])
            return _GitResult(returncode=1, stderr="fatal: not in HEAD")
        return _GitResult(returncode=1, stderr="unsupported")


def _cap_yaml(registered: list[str]) -> str:
    lines = ["creation_tokens:"]
    for p in registered:
        lines += [f'  - file: "{p}"', '    token: "auto-qcure"']
    return "\n".join(lines) + "\n"


def _trans_yaml(registered: list[str]) -> str:
    lines = ["entries:"]
    for p in registered:
        lines += [f'  - module_path: "{p}"', '    name_zh: "探针模块"', f'    plain_zh: "{_PLAIN_ZH}"']
    return "\n".join(lines) + "\n"


def _mk_new_py(root: Path, rel: str) -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_COMPLIANT_PY, encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# M2.1 CREATE-GUARD 落地同源化
# ---------------------------------------------------------------------------


def test_create_guard_blocks_token_only_on_session_disk_registry(tmp_path):
    """死因精确复现：token 只在盘面册、注册表不在袋 → 落地面=HEAD 册缺 → 预检 BLOCK。"""
    new_rel = "src/zephyr/qcure_probe/mod_x.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    # 盘面册（会话口径）已登记 token——改前口径据此放行=假绿
    (tmp_path / _CAP_REG).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _CAP_REG).write_text(_cap_yaml([new_rel]), encoding="utf-8")
    # HEAD 册（落地仿真态）无该 token
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([])})
    result = run_preflight(gw, [new_abs], "st-qcure-20260925", specs=[])
    assert result.blocking
    finding = next(f for f in result.findings if f.gate_id == "CREATE-GUARD")
    assert new_rel in finding.detail
    # 处方=登记命令模板（含裁定#375 merge_evaluation 一句话）
    assert "batch_creation_tokens.py" in finding.escape_hint
    assert "--merge-evaluation" in finding.escape_hint


def test_create_guard_passes_token_in_head_registry(tmp_path):
    """token 已在 HEAD 册（落地面同源）→ PASS。"""
    new_rel = "src/zephyr/qcure_probe/mod_x.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([new_rel])})
    result = run_preflight(gw, [new_abs], "s1", specs=[])
    assert not result.blocking, result.render_report("s1")


def test_create_guard_passes_registry_in_bag_uses_bag_bytes(tmp_path):
    """注册表 ∈ 袋 → 用袋内容（盘上字节=落地物化）判 PASS（HEAD 旧册无 token 也不假红）。"""
    new_rel = "src/zephyr/qcure_probe/mod_x.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    (tmp_path / _CAP_REG).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _CAP_REG).write_text(_cap_yaml([new_rel]), encoding="utf-8")
    # HEAD 册=被追踪的旧版（无该 token）——袋内新版落地物化后 token 补齐；
    # 若适配器误用 HEAD 面（无 token）应 BLOCK，本用例 PASS 即证袋面胜出
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([])})
    result = run_preflight(gw, [new_abs, str(tmp_path / _CAP_REG)], "s1", specs=[])
    assert not result.blocking, result.render_report("s1")


def test_create_guard_head_registry_unreadable_degrades(tmp_path):
    """HEAD 册不可读且不在袋=无法仿真落地面 → degraded 不阻断（锁内 fail-closed 兜底）。"""
    new_rel = "src/zephyr/qcure_probe/mod_x.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    gw = _HeadGateway(tmp_path, head_files={})
    result = run_preflight(gw, [new_abs], "s1", specs=[])
    assert not result.blocking
    assert "CREATE-GUARD" in result.degraded


# ---------------------------------------------------------------------------
# M2.3 TRANSLATION-COVERAGE 内联适配（同构三例）
# ---------------------------------------------------------------------------


def test_translation_blocks_entry_only_on_session_disk_registry(tmp_path):
    """同构复现：简介条目只在盘面翻译册、册不在袋 → HEAD 面=缺 → 预检 BLOCK。"""
    new_rel = "src/zephyr/qcure_probe/mod_y.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    (tmp_path / _TRANS_REG).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _TRANS_REG).write_text(_trans_yaml([new_rel]), encoding="utf-8")
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([new_rel]), _TRANS_REG: _trans_yaml([])})
    result = run_preflight(gw, [new_abs], "s1", specs=[])
    assert result.blocking
    finding = next(f for f in result.findings if f.gate_id == "TRANSLATION-COVERAGE")
    assert new_rel in finding.detail
    assert "add_module_translation.py" in finding.escape_hint


def test_translation_passes_entry_in_head_registry(tmp_path):
    """简介条目已在 HEAD 翻译册 → PASS。"""
    new_rel = "src/zephyr/qcure_probe/mod_y.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([new_rel]), _TRANS_REG: _trans_yaml([new_rel])})
    result = run_preflight(gw, [new_abs], "s1", specs=[])
    assert not result.blocking, result.render_report("s1")


def test_translation_passes_registry_in_bag_uses_bag_bytes(tmp_path):
    """翻译册 ∈ 袋 → 用袋内容判 PASS（HEAD 旧册缺该条目也不假红）。"""
    new_rel = "src/zephyr/qcure_probe/mod_y.py"
    new_abs = _mk_new_py(tmp_path, new_rel)
    (tmp_path / _TRANS_REG).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / _TRANS_REG).write_text(_trans_yaml([new_rel]), encoding="utf-8")
    # HEAD 翻译册=被追踪旧版（无该条目）——袋内新版落地物化后补齐；误用 HEAD 面应 BLOCK
    gw = _HeadGateway(tmp_path, head_files={_CAP_REG: _cap_yaml([new_rel]), _TRANS_REG: _trans_yaml([])})
    result = run_preflight(gw, [new_abs, str(tmp_path / _TRANS_REG)], "s1", specs=[])
    assert not result.blocking, result.render_report("s1")


# ---------------------------------------------------------------------------
# 注册面与处方文案
# ---------------------------------------------------------------------------


def test_inline_adapters_registered():
    ids = {gid for gid, _fn in _INLINE_PREFLIGHT_CHECKS}
    assert {"CREATE-GUARD", "NO-BARE-SQL", "TRANSLATION-COVERAGE"} <= ids


def test_escape_hints_prescriptions_updated():
    cap = _ESCAPE_HINTS["CREATE-GUARD"]
    assert "batch_creation_tokens.py" in cap and "--merge-evaluation" in cap
    pp = _ESCAPE_HINTS["PROTECTED-PATHS"]
    # M3 双通道口径：ARCH-APPROVAL 标记 或 活跃裁定 approved_paths
    assert "[ARCH-APPROVAL:" in pp and "approved_paths" in pp and "ruling_registry.yaml" in pp
    tc = _ESCAPE_HINTS["TRANSLATION-COVERAGE"]
    assert "add_module_translation.py" in tc and "--plain-zh" in tc
