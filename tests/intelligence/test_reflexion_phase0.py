# [MODULE] tests.intelligence.test_reflexion_phase0
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_reflexion_phase0.py -q
"""test_reflexion_phase0.py — 12号文 §4.2 Phase 0(P0-1~P0-4)自反Agent骨架测试。

覆盖:
  1. schema 严格校验 —— 缺必填字段拒收/未知字段拒收/非法 outcome 拒收/
     failure 缺归因类别或建议拒收/建议未锚定归因类别拒收
  2. 三角色合成样例端到端 —— "写一篇因子假设"任务分角色跑通, 评估报告字段完整
     (score/dimensions/defects), 角色协议 isinstance 契约
  3. L1 归因分类+建议 —— 失败轨迹→归因类别命中词表/建议非空/每条锚定类别+
     轨迹片段; 注入规则表 config 化生效
  4. 盘中拒执行 —— 工作日 09:30-15:00 run_batch 抛 IntradayReflectionForbidden;
     盘后/周末放行
  5. 落盘可读回 —— ReflectionStore 追加写 jsonl, read_all 对称往返;
     批量入口跑轨迹目录产出记录落盘
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from zephyr.intelligence.reflexion.batch_runner import (
    CN_TZ,
    BatchReflectionRunner,
    IntradayReflectionForbidden,
    is_intraday,
)
from zephyr.intelligence.reflexion.l1_reflector import (
    CATEGORY_DATA_ERROR,
    CATEGORY_UNKNOWN,
    L1Reflector,
)
from zephyr.intelligence.reflexion.reflection_schema import (
    ReflectionRecord,
    ReflectionSchemaError,
    ReflectionStore,
)
from zephyr.intelligence.reflexion.roles import (
    ActorProtocol,
    EvaluationReport,
    EvaluatorProtocol,
    L1SelfReflection,
    RubricEvaluator,
    SelfReflectionProtocol,
    SyntheticActor,
    TaskSpec,
    Trajectory,
    TrajectoryStep,
    run_three_role_flow,
)

# ── 通用构造辅助 ──


def _ok_record_kwargs() -> dict:
    return {
        "reflection_id": "rfl-test0001",
        "task_id": "task-001",
        "trajectory_ref": "traj/task-001.json",
        "outcome": "success",
        "failure_category": "",
        "improvement_suggestions": [],
        "created_at": "2026-08-22T16:00:00+00:00",
        "schema_version": "1.0",
    }


def _failed_trajectory(task_id: str = "task-fail") -> Trajectory:
    return Trajectory(
        task_id=task_id,
        steps=[
            TrajectoryStep(step_index=0, action="检索资料", observation="资料检索完成"),
            TrajectoryStep(
                step_index=1,
                action="读取财报",
                observation="读取中止: 数据缺失, 关键字段含 NaN 空值",
            ),
        ],
        final_output="",
        succeeded=False,
        error="任务执行失败: 数据缺失",
    )


# ── 1. schema 严格校验(缺必填字段拒收) ──


class TestSchemaStrict:
    def test_roundtrip_ok(self):
        record = ReflectionRecord(**_ok_record_kwargs())
        assert ReflectionRecord.from_dict(record.to_dict()) == record

    @pytest.mark.parametrize(
        "missing_field",
        ["reflection_id", "task_id", "trajectory_ref", "outcome", "created_at"],
    )
    def test_missing_required_field_rejected(self, missing_field: str):
        payload = _ok_record_kwargs()
        payload.pop(missing_field)
        with pytest.raises(ReflectionSchemaError, match="缺必填字段拒收"):
            ReflectionRecord.from_dict(payload)

    def test_unknown_field_rejected(self):
        payload = {**_ok_record_kwargs(), "surprise": "x"}
        with pytest.raises(ReflectionSchemaError, match="未知字段拒收"):
            ReflectionRecord.from_dict(payload)

    def test_invalid_outcome_rejected(self):
        payload = {**_ok_record_kwargs(), "outcome": "partial"}
        with pytest.raises(ReflectionSchemaError, match="outcome 非法取值拒收"):
            ReflectionRecord.from_dict(payload)

    def test_failure_without_category_rejected(self):
        trajectory = _failed_trajectory()
        report = RubricEvaluator().evaluate(trajectory)
        with pytest.raises(ReflectionSchemaError, match="failure_category 必填非空"):
            ReflectionRecord(
                reflection_id="rfl-x",
                task_id=trajectory.task_id,
                trajectory_ref="t",
                outcome="failure",
                failure_category="",
                improvement_suggestions=[],
            )
        assert report.defects  # 评估报告缺陷非空(佐证轨迹确为失败)

    def test_failure_suggestion_not_anchored_rejected(self):
        from zephyr.intelligence.reflexion.reflection_schema import (
            ImprovementSuggestion,
        )

        with pytest.raises(ReflectionSchemaError, match="未锚定记录归因类别"):
            ReflectionRecord(
                reflection_id="rfl-x",
                task_id="task-fail",
                trajectory_ref="t",
                outcome="failure",
                failure_category=CATEGORY_DATA_ERROR,
                improvement_suggestions=[
                    ImprovementSuggestion(
                        category="逻辑错误",  # 与记录归因类别不一致 → 拒收
                        suggestion="检查推理链",
                        evidence_ref="step[0]",
                    )
                ],
            )


# ── 2. 三角色合成样例端到端(评估报告字段完整) ──


class TestThreeRoleFlow:
    def test_protocol_conformance(self):
        assert isinstance(SyntheticActor(), ActorProtocol)
        assert isinstance(RubricEvaluator(), EvaluatorProtocol)
        assert isinstance(L1SelfReflection(), SelfReflectionProtocol)

    def test_synthetic_success_e2e(self):
        task = TaskSpec(task_id="task-factor-hyp", description="写一篇因子假设")
        trajectory, report, record = run_three_role_flow(task, SyntheticActor(), RubricEvaluator(), L1SelfReflection())
        # Actor 轨迹
        assert trajectory.task_id == task.task_id
        assert trajectory.succeeded is True
        assert len(trajectory.steps) == 3
        # Evaluator 评估报告字段完整(score/dimensions/defects)
        assert isinstance(report, EvaluationReport)
        assert 0.0 <= report.score <= 1.0
        assert set(report.dimensions) == {"完整性", "逻辑性", "契约符合"}
        assert report.defects == []
        # SelfReflection 反思记录(成功轨迹 → outcome=success)
        assert record.outcome == "success"
        assert record.task_id == task.task_id

    def test_synthetic_failure_e2e(self):
        task = TaskSpec(
            task_id="task-factor-fail",
            description="写一篇因子假设",
            params={"inject_failure": "数据缺失"},
        )
        trajectory, report, record = run_three_role_flow(task, SyntheticActor(), RubricEvaluator(), L1SelfReflection())
        assert trajectory.succeeded is False
        assert report.defects  # 缺陷清单非空
        assert record.outcome == "failure"
        assert record.failure_category == CATEGORY_DATA_ERROR
        assert record.improvement_suggestions  # 建议非空


# ── 3. L1 归因分类+建议非空(可追溯到轨迹片段) ──


class TestL1Reflector:
    def test_classify_data_error_and_suggestions(self):
        trajectory = _failed_trajectory()
        report = RubricEvaluator().evaluate(trajectory)
        reflector = L1Reflector()
        record = reflector.reflect(trajectory, report)
        assert record.outcome == "failure"
        # 归因命中"数据错误"词表
        assert record.failure_category == CATEGORY_DATA_ERROR
        # 建议非空且每条锚定归因类别+轨迹片段
        assert len(record.improvement_suggestions) >= 1
        for suggestion in record.improvement_suggestions:
            assert suggestion.category == record.failure_category
            assert suggestion.suggestion.strip()
            assert suggestion.evidence_ref == "step[1]"  # 命中步可追溯
            assert suggestion.evidence_ref in suggestion.suggestion

    def test_classify_unknown_fallback(self):
        trajectory = Trajectory(
            task_id="task-weird",
            steps=[TrajectoryStep(step_index=0, action="执行", observation="莫名中止")],
            final_output="",
            succeeded=False,
            error="完全陌生的失败形态",
        )
        record = L1Reflector().reflect(trajectory)
        assert record.failure_category == CATEGORY_UNKNOWN
        assert record.improvement_suggestions  # 兜底类别建议亦非空

    def test_custom_rules_configurable(self):
        custom = {"幻觉输出": ("虚构引用", "编造")}
        reflector = L1Reflector(rules=custom)
        trajectory = Trajectory(
            task_id="task-hallu",
            steps=[TrajectoryStep(step_index=0, action="撰写", observation="文中虚构引用三处")],
            final_output="",
            succeeded=False,
            error="审校驳回: 虚构引用",
        )
        record = reflector.reflect(trajectory)
        assert record.failure_category == "幻觉输出"

    def test_empty_rules_rejected(self):
        with pytest.raises(ValueError, match="归因规则表为空"):
            L1Reflector(rules={})

    def test_success_trajectory_record(self):
        trajectory = SyntheticActor().run(TaskSpec(task_id="task-ok", description="写一篇因子假设"))
        record = L1Reflector().reflect(trajectory)
        assert record.outcome == "success"
        assert record.failure_category == ""


# ── 4. 盘中拒执行(09:30-15:00 工作日) ──


def _cn(y: int, m: int, d: int, hh: int, mm: int) -> datetime:
    return datetime(y, m, d, hh, mm, tzinfo=CN_TZ)


class TestIntradayGuard:
    # 2026-08-21 为周五, 2026-08-22 为周六, 2026-08-24 为周一
    @pytest.mark.parametrize(
        "moment",
        [_cn(2026, 8, 24, 9, 30), _cn(2026, 8, 24, 10, 0), _cn(2026, 8, 24, 14, 59)],
    )
    def test_intraday_rejected(self, moment: datetime, tmp_path: Path):
        assert is_intraday(moment) is True
        runner = BatchReflectionRunner(store=ReflectionStore(root=tmp_path))
        with pytest.raises(IntradayReflectionForbidden, match="盘中零调用"):
            runner.run_batch(tmp_path, now=moment)

    @pytest.mark.parametrize(
        "moment",
        [
            _cn(2026, 8, 24, 9, 29),  # 盘前
            _cn(2026, 8, 24, 15, 0),  # 收盘即放行
            _cn(2026, 8, 24, 18, 30),  # 盘后窗口
            _cn(2026, 8, 22, 10, 0),  # 周六上午(非盘中)
        ],
    )
    def test_off_hours_allowed(self, moment: datetime, tmp_path: Path):
        assert is_intraday(moment) is False
        runner = BatchReflectionRunner(store=ReflectionStore(root=tmp_path / "s"))
        assert runner.run_batch(tmp_path, now=moment) == []  # 空目录放行零产出


# ── 5. 落盘可读回 + 批量入口端到端 ──


class TestStoreAndBatch:
    def test_store_roundtrip(self, tmp_path: Path):
        store = ReflectionStore(root=tmp_path)
        record = ReflectionRecord(**_ok_record_kwargs())
        store.append(record)
        store.append(record)  # 追加两行
        loaded = store.read_all()
        assert loaded == [record, record]
        assert store.path.name == "reflections.jsonl"

    def test_store_read_bad_line_raises(self, tmp_path: Path):
        store = ReflectionStore(root=tmp_path)
        store.path.write_text('{"task_id": 缺字段}\n', encoding="utf-8")
        with pytest.raises(ReflectionSchemaError, match="记录非法"):
            store.read_all()

    def test_batch_run_persists_records(self, tmp_path: Path):
        traj_dir = tmp_path / "trajectories"
        traj_dir.mkdir()
        for idx, (succeeded, error) in enumerate(
            [(True, ""), (False, "任务执行失败: 数据缺失"), (False, "超时: timeout")]
        ):
            payload = {
                "task_id": f"task-{idx}",
                "steps": [{"action": "执行", "observation": error or "执行完成, 产出齐整"}],
                "final_output": "产出" if succeeded else "",
                "succeeded": succeeded,
                "error": error,
            }
            (traj_dir / f"traj-{idx}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        (traj_dir / "bad.json").write_text("{not json", encoding="utf-8")  # 坏文件跳过

        store = ReflectionStore(root=tmp_path / "reflections")
        runner = BatchReflectionRunner(store=store)
        records = runner.run_batch(traj_dir, now=_cn(2026, 8, 24, 18, 0))

        assert len(records) == 3  # 坏文件不产出
        assert [r.outcome for r in records] == ["success", "failure", "failure"]
        assert records[1].failure_category == CATEGORY_DATA_ERROR
        assert records[2].failure_category == "环境问题"
        assert all(r.trajectory_ref.endswith(".json") for r in records)
        # 落盘可读回且与产出一致
        assert store.read_all() == records
