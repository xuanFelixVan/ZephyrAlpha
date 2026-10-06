# [MODULE] tests.skill.test_skill_factory_trigger_cas
# [DOMAIN] D_AUTONOMY_CORE
# [MATURITY] production
# [TTL] permanent
"""skill_factory._update_trigger_table CAS 防吞写测试（#ARCH-WORKTREE-WRITE-INTEGRITY-001 P1-1）。

复现 #71 场景：read-modify-write 窗口内文件被并发修改 → 放弃写入+落审计，
他人改动零丢失。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import zephyr.autonomy_core.skills.skill_factory as sf


class _FakePath:
    """模拟目标文件：first_read 后内容被第三方推进。"""

    def __init__(self, real: Path, hijack_on_second_read: bool):
        self._real = real
        self._hijack = hijack_on_second_read
        self._reads = 0

    def exists(self) -> bool:
        return True

    def read_text(self, encoding: str = "utf-8") -> str:
        self._reads += 1
        if self._hijack and self._reads >= 2:
            # 第二次读（CAS 重读）时返回并发修改后的内容
            return self._real.read_text(encoding=encoding) + "| other | session-write |\n"
        return self._real.read_text(encoding=encoding)

    def write_text(self, content: str, encoding: str = "utf-8") -> int:
        return self._real.write_text(content, encoding=encoding)


@pytest.fixture
def target(tmp_path: Path) -> Path:
    f = tmp_path / "AGENTS.md"
    f.write_text("# head\n\n| a | b | c |\n| d | e | f |\n", encoding="utf-8")
    return f


def _audit_rows(root: Path) -> list[dict]:
    p = root / ".runtime" / "audit" / "skill_factory_cas.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_cas_abort_on_concurrent_modification(target: Path, tmp_path: Path, monkeypatch) -> None:
    """读写窗口内第三方推进文件 → CAS 放弃写入 + 审计，他人内容零丢失。"""
    fake = _FakePath(target, hijack_on_second_read=True)
    monkeypatch.setattr(sf, "_AGENTS_MD_PATH", fake)
    monkeypatch.setattr("zephyr.shared.io.paths.REPO_ROOT", tmp_path)

    sf.SkillFactory()._update_trigger_table("my-module")

    content = target.read_text(encoding="utf-8")
    assert "my-module" not in content  # 未写入
    assert "| d | e | f |" in content  # 原内容完好
    rows = _audit_rows(tmp_path)
    assert any(r["event"] == "cas_abort" for r in rows)


def test_normal_insert_when_no_race(target: Path, tmp_path: Path, monkeypatch) -> None:
    """无并发修改 → 正常插入触发表条目。"""
    fake = _FakePath(target, hijack_on_second_read=False)
    monkeypatch.setattr(sf, "_AGENTS_MD_PATH", fake)
    monkeypatch.setattr("zephyr.shared.io.paths.REPO_ROOT", tmp_path)

    sf.SkillFactory()._update_trigger_table("my-module")

    content = target.read_text(encoding="utf-8")
    assert "| my-module | my-module | implementer |" in content
    assert "| d | e | f |" in content


def test_idempotent_existing_entry(target: Path, tmp_path: Path, monkeypatch) -> None:
    """条目已存在 → 幂等跳过不重复插入。"""
    target.write_text(
        "# head\n\n| a | b | c |\n| my-module | my-module | implementer |\n",
        encoding="utf-8",
    )
    fake = _FakePath(target, hijack_on_second_read=False)
    monkeypatch.setattr(sf, "_AGENTS_MD_PATH", fake)
    monkeypatch.setattr("zephyr.shared.io.paths.REPO_ROOT", tmp_path)

    sf.SkillFactory()._update_trigger_table("my-module")
    content = target.read_text(encoding="utf-8")
    assert content.count("my-module") == 2  # 仅原有那一行（每行两处提及）
