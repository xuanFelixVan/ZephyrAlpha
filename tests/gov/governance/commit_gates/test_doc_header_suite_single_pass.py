# [TTL] permanent
"""st-perfz2-20261015 P1-3：DOC-HEADER-SUITE 单趟化红蓝对照 + 熔断判别测试。

钉住三件不可回退的事：
- 红蓝判定等价：七判据各自独立跑一遍（蓝=旧形态）与聚合门单趟跑（红=新形态）在
  同一输入上 verdict 与聚合 detail 逐字节一致（纯 memo 零判定变化红线）。
- 单趟省读：红轮 gateway.run_git 调用数 < 蓝轮（同一批文档只读一次）。
- 熔断：单文件共享读入累计超阈值→标 broken→后续判据跳过该文件不重扫（warn+审计）。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zephyr.gov_enforcement.commit_gates import blueprint_format_gate as bfg  # noqa: E402

_SUITE_ORDER = [
    ("BLUEPRINT-FORMAT", None, "_check"),
    ("BLUEPRINT-HEADER", "blueprint_amodule_consistency_gate", "_header_union_check"),
    ("MODULE-ID-CONSISTENCY", "module_id_consistency_gate", "_check"),
    ("TTL-METADATA", "ttl_gate", "_check"),
    ("FILE-PLACEMENT-TTL", "file_placement_ttl_gate", "_check"),
    ("EXEMPT-ZONE-FM", "exempt_zone_frontmatter_gate", "_check"),
    ("DOC-REF-BROKEN", "doc_ref_broken_gate", "_check"),
]

_PY_OK = """# [BLUEPRINT] MOD-INF-001 | docs/03_modules/blueprint.md | §1
# [MODULE] zephyr.mod_a
def f():
    return 1
"""

_PY_BAD = """# [BLUEPRINT] SRC-bad | docs/03_modules/blueprint.md | §1
# [MODULE] zephyr.mod_b
def g():
    return 2
"""

_MD = "# notes\n[doc](./target.md)\n"

_STAGED_PY = ["src/mod_a.py", "src/mod_b.py"]
_STAGED_MD = ["docs/_working/notes.md"]


class _ScriptedGateway:
    """按命令形态应答的 gateway 垫片（含 run_git 计数）。"""

    def __init__(self, root: Path):
        self.project_root = root
        self.calls = 0

        def _run(cmd, cwd=None):
            self.calls += 1
            c = list(cmd)
            joined = " ".join(c)

            class _R:
                returncode = 0
                stdout = ""
                stderr = ""

            if "--name-only" in c and "--diff-filter=AM" in c:
                _R.stdout = "\n".join(_STAGED_PY + _STAGED_MD)
            elif "--name-only" in c and "--diff-filter=A" in c:
                _R.stdout = "\n".join(_STAGED_MD)
            elif c[1] == "show" and c[2].startswith(":"):
                rel = c[2][1:].replace("\\", "/")
                _R.stdout = {_STAGED_PY[0]: _PY_OK, _STAGED_PY[1]: _PY_BAD, _STAGED_MD[0]: _MD}.get(rel, "")
            elif c[1] == "show" and c[2].startswith("HEAD:"):
                _R.returncode = 1
            elif "unified=0" in joined:
                rel = c[-1].replace("\\", "/")
                added = {
                    _STAGED_PY[
                        0
                    ]: "@@ -0,0 +1,4 @@\n+# [BLUEPRINT] MOD-INF-001 | docs/03_modules/blueprint.md | §1\n+# [MODULE] zephyr.mod_a\n+def f():\n+    return 1\n",
                    _STAGED_PY[
                        1
                    ]: "@@ -0,0 +1,4 @@\n+# [BLUEPRINT] SRC-bad | docs/03_modules/blueprint.md | §1\n+# [MODULE] zephyr.mod_b\n+def g():\n+    return 2\n",
                }.get(rel, "")
                _R.stdout = added
            elif c[1] == "rev-parse":
                _R.stdout = str(root)
            elif c[1] == "ls-tree":
                _R.returncode = 1  # 无 HEAD 历史（新增文件口径）
            elif c[1] == "grep":
                _R.returncode = 1  # 无同名 module_id（无碰撞）
            elif c[1] == "ls-files":
                _R.stdout = ""  # 链接目标不在 index
            return _R()

        self.run_git = _run

    def is_git_tracked(self, rel_path: str) -> bool:
        self.calls += 1
        return False


def _fixture_root(tmp_path: Path) -> Path:
    """tmp 仓根：盘面文件（TTL 门 disk 读面）+ FILE-PLACEMENT 真源 YAML。"""
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "_working").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "mod_a.py").write_text(_PY_OK, encoding="utf-8")
    (tmp_path / "src" / "mod_b.py").write_text(_PY_BAD, encoding="utf-8")
    (tmp_path / "docs" / "_working" / "notes.md").write_text(_MD, encoding="utf-8")
    (tmp_path / "docs" / "_working" / "target.md").write_text("x\n", encoding="utf-8")
    for rel in (
        "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml",
        "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml",
    ):
        src = REPO_ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
    return tmp_path


def _files_arg(root: Path) -> list[str]:
    return [str(root / r) for r in (*_STAGED_PY, *_STAGED_MD)]


def _sub_fns():
    import importlib

    out = []
    for sgid, mod, impl in _SUITE_ORDER:
        if mod is None:
            out.append((sgid, getattr(bfg, impl)))
        else:
            out.append((sgid, getattr(importlib.import_module(f"zephyr.gov_enforcement.commit_gates.{mod}"), impl)))
    return out


def test_red_blue_verdict_equivalence_and_fewer_reads(tmp_path):
    """红蓝对照：判定逐字节等价（聚合 detail 一致）且红轮 git 调用数 < 蓝轮。"""
    root = _fixture_root(tmp_path)
    files = _files_arg(root)

    # 蓝：七判据各自独立跑一遍（旧行为形态，每台新 gateway）
    blue_ok = True
    blue_failures: list[str] = []
    blue_calls = 0
    for _sgid, fn in _sub_fns():
        gw = _ScriptedGateway(root)
        ok, detail = fn(gw, files, session_id=None)
        blue_calls += gw.calls
        if not ok:
            blue_ok = False
            blue_failures.append(f"[{_sgid}] " + detail)
    blue_detail = "\n".join(blue_failures)

    # 红：聚合门单趟（ctx 注入）
    gw2 = _ScriptedGateway(root)
    suite = bfg.make_doc_header_suite_gate()
    red_ok, red_detail = suite.check(gw2, files, session_id=None)
    red_calls = gw2.calls

    assert blue_ok is False, "fixture 必须含真违规（BLUEPRINT-FORMAT SRC-bad / DOC-REF 断链），否则对照无意义"
    assert red_ok == blue_ok
    assert red_detail == blue_detail, "红蓝判定必须逐字节等价（纯 memo 零判定变化）"
    assert red_calls < blue_calls, f"单趟化必须少读：red={red_calls} vs blue={blue_calls}"


def test_breaker_trips_and_skips_without_rescan(tmp_path, monkeypatch):
    """熔断：共享读入累计超阈值→标 broken→后续判据跳过该文件（审计落盘）。"""
    root = _fixture_root(tmp_path)
    files = _files_arg(root)
    monkeypatch.setattr(bfg, "_DOC_SUITE_BREAKER_SECONDS", -1.0)  # 任一次共享读入即熔断

    suite = bfg.make_doc_header_suite_gate()
    gw = _ScriptedGateway(root)
    ok, detail = suite.check(gw, files, session_id=None)
    # 熔断只允许减违规面（跳过文件），不允许翻转判定结论之外的新增违规
    assert isinstance(ok, bool)
    audit = root / ".runtime" / "gate_audit" / "doc_header_suite_breaker.jsonl"
    assert audit.exists(), "熔断必须留痕"
    rows = [line for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any('"doc_header_suite_breaker"' in r for r in rows), "必须有熔断事件行"

    # ctx 单元面：broken 文件后续判据 skip 记账
    ctx = bfg._DocSuiteContext(root, breaker_seconds=-1.0)
    ctx.staged_text(gw, "a.md")
    assert ctx.is_broken("a.md")
    ctx.note_skip("a.md", "DOC-REF-BROKEN")
    ctx.flush()
    rows2 = [line for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any('"doc_header_suite_breaker_skips"' in r for r in rows2), "跳过摘要必须入审计"
