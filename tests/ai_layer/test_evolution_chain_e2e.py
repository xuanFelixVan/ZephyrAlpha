# [MODULE] tests.ai_layer.test_evolution_chain_e2e
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_e2e
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.{perceive,intake,cleaning,comparator,scheduling,switch_engine,heritage};
#                zephyr.intelligence.switch_engine; scripts/ai_layer DDL 三件
# [CONSUMERS] pytest tests/ai_layer/test_evolution_chain_e2e.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 七段单函数按 L1→L7 顺序推进，断言消息一律 "[Lx]" 前缀定位段落；
#              DB 只写 ai_*_test_e2echain 一次性临时 schema（真 DDL、真 PG，finally DROP）；
#              journal/工单/种子/影子产物/registry sqlite 全落 tmp_path（零生产路径写入）；
#              LLM 调用为零（washer 网关/消毒器注入替身，同 test_washer 惯例）；
#              git 封存走注入 runner（记录调用不触真仓，同 conftest.fake_git 惯例）；
#              PG 不可达=skip 而非假绿
# [MODIFY-GUARD] docs/_working/ai_layer_vision/（L1 感知～L7 传承 DESIGN 套件）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；段内拒收路径以机读拒因断言
# [TESTS] tests/ai_layer/test_evolution_chain_e2e.py
# [TTL] permanent
"""test_evolution_chain_e2e - 进化链 L1→L7 端到端集成测试（七段推进，每段一个断言锚）。

链路语义（vision 定调）：
  L1 感知（源注册表/搜索任务单/翻译器）→ L2 收集（入库闸/查重/卡库状态机/事件）
  → L3 清洗（规格/washer/审计）→ L4 比较（实验执行器/判据冻结/考场）
  → L5 排产（路由/派工/种子）→ L6 切换（注册表/影子/迁移器）→ L7 传承（入库检查/先验/closure_check/forget）。

跨段真链路（非七个孤立测试）：
  L1 配额同步落 T5 → L2 配额闸真读；L1 搜索工单以候选卡出生证收单（produced_ref）；
  L2 候选卡经真 CardStore 进 L3 washer（card_reader/card_writer 同库）；L3 规格件作 L4 挑战者；
  L4 判据冻结哈希作 L6 switch 判据哈希、L7 判据档案哈希核对；L6 退役封存后复活票恒回 shadow；
  L7 forget 只降级不删；复活信号回灌 L1 同矿脉冷却节流（链路闭环）。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from zephyr.shared.io.paths import REPO_ROOT

INTAKE_SCHEMA = "ai_intake_test_e2echain"
COMPARE_SCHEMA = "ai_compare_test_e2echain"
HERITAGE_SCHEMA = "ai_heritage_test_e2echain"

FIXED_NOW: datetime = datetime(2026, 9, 24, 12, 0, 0, tzinfo=UTC)
T_FROZEN, T_DISPATCH, T_COMMIT = (
    FIXED_NOW.isoformat(),
    (FIXED_NOW + timedelta(days=1)).isoformat(),
    (FIXED_NOW + timedelta(days=2)).isoformat(),
)

VALID_LABOR = "消灭人工筛选论文、人工判重与人工建档三段重复劳动，全部转机检"
VALID_PROBE = "这份材料想让我相信行为格保优比单目标寻优更抗局部最优"


def _pg_reachable() -> bool:
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001  可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


pytestmark = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


def _load_script(rel_parts: tuple[str, ...], mod_name: str) -> Any:
    """按文件路径装载 scripts/ 脚本模块（exam_trigger_scheduler 同款先例，零改造）。"""
    import importlib.util
    import sys

    path = REPO_ROOT.joinpath(*rel_parts)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec and spec.loader, f"脚本缺失：{path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _four_gates() -> dict[str, Any]:
    """四闸合法形态（provenance pass / 双源已验证 / ashare 判词 / 可回测）。"""
    return {
        "provenance": {"status": "pass"},
        "cross_validation": {"independent_sources": 2, "status": "已验证"},
        "ashare_adaptation": {"verdict": "改造方案：适配 A 股 T+1 与涨跌停约束后重验"},
        "backtestable": {"verdict": "可得且可用", "data_fields": ["open", "close", "volume"]},
    }


def _wash_gateway():
    """LLM 网关替身：三工序按 OBJ_M 轨返回固定件（零真实外呼，同 test_washer 惯例）。"""
    from zephyr.ai_layer.cleaning.washer import GatewayReply

    spec_body = {
        "mechanism_one_liner": "动量因子在趋势市的加速入场效应",
        "mechanism_detail": "价格动量在高趋势 regime 下入场加速，回撤靠波动率滤窗控制。",
        "applicability": {"regime": "trend", "frequency": "daily", "universe": "CSI300"},
        "ashare_precheck": {
            "overall": "adapt_needed",
            "adaptation_plan": "T+1 下改为隔日开盘进场",
            "t_plus_1": {"verdict": "adapt", "note": "隔日化"},
            "price_limits": {"verdict": "pass", "note": "流动性充足"},
            "retail_dominance": {"verdict": "pass", "note": "影响有限"},
        },
        "risk_flags": ["overfit_history"],
        "data_fields": [{"field": "close", "source_ref": "tushare", "quality_note": "缺失率低"}],
        "reproduction_notes": "伪代码：动量排名前 10% 等权持有，月度再平衡。",
        "source_quotes": ["momentum accelerates in trending markets"],
    }
    localized = {"applicability": {"regime": "趋势", "frequency": "日", "universe": "沪深300"}}
    script = {
        "mining_deep": GatewayReply(
            content="结构化笔记：动量机制",
            model="deepseek-reasoner",
            request_id_ref="lsg:e2e:r1",
            tokens_in=500,
            tokens_out=200,
        ),
        "cleaning_rewrite": GatewayReply(
            content="```json\n" + json.dumps(spec_body, ensure_ascii=False) + "\n```",
            model="deepseek-chat",
            request_id_ref="lsg:e2e:r2",
            tokens_in=800,
            tokens_out=400,
        ),
        "translation_registry": GatewayReply(
            content=json.dumps(localized, ensure_ascii=False),
            model="glm-4.5-free",
            request_id_ref="lsg:e2e:r3",
            tokens_in=300,
            tokens_out=100,
        ),
    }

    def gateway(messages: list[dict[str, str]], *, task_type: str, tier: str) -> GatewayReply:
        return script[task_type]

    return gateway


class _PassSanitizer:
    """P1 消毒替身（通过态；duck: validate_llm_context）。"""

    def validate_llm_context(self, text: str) -> None:
        return None


def test_evolution_chain_l1_to_l7(tmp_path: Path) -> None:
    """进化链七段推进：L1 感知 → L7 传承，每段一个断言锚（消息 [Lx] 前缀定位）。"""
    # ---------------------------------------------------------------- 部署（一次性临时 schema，真 DDL）
    intake_ddl = _load_script(("scripts", "ai_layer", "apply_ai_intake_ddl.py"), "e2e_intake_ddl")
    heritage_ddl = _load_script(("scripts", "ai_layer", "apply_ai_heritage_ddl.py"), "e2e_heritage_ddl")
    quota_sync = _load_script(("scripts", "ai_layer", "sync_ai_source_quota.py"), "e2e_quota_sync")

    from zephyr.ai_layer.cleaning.spec_store import ensure_table
    from zephyr.ai_layer.comparator.experiment_store import deploy as deploy_compare
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    admin = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    for schema in (INTAKE_SCHEMA, COMPARE_SCHEMA, HERITAGE_SCHEMA):
        admin.cursor().execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    intake_ddl.deploy(schema=INTAKE_SCHEMA)  # L2 五表 + T5 配额表
    ensure_table(INTAKE_SCHEMA)  # L3 规格表（ai_cleaning_spec）
    deploy_compare(COMPARE_SCHEMA)  # L4 实验卡库（冻结/裁定触发器）
    heritage_ddl.deploy(schema=HERITAGE_SCHEMA)  # L7 传承库

    closables: list[Any] = []
    try:
        # ============================================================= L1 感知
        from zephyr.ai_layer.perceive.search_orders import SearchOrderJournal
        from zephyr.ai_layer.perceive.source_registry import (
            DEFAULT_REGISTRY_PATH,
            load_source_registry,
        )
        from zephyr.ai_layer.perceive.translator import (
            BudgetLedger,
            DetectorSignal,
            PerceiveTranslator,
        )

        registry = load_source_registry()
        assert len(registry.sources) == 12, "[L1] 源注册表应载入 12 源（URL/频率/配额/健康度/核验日齐）"
        assert registry.total_daily_cap == 40, "[L1] 共享日配额总量闸应为 40"

        synced = quota_sync.sync(INTAKE_SCHEMA, DEFAULT_REGISTRY_PATH)
        assert synced["synced"] == 12, "[L1] 配额同步器应把 12 源落成 T5 配额行"
        assert quota_sync.verify(INTAKE_SCHEMA, DEFAULT_REGISTRY_PATH) == [], (
            "[L1] 同步后 T5 应与真源零漂移（verify 机检）"
        )

        orders_journal = SearchOrderJournal(tmp_path / "search_orders")
        translator = PerceiveTranslator(orders_journal, ledger=BudgetLedger(orders_journal.state_dir))
        signal = DetectorSignal(
            channel="strategy_decay",
            signal_name="synthetic-strategy_decay",
            trigger_ref="e2e://decay/signal-001",
            occurred_at=FIXED_NOW,
            attributes={"decay_cause": "crowding"},
        )
        opened = translator.translate(signal, now=FIXED_NOW)
        assert opened.action == "opened" and opened.order is not None, (
            f"[L1] 五探测器合成信号应正确开单：{opened.reason}"
        )
        search_order_id = opened.order.order_id
        assert translator.ledger.reserved(now=FIXED_NOW) == 6, "[L1] 共享预算应按 expected_cards=6 扣减"

        # 收集单：E1 staging 纪律——开单即指定 staging 落点（collected 契约前置，§9.4）
        staging_dir = tmp_path / "staging"
        collect_order = orders_journal.open_order(
            vein_id="VEIN-FAC-E6",
            vein_family="E6",
            trigger="beat",
            trigger_ref="e2e://beat/collect",
            keyword_groups=("因子拥挤度监控", "factor crowding"),
            staging_path=str(staging_dir),
            now=FIXED_NOW,
        )
        assert collect_order.status == "open" and collect_order.staging_path, "[L1] 收集单应携带 E1 staging 落点"

        # ============================================================= L2 收集
        from zephyr.ai_layer.intake.gate import IntakeCandidate, IntakeGate
        from zephyr.ai_layer.intake.intake_events import IntakeJournal

        gate = IntakeGate(schema=INTAKE_SCHEMA)
        card_store = gate._store  # noqa: SLF001 - 同包写路径（test_gate 同款用法）
        closables.append(card_store)
        candidate = IntakeCandidate(
            card_id="CC-E2E-0001",
            domain_id="governance",
            title="MAP-Elites 行为格多样性保底机制（e2e 链样本）",
            novelty="以行为描述子网格取代单目标最优解",
            mechanism="逐格保留最高适应度个体，变异体入格竞争胜出者留档",
            source_name="qlib",
            source_url="https://github.com/qlib/qlib",
            source_year=2025,
            license="mit",
            labor_killed=VALID_LABOR,
            four_gates=_four_gates(),
            injection_probe=VALID_PROBE,
        )
        verdict, card_id = gate.admit_and_store(candidate)
        assert verdict.passed and card_id == "CC-E2E-0001", (
            f"[L2] 四闸全过候选卡应入库（配额真读 L1 同步行）：{verdict.reject_reasons}"
        )
        card = card_store.get(card_id)
        assert card is not None and card.funnel_stage == "L0", "[L2] 新卡应落 L0 态"
        assert card.elite_cell == "governance|unclassified", "[L2] 精英格应按 域|族 落格"

        reskin_verdict, reskin_id = gate.admit_and_store(
            IntakeCandidate(**{**candidate.__dict__, "card_id": "CC-E2E-0002"})
        )
        assert not reskin_verdict.passed and reskin_id is None, "[L2] 同 url+title 换皮必须被查重闸拒绝"
        assert any(r.startswith("duplicate_sha:CC-E2E-0001") for r in reskin_verdict.reject_reasons), (
            "[L2] 换皮拒因应指向原卡（精确层 sha256）"
        )

        intake_journal = IntakeJournal(state_dir=tmp_path / "intake_journal")
        intake_journal.emit(
            "intake_ingest_due",
            {"source_slug": "qlib", "raw_staging_path": "staging/cc-e2e-0001.json"},
        )
        intake_journal.emit("intake_clean_due", {"card_ids": [card_id], "domain_id": "governance"})
        assert intake_journal.journal_path.exists() and len(intake_journal.pending()) == 2, (
            "[L2] 事件行应落账两条（journal 先落盘，唯一真源）"
        )

        collected = orders_journal.transition(collect_order.order_id, "collected", produced_ref=f"card_id={card_id}")
        assert collected.status == "collected" and collected.produced_ref == f"card_id={card_id}", (
            "[L1→L2] 搜索工单应以候选卡出生证收单（produced_ref+staging 双契约）"
        )

        # ============================================================= L3 清洗
        from zephyr.ai_layer.cleaning.auditor import sample_decision
        from zephyr.ai_layer.cleaning.policy import load_cleaning_policy
        from zephyr.ai_layer.cleaning.spec_store import SpecStore
        from zephyr.ai_layer.cleaning.washer import Washer, WasherDeps

        card_store.transition(card_id, "L1")
        card_store.transition(card_id, "L2")  # 状态机单步推进到待洗位（E2 前一格）

        policy = load_cleaning_policy()
        spec_store = SpecStore(schema=INTAKE_SCHEMA)
        closables.append(spec_store)
        washer = Washer(
            WasherDeps(
                session_id="st-e2e-chain",
                store=spec_store,
                policy=policy,
                gateway=_wash_gateway(),
                sanitizer=_PassSanitizer(),
                dedup_query=lambda text: [],
                card_reader=card_store,
                card_writer=card_store,
                journal=intake_journal,
            )
        )
        raw_text = "A momentum strategy paper body.\n\n```python\nbad.package.install()\n```"
        wash = washer.wash_card(card_id, raw_text=raw_text)
        assert wash.status == "washed" and wash.spec_id, (
            f"[L3] spec 驱动 washer 应出清洗件：{wash.rejection_reason}/{wash.evidence_ref}"
        )
        spec = spec_store.get_active(card_id)
        assert spec is not None and spec.card_id == card_id, "[L3] 规格件应落 ai_cleaning_spec 且 active 可读"
        assert card_store.stage_of(card_id) == "E2", "[L3] 洗成后卡应经真 CardStore 推进 E2"

        audit = sample_decision(
            policy,
            card_id=card_id,
            cards_washed_total=1,
            cold_started_at=FIXED_NOW,
            as_of=FIXED_NOW + timedelta(days=3),
            four_gates={},
        )
        assert audit.sampled and audit.reason == "cold_start", "[L3] 冷启动窗内应强制抽验（审计抽验行）"

        # ============================================================= L4 比较
        from zephyr.ai_layer.comparator.executor import (
            VerdictRuling,
            issue_verdict_card,
            run_preflight,
        )
        from zephyr.ai_layer.comparator.experiment_store import (
            ExperimentDraft,
            ExperimentStore,
            canonical_criteria_text,
            criteria_hash,
            new_experiment_id,
            render_criteria_ref,
        )

        experiment_store = ExperimentStore(schema=COMPARE_SCHEMA)
        closables.append(experiment_store)
        experiment_id = new_experiment_id("20260924", "e2e-chain")
        criteria = {
            "primary": "OOS 衰减 < 0.5",
            "significance": "McNemar p < 0.05",
            "windows": ["2024H1", "2024H2"],
        }
        record = experiment_store.freeze(
            ExperimentDraft(
                experiment_id=experiment_id,
                challenger_ref=wash.spec_id,
                champion_ref="champ-current",
                venue_ref="venue_replay",
                evaluator_session="st-e2e-eval",
                contractor_session="st-e2e-ctor",
            ),
            criteria,
        )
        assert record.status == "frozen" and record.challenger_ref == wash.spec_id, (
            "[L4] 实验创建应冻结且挑战者=L3 规格件"
        )
        l4_hash = record.criteria_hash
        assert l4_hash == criteria_hash(canonical_criteria_text(criteria)), "[L4] 冻结哈希应=canonical 判据哈希"

        # 判据冻结触发器：DB 直改判据必须被拒（双道：应用层 guard 同判）
        tamper_conn = experiment_store.write_conn()
        with pytest.raises(Exception, match="frozen_criteria_immutable"):
            tamper_conn.cursor().execute(
                f"UPDATE {COMPARE_SCHEMA}.ai_comparison_experiment SET criteria_yaml = %s WHERE experiment_id = %s",
                ("tampered: true\n", experiment_id),
            )
        tamper_conn.rollback()  # 清 aborted 事务（写连接进程内复用）

        # 时序锁锚点=卡上真实 frozen_at（DB DEFAULT now()）：派发/首commit 取冻结+1d/+2d。
        # 原实现锚死 FIXED_NOW(2026-09-24)——真实时钟越过 T_DISPATCH 后必炸（time bomb，
        # 2026-09-29 复现 time_lock_inverted）；时序锁语义 frozen<dispatched<first_commit 不变。
        frozen_dt = datetime.fromisoformat(str(record.frozen_at))
        t_dispatch_live = frozen_dt + timedelta(days=1)
        t_commit_live = frozen_dt + timedelta(days=2)
        preflight = run_preflight(
            record,
            task_criteria_ref=render_criteria_ref(experiment_id, l4_hash),
            fairness_passed=True,
            dispatched_at=t_dispatch_live,
            first_commit_at=t_commit_live,
        )
        assert preflight.passed and not preflight.reasons, f"[L4] 考场预检三锁应全过：{preflight.reasons}"
        verdict_card = issue_verdict_card(
            record,
            "win",
            ruled_by_session="st-e2e-eval",
            ruling=VerdictRuling(evidence_pack={"experiment_id": experiment_id}, significance="p=0.01"),
            issued_at=t_commit_live,
        )
        assert verdict_card.verdict == "win" and verdict_card.evaluator_session == "st-e2e-eval", (
            "[L4] 裁定卡应仅由 evaluator 会话签发"
        )
        assert experiment_store.transition(experiment_id, "running") == (True, "ok")
        assert experiment_store.transition(experiment_id, "verdict") == (True, "ok")
        assert experiment_store.set_verdict(experiment_id, "win", evidence_ref=f"verdict-card:{experiment_id}")[0]
        assert experiment_store.archive(experiment_id) == (True, "ok")
        archived = experiment_store.get(experiment_id)
        assert archived is not None and archived.status == "archived" and archived.verdict == "win", (
            "[L4] 实验应沿 frozen→running→verdict→archived 归档且裁定落账"
        )

        # ============================================================= L5 排产
        from zephyr.ai_layer.scheduling.dispatcher import (
            QuotaReadings,
            evaluate_quota,
            rank_pending,
        )
        from zephyr.ai_layer.scheduling.maturity import load_gate_policy
        from zephyr.ai_layer.scheduling.seed_writer import (
            SEG_BUILD,
            build_seed,
            load_seeds,
            write_seeds,
        )

        spolicy = load_gate_policy()
        now = FIXED_NOW

        def _order(
            oid: str, sig: float, *, star: bool = False, age: float = 0, kind: str = "evolution", og: bool = False
        ) -> dict[str, Any]:
            return {
                "order_id": oid,
                "labor_killed": "a",
                "significance": sig,
                "starred": star,
                "kind": kind,
                "owner_gate": og,
                "created_at": now - timedelta(days=age),
            }

        ranked = rank_pending(
            [
                _order("WO-E2E-A", 0.25),
                _order("WO-E2E-B", 0.25),
                _order("WO-E2E-C", 0.25, star=True),
                _order("WO-E2E-D", 0.05, age=8),
                _order("WO-E2E-R", 0.99, kind="repair"),
                _order("WO-E2E-S", 0.99, og=True),
            ],
            spolicy,
            now,
        )
        assert [r["order_id"] for r in ranked] == [
            "WO-E2E-A",
            "WO-E2E-B",
            "WO-E2E-D",
            "WO-E2E-C",
        ], "[L5] 工单应按 分>防饥饿>带星 排序；repair/骨架级不混队"

        assert (
            evaluate_quota(
                QuotaReadings(
                    q1_active_sessions=1, q2_subagents_requested=3, q3_tokens_today=100, q4_commit_queue_pending=0
                ),
                spolicy,
            )
            == []
        ), "[L5] 配额四读数全绿应无降级旗"
        quota = spolicy["quota"]
        assert evaluate_quota(
            QuotaReadings(
                q1_active_sessions=int(quota["q1_active_session_cap"]),
                q2_subagents_requested=int(quota["q2_subagent_max"]) + 1,
                q3_tokens_today=int(quota["q3_daily_token_budget"]),
                q4_commit_queue_pending=int(quota["q4_commit_queue_pending_cap"]),
            ),
            spolicy,
        ) == ["Q1", "Q2", "Q3", "Q4"], "[L5] 四读数触线应齐亮 Q1-Q4"

        seed = build_seed("WO-E2E-A", SEG_BUILD, "local", "e2e 链种子", spolicy)
        seeds_path = write_seeds([seed], spolicy, path=tmp_path / "seeds.yaml")
        loaded = load_seeds(seeds_path)
        assert loaded["seeds"][0]["task_id"] == "evo_WO-E2E-A_build", (
            "[L5] 种子 writer 应落 tmp 盘且回读一致（排班真源=evolution_schedule_seeds）"
        )

        # ============================================================= L6 切换
        from zephyr.ai_layer.switch_engine.tombstone_manager import (
            REVIVAL_ROUTE,
            list_tombstones,
            revival_ticket,
            seal,
        )
        from zephyr.intelligence.switch_engine.shadow_runner import (
            ShadowRunConfig,
            ShadowRunner,
            write_corpus_manifest,
        )
        from zephyr.intelligence.switch_engine.switch_engine import (
            SwitchEngine,
            active_ref,
        )
        from zephyr.intelligence.switch_engine.switch_registry import (
            SwitchRegistryRecord,
            SwitchRegistryStore,
        )

        def _sqlite_factory() -> Any:
            def factory() -> sqlite3.Connection:
                conn = sqlite3.connect(tmp_path / "switch_registry_e2e.db")
                conn.execute("PRAGMA foreign_keys=ON")
                return conn

            return factory

        sw_store = SwitchRegistryStore(conn_factory=_sqlite_factory())
        sw_store.ensure_schema()
        engine = SwitchEngine(sw_store)
        switch_id = "SW-20260924-e2e"
        opened_switch = engine.open_switch(
            SwitchRegistryRecord(
                switch_id=switch_id,
                object_family="code_module",
                object_ref="zephyr.demo.e2e_challenger",
                domain="D_GOVERNANCE",
                champion_ref="main",
                challenger_ref=wash.spec_id,
                criteria_yaml_ref="config/switch_criteria.yaml",
                criteria_hash=l4_hash,
                state="shadow",
            )
        )
        assert opened_switch.state == "shadow", "[L6] switch 注册表开户应恒登记 shadow 影子态"
        with pytest.raises(Exception, match="仅可自 canary"):
            engine.promote(switch_id, approved_by="independent_review", receipt_ref="r-0")
        assert engine.store.require(switch_id).state == "shadow", "[L6] 影子禁直提（灰度语义，拒后仍在 shadow）"

        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()
        for i in range(2):
            (corpus_dir / f"case_{i}.json").write_text(json.dumps({"input": i}), encoding="utf-8")
        write_corpus_manifest(corpus_dir, seed=7)
        wt_champ = tmp_path / "wt-champion"
        wt_chall = tmp_path / "wt-challenger"
        wt_champ.mkdir()
        wt_chall.mkdir()
        same_stdout = json.dumps({"v": 1})
        shadow_config = ShadowRunConfig(
            switch_id=switch_id,
            champion_worktree=wt_champ,
            challenger_worktree=wt_chall,
            corpus_dir=corpus_dir,
            output_dir=tmp_path / "shadow_out",
            module_ref="demo_mod:run",
        )
        report = ShadowRunner(
            shadow_config,
            command_runner=lambda wt, ref, item, out: (same_stdout, ""),
        ).run()
        assert (
            report.total == 2
            and report.identical == 2
            and report.disagreement_rate == 0.0
            and report.consumer == "comparator_only"
        ), "[L6] 影子跑一趟应零分歧且产物只供对比器消费"

        engine.transition(switch_id, "graduate", "shadow-zero-disagreement")
        with pytest.raises(Exception, match="approved_by"):
            engine.promote(switch_id, approved_by="yolo", receipt_ref="r-1")  # 审批人必须在册
        promoted = engine.promote(switch_id, approved_by="independent_review", receipt_ref="rcpt-e2e")
        assert promoted.state == "promoted", "[L6] 审批晋升应到 promoted 态"
        assert active_ref(engine.store.require(switch_id)) == wash.spec_id, "[L6] 晋升后消费指针应切到挑战者"

        engine.transition(switch_id, "stabilize", "stable-window")
        engine.transition(switch_id, "supersede", "next-gen-promoted")
        git_calls: list[list[str]] = []

        def _fake_git(args: Any) -> str:
            git_calls.append([str(a) for a in args])
            return ""

        tombstoned = seal(
            engine,
            switch_id,
            failed_regime="低波动率 regime",
            revival_conditions=["regime_recurrence: 高波动重现", "owner_manual"],
            seal_ref="seal-e2e-1",
            git_runner=_fake_git,
        )
        assert tombstoned.state == "tombstone" and tombstoned.tombstone["revival_conditions"], (
            "[L6] 退役件应封存为墓碑并带复活条件"
        )
        assert git_calls and git_calls[0][0] == "tag", "[L6] 封存应 git tag（物理文件零删除）"
        assert [r.switch_id for r in list_tombstones(sw_store)] == [switch_id], "[L6] 退役件应可查询（list_tombstones）"
        ticket = revival_ticket(
            sw_store,
            switch_id,
            trigger="regime_recurrence",
            evidence_ref="L1-signal-e2e",
            out_dir=tmp_path,
        )
        assert ticket["revival_not_direct_promotion"] is True and ticket["route"] == REVIVAL_ROUTE, (
            "[L6→L1] 复活≠直提：恒回 shadow 重走对比"
        )

        # ============================================================= L7 传承
        from zephyr.ai_layer.heritage.closure_check import validate_receipt
        from zephyr.ai_layer.heritage.forget import HeritageForget
        from zephyr.ai_layer.heritage.policy import load_policy
        from zephyr.ai_layer.heritage.priors import HeritagePriors
        from zephyr.ai_layer.heritage.store import (
            HeritageDraft,
            HeritageStore,
            RegistrationRefused,
        )

        hpolicy = load_policy()
        hstore = HeritageStore(
            HERITAGE_SCHEMA,
            state_dir=tmp_path / "heritage_state",
            domain_lookup=lambda domain: True,
            l4_hash_lookup=lambda exp: l4_hash if exp == experiment_id else None,
        )
        closables.append(hstore)

        # 入库五道检查在岗：缺源锚 / 占位白话各自机读拒因
        with pytest.raises(RegistrationRefused) as ei:
            hstore.register(
                HeritageDraft(
                    **{
                        **_defect_kwargs(switch_suffix="x"),
                        "source_ref": "",
                    }
                ),
                as_of=FIXED_NOW,
            )
        assert ei.value.reason == "missing_source_anchor", "[L7] 闸1 缺源锚应机读拒收"
        with pytest.raises(RegistrationRefused) as ei2:
            hstore.register(
                HeritageDraft(**{**_defect_kwargs(switch_suffix="x"), "plain_zh": "待填"}),
                as_of=FIXED_NOW,
            )
        assert ei2.value.reason == "placeholder_plain_zh", "[L7] 闸5 占位白话应机读拒收"

        elite_id = hstore.register(
            HeritageDraft(
                entry_kind="elite",
                title="e2e 双窗胜者档案",
                plain_zh="挑战者在双窗实测以显著性优势胜出，档案供组合素材与祖先分支使用",
                domain_id="governance",
                source_kind="l6_switch",
                source_ref=switch_id,
                surface="code_module",
                winner_ref=wash.spec_id,
                loser_ref="champ-current",
                diff_summary="胜者把信号确认窗从固定 3 根改为波动自适应，回撤更小而胜率不降，双窗成绩稳定",
                evidence_ref=experiment_id,
                mechanism_family="prediction",
            ),
            as_of=FIXED_NOW,
        )
        assert elite_id.startswith("HT-20260924-"), "[L7] 精英档案应入库（source_ref=L6 switch 闭环）"

        criteria_id = hstore.register(
            HeritageDraft(
                entry_kind="criteria",
                title="e2e 双窗判据快照",
                plain_zh="当时为什么算它赢：OOS 衰减与置换检验双达标，判据冻结哈希随卡入档",
                domain_id="governance",
                source_kind="l4_experiment",
                source_ref=experiment_id,
                experiment_id=experiment_id,
                criteria_hash=l4_hash,
                venue="replay",
                verdict="win",
                why_win="OOS 衰减小于阈值且 McNemar 检验显著，判据冻结哈希与 L4 实验卡完全一致",
            ),
            as_of=FIXED_NOW,
        )
        assert criteria_id.startswith("HT-20260924-"), "[L7] 判据档案应入库且闸5 判据哈希与 L4 卡一致"

        defect_kwargs = _defect_kwargs(switch_suffix="chain")
        defect_id = hstore.register(HeritageDraft(**defect_kwargs), as_of=FIXED_NOW)
        assert hstore.status_of(defect_id) == "active", "[L7] 缺陷模式应过五道检查后 active 入库"

        # 先验回灌 L1（priors 读）：rationale 引用传承条目，非冻结态保真系数
        priors = HeritagePriors("ai_heritage", policy=hpolicy)
        prior = priors.build_prior_response(
            {"prior_factor": 1.3, "rationale_refs": [elite_id]}, ["stale_kw"], coverage_pct=65.0
        )
        assert prior == {
            "prior_factor": 1.3,
            "rationale_refs": [elite_id],
            "exclusion_keywords": ["stale_kw"],
            "frozen": False,
        }, "[L7→L1] 先验应带传承 rationale 回灌感知层（coverage 正常不冻结）"

        ok, why = validate_receipt("incident_fix", {"heritage_ref": defect_id})
        assert ok and why == "heritage_ref", "[L7] 关单应可凭 heritage_ref 通过登记机检"
        bad_ok, bad_why = validate_receipt("defect_fix", {})
        assert not bad_ok and bad_why.startswith("missing_heritage_registration"), (
            "[L7] 无登记关单应被拦（closure_check 负样本）"
        )

        forgetter = HeritageForget(
            hstore,
            state_dir=tmp_path / "heritage_state",
            surface_alive=lambda ref: False,
            policy=hpolicy,
        )
        forget_report = forgetter.run_monthly(as_of=FIXED_NOW, execute=True)
        assert defect_id in {row["entry_id"] for row in forget_report["executed"]}, (
            "[L7] 遗忘执行应降级受影响面全退役的缺陷 1 例"
        )
        entry = hstore.get(defect_id)
        assert entry is not None and entry["status"] == "retired", "[L7] forget=只降级不删：retired 条目仍可反查全量"

        # ============================================================= 链路闭环（L7→L1）
        replay = translator.translate(
            DetectorSignal(
                channel="strategy_decay",
                signal_name="synthetic-strategy_decay",
                trigger_ref="e2e://decay/signal-002",
                occurred_at=FIXED_NOW,
                attributes={"decay_cause": "crowding"},
            ),
            now=FIXED_NOW + timedelta(hours=1),
        )
        assert replay.action == "skipped_cooldown", (
            "[闭环] 复活信号回灌 L1：同矿脉冷却期应节流重复开单（进化链首尾相接）"
        )
    finally:
        for closable in closables:
            try:
                closable.close()
            except Exception:  # noqa: BLE001 - 清理路径不掩盖主流程结果
                pass
        for schema in (INTAKE_SCHEMA, COMPARE_SCHEMA, HERITAGE_SCHEMA):
            admin.cursor().execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


def _defect_kwargs(*, switch_suffix: str) -> dict[str, Any]:
    """L7 缺陷档案最小合规形态（五道检查全过；pattern 隔离防跨用例撞查重）。"""
    return {
        "entry_kind": "defect",
        "title": f"e2e 链缺陷模式 {switch_suffix}",
        "plain_zh": "工单收尾路径参数写错导致改动落错目录，登记签名与配方防再犯",
        "domain_id": "tooling",
        "source_kind": "work_order",
        "source_ref": "WO-20260924-E2E",
        "root_cause": "调用方按位置传参把 pathspec 传成了 path 语义",
        "signature": r"pathspec=.*\n.*unexpected positional arg",
        "recipe": "改关键字传参+补 smoke：对 git add 调用点逐一核对 pathspec 语义并加实单验证",
        "pattern_norm": f"e2e_chain_pattern_{switch_suffix}",
        "affected_surfaces": ("src/definitely_gone_e2e.py",),
        "tool_id": "git-cli",
        "scene": "python 子进程调用 git add -- <pathspec>",
    }
