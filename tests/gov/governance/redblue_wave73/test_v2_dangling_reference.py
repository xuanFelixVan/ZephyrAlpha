# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v2_dangling_reference
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 V2 断链引用：ARCH-REFERENCE 面拦未登记 #ARCH-NNN 引用（防御在）。

攻击：文件新增 #ARCH-99999999 引用而不在 architecture_issue_registry.yaml 登记
（grep-and-claim 占位）。防御：ARCH-REFERENCE 门 fail-closed 阻断新增悬空引用。
真源布置：工作区 registry（tmp 重锚）= commit 后新真源（模块裁定）；
对照组：已登记编号的引用放行。
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import yaml

from zephyr.gov_enforcement.commit_gates.arch_reference_gate import (
    _REGISTRY_REL,
    make_arch_reference_gate,
)

_REGISTRY_SUB = Path(*_REGISTRY_REL.split("/"))


def _make_root(tmp_path: Path, registered: list[str]) -> Path:
    root = tmp_path / "projroot"
    reg = root / _REGISTRY_SUB
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        yaml.safe_dump({"entries": [{"issue_id": f"#ARCH-{n}"} for n in registered]}, allow_unicode=True),
        encoding="utf-8",
    )
    # 独立 git 仓：截断 git 目录上溯（tmp 在宿主仓内），HEAD 语义归零 → L2 原子性跳过
    import subprocess

    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    return root


def _check(root: Path, rel: str, content: str) -> tuple[bool, str]:
    probe = root / rel
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(content, encoding="utf-8")
    gw = MagicMock()
    gw.project_root = root
    # helpers 以 os.path.isfile(files[i]) 过滤——必须传真实存在的绝对路径
    return make_arch_reference_gate().check(gw, [str(probe)])


def test_unregistered_arch_reference_blocks(tmp_path):
    root = _make_root(tmp_path, ["0001"])
    passed, detail = _check(root, "docs/note.md", "见 #ARCH-99999999 的设计\n")
    assert passed is False, "未登记 #ARCH 引用放行——grep-and-claim 占位得手（V2 防御缺位）"
    assert "ARCH_REFERENCE_VIOLATION" in detail and "99999999" in detail


def test_registered_arch_reference_passes(tmp_path):
    root = _make_root(tmp_path, ["0001", "0002"])
    passed, detail = _check(root, "docs/note2.md", "见 #ARCH-0001 的设计\n")
    assert passed is True, f"已登记引用被误伤：{detail}"


def test_missing_registry_fail_closed(tmp_path):
    root = tmp_path / "empty_root"
    root.mkdir()
    gw = MagicMock()
    gw.project_root = root
    probe = root / "x.md"
    probe.write_text("#ARCH-0001\n", encoding="utf-8")
    passed, detail = make_arch_reference_gate().check(gw, ["x.md"])
    assert passed is False and "fail-closed" in detail, "registry 缺席未 fail-closed——门禁静默失效面"
