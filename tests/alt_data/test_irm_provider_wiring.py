# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01 同 fx_ecb 先例）
# [MODULE] tests.alt_data.test_irm_provider_wiring
# [DOMAIN] D_DATA
# [INVARIANTS] 零网络零 CH 零 G 盘写——工厂路由全离线构造（startup_probes=False），
#   unsupported capability 走 error 行不 raise；_grade 纯函数参数化（宪法 §9.6 测试隔离）
# [TTL] permanent
"""IrmProvider 工厂接线测试（st-infoaxis-20261013 病灶 D1 修复，裁定#516）。

修复前病灶：IrmProvider 全仓零 import、create_provider 无 irm 分支——
tasks.yaml source=irm 两任务（irm_interactive_qa_refresh/ir_activity_record_refresh）
走"未知数据源"成孤儿，irm_interactive_qa 死水 27 天（A14 red）。

覆盖四链：
1. 工厂分支可发现性：create_provider("irm") 路由命中 IrmProvider；
2. IrmProvider 冒烟：无参构造+meta 契约+capability 路由（零盘写路径）；
3. 孤儿任务核：真实 tasks.yaml 两条 source=irm 任务经工厂走通（task→factory→provider）；
4. A14 复活预演：l9_readiness._grade 纯函数对 lag=1 输入给 green——数据活了灯自己绿
   （判定函数禁改，本测试只锁判定契约）。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.data.implementations.irm_provider import IrmProvider
from zephyr.data.l9_readiness_aggregator import _A_LINES_CH, _grade, _resolve_table
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload
from zephyr.data.scheduler import IntegratorScheduler

POLICY = SourcePolicy(rpm=0, max_retries=0)

_TASKS_YAML = Path(__file__).resolve().parents[2] / "src" / "zephyr" / "data" / "config" / "tasks.yaml"


@pytest.fixture
def scheduler(tmp_path):
    """最小离线 IntegratorScheduler（legacy test_data_scheduler 同范式）。

    startup_probes=False 隔离 live 探针（#ARCH-DATA-015）；tmp_path 隔离进度库/jobstore。
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "schedule.yaml").write_text(
        'schedules:\n  daily_capital:\n    cron: "0 6 * * *"\n    executor: light\n',
        encoding="utf-8",
    )
    (config_dir / "tasks.yaml").write_text("tasks: []\n", encoding="utf-8")
    return IntegratorScheduler(
        config_dir=config_dir,
        progress_db=tmp_path / "progress.db",
        jobs_db="sqlite:///" + str(tmp_path / "jobs.db"),
        startup_probes=False,
    )


class TestFactoryRouting:
    """工厂分支可发现性（D1 修复面）：source=irm 不再落"未知数据源"。"""

    def test_irm_source_routes_to_irm_provider(self, scheduler):
        provider = scheduler.create_provider("irm")
        assert provider is not None
        assert isinstance(provider, IrmProvider)
        assert provider.source_name == "irm"

    def test_unknown_source_still_returns_none(self, scheduler):
        """工厂既有形态回归护栏：未知源返回 None 不 raise。"""
        assert scheduler.create_provider("nonexistent") is None


class TestIrmProviderSmoke:
    """IrmProvider 冒烟：构造+方法签名+capability 路由（零网络零盘写）。"""

    def test_construct_and_meta_contract(self):
        p = IrmProvider()
        p.connect()
        assert p._connected is True
        p.disconnect()
        assert p._connected is False
        assert p.meta.name == "irm"
        assert set(p.meta.capabilities) >= {"irm_interactive_qa", "ir_activity_record"}
        for method in ("fetch", "health_check", "connect", "disconnect"):
            assert callable(getattr(p, method)), method

    def test_unsupported_capability_yields_error_not_raise(self):
        p = IrmProvider()
        payload = FetchPayload(
            table="c3_fundamental.irm_interactive_qa",
            symbols=None,
            start=None,
            end=None,
            incremental=False,
            extra={"capability": "no_such_capability"},
        )
        results = list(p.fetch(payload, POLICY))
        assert len(results) == 1
        assert results[0].error and "unsupported capability" in results[0].error


class TestOrphanTasksWiring:
    """tasks.yaml 两条 source=irm 任务经新工厂分支走通（任务面只核不改——归数据班管）。"""

    @pytest.fixture
    def irm_tasks(self) -> list[dict]:
        data = yaml.safe_load(_TASKS_YAML.read_text(encoding="utf-8"))
        return [t for t in data["tasks"] if t.get("source") == "irm"]

    def test_both_irm_tasks_present(self, irm_tasks):
        assert {t["task_id"] for t in irm_tasks} == {
            "irm_interactive_qa_refresh",
            "ir_activity_record_refresh",
        }

    @pytest.mark.parametrize(
        "task_id",
        ["irm_interactive_qa_refresh", "ir_activity_record_refresh"],
    )
    def test_task_routes_through_factory(self, scheduler, irm_tasks, task_id):
        task = next(t for t in irm_tasks if t["task_id"] == task_id)
        provider = scheduler.create_provider(task["source"])
        assert isinstance(provider, IrmProvider)
        # 任务声明的 capability 必须被 provider meta 覆盖（路由可达）
        assert task["capability"] in provider.meta.capabilities
        # provider fetch 的 extra 键契约（pages/page_size）与任务 extra 对齐
        assert "pages" in task["extra"] and "page_size" in task["extra"]


class TestA14RevivalGrade:
    """A14 复活预演：irm_interactive_qa 恢复日更后 lag<=7 → green（不改判定函数）。"""

    def test_a14_spec_anchors_irm_table(self):
        """l9_readiness A14 行读数面锚定 D1 修复的同一张表（链路一致）。"""
        spec = next(s for s in _A_LINES_CH if s.line == "A14")
        assert spec.category_id == "fund_irm_interactive_qa"
        assert spec.max_lag == 7
        assert _resolve_table(spec.category_id) == "c3_fundamental.irm_interactive_qa"

    @pytest.mark.parametrize(
        ("lag", "max_lag", "expected"),
        [
            (1, 7, "green"),  # 复活态：恢复日更 lag=1 → A14 转绿
            (7, 7, "green"),  # 阈值边界含
            (8, 7, "yellow"),  # 2×窗内黄
            (14, 7, "yellow"),
            (15, 7, "red"),  # 超 2×阈值红
            (27, 7, "red"),  # 死水 27 天实测态（当前 A14 red 在案）
            (None, 7, "red"),  # 空表/NULL=断供
        ],
    )
    def test_grade_ladder(self, lag, max_lag, expected):
        assert _grade(lag, max_lag) == expected
