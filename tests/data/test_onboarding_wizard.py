# [A_test] module_id: MOD-DATA-onboarding_wizard_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.data.test_onboarding_wizard
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.onboarding_wizard; stdlib(pytest/tmp_path/yaml)
# [CONSUMERS] CI pytest
# [STARTUP] test_only
# [MATURITY] testing
# [INVARIANTS] 全 mock：run_command 注入桩（禁真跑 DDL 脚本、禁连业务库）；五册三目录全部落 tmp_path
#   仿真仓（禁写 data/ 业务目录与真实注册表）；断言读盘核实不看返回值单证；
#   DDL 桩只验"命令派生正确+返回码语义"，不验 ClickHouse 行为（那属 apply_*_ddl 自身测试面）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=状态机契约不成立；无自愈
# [TESTS] python -m pytest tests/data/test_onboarding_wizard.py -q
# [TTL] permanent
"""onboarding_wizard 十环状态机测试（推进/断点续跑/人工暂停/机器环调用/dry-run，全 mock tmp_path）."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data.onboarding_wizard import (
    OnboardingRequest,
    OnboardingWizard,
    OnboardingWizardError,
    RingStatus,
    WizardDeps,
)

# ========== 仿真仓夹具 ==========

CAND_DOC = """---
ttl: task_bound
---

version: "0.0.0-test"
candidates:
  - cand_id: DS-CAND-999
    name: "测试候选"
    vendor: "测试机构"
    acquire_mode: api_free
    cost: free
    register_barrier: ""
    coverage: "测试覆盖"
    frequency: daily
    history_depth: "10 年"
    anti_crawl_risk: none
    tos_risk: ""
    score: {availability: 3, signal: 3, fit: 3, maintenance: 3}
    target_table: "c1_market.test_table"
    status: candidate
    notes: ""
"""

DS_DOC = """version: "0.0.0-test"
description: "测试 DS 册"
data_sources:
"""

TASKS_DOC = """version: 0
tasks:
  - task_id: existing_task
    table: c1_market.existing_table
    source: akshare
    schedule: daily_kline
    incremental: true
    date_col: trade_date
    dependencies: []
    capability: kline_daily
    fallback_sources: []
    extra:
      description: "存量任务"
"""

SCHEDULE_DOC = """version: 0
schedules:
  daily_kline:
    cron: "30 16 * * 1-5"
    executor: default
  daily_event:
    cron: "*/5 * * * *"
    executor: default
"""

CATEGORY_DOC = """- category_id: existing_table
  name: "存量表"
  engine: clickhouse
  database: c1_market
  table: existing_table
  schema_file: null
  data_type: 行情
  lifecycle: hot_90d
  enabled: true
"""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """五册三目录齐备的仿真仓。"""
    root = tmp_path / "repo"
    root.mkdir()
    _write(root / "docs/_working/altdata_line/10_data_source_candidates.yaml", CAND_DOC)
    _write(root / "architecture_model/data/data_sources_registry.yaml", DS_DOC)
    _write(root / "src/zephyr/data/config/tasks.yaml", TASKS_DOC)
    _write(root / "src/zephyr/data/config/schedule.yaml", SCHEDULE_DOC)
    _write(root / "docs/03_modules/_cross_layer/database/business_data_categories.yaml", CATEGORY_DOC)
    _write(root / "schemas/categories/market/test_table.py", "# DDL-as-Code 设计件（仿真）\n")
    _write(root / "src/zephyr/data/implementations/testprov_provider.py", "# provider（仿真）\n")
    return root


def _ddl_spy(calls: list[list[str]], rc: int = 0):
    def run(cmd: list[str]) -> tuple[int, str]:
        calls.append(list(cmd))
        return rc, "stub ok" if rc == 0 else "stub boom"

    return run


def _request(**over: Any) -> OnboardingRequest:
    base: dict[str, Any] = dict(
        source_id="DS-TEST",
        cand_id="DS-CAND-999",
        table="c1_market.test_table",
        schema_domain="market",
        provider="testprov",
        task_id="test_table_incremental",
        schedule_slot="daily_kline",
        date_col="trade_date",
        capability="test_cap",
        description="测试源",
        fallback_sources=["akshare"],
        consumer="回测引擎",
    )
    base.update(over)
    return OnboardingRequest(**base)


def _wizard(repo: Path, req: OnboardingRequest, run=None) -> OnboardingWizard:
    deps = WizardDeps(
        repo_root=repo, state_dir=Path("data/runtime/onboarding"), run_command=run, session="st-c9-f02-test"
    )
    return OnboardingWizard(deps, request=req)


def _ring(repo: Path, sid: str, ring_id: str) -> dict[str, Any]:
    state = json.loads((repo / "data/runtime/onboarding" / sid / "state.json").read_text(encoding="utf-8"))
    return state["rings"][ring_id]


# ========== ① 状态机推进（机器环顺序执行+人工环暂停） ==========


class TestStateMachineAdvance:
    def test_start_runs_r1_then_pauses_at_graduation(self, fake_repo: Path) -> None:
        # DS-CAND-888 不在仿真册 → R1 候选环暂停出待办（挖矿登记=人工件）
        wiz = _wizard(fake_repo, _request(cand_id="DS-CAND-888", candidate_entry=None))
        report = wiz.start()
        r1 = _ring(fake_repo, "DS-TEST", "candidate")
        assert r1["status"] == RingStatus.MANUAL_WAIT
        assert "三重扫描" in r1["instruction"]
        assert report.stopped_at == "candidate"
        # 后续环未被推进（状态机逐步暂停语义）
        assert _ring(fake_repo, "DS-TEST", "graduation")["status"] == RingStatus.PENDING
        # checklist 落盘
        assert "candidate" in (fake_repo / "data/runtime/onboarding/DS-TEST/checklist.md").read_text(encoding="utf-8")

    def test_full_chain_machine_rings_execute_in_order(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls))
        # R1 候选已仿真在册 → done；R2 人工毕业 → confirm 回执；R3-R8 机器环应顺序执行
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="Owner 批（测试）")
        report = wiz.resume("DS-TEST")
        # R3 DS 册：条目落 DS 册+候选翻转 promoted（O4 两册联动读盘核实）
        ds_doc = yaml.safe_load(
            (fake_repo / "architecture_model/data/data_sources_registry.yaml").read_text(encoding="utf-8")
        )
        assert any(e["id"] == "DS-TEST" for e in ds_doc["data_sources"])
        cand_doc = yaml.safe_load_all(
            (fake_repo / "docs/_working/altdata_line/10_data_source_candidates.yaml").read_text(encoding="utf-8")
        )
        cand = [d for d in cand_doc if isinstance(d, dict) and "candidates" in d][0]
        assert cand["candidates"][0]["status"] == "promoted"
        # R5 DDL：机器环调用注入桩，命令派生=apply_test_table_ddl.py
        assert calls and calls[0][-1].endswith("apply_test_table_ddl.py")
        # R6 品类：读盘核实
        cat = yaml.safe_load(
            (fake_repo / "docs/03_modules/_cross_layer/database/business_data_categories.yaml").read_text(
                encoding="utf-8"
            )
        )
        assert any(e["table"] == "test_table" for e in cat)
        # R7 任务：读盘核实+O2 键在
        tasks = yaml.safe_load((fake_repo / "src/zephyr/data/config/tasks.yaml").read_text(encoding="utf-8"))
        entry = [t for t in tasks["tasks"] if t["task_id"] == "test_table_incremental"][0]
        assert "fallback_sources" in entry and entry["fallback_sources"] == ["akshare"]
        # R8 槽位合法 → 推进到 R9 人工环暂停
        assert report.stopped_at == "first_run"
        assert _ring(fake_repo, "DS-TEST", "schedule_slot")["status"] == RingStatus.DONE

    def test_finish_after_manual_confirmations(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        wiz.resume("DS-TEST")
        wiz.confirm("DS-TEST", "first_run", note="首跑 11487 行对账平")
        report = wiz.resume("DS-TEST")
        assert report.stopped_at == "acceptance"
        wiz.confirm("DS-TEST", "acceptance", note="三查过+哨兵腿在岗")
        final = wiz.status("DS-TEST")
        assert all(r.status == RingStatus.DONE for r in final.rings)


# ========== ② 断点续跑 ==========


class TestResume:
    def test_resume_skips_done_rings_without_reexecution(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        wiz.resume("DS-TEST")  # 第一次跑：DDL 执行 1 次，停于 first_run
        assert len(calls) == 1
        wiz.confirm("DS-TEST", "first_run", note="首跑过")
        wiz.resume("DS-TEST")  # 停于 acceptance
        wiz.confirm("DS-TEST", "acceptance", note="三查过")
        wiz.resume("DS-TEST")  # 续跑：全部 done，DDL 不得重跑（幂等断点）
        assert len(calls) == 1

    def test_resume_without_state_raises(self, fake_repo: Path) -> None:
        with pytest.raises(OnboardingWizardError, match="无在途 state"):
            _wizard(fake_repo, _request()).resume("DS-NONE")

    def test_start_twice_raises(self, fake_repo: Path) -> None:
        _wizard(fake_repo, _request()).start()
        with pytest.raises(OnboardingWizardError, match="resume"):
            _wizard(fake_repo, _request()).start()


# ========== ③ 人工环暂停（产出待办不代做） ==========


class TestManualRingPause:
    def test_graduation_manual_waits_with_owner_routing(self, fake_repo: Path) -> None:
        # 候选在册但 status=candidate（未毕业）→ 毕业环必须停（四格 3+api_free → 路由建议=直接推进）
        wiz = _wizard(fake_repo, _request())
        report = wiz.start()
        assert report.stopped_at == "graduation"
        rec = _ring(fake_repo, "DS-TEST", "graduation")
        assert rec["status"] == RingStatus.MANUAL_WAIT
        assert "Owner" in rec["instruction"]

    def test_provider_manual_waits_until_file_exists(self, fake_repo: Path) -> None:
        (fake_repo / "src/zephyr/data/implementations/testprov_provider.py").unlink()
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        report = wiz.resume("DS-TEST")
        assert report.stopped_at == "provider"
        assert "三闸" in _ring(fake_repo, "DS-TEST", "provider")["instruction"]
        # 人工环不代做：provider 文件不得被向导凭空造出
        assert not (fake_repo / "src/zephyr/data/implementations/testprov_provider.py").exists()
        # 人工件落地后 resume 自动检出闭环
        _write(fake_repo / "src/zephyr/data/implementations/testprov_provider.py", "# 人工补\n")
        report2 = wiz.resume("DS-TEST")
        assert _ring(fake_repo, "DS-TEST", "provider")["status"] == RingStatus.DONE
        assert report2.stopped_at != "provider"

    def test_confirm_rejects_machine_ring_and_wrong_state(self, fake_repo: Path) -> None:
        wiz = _wizard(fake_repo, _request())
        wiz.start()
        with pytest.raises(OnboardingWizardError, match="非人工环"):
            wiz.confirm("DS-TEST", "ddl", note="越权")
        with pytest.raises(OnboardingWizardError, match="仅 manual_wait"):
            wiz.confirm("DS-TEST", "provider", note="状态未到")


# ========== ④ 机器环调用（全 mock） ==========


class TestMachineRings:
    def test_ddl_failure_marks_failed_and_stops(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls, rc=1))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        report = wiz.resume("DS-TEST")
        assert _ring(fake_repo, "DS-TEST", "ddl")["status"] == RingStatus.FAILED
        assert report.stopped_at == "ddl"
        # 失败环之后的品类/任务环不得推进
        assert _ring(fake_repo, "DS-TEST", "category")["status"] == RingStatus.PENDING

    def test_ddl_missing_schema_pauses_with_design_todo(self, fake_repo: Path) -> None:
        (fake_repo / "schemas/categories/market/test_table.py").unlink()
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy([]))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        report = wiz.resume("DS-TEST")
        assert report.stopped_at == "ddl"
        rec = _ring(fake_repo, "DS-TEST", "ddl")
        assert rec["status"] == RingStatus.MANUAL_WAIT
        assert "PIT" in rec["instruction"]

    def test_graduation_gate_blocks_ds_registry(self, fake_repo: Path) -> None:
        # 毕业环未 confirm → DS 册环拒绝执行（O4 前置），且不写任何册
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(candidate_entry=None), run=_ddl_spy(calls))
        wiz.start()
        before = (fake_repo / "architecture_model/data/data_sources_registry.yaml").read_text(encoding="utf-8")
        wiz.resume("DS-TEST")  # 停在 candidate（R1 未闭环）
        # 人工直接把候选登记进册（模拟走完 R1）但毕业未 confirm
        cand_path = fake_repo / "docs/_working/altdata_line/10_data_source_candidates.yaml"
        text = cand_path.read_text(encoding="utf-8")
        _write(cand_path, text + "  - cand_id: DS-CAND-888\n    name: x\n    status: candidate\n")
        wiz2 = _wizard(fake_repo, _request(cand_id="DS-CAND-888"), run=_ddl_spy(calls))
        wiz2.resume("DS-TEST")
        after = (fake_repo / "architecture_model/data/data_sources_registry.yaml").read_text(encoding="utf-8")
        assert before == after  # DS 册零写入

    def test_crawler_source_rejected_at_validation(self, fake_repo: Path) -> None:
        with pytest.raises(OnboardingWizardError, match="crawler"):
            _wizard(fake_repo, _request(candidate_entry={"cand_id": "DS-CAND-777", "acquire_mode": "crawler"})).start()


# ========== ⑤ O2/O3 硬校验（登记时拦截） ==========


class TestO2O3Gates:
    def test_o2_fallback_missing_blocks_task_registration(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(fallback_sources=[], fallback_note=""), run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        report = wiz.resume("DS-TEST")
        assert report.stopped_at == "task_register"
        assert "O2" in _ring(fake_repo, "DS-TEST", "task_register")["detail"]
        tasks = yaml.safe_load((fake_repo / "src/zephyr/data/config/tasks.yaml").read_text(encoding="utf-8"))
        assert all(t["task_id"] != "test_table_incremental" for t in tasks["tasks"])  # 条目未落

    def test_o2_explicit_empty_with_note_passes(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        req = _request(fallback_sources=[], fallback_note="显式置空：唯一免费结构化口径")
        wiz = _wizard(fake_repo, req, run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        wiz.resume("DS-TEST")
        tasks = yaml.safe_load((fake_repo / "src/zephyr/data/config/tasks.yaml").read_text(encoding="utf-8"))
        entry = [t for t in tasks["tasks"] if t["task_id"] == "test_table_incremental"][0]
        assert entry["fallback_sources"] == []
        assert "显式置空" in entry["extra"]["fallback_note"]

    def test_o3_disabled_without_reason_hard_blocked(self, fake_repo: Path) -> None:
        with pytest.raises(OnboardingWizardError, match="O3"):
            _request(disabled=True, disabled_reason="").validate()

    def test_o3_existing_entry_missing_reason_flags_failed(self, fake_repo: Path) -> None:
        # 已在册条目 disabled 且缺 disabled_reason → check 判 failed（O3 登记后巡检语义）
        tasks_path = fake_repo / "src/zephyr/data/config/tasks.yaml"
        _write(tasks_path, TASKS_DOC.replace("    extra:", "    disabled: true\n    extra:"))
        calls: list[list[str]] = []
        wiz = _wizard(
            fake_repo,
            _request(task_id="existing_task", table="c1_market.test_table"),
            run=_ddl_spy(calls),
        )
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        report = wiz.resume("DS-TEST")
        assert report.stopped_at == "task_register"
        rec = _ring(fake_repo, "DS-TEST", "task_register")
        assert rec["status"] == RingStatus.FAILED
        assert "O3" in rec["detail"]


# ========== ⑥ dry-run 零落盘 ==========


class TestDryRun:
    def test_dry_run_writes_nothing_anywhere(self, fake_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
        calls: list[list[str]] = []
        snapshots = {
            p: p.read_text(encoding="utf-8")
            for p in [
                fake_repo / "docs/_working/altdata_line/10_data_source_candidates.yaml",
                fake_repo / "architecture_model/data/data_sources_registry.yaml",
                fake_repo / "src/zephyr/data/config/tasks.yaml",
                fake_repo / "docs/03_modules/_cross_layer/database/business_data_categories.yaml",
            ]
        }
        wiz = _wizard(fake_repo, _request(), run=_ddl_spy(calls))
        report = wiz.start(dry_run=True)
        out = capsys.readouterr().out + report.render()
        assert "dry-run" in out
        assert calls == []  # 机器环不执行
        assert not (fake_repo / "data/runtime/onboarding/DS-TEST").exists()  # state/checklist 零落盘
        for path, before in snapshots.items():
            assert path.read_text(encoding="utf-8") == before  # 五册零写入

    def test_dry_run_resume_also_writes_nothing(self, fake_repo: Path) -> None:
        wiz = _wizard(fake_repo, _request())
        wiz.start()
        before = (fake_repo / "data/runtime/onboarding/DS-TEST/state.json").read_text(encoding="utf-8")
        _wizard(fake_repo, _request()).resume("DS-TEST", dry_run=True)
        assert (fake_repo / "data/runtime/onboarding/DS-TEST/state.json").read_text(encoding="utf-8") == before


# ========== ⑦ 请求契约 ==========


class TestRequestContract:
    def test_source_id_must_be_ds_prefixed(self) -> None:
        with pytest.raises(OnboardingWizardError, match="DS-"):
            _request(source_id="X-1").validate()

    def test_acquire_mode_enum_enforced(self) -> None:
        with pytest.raises(OnboardingWizardError, match="acquire_mode"):
            _request(candidate_entry={"cand_id": "DS-CAND-1", "acquire_mode": "teleport"}).validate()

    def test_cand_id_mismatch_rejected(self) -> None:
        with pytest.raises(OnboardingWizardError, match="不一致"):
            _request(
                cand_id="DS-CAND-999", candidate_entry={"cand_id": "DS-CAND-111", "acquire_mode": "api_free"}
            ).validate()

    def test_daily_event_slot_flagged_in_instruction(self, fake_repo: Path) -> None:
        calls: list[list[str]] = []
        wiz = _wizard(fake_repo, _request(schedule_slot="daily_event"), run=_ddl_spy(calls))
        wiz.start()
        wiz.confirm("DS-TEST", "graduation", note="批")
        wiz.resume("DS-TEST")
        detail = _ring(fake_repo, "DS-TEST", "schedule_slot")["detail"]
        assert "断供前科" in detail

    def test_render_report_lists_all_ten_rings(self, fake_repo: Path) -> None:
        report = _wizard(fake_repo, _request()).start(dry_run=True)
        assert len(report.rings) == 10
        text = report.render()
        assert text.count("环") >= 5 and "candidate" in text and "acceptance" in text
