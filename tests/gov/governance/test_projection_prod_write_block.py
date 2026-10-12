# [A_test] module_id=MOD-INF-037-TEST_PROJECTION_PROD_WRITE_BLOCK | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_projection_prod_write_block
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; pathlib; zephyr.governance.registry_projection.projection_generator
# [CONSUMERS] pytest 自动发现；#ARCH-084 测试面禁写生产投影册守卫的红绿自证
# [STARTUP] python -m pytest tests/gov/governance/test_projection_prod_write_block.py
# [MATURITY] testing
# [INVARIANTS] 全部落 tmp_path 沙盘（绝不写生产册，也绝不为测拒写而先写一次生产册）；四臂各自独立：
#              拒写臂＋无旗对照臂必须同根同路径成对出现（只有 env 变量之差），否则"能红"不成立
# [MODIFY-GUARD] 去掉 _write_rendered 的守卫调用或把判据反向（沙盘=拒／真根=放）即红
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] tests/gov/governance/test_projection_prod_write_block.py
# [TTL] permanent
"""test_projection_prod_write_block.py — 投影生成器"测试面禁写生产册"守卫自证。

病根（实测）：测试经导入链/在役落地链把 capability_canonical_file_registry.yaml 等生产册刷成
PG 现态，#ARCH-084 守护只在 teardown 事后 warn（`ZEPHYR_TEST_GUARD_STRICT=1` 才硬失败），
且 safe_write 审计里归因 session 全是空串——2026-10-12 夜班 03:11-03:14 三分钟内 5 个不同 pid
各写一次，主区因此长期挂着数百行"未提交新生代"。本守卫把"事后告警"前移到"当场拒写＋署名归因"。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.governance.registry_projection import projection_generator as pg

REL = "docs/01_policies_and_standards/_registry/catalogs/probe_book.yaml"
BODY = "total_entities: 1\n"


@pytest.fixture()
def counter():
    """每臂从 0 起算，拒写计数与"照常写"分开可观测（在册假绿教训＝降级态与无动作同形）。"""
    before = pg.TEST_PROD_PROJECTION_BLOCKED
    yield lambda: pg.TEST_PROD_PROJECTION_BLOCKED - before
    pg.TEST_PROD_PROJECTION_BLOCKED = before


def _point_guard_root(monkeypatch, tmp_path: Path, pretend_root: Path) -> Path:
    """把守卫眼里的"真仓根"换掉，目标仍落在 tmp 内（生产册一字节不碰）。"""
    target_dir = pretend_root / Path(REL).parent
    target_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pg, "_repo_root_for_guard", lambda: pretend_root)
    return pretend_root / REL


def test_prod_root_is_refused_under_pytest(monkeypatch, tmp_path, counter, caplog):
    """红证臂：PYTEST_CURRENT_TEST 在场＋目标在真仓根内 ⇒ 拒写、计数、报文带 nodeid。"""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/x.py::test_y (call)")
    monkeypatch.delenv(pg._NO_PROD_WRITE_ENV, raising=False)
    target = _point_guard_root(monkeypatch, tmp_path, tmp_path / "prodroot")
    pg._write_rendered(tmp_path / "prodroot", REL, BODY)
    assert not target.exists(), "生产面被测试写中＝本守卫白装"
    assert counter() == 1, "拒写无痕＝与'没触发'同形"
    assert any(
        "TEST-PROJECTION-WRITE-BLOCKED" in r.getMessage() and "tests/x.py::test_y" in r.getMessage()
        for r in caplog.records
    ), "归因必须把肇事 nodeid 打进日志"


def test_same_bytes_written_without_pytest_context(monkeypatch, tmp_path, counter):
    """对照臂：同一根同一路径，只去掉 pytest 上下文 ⇒ 照写（证明上一臂的红是守卫造成的）。"""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv(pg._NO_PROD_WRITE_ENV, raising=False)
    target = _point_guard_root(monkeypatch, tmp_path, tmp_path / "prodroot")
    pg._write_rendered(tmp_path / "prodroot", REL, BODY)
    assert target.read_text(encoding="utf-8") == BODY
    assert counter() == 0, "无守卫触发却计数＝尺在瞎报"


def test_sandbox_root_still_writes_under_pytest(monkeypatch, tmp_path, counter):
    """不误伤臂：project_root 是沙盘（不等于守卫眼里的真仓根）⇒ 照常写（在册注入点语义不变）。"""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/x.py::test_z (call)")
    monkeypatch.delenv(pg._NO_PROD_WRITE_ENV, raising=False)
    real = tmp_path / "prodroot"
    monkeypatch.setattr(pg, "_repo_root_for_guard", lambda: real)
    sandbox = tmp_path / "sandbox"
    (sandbox / Path(REL).parent).mkdir(parents=True, exist_ok=True)
    pg._write_rendered(sandbox, REL, BODY)
    assert (sandbox / REL).read_text(encoding="utf-8") == BODY
    assert counter() == 0, "沙盘被误拒＝在册注入点测试全被打死"


def test_kill_switch_restores_previous_behavior(monkeypatch, tmp_path, counter):
    """回退臂：ZEPHYR_TEST_NO_PROD_PROJECTION=0 ⇒ 现行为（一键回退，不改判据只改开关）。"""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/x.py::test_k (call)")
    monkeypatch.setenv(pg._NO_PROD_WRITE_ENV, "0")
    target = _point_guard_root(monkeypatch, tmp_path, tmp_path / "prodroot")
    pg._write_rendered(tmp_path / "prodroot", REL, BODY)
    assert target.read_text(encoding="utf-8") == BODY
    assert counter() == 0


def test_guard_self_unreachable_fails_open(monkeypatch, tmp_path, counter):
    """守卫判据不可得＝不拒写（宁可保留既有行为，也不因自身故障挡生产落地）。"""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/x.py::test_f (call)")
    monkeypatch.delenv(pg._NO_PROD_WRITE_ENV, raising=False)

    def _boom() -> Path:
        raise RuntimeError("paths 不可达")

    monkeypatch.setattr(pg, "_repo_root_for_guard", _boom)
    root = tmp_path / "prodroot"
    (root / Path(REL).parent).mkdir(parents=True, exist_ok=True)
    pg._write_rendered(root, REL, BODY)
    assert (root / REL).read_text(encoding="utf-8") == BODY
    assert counter() == 0
