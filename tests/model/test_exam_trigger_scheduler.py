# [BLUEPRINT] MOD-INF-054 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §
# [MODULE] tests.model.test_exam_trigger_scheduler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""
test_exam_trigger_scheduler.py — 触发式考试调度器单测（06号文 §4 Phase 1，P1-2/P1-3）
=====================================================================================
LLM/模型/DB 全 mock：ModelDiscovery 假发现、Quick 考试假 runner（零真实考试）、
护照/QuickProfile 目录重定向 tmp_path。覆盖：
- 新模型自动 Quick 考试 -> QuickProfile 落盘（P1-2 验收点）；远程 API 模型跳过；已知模型不重复触发
- 单模型考试失败不中断批量 + seen 快照防重复触发风暴
- TaskGate 连续 low_accuracy 超阈 -> 复核建议（只发建议 human_gated，Standard/Deep 不自动执行）
- 放行/非 low_accuracy 拦截计数清零；check_and_record 透传判定且建议落盘 JSONL
- 阈值非法/快照损坏 fail-closed（ExamTriggerError ZA-IT-0011）
"""

from __future__ import annotations

import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

cp_mod = pytest.importorskip("zephyr.intelligence.model_profiling.capability_passport")
md_mod = pytest.importorskip("zephyr.intelligence.model_profiling.model_discovery")
sched_mod = pytest.importorskip("zephyr.intelligence.model_profiling.exam_trigger_scheduler")

ExamTriggerError = sched_mod.ExamTriggerError
ExamTriggerScheduler = sched_mod.ExamTriggerScheduler
QuickProfile = cp_mod.QuickProfile
DiscoveredModel = md_mod.DiscoveredModel


class _FakeDiscovery:
    """假模型发现器（模型清单注入，零 Ollama/API 调用）。"""

    def __init__(self, models):
        self._models = models
        self.calls = 0

    def discover_all(self):
        self.calls += 1
        return list(self._models)


def _ollama(name):
    return DiscoveredModel(name=name, source="ollama")


def _remote(name):
    return DiscoveredModel(name=name, source="remote_api", provider=name.split(":")[0])


def _fake_runner(profile_by_model, errors=()):
    """假 Quick 考试 runner：按注入表返回 QuickProfile；errors 名单内模型抛异常。"""

    def _run(model_id: str) -> QuickProfile:
        if model_id in errors:
            raise RuntimeError(f"fake exam crash: {model_id}")
        profile = profile_by_model.get(model_id) or QuickProfile(model_id=model_id, overall_score=0.5)
        return profile

    return _run


@pytest.fixture()
def isolated_dirs(tmp_path, monkeypatch):
    """护照/QuickProfile 目录重定向到 tmp（不触碰 data/brain 真目录）。"""
    passports = tmp_path / "passports"
    quick = tmp_path / "quick_profiles"
    monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", passports)
    monkeypatch.setattr(cp_mod, "QUICK_PROFILES_DIR", quick)
    return {"passports": passports, "quick": quick}


class TestNewModelQuickExam:
    def test_new_ollama_model_produces_quick_profile_on_disk(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("qwen3:8b"), _remote("deepseek:pro")])
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams()
        assert report["examined"] == ["qwen3:8b"]  # 远程 API 模型不触发本地 Quick 考试
        assert report["failed"] == {}
        saved = isolated_dirs["quick"] / "qwen3_8b.json"
        assert saved.exists()  # P1-2 验收点：QuickProfile 落盘 quick_profiles/
        data = json.loads(saved.read_text(encoding="utf-8"))
        assert data["model_id"] == "qwen3:8b" and data["exam_mode"] == "quick"

    def test_known_model_with_quick_profile_skipped(self, isolated_dirs, tmp_path):
        QuickProfile(model_id="qwen3:8b").save()  # 已有 QuickProfile -> 非新模型
        discovery = _FakeDiscovery([_ollama("qwen3:8b"), _ollama("qwen2.5-coder:14b")])
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        assert sched.scan_new_models() == ["qwen2.5-coder:14b"]

    def test_seen_store_prevents_retrigger(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("qwen3:8b")])
        seen_path = tmp_path / "seen.json"
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=seen_path,
        )
        sched.trigger_quick_exams()
        assert sched.scan_new_models() == []
        # 新实例加载同一快照 -> 仍不重复触发（跨会话幂等）
        sched2 = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=seen_path,
        )
        report = sched2.trigger_quick_exams()
        assert report["targets"] == [] and report["examined"] == []

    def test_exam_failure_does_not_break_batch(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("bad:7b"), _ollama("good:7b")])
        runner = _fake_runner({}, errors=("bad:7b",))
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=runner,
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams()
        assert report["examined"] == ["good:7b"]
        assert "bad:7b" in report["failed"] and "fake exam crash" in report["failed"]["bad:7b"]
        # 失败模型也记 seen（防每次扫描重复触发风暴）
        assert sched.scan_new_models() == []

    def test_explicit_model_list_runs_regardless_of_known(self, isolated_dirs, tmp_path):
        QuickProfile(model_id="qwen3:8b").save()
        sched = ExamTriggerScheduler(
            discovery=_FakeDiscovery([]),
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams(["qwen3:8b"])  # 显式名单=人工点名复跑 Quick（human 触发）
        assert report["examined"] == ["qwen3:8b"]


class TestLowAccuracyReviewSuggestion:
    def _sched(self, tmp_path, threshold=3):
        return ExamTriggerScheduler(
            discovery=_FakeDiscovery([]),
            quick_exam_runner=_fake_runner({}),
            low_accuracy_threshold=threshold,
            suggestion_sink_path=tmp_path / "suggestions.jsonl",
        )

    def test_consecutive_low_accuracy_triggers_suggestion_at_threshold(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        suggestion = sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert suggestion is not None
        assert suggestion["type"] == "review_exam_suggestion"
        assert suggestion["consecutive_low_accuracy"] == 3
        assert suggestion["suggested_mode"] == "standard"
        assert suggestion["human_gated"] is True  # 只发建议：Standard/Deep 始终人工确认
        # 同一连续段不重复发建议
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        assert len(sched.suggestions) == 1

    def test_suggestion_persisted_to_jsonl_sink(self, tmp_path):
        sched = self._sched(tmp_path, threshold=2)
        reason = "low_accuracy: f1_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sink = tmp_path / "suggestions.jsonl"
        lines = sink.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1  # P1-3 验收点：拦截日志含触发建议记录
        record = json.loads(lines[0])
        assert record["model_id"] == "qwen3:8b" and record["capability"] == "code_fix"

    def test_allowed_decision_resets_streak(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.record_gate_decision("qwen3:8b", "code_fix", True, "ok") is None
        assert sched.block_streaks == {}
        # 重新累计需再满阈值才发建议
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.suggestions == []

    def test_non_low_accuracy_block_resets_streak(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, "no_passport")  # 非 low_accuracy
        assert sched.block_streaks == {}
        assert sched.suggestions == []

    def test_streaks_tracked_per_model_capability_pair(self, tmp_path):
        sched = self._sched(tmp_path, threshold=2)
        reason = "low_accuracy: x"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.record_gate_decision("qwen3:8b", "refactor", False, reason) is None
        assert sched.suggestions == []  # 不同能力各自计数，互不累计

    def test_check_and_record_passthrough_and_suggestion(self, tmp_path):
        class _FakeGate:
            def __init__(self, verdict):
                self._verdict = verdict

            def can_dispatch(self, model_id, capability):
                return self._verdict

        sched = self._sched(tmp_path, threshold=2)
        gate = _FakeGate((False, "low_accuracy: low_precision_below_threshold"))
        assert sched.check_and_record(gate, "qwen3:8b", "code_fix") == (
            False,
            "low_accuracy: low_precision_below_threshold",
        )
        ok, _ = sched.check_and_record(gate, "qwen3:8b", "code_fix")
        assert ok is False
        assert len(sched.suggestions) == 1


class TestFailClosed:
    def test_invalid_threshold(self, tmp_path):
        with pytest.raises(ExamTriggerError) as exc_info:
            ExamTriggerScheduler(low_accuracy_threshold=0)
        assert exc_info.value.error_code == "ZA-IT-0011"

    def test_corrupted_seen_store(self, tmp_path):
        seen_path = tmp_path / "seen.json"
        seen_path.write_text("{not-json", encoding="utf-8")
        with pytest.raises(ExamTriggerError, match="seen 快照损坏"):
            ExamTriggerScheduler(seen_store_path=seen_path)


class TestCliScanNewModels:
    """CLI 入口（python -m ... scan-new-models [--dry-run]）。

    dry-run 只列新模型不跑考试（只读预览，盘中可用）；真实模式跑 Quick 考试落盘
    QuickProfile；盘中守卫拒跑真实模式（复用 reflexion is_intraday 口径，测试注入假守卫，
    Quick 考试吃 GPU 盘后是设计口径）。发现器/runner 全 fake，零真考试零网络。
    """

    def _factory(self, tmp_path, models, runner):
        def factory():
            return ExamTriggerScheduler(
                discovery=_FakeDiscovery(models),
                quick_exam_runner=runner,
                seen_store_path=tmp_path / "seen.json",
            )

        return factory

    def _runner(self, called):
        def run(model_id):
            called.append(model_id)
            return QuickProfile(model_id=model_id, overall_score=0.5)

        return run

    def test_dry_run_lists_new_models_without_exams(self, isolated_dirs, tmp_path, capsys):
        called = []
        factory = self._factory(tmp_path, [_ollama("qwen3:8b")], self._runner(called))
        rc = sched_mod.main(
            ["scan-new-models", "--dry-run"],
            scheduler_factory=factory,
            intraday_check=lambda: False,
        )
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["dry_run"] is True
        assert out["new_models"] == ["qwen3:8b"]
        assert called == []  # dry-run 不跑考试
        assert not (isolated_dirs["quick"] / "qwen3_8b.json").exists()

    def test_real_run_executes_quick_exams_off_hours(self, isolated_dirs, tmp_path, capsys):
        called = []
        factory = self._factory(tmp_path, [_ollama("qwen3:8b")], self._runner(called))
        rc = sched_mod.main(
            ["scan-new-models"],
            scheduler_factory=factory,
            intraday_check=lambda: False,
        )
        assert rc == 0
        assert called == ["qwen3:8b"]  # 真实模式跑 Quick 考试
        out = json.loads(capsys.readouterr().out)
        assert out["dry_run"] is False and out["examined"] == ["qwen3:8b"]
        assert (isolated_dirs["quick"] / "qwen3_8b.json").exists()  # QuickProfile 落盘

    def test_intraday_guard_refuses_real_run(self, isolated_dirs, tmp_path, capsys):
        called = []
        factory = self._factory(tmp_path, [_ollama("qwen3:8b")], self._runner(called))
        rc = sched_mod.main(
            ["scan-new-models"],
            scheduler_factory=factory,
            intraday_check=lambda: True,  # 盘中
        )
        assert rc == 2
        assert called == []  # 盘中拒跑：Quick 考试吃 GPU，盘后是设计口径
        assert "盘中" in capsys.readouterr().err

    def test_dry_run_allowed_during_intraday(self, isolated_dirs, tmp_path, capsys):
        called = []
        factory = self._factory(tmp_path, [_ollama("qwen3:8b")], self._runner(called))
        rc = sched_mod.main(
            ["scan-new-models", "--dry-run"],
            scheduler_factory=factory,
            intraday_check=lambda: True,  # 盘中
        )
        assert rc == 0  # dry-run 只读预览不碰 GPU，盘中可用
        assert called == []


# ── C-3 对拍（v2 方案）：新 e0_window_refusal（E0 单源）↔ 旧 is_intraday（墙钟自判）──
# 钉的是**三处有意差异本身**（更宽带 / 日历真源 / fail-closed），不是钉两者相等：
# 差异方向全部朝"更保守 + 日历说真话"，故新口径拒跑面 ⊇ 旧口径拒跑面（同一交易日上）。
# 日历通道注入假值 → 零 CH 连接、零网络；执行体/考试 runner 全 fake，零真考试。

_CN_TZ = ZoneInfo("Asia/Shanghai")
_TRADING_DAY = date(2026, 9, 16)  # 周三（真·交易日样例）
_HOLIDAY_THURSDAY = date(2026, 10, 1)  # 法定节假日落在周四（日历判休市）
_MAKEUP_SATURDAY = date(2026, 10, 10)  # 调休补班的周六（日历判开市）
_DEAD_SATURDAY = date(2026, 9, 19)  # 普通周六（两口径都该盘外）


def _cn(d: date, hh: int, mm: int) -> datetime:
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=_CN_TZ)


def _old_is_intraday(moment: datetime) -> bool:
    """对拍基准：旧 reflexion 墙钟工作日 09:30-15:00 自判（已退役为口径，代码仍在盘）。"""
    br = pytest.importorskip("zephyr.intelligence.reflexion.batch_runner")
    return br.is_intraday(moment)


@pytest.fixture()
def fake_calendar(monkeypatch):
    """把 E0 的日历通道换成假日历（value=True/False/None），并回收被问到的日期。"""
    e0 = sched_mod._load_e0_module()
    asked: list[date] = []

    def install(value):
        def _fetch(d: date):
            asked.append(d)
            return value

        monkeypatch.setattr(e0, "fetch_is_trading_day", _fetch)
        return asked

    return install


class TestE0WindowRefusalDifferential:
    """Quick 考试盘中守卫=E0 算力窗闸：盘中拒跑/盘外放行/边界分钟逐一钉。"""

    @staticmethod
    def _cli_factory(tmp_path, models, runner):
        def factory():
            return ExamTriggerScheduler(
                discovery=_FakeDiscovery(models),
                quick_exam_runner=runner,
                seen_store_path=tmp_path / "seen.json",
            )

        return factory

    @staticmethod
    def _cli_runner(called):
        def run(model_id):
            called.append(model_id)
            return QuickProfile(model_id=model_id, overall_score=0.5)

        return run

    def test_guard_asks_gate_with_local_date_not_wall_clock_weekday(self, fake_calendar):
        """守卫问闸的姿势=按北京日历日问真源（而非自己数星期几）。"""
        asked = fake_calendar(True)
        refused, reason = sched_mod.e0_window_refusal(_cn(_TRADING_DAY, 10, 0))
        assert refused is True and asked == [_TRADING_DAY]
        assert "gate_deny_trading_hours" in reason and "is_trading_day=True" in reason

    def test_utc_moment_converted_to_beijing_day_before_asking(self, fake_calendar):
        """跨时区注入：20:00Z=次日 04:00 北京 → 问的是北京那一天（旧口径同样 astimezone，
        但新口径的日历键由此对齐，不出现"北京时间问昨天日历"的错档）。"""
        asked = fake_calendar(True)
        moment = datetime(2026, 9, 19, 20, 0, tzinfo=ZoneInfo("UTC"))  # = 09-20 04:00 CST
        assert moment.astimezone(_CN_TZ).date() == date(2026, 9, 20)
        refused, _ = sched_mod.e0_window_refusal(moment)
        assert refused is False  # 周日 04:00=盘外黄金窗（日历按 True 注入仍放行）
        assert asked == [date(2026, 9, 20)]

    @pytest.mark.parametrize(
        "hh,mm,refused,reason_code",
        [
            (0, 0, False, "gate_allow_off_hours"),      # 凌晨黄金窗
            (4, 0, False, "gate_allow_off_hours"),      # 演练/排产起跑档同窗
            (8, 59, False, "gate_allow_off_hours"),     # 开盘缓冲前 1 分钟
            (9, 0, True, "gate_deny_trading_hours"),    # 差异①新增拒（旧口径此刻放行）
            (9, 29, True, "gate_deny_trading_hours"),   # 差异①新增拒
            (9, 30, True, "gate_deny_trading_hours"),   # 两口径共同拒的起点
            (10, 0, True, "gate_deny_trading_hours"),   # 盘中
            (14, 59, True, "gate_deny_trading_hours"),  # 收盘前 1 分钟
            (15, 0, True, "gate_deny_trading_hours"),   # 差异①新增拒（旧口径此刻放行）
            (15, 29, True, "gate_deny_trading_hours"),  # 差异①新增拒
            (15, 30, False, "gate_allow_off_hours"),    # 收盘缓冲尾（含）→ 放行
            (16, 0, False, "gate_allow_off_hours"),
            (23, 59, False, "gate_allow_off_hours"),
        ],
    )
    def test_trading_day_refusal_band(self, fake_calendar, hh, mm, refused, reason_code):
        """交易日保守带 09:00-15:30 拒重算力，带外放行（边界分钟含头不含尾）。"""
        fake_calendar(True)
        got, reason = sched_mod.e0_window_refusal(_cn(_TRADING_DAY, hh, mm))
        assert got is refused
        assert reason_code in reason

    def test_dif1_new_band_is_strict_superset_of_old(self, fake_calendar):
        """差异①：新口径在 09:00-09:30 与 15:00-15:30 双侧各多拒 30 分钟，无一分钟放松。"""
        fake_calendar(True)
        moment = _cn(_TRADING_DAY, 9, 15)
        assert _old_is_intraday(moment) is False and sched_mod.e0_window_refusal(moment)[0] is True
        moment2 = _cn(_TRADING_DAY, 15, 15)
        assert _old_is_intraday(moment2) is False and sched_mod.e0_window_refusal(moment2)[0] is True
        # 超集性质：08:00-17:00 每 5 分钟扫一遍——旧判盘中处，新必判拒（绝无放松）
        relaxed = []
        for minute in range(8 * 60, 17 * 60, 5):
            m = _cn(_TRADING_DAY, minute // 60, minute % 60)
            if _old_is_intraday(m) and not sched_mod.e0_window_refusal(m)[0]:
                relaxed.append(m.strftime("%H:%M"))
        assert relaxed == []

    def test_dif2_calendar_truth_beats_wall_clock_weekday(self, fake_calendar):
        """差异②：日历说真话——法定假日的周四旧误拒（该跑被拦）新放行；调休补班的周六
        旧漏拒（不该跑却裸奔）新受闸。两个方向都是"新跟着日历、旧跟着星期几"。"""
        # 法定假日（周四 10:00，日历休市）：旧拒 → 新放行
        fake_calendar(False)
        holiday = _cn(_HOLIDAY_THURSDAY, 10, 0)
        assert _old_is_intraday(holiday) is True
        assert sched_mod.e0_window_refusal(holiday) == (False, "gate_allow_off_hours")
        # 调休补班（周六 10:00，日历开市）：旧放行 → 新拒
        fake_calendar(True)
        makeup = _cn(_MAKEUP_SATURDAY, 10, 0)
        assert _old_is_intraday(makeup) is False
        refused, reason = sched_mod.e0_window_refusal(makeup)
        assert refused is True and "gate_deny_trading_hours" in reason

    def test_dif3_unreachable_calendar_fails_closed(self, fake_calendar):
        """差异③：日历缺席（CH 断/未覆盖）→ fail-closed 拒跑，而非退回墙钟自判放行。"""
        fake_calendar(None)
        refused, reason = sched_mod.e0_window_refusal(_cn(_TRADING_DAY, 10, 0))
        assert refused is True and "gate_deny_calendar_unknown" in reason
        # 关键对照：普通周六盘外（旧口径放行）遇日历不可达，新口径仍拒=真 fail-closed
        saturday = _cn(_DEAD_SATURDAY, 10, 0)
        assert _old_is_intraday(saturday) is False
        assert sched_mod.e0_window_refusal(saturday)[0] is True

    def test_dif3_calendar_channel_exception_fails_closed(self, fake_calendar, monkeypatch):
        """日历通道抛异常 → 同样拒跑并留"判定异常"痕（守卫不得因自身故障放行）。"""
        e0 = sched_mod._load_e0_module()

        def _boom(_d):
            raise RuntimeError("CH 不可达")

        monkeypatch.setattr(e0, "fetch_is_trading_day", _boom)
        refused, reason = sched_mod.e0_window_refusal(_cn(_TRADING_DAY, 10, 0))
        assert refused is True
        assert "判定异常" in reason and "CH 不可达" in reason

    def test_naive_datetime_fails_closed(self, fake_calendar):
        """naive 时刻（违 RULE-SCHEMA-TZ）不得被当成盘外放行——E0 拒收 → 守卫拒跑。"""
        fake_calendar(True)
        refused, reason = sched_mod.e0_window_refusal(datetime(2026, 9, 16, 10, 0))
        assert refused is True and "naive" in reason

    def test_missing_e0_module_fails_closed(self, tmp_path, monkeypatch):
        """E0 闸装不上（文件缺席）→ 拒跑并点名"不可装载"，绝不静默放行裸奔 GPU。"""
        from zephyr.shared.io import paths as paths_mod

        saved = dict(sched_mod._E0_MODULE_CACHE)
        sched_mod._E0_MODULE_CACHE.clear()
        monkeypatch.setattr(paths_mod, "REPO_ROOT", tmp_path / "no_such_repo")
        try:
            refused, reason = sched_mod.e0_window_refusal(_cn(_DEAD_SATURDAY, 10, 0))
            assert refused is True
            assert "闸模块不可装载" in reason
        finally:  # 单例缓存必须复原，否则污染同进程后续测试
            sched_mod._E0_MODULE_CACHE.clear()
            sched_mod._E0_MODULE_CACHE.update(saved)
        assert sched_mod._load_e0_module().__file__.replace("\\", "/").endswith(
            "scripts/backtest/compute_window_gate.py")

    def test_quick_exam_is_declared_heavy_so_the_band_bites(self, fake_calendar):
        """考试申报口径=local_gpu（吃 GPU）→ 属重车道，才会被保守带拦；轻车道随时跑。"""
        e0 = sched_mod._load_e0_module()
        assert sched_mod._E0_COMPUTE_CLASS == "local_gpu"
        assert e0.needs_heavy_window(sched_mod._E0_COMPUTE_CLASS) is True
        assert e0.needs_heavy_window("local") is False  # 对照：轻类不受带管辖
        fake_calendar(True)
        assert sched_mod.e0_window_refusal(_cn(_TRADING_DAY, 10, 0))[0] is True

    def test_is_intraday_alias_now_follows_e0_not_wall_clock(self, fake_calendar):
        """双实现归一钉：沿用旧名的 `is_intraday` 在本模块已改口 E0——09:15 交易日旧口径
        判"盘外"、本模块判"受闸"，且与 e0_window_refusal 逐点同值（名字未变语义已换）。"""
        fake_calendar(True)
        moment = _cn(_TRADING_DAY, 9, 15)
        assert _old_is_intraday(moment) is False
        assert sched_mod.is_intraday(moment) is True
        for hh, mm in [(0, 0), (8, 59), (9, 0), (10, 0), (15, 29), (15, 30), (23, 59)]:
            m = _cn(_TRADING_DAY, hh, mm)
            assert sched_mod.is_intraday(m) is sched_mod.e0_window_refusal(m)[0]

    def test_cli_real_run_asks_e0_guard_when_no_injected_check(self, isolated_dirs, tmp_path,
                                                               capsys, monkeypatch):
        """CLI 真实模式（无注入缝）必问 E0：拒跑→rc2 且零考试；放行→rc0 跑 Quick。"""
        called: list[str] = []
        factory = self._cli_factory(tmp_path, [_ollama("qwen3:8b")], self._cli_runner(called))
        seen: list[bool] = []

        def _refused(now=None):
            seen.append(True)
            return True, "E0 gate_deny_trading_hours（window=light_only，is_trading_day=True）"

        monkeypatch.setattr(sched_mod, "e0_window_refusal", _refused)
        assert sched_mod.main(["scan-new-models"], scheduler_factory=factory) == 2
        assert seen == [True] and called == []
        err = capsys.readouterr().err
        assert "盘中拒跑" in err and "FAC-E0" in err and "gate_deny_trading_hours" in err

        called.clear()
        monkeypatch.setattr(sched_mod, "e0_window_refusal",
                            lambda now=None: (False, "gate_allow_off_hours"))
        assert sched_mod.main(["scan-new-models"], scheduler_factory=factory) == 0
        assert called == ["qwen3:8b"]  # 放行走完 Quick 考试
        assert "盘中拒跑" not in capsys.readouterr().err

    def test_injected_seam_short_circuits_e0_guard(self, isolated_dirs, tmp_path, monkeypatch):
        """测试注入缝优先：注入 intraday_check 时不再问 E0（既有 CLI 测试的契约不变）。"""
        called: list[str] = []
        factory = self._cli_factory(tmp_path, [_ollama("qwen3:8b")], self._cli_runner(called))

        def _never():  # pragma: no cover — 被调到即失败
            raise AssertionError("注入守卫在场时不应再问 E0")

        monkeypatch.setattr(sched_mod, "e0_window_refusal", _never)
        assert sched_mod.main(["scan-new-models"], scheduler_factory=factory,
                              intraday_check=lambda: False) == 0
        assert called == ["qwen3:8b"]
