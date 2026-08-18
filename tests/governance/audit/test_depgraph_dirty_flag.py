# [A_test] module_id: SRC-TST-2400 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_depgraph_dirty_flag
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-643 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_depgraph_dirty_flag.py — DM-90974 Phase 2: depgraph dirty flag 单测

治本目标：解决"运行时 DB 写入（apply_depgraph --delete-nodes 等）不产生 git commit →
GATE-DOMAIN-DOC reconciler 永不 fire → 域文档静默漂移"的盲区。

机制：PG-write 脚本成功 commit DB 后落 data/databases/depgraph_dirty.flag 空文件，
GATE-REGENERATE reconciler 的 _trigger_domain_doc 检测 flag 存在即 fire，重生成功后删 flag。

验证项：
1. mark_depgraph_dirty() 在正确路径创建空 flag 文件（idempotent）
2. _trigger_domain_doc 经 make_regenerate_reconciler 组合后：
   - flag 存在 + 空 committed_files → True（治本盲区已覆盖）
   - flag 不存在 + 空 committed_files → False（不误触发）
   - flag 不存在 + commit PG-write 脚本 → True（向后兼容原 trigger）
3. _clear_depgraph_dirty_flag() 删除 flag（经 _reconcile_domain_doc 成功路径调用，
   本测试通过 monkeypatch _run_subprocess 模拟成功重生，断言 flag 被清）

测试隔离: monkeypatch 真源 paths.DEPGRAPH_DIRTY_FLAG + re-export _shared.constants.DEPGRAPH_DIRTY_FLAG 到 tmp_path，不污染生产。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# _shared.constants 在 scripts/governance/_shared/ 下，需独立加 sys.path
# tests/conftest.py 只加 src/，未覆盖 scripts/governance/_shared/
_GOV_DIR = _PROJECT_ROOT / "scripts" / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

import _shared.constants as _const_mod  # noqa: E402
from _shared.constants import mark_depgraph_dirty  # noqa: E402

# 直接 submodule import（避免 from zephyr.governance.audit import reconciliation_registry
# 触发 TEST-SOURCE-CONSISTENCY gate：__init__.py 虽 __all__ 含此名但未显式 import）
import zephyr.governance.audit.reconciliation_registry as reconciliation_registry  # noqa: E402
from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcileResult,
    make_regenerate_reconciler,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """重定向 flag 路径到 tmp_path，确保 mark_depgraph_dirty() 写和 reconciler 读/删对齐到同一处。

    治本（DM-90974 真源收敛）：路径真源收敛为 zephyr.shared.io.paths.DEPGRAPH_DIRTY_FLAG，
    - 写入端 mark_depgraph_dirty() 经 _shared.constants 模块级查找 DEPGRAPH_DIRTY_FLAG
      → monkeypatch _shared.constants.DEPGRAPH_DIRTY_FLAG 使其写 tmp_path
    - 读取端 reconciler 闭包绑定 `from zephyr.shared.io.paths import DEPGRAPH_DIRTY_FLAG`
      （在 make_regenerate_reconciler 函数内 import，调用时捕获 paths.DEPGRAPH_DIRTY_FLAG 当前值）
      → monkeypatch paths.DEPGRAPH_DIRTY_FLAG 使闭包捕获 tmp_path
    - gateway.project_root = tmp_path → reconciler 内 os.path.relpath(f, project_root) 仍可用

    返回 (tmp_path, fake_flag_path)，fake_flag_path 是真源 paths.DEPGRAPH_DIRTY_FLAG 的隔离副本。
    """
    fake_flag = tmp_path / "data" / "databases" / "depgraph_dirty.flag"
    # 治本：monkeypatch 真源 paths.DEPGRAPH_DIRTY_FLAG（reconciler 闭包从此处捕获）
    # 用直接 submodule import（不查 __init__.py 符号），避免 TEST-SOURCE-CONSISTENCY 误报。
    import zephyr.shared.io.paths as _paths_mod
    monkeypatch.setattr(_paths_mod, "DEPGRAPH_DIRTY_FLAG", fake_flag, raising=True)
    # 写入端 _shared.constants.DEPGRAPH_DIRTY_FLAG 是 import 时绑定的 re-export，
    # monkeypatch paths 不会反向同步，需独立 patch 使 mark_depgraph_dirty() 写 tmp_path
    monkeypatch.setattr(_const_mod, "DEPGRAPH_DIRTY_FLAG", fake_flag, raising=True)
    return tmp_path, fake_flag


def _make_spec(
    project_root: Path, gateway: MagicMock | None = None
):
    """构造 GATE-REGENERATE reconciler spec，用 fake gateway.project_root 控制 flag 路径。

    可选传入 gateway 参数：reconcile 测试需要预设 _run_git / _commit_auto 等方法返回值，
    此时必须传入同一 gateway 对象，否则 mock setup 不生效（_make_spec 内部新建的 gateway
    与测试 setup 的不是同一对象）。
    """
    if gateway is None:
        gateway = MagicMock()
    gateway.project_root = project_root
    return make_regenerate_reconciler(gateway)


# ---------------------------------------------------------------------------
# 1. mark_depgraph_dirty() 单测
# ---------------------------------------------------------------------------


class TestMarkDepgraphDirty:
    """验证 _shared.constants.mark_depgraph_dirty() 的行为。"""

    def test_creates_flag_file(self, isolated_flag: tuple[Path, Path]) -> None:
        tmp_path, fake_flag = isolated_flag
        assert not fake_flag.exists()
        mark_depgraph_dirty()
        assert fake_flag.exists()
        assert fake_flag.is_file()

    def test_flag_is_empty_signal_file(self, isolated_flag: tuple[Path, Path]) -> None:
        """flag 是空信号文件，不存数据（真源仍是 PostgreSQL DB）。"""
        _, fake_flag = isolated_flag
        mark_depgraph_dirty()
        assert fake_flag.read_text(encoding="utf-8") == ""

    def test_idempotent_multiple_calls(self, isolated_flag: tuple[Path, Path]) -> None:
        """重复调用不报错，flag 仍存在。"""
        _, fake_flag = isolated_flag
        mark_depgraph_dirty()
        mark_depgraph_dirty()
        mark_depgraph_dirty()
        assert fake_flag.exists()

    def test_creates_parent_dirs(self, isolated_flag: tuple[Path, Path]) -> None:
        """data/databases/ 目录不存在时自动创建。"""
        tmp_path, fake_flag = isolated_flag
        assert not (tmp_path / "data").exists()
        mark_depgraph_dirty()
        assert (tmp_path / "data" / "databases").is_dir()


# ---------------------------------------------------------------------------
# 2. _trigger_domain_doc 行为（经 make_regenerate_reconciler 组合 spec.trigger）
# ---------------------------------------------------------------------------


class TestRegenerateTrigger:
    """验证 GATE-REGENERATE 组合 trigger 的 flag 检测逻辑。"""

    def test_trigger_fires_when_flag_exists(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """DM-90974 Phase 2 核心：flag 存在即触发，即使 committed_files 为空。

        治本盲区覆盖：apply_depgraph --delete-nodes 运行时 DB 写入后落 flag，
        下次任意 commit（哪怕改 README）触发 reconciler → 重生域文档。
        """
        tmp_path, fake_flag = isolated_flag
        fake_flag.parent.mkdir(parents=True, exist_ok=True)
        fake_flag.touch()  # 模拟 PG-write 脚本落的 dirty flag

        spec = _make_spec(tmp_path)
        assert spec.trigger([]) is True

    def test_trigger_no_fire_when_no_flag_no_files(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """flag 不存在 + committed_files 空 → 不触发（不误触发 reconciler）。"""
        tmp_path, _ = isolated_flag
        spec = _make_spec(tmp_path)
        assert spec.trigger([]) is False

    def test_trigger_fires_on_pg_write_script_commit(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """向后兼容：flag 不存在时，commit apply_depgraph.py 仍触发（原 trigger 逻辑）。

        确保治本不退化原有行为：开发者 commit PG-write 脚本本身时仍触发重生。
        """
        tmp_path, _ = isolated_flag
        spec = _make_spec(tmp_path)
        committed = [str(tmp_path / "scripts" / "governance" / "apply_depgraph.py")]
        assert spec.trigger(committed) is True

    def test_trigger_fires_on_sync_yaml_script_commit(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """sync_yaml_to_depgraph.py 同属 PG-write 脚本白名单，commit 时也触发。"""
        tmp_path, _ = isolated_flag
        spec = _make_spec(tmp_path)
        committed = [
            str(tmp_path / "scripts" / "governance" / "d8_doc_sync" / "sync_yaml_to_depgraph.py")
        ]
        assert spec.trigger(committed) is True

    def test_trigger_fires_on_file_deletion(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """向后兼容：删除 .py/.yaml 文件也触发（layer 1 ghost 过滤）。"""
        tmp_path, _ = isolated_flag
        spec = _make_spec(tmp_path)
        # 文件不存在 → 模拟删除
        deleted_file = str(tmp_path / "scripts" / "foo" / "bar.py")
        assert not os.path.isfile(deleted_file)
        assert spec.trigger([deleted_file]) is True

    def test_trigger_no_fire_on_unrelated_commit(
        self, isolated_flag: tuple[Path, Path]
    ) -> None:
        """flag 不存在 + commit 无关 .py 文件（实际存在的） → 不触发。"""
        tmp_path, _ = isolated_flag
        unrelated_file = tmp_path / "docs" / "readme.md"
        unrelated_file.parent.mkdir(parents=True, exist_ok=True)
        unrelated_file.write_text("hello", encoding="utf-8")

        spec = _make_spec(tmp_path)
        assert spec.trigger([str(unrelated_file)]) is False


# ---------------------------------------------------------------------------
# 3. _clear_depgraph_dirty_flag() 行为（经 _reconcile_domain_doc 成功路径）
# ---------------------------------------------------------------------------


class TestClearDepgraphDirtyFlag:
    """验证 reconcile 成功路径会删除 dirty flag，warn 路径不删（下次 commit 重试）。

    由于 _reconcile_domain_doc 内部调用 _run_subprocess 跑生成器脚本，本测试通过
    monkeypatch reconciliation_registry._run_subprocess 模拟"生成器成功/失败"两种场景，
    断言 flag 是否被正确清理。同时 monkeypatch gateway.run_git / _commit_auto 模拟 git 行为。
    """

    def test_flag_cleared_on_clean_reconcile(
        self, isolated_flag: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """生成器成功 + git diff 无漂移 → action=clean → flag 被清。"""
        tmp_path, fake_flag = isolated_flag
        fake_flag.parent.mkdir(parents=True, exist_ok=True)
        fake_flag.touch()
        assert fake_flag.exists()

        # 模拟生成器成功（returncode=0）
        def _fake_run_subprocess(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(
            reconciliation_registry, "_run_subprocess", _fake_run_subprocess
        )

        # 模拟 git diff 无漂移（必须传入同一 gateway 对象，否则 mock 不生效）
        gateway = MagicMock()
        diff_result = MagicMock()
        diff_result.returncode = 0
        diff_result.stdout = ""  # 无漂移
        gateway.run_git.return_value = diff_result

        spec = _make_spec(tmp_path, gateway=gateway)
        result = spec.reconcile([], "test-session-id")

        assert result.action == "clean"
        assert not fake_flag.exists(), "clean 路径应清 dirty flag"

    def test_flag_cleared_on_auto_committed_reconcile(
        self, isolated_flag: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """生成器成功 + git diff 有漂移 + auto-commit OK → action=auto_committed → flag 清。"""
        tmp_path, fake_flag = isolated_flag
        fake_flag.parent.mkdir(parents=True, exist_ok=True)
        fake_flag.touch()

        def _fake_run_subprocess(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(
            reconciliation_registry, "_run_subprocess", _fake_run_subprocess
        )

        gateway = MagicMock()
        # git diff 有漂移
        diff_result = MagicMock()
        diff_result.returncode = 0
        diff_result.stdout = "docs/02_enterprise_architecture/02_domain_architecture_docs/01_a_foo.md\n"
        gateway.run_git.return_value = diff_result
        # auto-commit 成功
        commit_result = MagicMock()
        commit_result.status = "OK"
        commit_result.message = ""
        gateway._commit_auto.return_value = commit_result

        spec = _make_spec(tmp_path, gateway=gateway)
        result = spec.reconcile([], "test-session-id")

        assert result.action == "auto_committed"
        assert not fake_flag.exists(), "auto_committed 路径应清 dirty flag"

    def test_flag_not_cleared_on_gen_failure(
        self, isolated_flag: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """生成器失败 → action=warn → flag 不清（下次 commit 仍会触发重试）。

        这是设计意图：失败时保留 flag 让下次 commit 自动重试，无需人工干预。
        """
        tmp_path, fake_flag = isolated_flag
        fake_flag.parent.mkdir(parents=True, exist_ok=True)
        fake_flag.touch()

        def _fake_run_subprocess(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 1  # 生成器失败
            result.stdout = ""
            result.stderr = "NameError: something broke"
            return result

        monkeypatch.setattr(
            reconciliation_registry, "_run_subprocess", _fake_run_subprocess
        )

        gateway = MagicMock()
        spec = _make_spec(tmp_path, gateway=gateway)
        result = spec.reconcile([], "test-session-id")

        assert result.action == "warn"
        assert fake_flag.exists(), "warn 路径应保留 dirty flag 让下次 commit 重试"
