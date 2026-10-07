# [A_test] module_id: MOD-GOV_reconciler_file_ops_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.commit_gates.test_reconciler_file_ops_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/commit_gates/test_reconciler_file_ops_gate.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（假 gateway 注入 diff/HEAD/index 面，零 git 真仓零生产写入）；
#              own-diff 作用域三态钉死：modified 只判新增行/新文件保持全文/无新增行放行
# [MODIFY-GUARD] C338 own-diff 化回归闸：存量违规行误报复辟（假新增）即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""RECONCILER-FILE-OPS own-diff 作用域永久尺（C338，st-mastertc-l2）。

生产侧 scan_own_diff_for_bare_primitives（#ARCH-GATE-OWN-SCOPE 同族口径）：
modified 文件只判本包新增行（unified=0 diff 行号集合化），新文件保持全文扫描。
本尺钉死三态，防"format 重排致伪新增"（2026-08-20 波3 同族病形）回潮。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (
    scan_own_diff_for_bare_primitives,
)

_REL = "src/zephyr/governance/sample_mod.py"


class _Result:
    def __init__(self, returncode: int = 0, stdout: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout


class _FakeGateway:
    """最小 gateway 替身：HEAD/index/diff 三面注入（_read_head_file/_read_staged_file/
    _get_added_lines 的 git 面；S1 视图分支不在本尺范围）。"""

    def __init__(
        self,
        root: Path,
        *,
        head_text: str | None,
        staged_text: str | None,
        diff: str,
    ) -> None:
        self.project_root = str(root)
        self._head = head_text
        self._staged = staged_text
        self._diff = diff

    def run_git(self, args: list[str]) -> _Result:
        cmd = " ".join(args)
        if cmd.startswith("git show HEAD:"):
            return _Result(0, self._head) if self._head is not None else _Result(1, "")
        if cmd.startswith("git show :"):
            return _Result(0, self._staged) if self._staged is not None else _Result(1, "")
        if cmd.startswith("git diff --cached"):
            return _Result(0, self._diff)
        return _Result(1, "")


def _write_disk(root: Path, body: str) -> None:
    p = root / _REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


HEAD_BODY = "import os\n\n\ndef legacy(x):\n    os.remove(x)\n"
DIFF_NEW_VIOLATION = f"diff --git a/{_REL} b/{_REL}\n@@ -4,1 +4,2 @@\n     os.remove(x)\n+    shutil.rmtree(p)\n"


def test_modified_only_added_lines_judged(tmp_path: Path) -> None:
    """own-diff 主案：存量违规行（HEAD 已有 os.remove）不误报，仅新增行（shutil.rmtree）拦。"""
    staged = HEAD_BODY + "    shutil.rmtree(p)\n"
    _write_disk(tmp_path, staged)
    gateway = _FakeGateway(tmp_path, head_text=HEAD_BODY, staged_text=staged, diff=DIFF_NEW_VIOLATION)
    hits = scan_own_diff_for_bare_primitives(gateway, _REL, tmp_path)
    assert len(hits) == 1, f"存量行必须零误报、新增行必须命中，实得 {hits!r}"
    lineno, snippet = hits[0]
    assert lineno == 5 and "shutil.rmtree" in snippet


def test_new_file_keeps_full_text_scan(tmp_path: Path) -> None:
    """新文件（HEAD 无）＝全文扫描语义不变窄：两处存量形态违规全数命中。"""
    new_rel = "src/zephyr/governance/sample_new.py"
    body = "import os\nimport shutil\nos.remove(a)\nshutil.rmtree(b)\n"
    p = tmp_path / new_rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    gateway = _FakeGateway(tmp_path, head_text=None, staged_text=body, diff="")
    hits = scan_own_diff_for_bare_primitives(gateway, new_rel, tmp_path)
    assert len(hits) == 2, f"新文件全文扫描必须两处全命中，实得 {hits!r}"


def test_no_added_lines_passes(tmp_path: Path) -> None:
    """modified 而无新增行（format 重排/无关触碰）＝own-diff 放行，存量违规不浮出。"""
    _write_disk(tmp_path, HEAD_BODY)
    gateway = _FakeGateway(tmp_path, head_text=HEAD_BODY, staged_text=HEAD_BODY, diff="")
    assert scan_own_diff_for_bare_primitives(gateway, _REL, tmp_path) == []


@pytest.mark.parametrize(
    ("head", "staged", "diff"),
    [
        (None, None, ""),  # 全 git 面不可得 → 新文件口径退磁盘全文（盘也无=零命中放行）
        (HEAD_BODY, None, DIFF_NEW_VIOLATION),  # index 面缺失 → 退磁盘 docstring 上下文
    ],
)
def test_fail_open_degraded_faces(head, staged, diff, tmp_path: Path) -> None:
    """git 面降级 fail-open：不抛异常、按退化口径放行或退旧口径（gate ERROR_CONTRACT）。"""
    gateway = _FakeGateway(tmp_path, head_text=head, staged_text=staged, diff=diff)
    hits = scan_own_diff_for_bare_primitives(gateway, _REL, tmp_path)
    assert isinstance(hits, list)
