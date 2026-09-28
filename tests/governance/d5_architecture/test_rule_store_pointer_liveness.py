# [A_test] module_id: MOD-GOV_rule_store_pointer_liveness_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.d5_architecture.test_rule_store_pointer_liveness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths（仅取 MAIN_REPO_ROOT 数据卷锚点）
# [CONSUMERS] —（pytest 采集即消费者；波 1A.5 出口判据"禁留死指针"的测试化身）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# [INVARIANTS] 永久规则册（docs/01_policies_and_standards/rules/*.yaml，ttl: permanent）点名的
#   data/**/*.db 存储真源必须"存在且 >0 字节"——0 字节 .db 在 sqlite/duckdb 眼里是"合法空库"
#   （connect 成功、查询返回 0 行），下游一切"读得到=库正常"的判定因此假绿；本尺锁的正是这一档
#   既有 FMS-HYGIENE 棘轮看不见的面（其存在性口径=git 跟踪集，而 .gitignore 第 100 行 `*.db`
#   整体排除数据卷 ⇒ 活库 governance.db 与 0 字节死库在该口径下同判"死"）；尺本体是纯函数
#   （喂目录+仓根进、吐违规清单出），故红证可全部在 tmp_path 里造，零写生产 data/；
#   数据卷不可见时显式 skip（禁把"看不见"当成"通过"）
# [TESTS] 本文件即测试
"""test_rule_store_pointer_liveness.py — 规则册存储真源存活尺（波 1A.5 死指针锁）

病根（实测，2026-09-27）：永久规则 `trae_034_task_card_standard.yaml` 三处明文把
"任务卡唯一创建入口写入 SQLite"的存储真源写成 `data/zalpha_metadata.db`，而该文件
**0 字节 / sqlite_master 0 表**；活库是 `data/databases/governance.db`（实测 205,246,464
字节、`tasks` 表 2566 行，且 `zephyr.shared.io.paths.DB_PATH` 亦此）。规则在册、指针指空，
任何照规则去核对落地的会话都会把"0 行"读成"合法空表"。

三向可证伪（本文件的红证设计）：
1. 正向：现状 rules/*.yaml 全部指活库 ⇒ 尺绿。
2. 反向（可复红）：把死指针写回临时规则册 + 盘面上真有 0 字节同名库 ⇒ 尺必红。
3. 特异性：`data/zalpha_metadata.db` 这一具体死路径一旦回到任何规则册里 ⇒ 必红
   （`test_reintroducing_the_dead_pointer_goes_red`）。
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.shared.io.paths import MAIN_REPO_ROOT  # noqa: E402  数据卷锚点（worktree 进程锚主仓）

_RULES_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"
_DB_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.db")
# 波 1A.5 点名的死指针（1A.5 出口判据："禁留死指针"）
_KNOWN_DEAD_POINTER = "data/zalpha_metadata.db"
_LIVE_SUCCESSOR = "data/databases/governance.db"


def scan_dead_store_pointers(rule_files: list[Path], repo_root: Path) -> list[str]:
    """扫规则册里点名的 `data/...*.db`，返回"指向不存在或 0 字节库"的违规清单。

    纯函数：只读输入目录，零副作用。返回空列表=该作用域无死指针。
    """
    violations: list[str] = []
    for rule_file in sorted(rule_files):
        text = Path(rule_file).read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for token in _DB_TOKEN_RE.findall(line):
                rel = token.strip("/.\\")
                if not rel.startswith("data/"):
                    continue
                target = repo_root / rel
                if not target.exists():
                    violations.append(f"{rule_file.relative_to(_REPO_ROOT)}:{line_no} 点名 {rel} —— 文件不存在")
                elif target.stat().st_size == 0:
                    violations.append(f"{rule_file.relative_to(_REPO_ROOT)}:{line_no} 点名 {rel} —— 0 字节空壳（死库）")
    return violations


def _require_data_volume() -> Path:
    data_dir = MAIN_REPO_ROOT / "data"
    if not data_dir.is_dir():
        pytest.skip(f"数据卷不可见（{data_dir} 不存在）——死指针尺拒绝把『看不见』当成『通过』")
    return MAIN_REPO_ROOT


class TestPermanentRuleStorePointers:
    """现状锁：永久规则册点名的 .db 真源必须存活且非空壳。"""

    def test_rules_dir_is_scanned(self) -> None:
        assert _RULES_DIR.is_dir(), f"规则册目录不存在：{_RULES_DIR}"
        assert list(_RULES_DIR.glob("*.yaml")), f"规则册目录为空：{_RULES_DIR}"

    def test_permanent_rules_name_live_stores(self) -> None:
        repo_root = _require_data_volume()
        violations = scan_dead_store_pointers(list(_RULES_DIR.glob("*.yaml")), repo_root)
        assert not violations, "永久规则册留有死指针（波 1A.5 出口判据=禁留死指针）：\n  " + "\n  ".join(violations)

    def test_task_card_store_is_the_live_governance_db(self) -> None:
        """trae_034 声明的建卡真源必须是活库，且该库真的有 tasks 表。"""
        repo_root = _require_data_volume()
        trae034 = _RULES_DIR / "trae_034_task_card_standard.yaml"
        text = trae034.read_text(encoding="utf-8")
        assert _KNOWN_DEAD_POINTER not in text, "trae_034 复现死指针 " + _KNOWN_DEAD_POINTER
        assert _LIVE_SUCCESSOR in text, "trae_034 未指向活库 " + _LIVE_SUCCESSOR
        live = repo_root / _LIVE_SUCCESSOR
        assert live.stat().st_size > 0, f"活库为 0 字节：{_LIVE_SUCCESSOR}"
        conn = sqlite3.connect(f"{live.as_uri()}?mode=ro", uri=True)
        try:
            n_task_tables = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='tasks'"
            ).fetchone()[0]
        finally:
            conn.close()
        assert int(n_task_tables) == 1, "活库无 tasks 表——规则声明与盘面再次脱钩"


class TestPointerRulerCanGoRed:
    """红证锁：同一把尺喂"死指针 + 0 字节库"必吐违规（防尺自身退化为恒真）。"""

    def _write_rule(self, path: Path, pointer: str) -> None:
        path.write_text(
            "rule_id: TRAE-999\nttl: permanent\nsections:\n  s1:\n"
            f"    actions:\n    - step: 唯一创建入口写入 SQLite({pointer})\n",
            encoding="utf-8",
        )

    def test_reintroducing_the_dead_pointer_goes_red(self, tmp_path: Path) -> None:
        fake_root = tmp_path / "repo"
        rules = fake_root / "docs" / "01_policies_and_standards" / "rules"
        rules.mkdir(parents=True)
        # 盘面上复现"0 字节死库"（波 1A.5 实测态）
        data = fake_root / "data"
        data.mkdir()
        (data / "zalpha_metadata.db").write_bytes(b"")
        self._write_rule(rules / "trae_034_task_card_standard.yaml", _KNOWN_DEAD_POINTER)

        violations = scan_dead_store_pointers(list(rules.glob("*.yaml")), fake_root)
        assert len(violations) == 1, f"死指针未被抓（尺退化）：{violations}"
        assert _KNOWN_DEAD_POINTER in violations[0]
        assert "0 字节" in violations[0]

    def test_absent_store_also_goes_red(self, tmp_path: Path) -> None:
        fake_root = tmp_path / "repo"
        rules = fake_root / "docs" / "01_policies_and_standards" / "rules"
        rules.mkdir(parents=True)
        (fake_root / "data").mkdir()
        self._write_rule(rules / "trae_999.yaml", "data/databases/nonexistent.db")
        violations = scan_dead_store_pointers(list(rules.glob("*.yaml")), fake_root)
        assert len(violations) == 1 and "不存在" in violations[0], violations

    def test_live_store_with_bytes_is_green(self, tmp_path: Path) -> None:
        fake_root = tmp_path / "repo"
        rules = fake_root / "docs" / "01_policies_and_standards" / "rules"
        (rules / "sub").mkdir(parents=True)
        (fake_root / "data" / "databases").mkdir(parents=True)
        (fake_root / "data" / "databases" / "governance.db").write_bytes(b"\x00page1\x00")
        self._write_rule(rules / "sub" / "trae_034.yaml", _LIVE_SUCCESSOR)
        files = [p for p in rules.rglob("*.yaml")]
        assert scan_dead_store_pointers(files, fake_root) == []
