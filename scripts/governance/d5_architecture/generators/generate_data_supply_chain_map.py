#!/usr/bin/env python3
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §data-supply-chain-map
# [MODULE] scripts.governance.d5_architecture.generators.generate_data_supply_chain_map
# create-guard-not-dup: 本件是数据供应链图D11-G02生成器(骨架驱动机生图件),命中词n16/词汇装载系yaml读取语文巧合,非豁免装载器/词汇加载能力的第二实现
# [DOMAIN] D_DATA
# [TTL] permanent
# [DEPENDENCIES] yaml; scripts.governance._shared.terminology_loader (get_zh);
#   scripts.governance._shared.module_translation_loader (get_module_name_bilingual);
#   zephyr.shared.io.file_utils (safe_write_text, 延迟导入)
# [CONSUMERS] config/data_supply_chain_map.yaml（图12 数据供给链图真源）;
#   scripts.governance.d5_architecture.validators.validate_data_supply_chain_map;
#   zephyr.gov_enforcement.commit_gates.data_supply_chain_map_gate;
#   tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 双层=机生层(tasks.yaml/schedule.yaml/scheduler 分派面/data_asset_registry/执行体文件实存
# [MODIFY-GUARD] 环节增删先回写骨架 §1、槽位归属变更同步 _HUMAN 节点 slots 清单；
#   产出 config/data_supply_chain_map.yaml 禁手改后不回生成
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 机器真源缺失致契约环节未入图、双轴与骨架不一致=raise RuntimeError（禁产半图）；
#   单条目旧别名=WARN 后按统一名记账；写盘失败=返回码 1；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py
#   /骨架 §1 状态列/depgraph 派生在册投影 path_ownership) 每次全量重建、人工语义层(环节名/
#   decision_question/laws/失败降级/缺口登记/freshness_evidence) existing-wins 保留;
#   同输入两次产出逐字节等（禁 datetime.now()/time.time()，时间戳唯一经 --as-of 入参注入，
#   freshness_evidence 的 probe_at_utc 是人工层实测常量而非取时）;
#   INV-1=节点只存标识符与指针(task_id/slot 名/MOD-*/文件路径/表名)，禁复制 tasks.yaml 或注册表条目正文;
#   静态清单禁手维=所有计数/槽位/任务分布由本生成器扫出，散文里不写数;
#   标签必经三层翻译 loader(terminology_glossary/data_asset 域/模块翻译册)，禁硬编码翻译字典;
#   双轴同源=verified_scope: production 一律由骨架 §1 状态列实扫推导（禁在本件另立一套 ✅ 口径）;
#   环节枚举四源并存=tasks.yaml + schedule.yaml 槽 + scheduler 特殊槽分派 + 骨架 §1 契约全集
#   （单源必结构性漏段，WB12-35/批次4 三案例坐实）;
#   L0/L1 字段统一名=note_zh/fallback/source_anchors/doc_refs/downstream_action（旧别名一律丢弃并 WARN，
#   内容以统一名承载，废止清单见校验器 CV-L0）
# [MODIFY-GUARD] config/data_supply_chain_map.yaml；人工语义层改动写在本文件 _HUMAN，或经生成后
#   直接改图 YAML（existing-wins，下次重跑保留）；槽位归属变更 MUST 同步 _HUMAN 节点 slots 清单；
#   环节增删（含拆行/退役）MUST 先回写骨架 §1（真源方向=骨架→图），本件 STAGE_IDS 随之改
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 机器真源缺失/解析失败=raise 退出非 0（禁静默产半图）；单条目字段缺失=按缺省值记账并计数；
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [TESTS] 见同批 tests/ 下 canary 件
#   骨架 §1 状态列实扫为空/production 集与骨架 ✅ 不一致=raise（禁产出自相矛盾的图）
# [TESTS] tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_data_supply_chain_map.py — 图12 数据供给链图（DSC 22 环节 + 缺口显性化）骨架生成器。

战役=全景图六图战役 图12（骨架与作业簿真源=``docs/_working/map_build/fig12_datachain/``）。
本批=L-REGEN12（批次4 落地）：18→**22 环节**（D12-10 拆 a/b、新立 D19 探测器/D20 任务级对账/
D21 任务表外进程内派生），并按六图终局卷（``03_final_blueprint_and_schema.md``）做三件事——
①L0/L1 字段统一名（note_zh/fallback/source_anchors/doc_refs，旧别名残留即 CV-L0 红）；
②双轴正交（``confidence`` + ``verified_scope``，production 数=骨架 ✅ 数，逐节点+计数双判）；
③缺口显性化（5 处"消费方在等未产表"+1 处幽灵引用落成 gap 节点，各生产节点携 ``gap_refs`` 指回）。

双层结构（对标 ``scripts/governance/generate_governance_map.py``，比对忽略 generated_at/counts）：

1. **机生层**（每次全量重建，禁手画手维）——扫六类可执行真相源：
   - ``src/zephyr/data/config/tasks.yaml``：任务全集/源分布/目标表数/fallback 配置数/disabled 数/
     ``date_col`` 覆盖率/依赖 DAG 边数与跨槽边数/重复 task_id
   - ``src/zephyr/data/config/schedule.yaml``：cron 槽位全集/执行器池分布/正反两向差分
   - ``src/zephyr/data/scheduler.py``：分派面实存性（``schedule_name == "<槽名>"`` 分支集）——
     槽在、无任务、无分派分支 = 空转槽（本图判"挂槽≠在跑"的机械尺）
   - ``docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml``：declared vs 实际
   - 五段执行体文件实存性
   - **骨架 §1 状态列**（``fig12_datachain/00_skeleton.md``）：行级三态 + 分面行清单 ⇒ verified_scope
   - **depgraph 派生在册投影**（``docs/03_modules/path_ownership_map.yaml`` claim_type=depgraph_node）
     ⇒ module_id（禁自造号；查不到即 null + red_reason）
2. **人工语义层**（环节名、decision_question、laws、失败降级语义、缺口登记、freshness_evidence）——
   首跑取 ``_HUMAN`` 常量，此后 existing-wins（键级）。

CLI::

    python scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py
    python .../generate_data_supply_chain_map.py --dry-run
    python .../generate_data_supply_chain_map.py --as-of 2026-09-25   # 时间戳唯一注入口
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.module_translation_loader import get_module_name_bilingual  # noqa: E402
from _shared.terminology_loader import get_zh  # noqa: E402
from d5_architecture.generators._common import (  # noqa: E402  # noqa: import-integrity  sys.path 注入的 governance 包
    tbl_name,
)
from d5_architecture.validators.validate_construction_steps import (  # noqa: E402  # noqa: import-integrity  sys.path 注入的 governance 包
    scan_module_id_index,
)

_REPO_SRC = str(Path(__file__).resolve().parents[4] / "src")
if _REPO_SRC not in sys.path:
    sys.path.insert(0, _REPO_SRC)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  # SSOT 唯一真源（禁重复定义，SSOT-REDEFINITION）

OUTPUT_REL = "config/data_supply_chain_map.yaml"

_tbl = tbl_name  # 表名取数单源化（_common.tbl_name，CR-15 同批收内）

TASKS_YAML_REL = "src/zephyr/data/config/tasks.yaml"
SCHEDULE_YAML_REL = "src/zephyr/data/config/schedule.yaml"
SCHEDULER_PY_REL = "src/zephyr/data/scheduler.py"
ASSET_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"
SKELETON_REL = "docs/_working/map_build/fig12_datachain/00_skeleton.md"
PATH_OWNERSHIP_REL = "docs/03_modules/path_ownership_map.yaml"
BOOK_DIR = "docs/_working/map_build/fig12_datachain"

# ── 契约：22 环节（骨架 §1 正身，批次4 落地）────────────────────────────────
# 值=骨架行号（D12-*），键=图内 node_id。拆行后 D12-10a/10b 分别对应 DSC-10A/DSC-10B。
STAGE_TO_SKELETON: dict[str, str] = {
    **{f"DSC-{i:02d}": f"D12-{i:02d}" for i in range(1, 10)},
    "DSC-10A": "D12-10a",
    "DSC-10B": "D12-10b",
    **{f"DSC-{i:02d}": f"D12-{i:02d}" for i in range(11, 22)},
}
STAGE_IDS: tuple[str, ...] = tuple(STAGE_TO_SKELETON)
# 图内辅助节点（非中类契约行：源面/汇聚/交接/通道/缺口显性化）——node_type 必须落在 AUX_NODE_TYPES
GAP_NODE_IDS: tuple[str, ...] = (
    "DSC-GAP-NEWSGHOST",
    "DSC-GAP-MACRO",
    "DSC-GAP-L2TICK",
    "DSC-GAP-REPLAY",
    "DSC-GAP-DUPGUARD",
    "DSC-GAP-CONSENSUSCHAIN",
    "DSC-GAP-NAV",
    "DSC-GAP-EXECEP",
    "DSC-GAP-FFVAL",
    "DSC-GAP-FFSIG",
    "DSC-GAP-ARCHIVE-AUDIT",
    "DSC-GAP-CODEBACKUP",
    "DSC-GAP-MIRROR",
    "DSC-GAP-TERMINUS",
    "DSC-GAP-RECDIFF",
)
AUX_NON_GAP_IDS: tuple[str, ...] = ("DSC-SRC", "DSC-FB", "DSC-HA", "DSC-HB", "DSC-HC", "DSC-14D")
AUX_NODE_IDS: tuple[str, ...] = AUX_NON_GAP_IDS + GAP_NODE_IDS
NODE_ORDER: tuple[str, ...] = STAGE_IDS + AUX_NODE_IDS
# 消费方在等的未产表（11 卷 §1-C 五表）+ 幽灵引用（11 卷 §1-D 一条）→ 终局验收判据面
WAITING_TABLE_GAPS: dict[str, str] = {
    _tbl("market_account_nav_daily"): "DSC-GAP-NAV",
    _tbl("market_execution_report"): "DSC-GAP-EXECEP",
    "c1_market.factor_feature_value": "DSC-GAP-FFVAL",
    "c1_market.factor_signal": "DSC-GAP-FFSIG",
    _tbl("market_reconciliation_differences"): "DSC-GAP-RECDIFF",
}
GHOST_REF_GAPS: dict[str, str] = {"c1_market.news_data": "DSC-GAP-NEWSGHOST"}
# 分面行（骨架状态格以 `分面` 起首；行级不 ✅，图节点必带 facets 且禁 production）
FACET_NODES: tuple[str, ...] = ("DSC-07", "DSC-08", "DSC-09", "DSC-14")

# ── 人工语义层：五段（骨架 §2 划分，照用不改判据口径）────────────────────────
_SEGMENTS: list[dict[str, Any]] = [
    {
        "segment_id": "S1_collect",
        "order": 1,
        "name_zh": "采集",
        "intro_zh": "23 家外部源经 provider 归一为 normalized rows",
    },
    {
        "segment_id": "S2_ingest",
        "order": 2,
        "name_zh": "入库",
        "intro_zh": "CH 两条二级降级写通道 + 实时 WAL + 幂等判重（共用 local_fallback 汇聚）",
    },
    {
        "segment_id": "S3_derive",
        "order": 3,
        "name_zh": "衍生",
        "intro_zh": "internal DAG 任务 + 任务表外进程内写手把原始表加工为派生表",
    },
    {
        "segment_id": "S4_coldstore",
        "order": 4,
        "name_zh": "冷备",
        "intro_zh": "契约决策→滚动归档/手动归档→镜像灾备（全项目唯一含不可逆删除的日常面）",
    },
    {
        "segment_id": "S5_recon",
        "order": 5,
        "name_zh": "对账修复",
        "intro_zh": "检测/任务级对账/回补/修复/互验/维护/自愈构成的反馈环",
    },
]
_SEGMENT_ORDER = {s["segment_id"]: s["order"] for s in _SEGMENTS}

# ── 人工语义层：执行体文件（机生层只做实存性扫描，不在节点里复制其内容）───────
_EXECUTOR_FILES: dict[str, list[str]] = {
    "DSC-SRC": ["src/zephyr/data/provider_base.py"],
    "DSC-01": ["src/zephyr/data/scheduler.py", "src/zephyr/data/provider_base.py"],
    "DSC-02": ["src/zephyr/data/tick_subscriber.py", "src/zephyr/data/implementations/ch_tick_kline.py"],
    "DSC-03": ["src/zephyr/data/news_dedup.py", "src/zephyr/data/implementations/internal_compute_provider.py"],
    "DSC-04": [
        "src/zephyr/data/ch_writer.py",
        "src/zephyr/data/local_replay.py",
        "src/zephyr/data/quality_gate.py",
        "src/zephyr/data/cleaning_rule_engine.py",
    ],
    "DSC-05": ["src/zephyr/data/wal_writer.py", "src/zephyr/data/buffered_writer.py"],
    "DSC-FB": ["src/zephyr/data/local_replay.py"],
    "DSC-06": ["scripts/governance/data_quality/check_tick_duplication.py", "src/zephyr/data/ch_reader.py"],
    "DSC-07": [
        "src/zephyr/data/kline_resampler.py",
        "src/zephyr/data/implementations/ch_tick_kline.py",
        "src/zephyr/data/implementations/tqcenter_provider.py",
    ],
    "DSC-08": [
        "src/zephyr/data/implementations/financial_derived_compute.py",
        "src/zephyr/data/implementations/consensus_daily_compute.py",
    ],
    "DSC-09": [
        "src/zephyr/data/sector_state_pipeline.py",
        "src/zephyr/signal_ashare/strategy_signal/series_transform.py",
    ],
    "DSC-21": [
        "src/zephyr/pf_alloc/allocation_inputs.py",
        "src/zephyr/plan_engine/daily_plan.py",
        "src/zephyr/backtest/core/n_trial_ledger.py",
        "src/zephyr/pf_alloc/core/strategy_screener_3d.py",
        "src/zephyr/position/live_nav_recorder.py",
    ],
    "DSC-10A": ["scripts/ch/archiver.py"],
    "DSC-10B": ["scripts/ch/rolling_archive_reconciler.py", "scripts/backup/backup.ps1"],
    "DSC-11": ["scripts/backup/backup.ps1", "scripts/backup/backup_reconciler.py", "scripts/backup/backup_config.yaml"],
    "DSC-12": [
        "docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml",
        "src/zephyr/data/storage_tiering.py",
        "src/zephyr/data/data_compression_archiver.py",
    ],
    "DSC-13": [
        "src/zephyr/data/integrity_checker.py",
        "src/zephyr/data/supply_sentinel.py",
        "src/zephyr/data/calendar_coverage_checker.py",
        "src/zephyr/data/alerter.py",
    ],
    "DSC-14": ["src/zephyr/data/backfill_checker.py", "src/zephyr/data/catchup_guard.py"],
    "DSC-14D": ["src/zephyr/data/auto_backfiller.py"],
    "DSC-15": ["src/zephyr/trading/recon_runner.py", "src/zephyr/ex_core/eod_reconciliation.py"],
    "DSC-16": ["scripts/data/repair_kline_degraded_pull.py", "src/zephyr/data/c4_history_repair.py"],
    "DSC-17": ["src/zephyr/data/consensus_crosscheck.py"],
    "DSC-18": ["scripts/ch/optimize_merge.py", "config/resource_profile_registry.yaml"],
    "DSC-19": ["src/zephyr/data/scheduler.py"],
    "DSC-20": ["src/zephyr/data/integrity_checker.py", "src/zephyr/data/progress_store.py"],
}

# ── 人工语义层：槽位归属（机生层据此回填 task 计数与分派证据）───────────────
_SLOT_OWNERSHIP: dict[str, list[str]] = {
    "DSC-01": [
        "daily_kline",
        "daily_capital",
        "daily_event",
        "nightly_financial",
        "monthly_static",
        "weekend_calibration",
    ],
    "DSC-02": [
        "pre_market",
        "intraday_realtime",
        "intraday_minute",
        "intraday_sector",
        "auction_highfreq",
        "post_auction",
    ],
    "DSC-03": ["event_driven", "news_slow", "research_nightly", "daily_alt_fx", "daily_crypto", "nightly_sentiment"],
    "DSC-09": ["sector_close_final", "sector_pre_open"],
    "DSC-13": ["integrity_check", "data_supply_sentinel", "calendar_coverage_check"],
    "DSC-14": ["weekend_backfill", "daily_backfill", "catchup_guard"],
    "DSC-15": ["eod_reconciliation"],
    "DSC-17": ["consensus_crosscheck"],
}

# ── 人工语义层：节点文档指针（L0 统一名 doc_refs）────────────────────────────
_BOOK_OF: dict[str, str] = {
    "DSC-01": "01_采集三段与源熔断.md",
    "DSC-02": "01_采集三段与源熔断.md",
    "DSC-03": "01_采集三段与源熔断.md",
    "DSC-SRC": "01_采集三段与源熔断.md",
    "DSC-04": "02_入库单通道与幂等判重.md",
    "DSC-05": "02_入库单通道与幂等判重.md",
    "DSC-FB": "02_入库单通道与幂等判重.md",
    "DSC-06": "02_入库单通道与幂等判重.md",
    "DSC-GAP-DUPGUARD": "02_入库单通道与幂等判重.md",
    "DSC-07": "03_衍生加工三族.md",
    "DSC-08": "03_衍生加工三族.md",
    "DSC-09": "03_衍生加工三族.md",
    "DSC-HA": "03_衍生加工三族.md",
    "DSC-21": "11_消费端需求反查.md",
    "DSC-GAP-NAV": "11_消费端需求反查.md",
    "DSC-GAP-EXECEP": "11_消费端需求反查.md",
    "DSC-GAP-FFVAL": "11_消费端需求反查.md",
    "DSC-GAP-FFSIG": "11_消费端需求反查.md",
    "DSC-10A": "04_冷备灾备与分层.md",
    "DSC-10B": "04_冷备灾备与分层.md",
    "DSC-11": "04_冷备灾备与分层.md",
    "DSC-12": "04_冷备灾备与分层.md",
    "DSC-HB": "04_冷备灾备与分层.md",
    "DSC-HC": "04_冷备灾备与分层.md",
    "DSC-13": "05_对账修复六环.md",
    "DSC-14": "05_对账修复六环.md",
    "DSC-14D": "05_对账修复六环.md",
    "DSC-15": "05_对账修复六环.md",
    "DSC-GAP-TERMINUS": "05_对账修复六环.md",
    "DSC-GAP-RECDIFF": "11_消费端需求反查.md",
    "DSC-16": "05_对账修复六环.md",
    "DSC-17": "05_对账修复六环.md",
    "DSC-18": "05_对账修复六环.md",
    "DSC-19": "12_扩行提案与封顶重宣.md",
    "DSC-20": "12_扩行提案与封顶重宣.md",
    "DSC-GAP-NEWSGHOST": "11_消费端需求反查.md",
    "DSC-GAP-MACRO": "12_扩行提案与封顶重宣.md",
    "DSC-GAP-L2TICK": "01_采集三段与源熔断.md",
    "DSC-GAP-REPLAY": "02_入库单通道与幂等判重.md",
    "DSC-GAP-CONSENSUSCHAIN": "03_衍生加工三族.md",
    "DSC-GAP-ARCHIVE-AUDIT": "04_冷备灾备与分层.md",
    "DSC-GAP-CODEBACKUP": "04_冷备灾备与分层.md",
    "DSC-GAP-MIRROR": "04_冷备灾备与分层.md",
    "DSC-GAP-RECDIFF": "11_消费端需求反查.md",
}

_BLUEPRINT_REL = "docs/_working/map_build/03_final_blueprint_and_schema.md"


def _docs(node_id: str) -> list[str]:
    """doc_refs 统一构造：骨架契约行 + 出料簿 + 终局卷（禁把正文抄进来，只给指针）。"""
    refs = [
        f"{BOOK_DIR}/00_skeleton.md §1 {STAGE_TO_SKELETON.get(node_id, '（辅助/缺口节点，见 §6）')}",
        f"{BOOK_DIR}/{_BOOK_OF[node_id]}",
        _BLUEPRINT_REL,
    ]
    return sorted(set(refs))


# ── L2 图12 专属：freshness_evidence 构造器（口径真源=12 号卷 §5-3，含本役两次实测坑）──
def _fe(
    table: str,
    date_col: str,
    max_date: str,
    probe_at_utc: str,
    lag: int,
    channel: str,
    verdict: str,
    final_variant: str,
    err: str | None = None,
) -> dict[str, Any]:
    ev: dict[str, Any] = {
        "table": table,
        "date_col": date_col,
        "max_date": max_date,
        "probe_at_utc": probe_at_utc,
        "lag_trading_days": lag,
        "channel": channel,
        "verdict": verdict,
        "final_variant": final_variant,
    }
    if err:
        ev["probe_err"] = err
    return ev


_CH = "DatabaseService.get_clickhouse_conn(role='reader') 失败即抛"
_SQLITE = "sqlite_ro_uri:data/integrator_progress.db（只读）"
_FS = "fs_readonly:F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl"
_SCH = "os_scheduled_task:Get-ScheduledTaskInfo"
_P = "2026-09-25T15:2xZ（L-REGEN12 只读复跑；09-25 非交易日，末开盘 09-24）"

_FRESHNESS: dict[str, list[dict[str, Any]]] = {
    "DSC-01": [
        _fe(
            _tbl("market_kline_daily"),
            "trade_date",
            "2026-09-24",
            _P,
            0,
            _CH,
            "fresh",
            "both: non_final=10108162 / FINAL=10108049（WB12-37 双版并报）",
        )
    ],
    "DSC-02": [
        _fe(
            _tbl("market_tick"),
            "trade_date",
            "2026-09-24",
            _P,
            0,
            _CH,
            "fresh",
            "non_final_only（本表按 trade_date 分区，无未合并多版本争议）",
        )
    ],
    "DSC-03": [
        _fe(
            _tbl("fund_news_data"),
            "publish_time(+08 列)",
            "2026-09-25T23:17:49+08",
            _P,
            0,
            _CH,
            "fresh",
            "non_final",
            err="近 6h ingest_ts 计数 31,831 行为主口径；裸 max(publish_time) 含未来污染（在册）",
        ),
        _fe(
            _tbl("market_macro_data"),
            "report_date",
            "2026-09-24",
            _P,
            0,
            _CH,
            "fresh",
            "non_final",
            err="批次4 09-25T03:55 该表因 187×0 字节部件装载失败（probe_failed 判例），本时点已可读",
        ),
        _fe(_tbl("alt_fx_rate_ecb"), "trade_date", "2026-09-24", _P, 0, _CH, "fresh", "non_final"),
    ],
    "DSC-04": [
        _fe(
            _tbl("market_kline_daily"),
            "trade_date",
            "2026-09-24",
            _P,
            0,
            _CH,
            "fresh",
            "both: 10108162/10108049（写通道产出见证）",
        )
    ],
    "DSC-05": [_fe(_tbl("market_tick"), "trade_date", "2026-09-24", _P, 0, _CH, "fresh", "末开盘日 27,766,260 行")],
    "DSC-10B": [
        _fe(
            "archive_manifest.jsonl",
            "archived_at",
            "2026-09-24T02:07:50Z",
            _P,
            1,
            _FS,
            "lagging",
            "not_appended_after_0924",
            err="skip 原因零留痕（🌑-6），rolling_archive_state.json mtime=09-21T07:37Z 与 manifest 不自洽",
        ),
        _fe(
            "system.backup_log",
            "end_time",
            "2026-09-24T22:47:25Z",
            _P,
            0,
            _CH,
            "fresh",
            "n/a（系统表，非 ReplacingMergeTree）",
            err="此处用 system.backup_log 系 WB12-29 钦定 CH 备份真值唯一口径，非新鲜度枚举面",
        ),
    ],
    "DSC-11": [
        _fe(
            "system.backup_log",
            "end_time",
            "2026-09-24T22:47:25Z（=北京 09-25 06:47）",
            _P,
            0,
            _CH,
            "fresh",
            "n/a",
            err="同日 schtasks Result=267014（未终态）+ backup_report code_backup.status=failed",
        ),
        _fe("data/databases/backup_state.json", "last_ch_backup", "2026-09-25T06:0x+08", _P, 0, _SCH, "fresh", "n/a"),
    ],
    "DSC-13": [
        _fe(
            "integrator_progress.db:task_progress[integrity_check_daily]",
            "last_run_at",
            "2026-09-24T15:01:36Z（=北京 23:01，与 23:00 cron 秒合）",
            _P,
            1,
            _SQLITE,
            "lagging",
            "n/a（SQLite 台账面，非 FINAL 语义）",
            err="本车道 09-25T15:2xZ 复跑未见当日案卷，23:00 档缺跑疑点入 gaps",
        )
    ],
    "DSC-17": [
        _fe(
            _tbl("market_cross_validation_log"),
            "check_date",
            "2026-09-25",
            _P,
            0,
            _CH,
            "fresh",
            "count=1601（近 3 日窗 21 行）",
            err="禁改用 check_time 判新鲜（自 09-21 恒 epoch，P-7 在册）",
        )
    ],
    "DSC-20": [
        _fe(
            "integrator_progress.db:task_runs",
            "started_at",
            "2026-09-25T15:39:07Z",
            _P,
            0,
            _SQLITE,
            "fresh",
            "188,702 行/266 task_id/当日 1,714 runs",
        ),
        _fe(
            "data/failures/<ds>_integrity_check_task_reconcile_*.json",
            "casefile_date",
            "2026-09-24",
            _P,
            1,
            "fs_readonly:data/failures（主区只读）",
            "lagging",
            "n/a",
            err="09-25 当日案卷在复跑时点未生成",
        ),
    ],
}


def _n(node_id: str, segment: str, node_type: str, name_zh: str, question: str, **kw: Any) -> dict[str, Any]:
    """节点构造器——L0/L1 统一名一次给齐，避免散写漏字段（旧别名一律不用）。"""
    node: dict[str, Any] = {
        "node_id": node_id,
        "name_zh": name_zh,
        "segment": segment,
        "node_type": node_type,
        "decision_question": question,
        "note_zh": kw.pop("note_zh", ""),
        "build_status": kw.pop("build_status", "partial"),
        "wiring_status": kw.pop("wiring_status", "wired_cron"),
        "slot_source": kw.pop("slot_source", "none"),
        "slot_refs": kw.pop("slot_refs", list(_SLOT_OWNERSHIP.get(node_id, []))),
        "downstream_action": kw.pop("downstream_action", "none"),
        "fallback": kw.pop("fallback", []),
        "invalidation": kw.pop("invalidation", None),
        "module_id": kw.pop("module_id", None),
        "module_ref": kw.pop("module_ref", None),
        "source_anchors": kw.pop("source_anchors", []),
        "data_refs": kw.pop("data_refs", []),
        "store_refs": kw.pop("store_refs", []),
        "runtime_refs": kw.pop("runtime_refs", []),
        "doc_refs": _docs(node_id),
        "gap_refs": kw.pop("gap_refs", []),
        "red_reason": kw.pop("red_reason", None),
        "confidence": kw.pop("confidence", "proposed"),
        "verified_scope": kw.pop("verified_scope", None),
        "evidence": kw.pop("evidence", []),
        "freshness_evidence": kw.pop("freshness_evidence", []),
        "task_family": kw.pop("task_family", None),
        "facets": kw.pop("facets", []),
        "gaps": kw.pop("gaps", []),
    }
    node.update(kw)
    return node


_HUMAN: dict[str, Any] = {
    "schema_version": "0.2",
    "map_id": "DSCMAP-012",
    "name_zh": "数据供给链图",
    "nickname": "图12 数据供给链",
    "ttl": "permanent",
    "effective_from": "2026-09-25",
    "generator": "scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py",
    "segments": _SEGMENTS,
    "ssot_note_zh": (
        "双层图：machine 层（含每节点 machine 子块）由生成器从 tasks.yaml/schedule.yaml/scheduler 分派面/"
        "data_asset_registry/执行体文件实存性/**骨架 §1 状态列**/**depgraph 派生在册投影**全量重建，禁手工编辑；"
        "nodes/edges/feedback_loops/laws/segments/boundary 为人工语义层，落盘后 existing-wins。\n"
        "INV-1：节点只存标识符与指针（task_id/槽名/MOD-*/文件路径/表名），禁复制真源条目正文。\n"
        "字段分层（六图终局卷 §1 裁定一）：L0 统一名 note_zh/doc_refs/source_anchors/data_refs/store_refs/"
        "runtime_refs/module_id/module_ref/build_status/confidence/verified_scope/decision_question/"
        "node_type/segment；L1 纵轴层取用 slot_source/slot_refs/wiring_status/downstream_action/fallback/"
        "invalidation/gap_refs/red_reason；L2 图12 专属层字段清单=task_family（任务归簇）/facets（分面腿）/"
        "gaps（叶层缺陷台账：anchor+symptom+pointer+实测时点，是 gap_refs 的明细面）/freshness_evidence"
        "（max(date)+近窗计数+滞后交易日数+通道+verdict+FINAL 双版）。"
        "三个旧注解别名与 degradation/data_anchors/silent_failover/detection_only 等旧名一律废止，残留即 CV-L0 红。\n"
        "双轴口径（六图终局卷 §3）：verified_scope=production ⇔ 骨架 §1 行级 ✅（本批 10 个，多了算谎少了算欠），"
        "structure=仅结构性事实已核（含 3 个分面行与 ⬜/🔨 行）；分面行永不成 production（行级 ✅ 仅当全腿 ✅）。\n"
        "本图与横向 dataflowgraph（血缘轴）是同资产两轴，与图13（同一批 schedule.yaml 槽的时序轴）共享真源、"
        "分界引用：判据一句话=这条边是否关于数据本身的产出/新鲜/保全/修复。"
    ),
    "laws": [
        "INV-1 引用不复制：环节节点只挂标识符与指针（task_id/槽名/表名/文件路径/MOD-*），禁抄真源条目正文",
        "挂槽≠在跑：槽名存在不构成执行证据，判 wired 必同时拿到「槽有任务」或「scheduler 有分派分支」＋产出侧留痕",
        "新鲜度主口径=业务表 max(date)＋近窗计数（UTC 折北京比对档期），max 只作旁证；system.parts 末写降为可选附加腿且失败必记 probe_failed",
        "禁依赖 system.* 枚举面：09-25 实测一张坏表（187×0 字节部件）可打死 system.tables/parts/columns 全枚举面；探测失败必判红，禁把「查不到」写成「无问题」",
        "静默失败即假绿：ch_reader/ch_writer query 失败返回空串不抛，凡空串一律复跑排除，禁把「读不到」读成「没缺口」；证据通道只认 DatabaseService 失败即抛版",
        "ReplacingMergeTree 判真值必带 FINAL 且双版并报；判重只走 check_tick_duplication 正门，禁聚合数判重（RULE-DATA-OPS）",
        "不可逆动作三步验证（必要/真实/可逆），不可逆升 Owner 门位；冷库禁反向更新 CH（防双真源）",
        "检测≠修复：downstream_action=detect_only/alert_only 的环节其结论无下游补跑通道时须登记为缺口（gaps/gap_refs）",
        "环节枚举四源并存（tasks.yaml/schedule.yaml/scheduler 特殊槽/进程内在产写手），单源枚举结构性漏段；增枝须过停止判据三问+点名生产者类别+回写骨架 §1",
        "行级 ✅ 仅当全腿 ✅：多腿环节以 facets 逐腿挂证据，任一整腿不 ✅ 则行级不 ✅ 且禁宣 production",
    ],
    "boundary": {
        "domain_scope_zh": "外部源→采集→入库→衍生→冷备→对账修复的全生命周期运营环节（怎么被产出/保住/修回）",
        "out_of_domain": [
            "交易日时点编排与节拍（盘前/盘中/盘后/夜窗先后次序）→ 图13 交易日循环图；本图以 schedule.yaml 为共享真源锚交叉引用，互不吞并",
            "派生算法本体（因子/形态/板块聚合口径）→ 各算法域；本图节点只挂「驱动＋落库」运营面",
            "提交自愈环台账 reconcile_execution_log → 图11；与本环节近亲命名，禁按名字相似认领证据（列名集双向核对）",
            "D12-21 之外的决策用途（这些资产被谁怎么用）→ 图9/图15；本图只画生产供给环",
        ],
        "terminal_declared": ["DSC-15"],
        "terminal_provable": ["DSC-10B", "DSC-11", "DSC-17", "DSC-20"],
        "terminal_gap": "DSC-GAP-TERMINUS",
        "terminal_note_zh": (
            "骨架 §0 门① 于批次4 改写：可证终点=归档清单（D12-10b 产 archive_manifest.jsonl）＋任务级对账案卷"
            "（D12-20 产 data/failures/*task_reconcile*.json）双实锚；「对账 PASS」在 D12-15 接线前不是可达终点，"
            "以 gap 节点 DSC-GAP-TERMINUS（red_reason: terminal）显性化，禁标 built、禁以散文掩盖。"
        ),
        "waiting_table_gaps": dict(sorted(WAITING_TABLE_GAPS.items())),
        "ghost_ref_gaps": dict(sorted(GHOST_REF_GAPS.items())),
        "skeleton_contract": f"{BOOK_DIR}/00_skeleton.md §1（22 环节契约全集）+ §6.3（批次4 封顶重宣）",
    },
    "nodes": [],  # 由 _NODES 填充（见下，保持本文件可读）
    "edges": [],  # 由 _EDGES 填充
    "feedback_loops": [],  # 由 _FEEDBACK 填充
}

# ══════════════════════════════════════════════════════════════════════════
# 人工语义层：节点（L0/L1 统一名；血肉源=骨架 §1/§2 + 01~05 作业簿 + 11/12 两卷实测）
# ══════════════════════════════════════════════════════════════════════════
_S = "S1_collect"
_I = "S2_ingest"
_D = "S3_derive"
_C = "S4_coldstore"
_R = "S5_recon"

_NODES: list[dict[str, Any]] = [
    # ── S1 采集 ──────────────────────────────────────────────────────────────
    _n(
        "DSC-SRC",
        _S,
        "source",
        "外部源面（provider 归一前）",
        "哪些源在供、供到什么档期、源侧停供与本仓断链怎么分开定性？",
        note_zh="23 家源的行为差异全部吸进 provider 归一层（FetchPayload→FetchResult + CapabilityContract 启动期 fail-closed 校验），本节点只代表源面，不代表本仓代码。",
        build_status="partial",
        wiring_status="wired_cron",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/provider_base.py",
        source_anchors=[f"file:{TASKS_YAML_REL}", "file:src/zephyr/data/provider_base.py"],
        store_refs=[
            {
                "artifact": "源能力契约",
                "location": "src/zephyr/data/provider_base.py::CapabilityContract",
                "key": "source+capability",
                "retention": "随码版本化",
            }
        ],
        fallback=[
            {
                "kind": "switch_source",
                "when": "error_classifier 判 unrecoverable 即换 fallback_sources",
                "residual": "配副源任务占比低（见 machine.tasks.fallback_nonempty），多数任务一源到底",
            },
            {
                "kind": "circuit_break",
                "when": "per-source 熔断阈值跳闸",
                "residual": "纯内存不持久＝重启即复位，事后无法证明熔过没有（🌑-4）",
            },
        ],
        gaps=[
            {
                "anchor": "source:akshare_alt",
                "symptom": "attribution_moved",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §3 ★归属误置",
                "note_zh": "36 个 akshare_alt 任务实测全部落盘后档期，event_driven 槽 0 个——D12-03 归属已移正 D12-01",
            },
            {
                "anchor": "source:pause_cli",
                "symptom": "nominal_switch",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §1 内-2",
                "note_zh": "CLI pause 三处断链坐实（真源无 enabled 键/热重载复位/跨进程零效力），可用停摆开关实为 schedule:disabled / extra.disabled / *.disabled 三类",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/01_采集三段与源熔断.md §1 内-1（实测 2026-09-24）",
            f"{BOOK_DIR}/00_skeleton.md §7-B 逐源计数（可复跑）",
        ],
    ),
    _n(
        "DSC-01",
        _S,
        "stage",
        "盘后批量采集（日K/估值/资金/事件/财务/静态/校准族）",
        "盘后各档期该产出的原始表今天出齐了吗？缺的是源侧现实还是本仓断链？",
        note_zh="六个盘后档期按 tasks.yaml schedule 字段精确字符串匹配派工（一任务只属一槽），同槽任务进 TaskQueue 按 DAG 跑。第三腿已从 parts 代理升级为 task_runs 打卡（批次4）。",
        build_status="built",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/scheduler.py",
        source_anchors=[
            "slot:daily_kline",
            "slot:weekend_calibration",
            "slot:monthly_static",
            "task:kline_daily_incremental",
            f"file:{TASKS_YAML_REL}",
            f"file:{SCHEDULE_YAML_REL}",
        ],
        data_refs=[_tbl("market_kline_daily"), _tbl("market_stock_daily_basic"), _tbl("market_money_flow")],
        store_refs=[
            {
                "artifact": "盘后原始表族",
                "location": "c1_market / c3_fundamental（表集见 machine.tasks.target_tables）",
                "key": "trade_date",
                "retention": "Hot 层无 TTL（INV-RET-003）",
            }
        ],
        fallback=[
            {
                "kind": "switch_source",
                "when": "主源不可恢复错立即切副源；可恢复错重试用尽再切",
                "residual": "每次用副源发 LEVEL_ERROR 告警，但副源长期顶班无收敛指标",
            },
            {
                "kind": "skip_source",
                "when": "source_health_check 五态预筛跳过",
                "residual": "跳过是静默的，与真断供在 CH 侧不可区分",
            },
        ],
        gap_refs=["DSC-GAP-NEWSGHOST"],
        task_family="akshare/miniqmt/tushare 盘后六档期族",
        gaps=[
            {
                "anchor": "slot:monthly_static",
                "symptom": "unprovable_slot",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §1 判定",
                "note_zh": "该槽 20 表中仅 4 表两日内有写，与每月 1 日 09:16 档期不吻合——月度子族档期级执行不可证（行级 ✅ 的限定面）",
            },
            {
                "anchor": "slot:weekend_calibration",
                "symptom": "dow_semantics_conflict",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §4 溢-2",
                "note_zh": "同文件对 crontab dow 给两种口径（0=周日 vs APScheduler 0=周一），实测写入簇支持后者",
            },
            {
                "anchor": "task:cohort_ledger_daily",
                "symptom": "duplicate_task_id",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §4 溢-4",
                "note_zh": "全仓唯一重复 task_id（双槽两条），与一任务只属一槽律正冲突＝同日两跑同表",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/01_采集三段与源熔断.md §1（末写小时直方四簇＝盘后按档期在跑）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2（task_runs 秒合见证）",
            "本图 machine 层（tasks/schedule/scheduler 分派面实测，走生成器可复跑）",
        ],
        freshness_evidence=_FRESHNESS["DSC-01"],
    ),
    _n(
        "DSC-02",
        _S,
        "stage",
        "盘中实时/竞价采集（Tick/L2/Greeks/分钟K/880板块/集合竞价）",
        "盘中这条流今天还在产数吗？哪些子腿已经静默空转？",
        note_zh="盘中五槽＋秒级竞价窗（6 段 cron + max_instances=1 + coalesce 节流）；产数走 WAL 通道，与盘后批共用写手但不同入口。静默失败在册：占位任务与真断供在档期面同形。",
        build_status="built",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/tick_subscriber.py",
        source_anchors=["slot:intraday_realtime", "slot:auction_highfreq", "slot:post_auction", "slot:intraday_sector"],
        data_refs=[
            _tbl("market_tick"),
            _tbl("market_realtime_snapshot"),
            _tbl("market_kline_1min"),
            _tbl("market_l2_tick"),
            _tbl("market_suspend"),
        ],
        store_refs=[
            {
                "artifact": "盘中行情表族",
                "location": "c1_market（tick_data/kline_*min/sector_snapshot 等）",
                "key": "trade_date+symbol",
                "retention": "Hot 层无 TTL，超线走 DSC-10A/10B 归档",
            }
        ],
        fallback=[
            {
                "kind": "placeholder_task",
                "when": "QMT 无接口的标的以 *_placeholder 任务占位",
                "residual": "占位任务与真断供在档期面同形，须按 task_id 后缀区分（不误判断供）",
            }
        ],
        gap_refs=["DSC-GAP-L2TICK"],
        task_family="miniqmt/tqcenter/tdx/tickflow 盘中族",
        gaps=[
            {
                "anchor": _tbl("market_l2_tick"),
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §2 内表",
                "note_zh": "坐实断供：表在、任务在、0 行（本车道 09-25 复跑仍 0）——L2 行情权限缺失（💰-4）＋降级腿 09-09 被清＝静默空转",
            },
            {
                "anchor": _tbl("market_suspend"),
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §2 内表",
                "note_zh": "三个任务写同一表、0 行（复跑仍 0）——停复牌面从未产数",
            },
            {
                "anchor": _tbl("market_realtime_snapshot"),
                "symptom": "written_but_stale",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-B",
                "note_zh": "供数形态疑点：11 卷实测盘中段零供给；本车道复跑 09-01 后计数 0 且 max(snapshot_time)=1970 哨兵——E8 期望未定，待裁不武断标红（N4）",
            },
            {
                "anchor": "slot:post_auction",
                "symptom": "unprovable_slot",
                "measured_on": "2026-09-24",
                "pointer": "本图 machine.scheduler_dispatch.slots_hollow（槽在、零任务、无分派分支）",
                "note_zh": "空转槽：到点后进常规 DAG 分支、该槽名下 0 任务、静默返回成功（R-021 假通道形态）",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/01_采集三段与源熔断.md §2（逐表新鲜度实测）",
            f"{BOOK_DIR}/02_入库单通道与幂等判重.md §2",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2（本车道复跑读数）",
        ],
        freshness_evidence=_FRESHNESS["DSC-02"],
    ),
    _n(
        "DSC-03",
        _S,
        "stage",
        "事件驱动采集（新闻/宏观/研报/另类/加密；口径=数据源事件）",
        "7×24 事件流今天还在进吗？新鲜度该用哪个尺读才不会假绿？",
        note_zh="event_driven */3 全周＋news_slow/research_nightly/daily_alt_fx/daily_crypto；本节点语义限定数据源事件，与交易域 position 事件入口（R-015）是两套事件面。静默失败在册：max(publish_time) 含未来污染，主口径改用近窗计数。",
        build_status="built",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/news_dedup.py",
        source_anchors=["slot:event_driven", "slot:news_slow", "slot:daily_alt_fx", "slot:research_nightly"],
        data_refs=[
            _tbl("fund_news_data"),
            _tbl("market_macro_data"),
            _tbl("alt_fx_rate_ecb"),
            _tbl("research_report"),
            _tbl("crypto_kline_daily"),
        ],
        store_refs=[
            {
                "artifact": "新闻/宏观/另类原始表",
                "location": f"{_tbl('fund_news_data')} / {_tbl('market_macro_data')}",
                "key": "news_id+publish_time（排序键）",
                "retention": "Hot 层无 TTL，超线走冷备段",
            }
        ],
        fallback=[
            {
                "kind": "dedup_on_write",
                "when": "news_dedup 标题 MD5 + ReplacingMergeTree 幂等",
                "residual": "去重靠排序键，与全字段判重（DSC-06）不同口径",
            }
        ],
        gap_refs=["DSC-GAP-NEWSGHOST", "DSC-GAP-MACRO", "DSC-GAP-CONSENSUSCHAIN"],
        task_family="akshare_alt/rss/fred/eia/qweather 事件族",
        gaps=[
            {
                "anchor": _tbl("fund_news_data"),
                "symptom": "future_value_polluted_max",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §3 内表",
                "note_zh": "max(publish_time) 超前 now()（脏值少量）——第三型假读：既非空串也非 1970，裸 max 不可当新鲜度",
            },
            {
                "anchor": _tbl("market_road_freight_index"),
                "symptom": "source_side_lag",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §3 内表",
                "note_zh": "源侧现实滞后（disabled_reason 在册），非本仓断链，勿误判为管线停摆",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/01_采集三段与源熔断.md §3（五族新鲜度实测，🔨→✅ 转判）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2/§5-2",
        ],
        freshness_evidence=_FRESHNESS["DSC-03"],
    ),
    _n(
        "DSC-GAP-NEWSGHOST",
        _S,
        "gap",
        f"幽灵引用：c1_market.news_data（库名前缀写错，真身 {_tbl('fund_news_data')}）",
        "消费册里这个限定名指向的表真的存在吗？按它建的供数监控会不会永远查不到？",
        note_zh=f"图内唯一 ghost_ref 节点。本车道 09-25 fail-visible 复跑：CH 查该限定名报 Code 60 does not exist；真身 {_tbl('fund_news_data')} 8,198,023 行在产。错的是册面库名前缀——改册件在 SPM 侧，图内只留幽灵节点防再引。",
        build_status="pending",
        wiring_status="wired_manual",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="ghost_ref",
        source_anchors=["file:config/strategy_production_map.yaml"],
        data_refs=["table:c1_market.news_data", _tbl("fund_news_data")],
        store_refs=[
            {
                "artifact": "幽灵引用登记",
                "location": f"{BOOK_DIR}/11_消费端需求反查.md §1-D",
                "key": "ref_string",
                "retention": "改册落地后本节点退役",
            }
        ],
        gaps=[
            {
                "anchor": "table:c1_market.news_data",
                "symptom": "ghost_ref",
                "measured_on": "2026-09-25",
                "pointer": "config/strategy_production_map.yaml:76（FAC-E1 进货）＋本车道直查复跑",
                "note_zh": f"Code 60 不存在；真身={_tbl('fund_news_data')}。存在性判据用直查抛错，不依赖 system.tables 枚举面（本役纪律）",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-D", f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §5-2"],
    ),
    _n(
        "DSC-GAP-MACRO",
        _S,
        "gap",
        "运行事故：macro_data 0 字节部件装载失败致读链不可达（探测器口径外）",
        "一张表的部件坏了，谁会先知道？现有检核里有谁的口径抓得住它？",
        note_zh="批次4（09-25T03:55）实录 187×0 字节 parts 致该表装载失败，并连锁打死 system.tables/parts/columns 全枚举面；本车道 09-25T15:2x 复跑该表已可读（max(report_date)=09-24）＝事故态解除。可修问题禁洗成 🌑：本节点按运行事故红项入账，检测口径缺口（CHECKSUM 之外的 0 字节部件族）挂 DSC-19。",
        build_status="pending",
        wiring_status="wired_stream",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=[_tbl("market_macro_data"), "file:src/zephyr/data/scheduler.py"],
        data_refs=[_tbl("market_macro_data")],
        store_refs=[
            {
                "artifact": "事故案卷",
                "location": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md 卷首红条/§5-2",
                "key": "table+probe_ts",
                "retention": "扩口径施工落地＋周期抽检转正后本节点退役",
            }
        ],
        gaps=[
            {
                "anchor": _tbl("market_macro_data"),
                "symptom": "probe_failed",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §3 新证（红）",
                "note_zh": "探测器只查 CHECKSUM_DOESNT_MATCH，抓不到装载期 0-byte parts；且事故同时瘫痪其依赖面之外的 parts 枚举——在册环节无一拦住本次事故",
            },
            {
                "anchor": "task:macro_data_incremental",
                "symptom": "source_side_lag",
                "measured_on": "2026-09-25",
                "pointer": "data/failures/20260925_macro_data_incremental_145625.json（本车道实读）",
                "note_zh": "当日该任务仍失败（源侧 SSL EOF，非部件问题）——两码事，禁混判",
            },
        ],
        evidence=[f"{BOOK_DIR}/12_扩行提案与封顶重宣.md 卷首红条", "本车道 09-25T15:2xZ fail-visible 复跑（直查可读）"],
    ),
    # ── S2 入库 ──────────────────────────────────────────────────────────────
    _n(
        "DSC-04",
        _I,
        "stage",
        "ClickHouse 写入通道（两条二级降级）",
        "写不进去时数据落在哪里、什么时候回灌、回灌排空过没有？",
        note_zh="读/DDL 链 TCP(9000)→HTTP(8123)；批量写链 HTTP(8123)→本地 TSV 落盘——批量写从不过 TCP，骨架三级降级是把两条链串成一条（退役的 WSL subprocess 通道是三级说法的记忆残留）。",
        build_status="built",
        wiring_status="wired_import",
        slot_source="none",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/ch_writer.py",
        source_anchors=["file:src/zephyr/data/ch_writer.py", "file:src/zephyr/data/local_replay.py"],
        data_refs=[_tbl("market_kline_daily")],
        store_refs=[
            {
                "artifact": "写失败落盘件",
                "location": "data/local_fallback/<table>/ + _manifest.jsonl",
                "key": "table+file",
                "retention": "回灌成功即 unlink（失败保留待重试）",
            }
        ],
        fallback=[
            {
                "kind": "tcp_to_http",
                "when": "TCP 构造/探针/execute 抛 → 弃连接槽＋15s 冷却 → HTTP",
                "residual": "冷却期内直接返回空串，调用方须自行降级",
            },
            {
                "kind": "http_to_local_durable",
                "when": "http_host 探活失败或 http_insert 返 False → save_fallback 落 TSV",
                "residual": "该路径曾 3h 零日志，现每 500 次一条限频告警；三态 WriteDisposition 明文禁把本地持久化伪装成 CH 已提交",
            },
            {
                "kind": "cascade_self_heal",
                "when": "HTTP 连续 5 次 5xx → 同时作废 TCP/HTTP 两单例",
                "residual": "4xx 不计（数据问题非链路问题）；恢复只能靠下次调用自然重探或人工 health_check()",
            },
        ],
        gap_refs=["DSC-GAP-REPLAY"],
        task_family="全量写路径（两链二级降级）",
        gaps=[
            {
                "anchor": "task:dynamic_local_replay",
                "symptom": "unregistered_running",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §1 下",
                "note_zh": "回灌排水在册 resource_profile_registry（planned/dynamic），samples 落点本 worktree 不可见→回灌真排空过没有仍不可证",
            }
        ],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §1（每级触发/恢复判据逐行号实测）"],
        freshness_evidence=_FRESHNESS["DSC-04"],
    ),
    _n(
        "DSC-05",
        _I,
        "stage",
        "实时 WAL 落盘排空（tick 先段落盘→异步 drain）",
        "tick 流落盘的段什么时候被排空？容量告急时是减速还是拒收？",
        note_zh="段落盘与 drain 复用 DSC-04 的同一套 local_fallback 目录/manifest/回灌器（不是两套积压）；90% 容量是硬阻断（add() 直接拒收）不是软减速；攒批写（buffered_writer，32 任务）与 WAL 同形不同物。",
        build_status="built",
        wiring_status="wired_stream",
        slot_source="event",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/wal_writer.py",
        source_anchors=["file:src/zephyr/data/wal_writer.py", "file:src/zephyr/data/buffered_writer.py"],
        data_refs=[_tbl("market_tick"), _tbl("market_tick_depth_5")],
        store_refs=[
            {
                "artifact": "WAL 段文件",
                "location": "data/local_fallback/（与 DSC-04 同目录）",
                "key": "table+segment",
                "retention": "drain 成功即删，容量阈值 2 GiB",
            }
        ],
        fallback=[
            {
                "kind": "backpressure",
                "when": "目录实扫 ≥90% → 拒收新行",
                "residual": "单一指标 zephyr_wal_backlog_files 两义——分不清背压积压还是链路故障积压（🌑-5）",
            }
        ],
        gap_refs=["DSC-GAP-REPLAY"],
        task_family="tick/depth5 两路 WAL",
        gaps=[
            {
                "anchor": "file:src/zephyr/data/wal_writer.py",
                "symptom": "unprovable_slot",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §2 判定欠项",
                "note_zh": "warning/critical 档历史上是否真触发过无 metrics 落盘可证（🌑-5）",
            }
        ],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §2（阈值/背压/drain 退避逐行号＋写入见证）"],
        freshness_evidence=_FRESHNESS["DSC-05"],
    ),
    _n(
        "DSC-FB",
        _I,
        "convergence",
        "local_fallback 汇聚（TSV + manifest + 回灌器一套两用途）",
        "降级落盘与 WAL 积压是不是同一个袋子里的两堆？",
        note_zh="一个汇聚节点收两条入边（DSC-04 降级写、DSC-05 WAL 段），共用 _manifest.jsonl 与 replay_batch——骨架把两行分列易被读成两套存储，此处并置（WB12-26）。",
        build_status="built",
        wiring_status="wired_import",
        slot_source="none",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/local_replay.py",
        source_anchors=["file:src/zephyr/data/local_replay.py"],
        store_refs=[
            {
                "artifact": "回灌清单",
                "location": "data/local_fallback/_manifest.jsonl",
                "key": "table+file+ts",
                "retention": "append（成功 unlink 对应 TSV）",
            }
        ],
        gap_refs=["DSC-GAP-REPLAY"],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §4 溢-3"],
    ),
    _n(
        "DSC-06",
        _I,
        "stage",
        "幂等写与判重（引擎语义 + 全字段判重正门）",
        "这批行是引擎合并造成的读数差，还是真重复？能不能据此删？",
        note_zh="幂等由调用方决定（ReplacingMergeTree 直接 INSERT / MergeTree 写前 DELETE）；判重口径是破坏性操作的准入闸——真重复定义=全字段相同，禁 count()-uniqExact(排序键)（2026-07-16 tick 21 个月误删事故的治本件）。静默失败在册：判重器自身红被吞成 0。",
        build_status="partial",
        wiring_status="wired_import",
        slot_source="none",
        slot_refs=[],
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="structure",
        module_ref="scripts/governance/data_quality/check_tick_duplication.py",
        source_anchors=["file:scripts/governance/data_quality/check_tick_duplication.py"],
        data_refs=[_tbl("market_tick")],
        store_refs=[
            {
                "artifact": "判重报告",
                "location": "stdout/人工案卷（无落库台账）",
                "key": "table+month",
                "retention": "无（案卷不入库＝审计缺口）",
            }
        ],
        fallback=[
            {
                "kind": "engine_merge",
                "when": "未合并多版本查询可见 → 判真值须 FINAL",
                "residual": "ch_reader 自动注 FINAL、DatabaseService 原生连接不注，同一 SQL 两通道结果可不同",
            }
        ],
        gap_refs=["DSC-GAP-DUPGUARD"],
        task_family="引擎幂等 + 判重正门",
        gaps=[
            {
                "anchor": "file:scripts/governance/data_quality/check_tick_duplication.py",
                "symptom": "tool_broken",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §3 内-5",
                "note_zh": "见 DSC-GAP-DUPGUARD——聚合对照腿一跑必红且红被吞成 0",
            }
        ],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §3（引擎/排序键/分区键实测＋Code 42 复现）"],
    ),
    _n(
        "DSC-GAP-DUPGUARD",
        _I,
        "gap",
        "缺口：判重器聚合对照腿不可用（准入闸半假绿）",
        "被判重器放行的无重复结论，今天能不能信？",
        note_zh="RULE-DATA-OPS 指定的判重唯一正门自身坏着：不得以工具跑过了当作删数据的许可。",
        build_status="pending",
        wiring_status="wired_manual",
        slot_source="manual",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=["file:scripts/governance/data_quality/check_tick_duplication.py"],
        data_refs=[_tbl("market_tick")],
        store_refs=[
            {
                "artifact": "缺陷登记",
                "location": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §4 溢-5",
                "key": "script+line",
                "retention": "施工期改后本节点应退役",
            }
        ],
        gaps=[
            {
                "anchor": "file:scripts/governance/data_quality/check_tick_duplication.py:230",
                "symptom": "false_success",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §3 内-5",
                "note_zh": "_SQL_TOTAL_ROW 平铺 14 列 × tick_data 4 个 Nullable 列 → Code 42 恒抛 → 空串 → 解析成 0 行 → 报告印总行数 0/去重 0/差 0，exit 码只由真重复腿决定＝半假绿",
            },
            {
                "anchor": "file:scripts/governance/data_quality/check_tick_duplication.py:125",
                "symptom": "hardcoded_main_repo",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §4 溢-5(b)",
                "note_zh": "脚本硬编码主区 src 并插 sys.path → 在 worktree 里跑会加载主区代码，判重结论与被审仓不同源",
            },
        ],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §3 内-5（Code 42 原样复跑复现＋行号级因果链）"],
    ),
    _n(
        "DSC-07",
        _D,
        "stage",
        "技术指标 / 多周期重采样",
        "派生表比上游新吗？多周期 K 线该走哪一条实现？",
        note_zh="指标腿＝2 个 internal 任务（增量挂 daily_kline、全刷挂周末校准）；重采样腿在生产上有 5 处并行实现互不复用，kline_resampler.py 作为独立合成器事实已被 provider 内联实现取代。行级状态=分面（骨架 §1 口径：任一整腿不 ✅ 则行级不 ✅）。",
        build_status="partial",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/kline_resampler.py",
        source_anchors=[
            "task:technical_indicator_incremental",
            "slot:daily_kline",
            "file:src/zephyr/data/kline_resampler.py",
            "file:src/zephyr/data/implementations/ch_tick_kline.py",
        ],
        data_refs=[
            _tbl("market_technical_indicator"),
            _tbl("market_sector_kline_intraday"),
            _tbl("market_kline_weekly"),
            _tbl("market_kline_monthly"),
        ],
        store_refs=[
            {
                "artifact": "指标/多周期 K 线表",
                "location": _tbl("market_technical_indicator") + " / kline_{15,30,60}min / kline_sector_*",
                "key": "trade_date+symbol",
                "retention": "Hot 层无 TTL",
            }
        ],
        fallback=[
            {
                "kind": "advisory_deps",
                "when": "跨槽 dependencies 在 task_queue 里判已满足（防永久 PENDING 死锁）",
                "residual": "跨槽依赖全 advisory，引用不存在的 task_id 也判已满足＝假依赖不报错；倒挂只由 manual 件检测，无档期/闸消费",
            },
            {
                "kind": "slot_inversion",
                "when": "下游档期早于上游档期 → 静默吃 T-1 数据",
                "residual": "实测 3 组倒挂在册（cohort_ledger/emotion_index_close_final/daban_engine_load）",
            },
        ],
        task_family="internal 指标族 + 重采样五实现簇",
        facets=[
            {
                "leg_id": "indicator",
                "name_zh": "技术指标腿",
                "status": "✅",
                "evidence": [
                    f"本车道复跑 {_tbl('market_technical_indicator')} max=2026-09-24（362,215,198 行）",
                    "task_runs 5×SUCCESS（max 09-24T09:32Z）",
                ],
            },
            {
                "leg_id": "resample",
                "name_zh": "多周期重采样腿",
                "status": "🔨",
                "evidence": [
                    f"{_tbl('market_sector_kline')}_intraday max=2026-09-22 15:00+08（本车道复跑未涨）",
                    "该族 5 任务 ≥09-21 零打卡，09-24 案卷列漏跑（DSC-20 输出）",
                ],
            },
        ],
        gaps=[
            {
                "anchor": _tbl("market_sector_kline_intraday"),
                "symptom": "stale_as_of",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §1 内-3",
                "note_zh": "板块分钟线 5 个 period 全写同一表，停在 09-22 15:00＝跨两交易日零写入；根因二选一（tdx 源静默跳过 vs 串行超时）CH 侧不可判",
            },
            {
                "anchor": _tbl("market_kline_weekly"),
                "symptom": "stale_as_of",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §1 内-2 表 c",
                "note_zh": "周/月线（miniqmt pandas resample 路径）停 9 日",
            },
            {
                "anchor": "file:src/zephyr/data/kline_resampler.py",
                "symptom": "parallel_impl_cluster",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §4 溢-2",
                "note_zh": "重采样 5 处并行实现同域重复簇→内收判据要求收敛唯一正门（叶层收簇项，不增枝）",
            },
        ],
        evidence=[f"{BOOK_DIR}/03_衍生加工三族.md §1（指标腿三证＋档期不可证限定；重采样 5 实现逐条 manifest）"],
    ),
    _n(
        "DSC-08",
        _D,
        "stage",
        "财务 / 一致预期派生（PIT 双守卫）",
        "派生层滞后是派生自己的锅，还是上游的锅？",
        note_zh="两条 internal 腿：financial_derived_build（deps=三大报表）与 consensus_daily_build（deps=研报明细+交易日历）；PIT 铁律在派生侧有第二道守卫（1970 哨兵 + publish_date<=trade_date 零 embargo）。行级状态=分面。",
        build_status="partial",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/implementations/consensus_daily_compute.py",
        source_anchors=[
            "task:consensus_daily_build",
            "task:financial_derived_build",
            "file:src/zephyr/data/implementations/financial_derived_compute.py",
        ],
        data_refs=[_tbl("fund_financial_derived"), _tbl("fund_consensus_daily")],
        store_refs=[
            {
                "artifact": "派生层表",
                "location": f"{_tbl('fund_financial_derived')} / consensus_daily",
                "key": "announce_date / trade_date",
                "retention": "Hot 层无 TTL",
            }
        ],
        fallback=[
            {
                "kind": "dual_entry",
                "when": "调度入口（internal provider）与 CLI 回补入口（scripts/ch/build_*.py --check）并存",
                "residual": "两入口幂等条件同为窗口 DELETE+INSERT，人工重跑与档期重跑在台账上不可区分",
            }
        ],
        gap_refs=["DSC-GAP-CONSENSUSCHAIN"],
        task_family="internal 财务/预期两腿",
        facets=[
            {
                "leg_id": "financial",
                "name_zh": "财务派生腿",
                "status": "🔨",
                "evidence": [
                    "本车道复跑：financial_derived_build 末次 2026-09-24T23:27:35Z(北京) status=FAILED",
                    "error='<' not supported between instances of 'str' and 'datetime.date'",
                    "financial_derived max(announce_date)=09-02；09-23/24 案卷均列漏跑",
                ],
            },
            {
                "leg_id": "consensus",
                "name_zh": "一致预期腿",
                "status": "🔴",
                "evidence": [
                    "consensus_daily max=2026-09-14（本车道复跑 6,797,719 行，停更持续）",
                    "consensus_daily_build 末次 09-18 FAILED＋连日漏跑",
                ],
            },
        ],
        gaps=[
            {
                "anchor": "task:financial_derived_build",
                "symptom": "run_failing",
                "measured_on": "2026-09-25",
                "pointer": "integrator_progress.db task_progress（本车道只读复跑）＋ 05 簿 §1.2 案卷",
                "note_zh": "财务腿由批次4 的案卷漏跑升级为跑必失败（类型比较异常），三腿中档期留痕有但结果为红",
            },
            {
                "anchor": "file:src/zephyr/data/financial_parser.py",
                "symptom": "path_ghost",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §4 溢-7",
                "note_zh": "骨架原列真源，其 CONSUMERS 自证接线尚未发生——不在产数路径，真源映射已改挂两个 compute 实现件",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/03_衍生加工三族.md §2（上游三表 max 与派生 max 严格相等判据）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2（D12-08 分面下调）",
        ],
    ),
    _n(
        "DSC-09",
        _D,
        "stage",
        "形态 / 情绪 / 板块状态衍生",
        "板块状态这张表该不该有 T 日截面？派生全集能不能只靠 tasks.yaml 枚举？",
        note_zh="两类触发面并存：tasks.yaml 档期（形态/情绪/打板）＋ scheduler 硬编码特殊槽（sector_close_final / sector_pre_open，产物在 tasks.yaml 之外）；renko/point_figure/kagi 真身是信号域纯函数算法叶（不落库）。行级状态=分面。",
        build_status="partial",
        wiring_status="wired_special_branch",
        slot_source="schedule",
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/implementations/internal_compute_provider.py",
        source_anchors=[
            "slot:sector_close_final",
            "slot:sector_pre_open",
            "task:pattern_event_incremental",
            "task:emotion_index_close_final",
            "file:src/zephyr/data/sector_state_pipeline.py",
            "file:src/zephyr/signal_ashare/strategy_signal/series_transform.py",
        ],
        data_refs=[
            _tbl("market_pattern_event"),
            _tbl("market_emotion_index"),
            _tbl("market_sector_state"),
            _tbl("market_sector_preference"),
            _tbl("market_daban_board_event"),
        ],
        store_refs=[
            {
                "artifact": "形态/情绪/板块派生表",
                "location": "c1_market.market_pattern_* / emotion_index / sector_state / sector_preference",
                "key": "trade_date+stage",
                "retention": "Hot 层无 TTL",
            }
        ],
        fallback=[
            {
                "kind": "special_slot",
                "when": "零任务槽走 scheduler._run_special_schedule 硬编码白名单",
                "residual": "以 tasks.yaml 为唯一枚举源的生成器会结构性漏掉这条腿（见 machine.schedule + machine.scheduler_dispatch）",
            }
        ],
        task_family="internal 形态/情绪/打板 + 特殊槽板块族",
        facets=[
            {
                "leg_id": "pattern",
                "name_zh": "形态腿",
                "status": "✅",
                "evidence": ["本车道复跑 market_pattern_event max(anchor_trade_date)=2026-09-24"],
            },
            {
                "leg_id": "emotion",
                "name_zh": "情绪腿",
                "status": "✅",
                "evidence": ["本车道复跑 emotion_index max=2026-09-24（8,650 行）"],
            },
            {
                "leg_id": "daban",
                "name_zh": "打板腿",
                "status": "🟡",
                "evidence": ["daban_board_event max=2026-09-22，末写不吻合任何档期"],
            },
            {
                "leg_id": "sector",
                "name_zh": "板块状态腿",
                "status": "🔴",
                "evidence": [
                    "sector_state close_final=09-24／pre_open=09-23（非交易日下 pre_open 落后 1 日，倒挂缺陷未销）",
                    "sector_preference 全表 2 行（批次4 记 1 行）＝丁线 owner_gate 供料端近乎空转",
                ],
            },
        ],
        gaps=[
            {
                "anchor": "file:src/zephyr/data/sector_state_pipeline.py",
                "symptom": "malformed_bus_id",
                "measured_on": "2026-09-25",
                "pointer": "docs/03_modules/path_ownership_map.yaml（在册投影查无此路径）＋depgraph nodes 表",
                "note_zh": "depgraph 侧该件 blueprint_id 写作含空格的非 MOD-* 形态，且不在派生投影里⇒本节点 module_ref 改挂在册代表路径 internal_compute_provider.py，禁自造号，登记收口请求",
            },
            {
                "anchor": _tbl("market_sector_state"),
                "symptom": "inversion",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §3 内表",
                "note_zh": "两 stage 的 trade_date 关系按定义 pre_open 只能复制已存在的 close_final；批次4 倒挂消除、本车道复跑 pre_open 又落后 1 日＝产物一致性仍无校验",
            },
            {
                "anchor": "file:src/zephyr/data/transformations/renko.py",
                "symptom": "path_ghost",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/03_衍生加工三族.md §4 溢-12",
                "note_zh": "骨架与注册表 DS-077/078/079 三处同指不存在的 transformations/ 目录（真身 series_transform）",
            },
        ],
        evidence=[f"{BOOK_DIR}/03_衍生加工三族.md §3（逐表新鲜度＋stage 分组实测）"],
    ),
    _n(
        "DSC-21",
        _D,
        "stage",
        "任务表外进程内派生生产（工厂/回测/组合域直写 CH）",
        "消费端在用的这批表是谁产的？没有 task_id 与档期的产线怎么被检核？",
        note_zh="生产者在工厂/回测/组合/计划域进程内，不走 tasks.yaml/schedule.yaml⇒任务在策与档期留痕两腿结构性缺位，只能以表新鲜＋写器代码在位证（🔨 为该格状态天花板）。D12-21 专款防腐：新表入本格必过三问，应挂任务表而未挂者不得入格、一律走 gap 红项。",
        build_status="partial",
        wiring_status="wired_import",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/pf_alloc/allocation_inputs.py",
        source_anchors=[
            "file:src/zephyr/pf_alloc/allocation_inputs.py",
            "file:src/zephyr/pf_alloc/allocation_orchestrator.py",
            "file:src/zephyr/plan_engine/daily_loop_master_switch.py",
            "file:src/zephyr/backtest/core/n_trial_ledger.py",
            "file:src/zephyr/pf_alloc/core/strategy_screener_3d.py",
        ],
        data_refs=["c1_backtest.regime_snapshot_history", "c1_backtest.strategy_screen"],
        store_refs=[
            {
                "artifact": "进程内派生表集",
                "location": "c1_backtest.regime_snapshot_history / strategy_screen（+ C 态 4 表见 gap 节点）",
                "key": "trade_date",
                "retention": "Hot 层无 TTL",
            }
        ],
        gap_refs=["DSC-GAP-NAV", "DSC-GAP-EXECEP", "DSC-GAP-FFVAL", "DSC-GAP-FFSIG", "DSC-GAP-RECDIFF"],
        task_family="任务表外进程内写手（六表起步）",
        gaps=[
            {
                "anchor": "table:regime_snapshot_history",
                "symptom": "no_task_row",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.4",
                "note_zh": "六表名在 tasks.yaml 命中数全部 0（本车道复跑）；表在产（regime 3,629 行 max=09-24 / screen 1,341 行 max=09-24）但两腿缺位",
            },
            {
                "anchor": "file:src/zephyr/position/live_nav_recorder.py",
                "symptom": "unwired",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C",
                "note_zh": "account_nav_daily 写器全仓零调用方（含 scripts）⇒见 DSC-GAP-NAV",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/11_消费端需求反查.md §1-A/§1-C/§4-N1",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.4（三问裁定+反方理由）",
        ],
    ),
    _n(
        "DSC-GAP-CONSENSUSCHAIN",
        _D,
        "gap",
        "断链：research_report→consensus_daily 预期重建链停摆",
        "预期因子食的是哪一天的数据？上游断与下游断怎么分？",
        note_zh="研报明细 max(publish_date)=09-18（本车道复跑未涨）→ 预期重建 max=09-14（比上游还早 4 天＝派生自身也停）→ 因子族与 15 卷卡直接食旧；build 任务连日列漏跑、末次 FAILED。",
        build_status="pending",
        wiring_status="wired_cron",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=["task:consensus_daily_build", _tbl("research_report")],
        data_refs=[_tbl("fund_consensus_daily")],
        store_refs=[
            {
                "artifact": "断链登记",
                "location": f"{BOOK_DIR}/03_衍生加工三族.md §2 内-4",
                "key": "table+probe_ts",
                "retention": "重跑通＋新鲜度回正后本节点退役",
            }
        ],
        gaps=[
            {
                "anchor": _tbl("fund_consensus_daily"),
                "symptom": "stale_as_of",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-B",
                "note_zh": "max=09-14（停 10 日）；消费侧受损=因子族食旧（expectations.py/factor_registry 在册锚）",
            }
        ],
        evidence=[f"{BOOK_DIR}/03_衍生加工三族.md §2", f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §5-2"],
    ),
    _n(
        "DSC-GAP-NAV",
        _D,
        "gap",
        f"等未产表：{_tbl('market_account_nav_daily')}（三消费方在等，写器零接线）",
        "净值日频这张表有活引用，但今天谁在写它？",
        note_zh="消费方在等=SPM FAC-E8/FAC-E9 + ops_alert_feed 存活度分析（只读净值序列）；生产者实况=写器 live_nav_recorder 的 record_daily_nav/persist_nav_points 全仓零调用方，表 0 行且 max(trade_date)=1970 哨兵。",
        build_status="pending",
        wiring_status="unwired_no_caller",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=[
            "file:src/zephyr/position/live_nav_recorder.py",
            "file:src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py",
        ],
        data_refs=[_tbl("market_account_nav_daily")],
        store_refs=[
            {
                "artifact": "净值表",
                "location": _tbl("market_account_nav_daily"),
                "key": "trade_date+account",
                "retention": "接线后按 Hot 层；现 0 行",
            }
        ],
        gaps=[
            {
                "anchor": _tbl("market_account_nav_daily"),
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C（本车道复跑同值）",
                "note_zh": "本车道 fail-visible 复跑：max(trade_date)=1970-01-01、count=0＝哨兵值而非数据",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-C", f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §5-2"],
    ),
    _n(
        "DSC-GAP-EXECEP",
        _D,
        "gap",
        f"等未产表：{_tbl('market_execution_report')}（实盘链未接，仅 sim 钩子）",
        "执行质量报告是 E8 的输入，实盘链路今天接了吗？",
        note_zh="消费方=SPM:334/380；生产端 ExecutionReportProducer 仅在 qmt_file_bridge_integration 对 sim 桥可选接线，broker 件自述 real 保持现状不触校验（断点 E4）；全表 1 行（末次 09-18）。",
        build_status="pending",
        wiring_status="partial",
        slot_source="event",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=[
            "file:src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py",
            "file:src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py",
        ],
        data_refs=[_tbl("market_execution_report")],
        store_refs=[
            {
                "artifact": "执行报告表",
                "location": _tbl("market_execution_report"),
                "key": "order_id+idempotency_key",
                "retention": "随 CH 表",
            }
        ],
        gaps=[
            {
                "anchor": _tbl("market_execution_report"),
                "symptom": "near_empty",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C（本车道复跑）",
                "note_zh": "count=1、max(toDate(ingest_ts))=2026-09-18＝sim 链路偶发、实盘链路零供给",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-C"],
    ),
    _n(
        "DSC-GAP-FFVAL",
        _D,
        "gap",
        "等未产表：c1_market.factor_feature_value（DDL 未 apply，表不存在）",
        "因子在线服务面写哪张表？这张表今天存不存在？",
        note_zh="消费/写入点=feature_store_writer.py:125 + offline_store 的在线面定位 + ufl 层；CH 侧 Code 60 does not exist（本车道 fail-visible 复跑，不依赖 system.tables）；DDL 件在仓未 apply（Owner 窗口）。写器 docstring 自证预期失败。",
        build_status="pending",
        wiring_status="unwired_slot_hollow",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=[
            "file:src/zephyr/factor/feature_store_writer.py",
            "file:schemas/categories/factor_feature_value.py",
        ],
        data_refs=["table:c1_market.factor_feature_value"],
        store_refs=[
            {
                "artifact": "未建表 DDL",
                "location": "schemas/categories/factor_feature_value.py（在仓未 apply）",
                "key": "table",
                "retention": "apply 后转 DSC-21 在产面，本节点退役",
            }
        ],
        gaps=[
            {
                "anchor": "table:c1_market.factor_feature_value",
                "symptom": "table_missing",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C",
                "note_zh": "工厂在线面整体悬空；子类=DDL 未 apply（与 factor_signal 同因不同件）",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-C", "本车道 09-25 fail-visible 直查复跑（Code 60）"],
    ),
    _n(
        "DSC-GAP-FFSIG",
        _D,
        "gap",
        "等未产表：c1_market.factor_signal（默认落点未建表）",
        "因子批量输出的默认 target_table 落得下去吗？",
        note_zh="默认落点=buffer.py:25/78/87；契约 shared/contracts/factor_signal.py 在仓；CH 侧 Code 60 表不存在（本车道复跑）。与 FFVAL 同族未建表，独立挂账防一修掩二。",
        build_status="pending",
        wiring_status="unwired_slot_hollow",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=[
            "file:src/zephyr/factor/core/batch_output/buffer.py",
            "file:src/zephyr/shared/contracts/factor_signal.py",
        ],
        data_refs=["table:c1_market.factor_signal"],
        store_refs=[
            {
                "artifact": "因子信号契约",
                "location": "src/zephyr/shared/contracts/factor_signal.py",
                "key": "contract",
                "retention": "规则真源 Python 契约",
            }
        ],
        gaps=[
            {
                "anchor": "table:c1_market.factor_signal",
                "symptom": "table_missing",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C",
                "note_zh": "未建表＋默认落点悬空",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-C", "本车道 09-25 fail-visible 直查复跑（Code 60）"],
    ),
    _n(
        "DSC-HA",
        _D,
        "handoff",
        "交接 A：派生表出图（→ TDM 因子 / 工厂 / 图13 消费）",
        "数据供给链在哪个点上把资产交给消费端、交完之后还归本图管吗？",
        note_zh="出图12 域边界点：原始/派生表就绪后交因子族、图9 工厂与图13 消费；本图不再管其品质判定，但保留交叉锚（DS-*/JOB-* 与 module_id）。消费端 174 点的分布即从此点外溢（11 卷分母）。",
        build_status="partial",
        wiring_status="wired_import",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="terminal",
        module_ref=None,
        source_anchors=[
            "file:docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml",
            _tbl("market_technical_indicator"),
            _tbl("fund_consensus_daily"),
        ],
        data_refs=[_tbl("market_technical_indicator"), _tbl("fund_consensus_daily")],
        store_refs=[
            {
                "artifact": "消费端交叉锚",
                "location": "data_asset_registry.yaml（DS-*/JOB-* 标识符）",
                "key": "ds_id",
                "retention": "随注册表版本化",
            }
        ],
        gap_refs=["DSC-GAP-NAV", "DSC-GAP-EXECEP", "DSC-GAP-FFVAL", "DSC-GAP-FFSIG", "DSC-GAP-NEWSGHOST"],
        evidence=[f"{BOOK_DIR}/00_skeleton.md §2 交接 A", f"{BOOK_DIR}/11_消费端需求反查.md §0 分母"],
    ),
    # ── S4 冷备 ──────────────────────────────────────────────────────────────
    _n(
        "DSC-10A",
        _C,
        "stage",
        "手动 CLI 归档（archiver 五子命令 export→verify→drop）",
        "人工批归档今天该不该跑、跑完有没有对到位次？",
        note_zh="D12-10 于批次4 拆行后的 a 腿：生产者=人工 CLI（scripts/ch/archiver.py），验证口径=dry-run＋人工判断，无档期。与 b 腿共享同一执行体（export→verify→drop 同码），拆行的理由是生产者与验证口径同时变（三问已过），不是产出物不同。",
        build_status="built",
        wiring_status="wired_manual",
        slot_source="manual",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="scripts/ch/archiver.py",
        source_anchors=["file:scripts/ch/archiver.py"],
        store_refs=[
            {
                "artifact": "归档清单",
                "location": "F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl",
                "key": "table+partition",
                "retention": "append-only 永久",
            }
        ],
        fallback=[
            {
                "kind": "verify_gate",
                "when": "verify False → unlink 不可信 Parquet 且不 drop（安全侧失败）",
                "residual": "顺序控制非事务控制：drop 成功而 manifest 写失败会盘已删、清单无记",
            },
            {
                "kind": "sampling_limited",
                "when": "行数容差 >1M 允许差 1 行；>10M 行跳过抽样；抽样 0 行放行",
                "residual": "四条放行口同时成立≈行数像就行，超大分区无逐位保证",
            },
        ],
        gap_refs=["DSC-GAP-ARCHIVE-AUDIT"],
        task_family="archiver 五子命令",
        gaps=[
            {
                "anchor": "file:scripts/ch/archiver.py",
                "symptom": "no_periodic_audit",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §末B P-2",
                "note_zh": "冷档案完好性无周期抽检；归档件从未被端到端 restore 验证覆盖（批量史 08-10/11/16 三日留痕后再无）",
            }
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §1.2/§1.3（verify 判据行号＋manifest 条数读数）"],
    ),
    _n(
        "DSC-10B",
        _C,
        "stage",
        "滚动归档事件触发器（backup-success hook，五重安全阀）",
        "备份成功之后自动归档这一环今天真的动了吗？动了几格？为什么没动？",
        note_zh="D12-10 拆行后的 b 腿：backup.ps1 STAGE 4b 成功事件钩子链调 rolling_archive_reconciler --mode full_auto（件头明文 Event-triggered only - NO new scheduled task）；验证口径=五重安全阀自评＋契约限量（batch_max_partitions=3/circuit_breaker_failures=3）。骨架原判词触发靠人工已被实测推翻。",
        build_status="built",
        wiring_status="wired_event",
        slot_source="event",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="scripts/ch/archiver.py",
        source_anchors=[
            "file:scripts/ch/archiver.py",
            "file:scripts/ch/rolling_archive_reconciler.py",
            "file:scripts/backup/backup.ps1",
            "file:docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml",
        ],
        store_refs=[
            {
                "artifact": "归档清单",
                "location": "F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl",
                "key": "table+partition",
                "retention": "append-only 永久",
            },
            {
                "artifact": "滚动状态机",
                "location": "data/databases/rolling_archive_state.json",
                "key": "consecutive_failures/kill_switch/circuit_open",
                "retention": "覆盖写（无历史）",
            },
        ],
        fallback=[
            {
                "kind": "five_valves",
                "when": "契约 enabled/批限量/熔断失败数/kill switch 任一不满足即跳批",
                "residual": "skip 原因零留痕（🌑-6）＝今天没备与备了没成功要读不同案卷才能分",
            }
        ],
        gap_refs=["DSC-GAP-ARCHIVE-AUDIT", "DSC-GAP-MIRROR"],
        task_family="事件触发滚动归档（限量 3/批）",
        gaps=[
            {
                "anchor": "file:data/databases/rolling_archive_state.json",
                "symptom": "ledger_conflict",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §1.3 待补矛盾（P-1）",
                "note_zh": "本车道复跑：state mtime=2026-09-21T07:37Z 而 manifest 末条 2026-09-24T02:07:50Z、consecutive_failures=1——谁在动 drop 仍不可判；✅ 带此限定",
            },
            {
                "anchor": "file:scripts/ch/rolling_archive_reconciler.py",
                "symptom": "skip_silent",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.1（🌑-6）",
                "note_zh": "4b stdout 仅 Write-Host 不落档、audit-trail 无 rolling 件⇒施工项：给 4b 加独立 jsonl 留痕",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/04_冷备灾备与分层.md §1.2/§1.3",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.1/§2（manifest 2,515 行末条读数）",
        ],
        freshness_evidence=_FRESHNESS["DSC-10B"],
    ),
    _n(
        "DSC-GAP-ARCHIVE-AUDIT",
        _C,
        "gap",
        "缺口：冷档案零周期抽检 + 从未端到端 restore 验证",
        "删过原件的冷档，凭什么说它今天还可读？",
        note_zh="归档段终产物（archive_manifest.jsonl）只证明导出与删除发生过，不证明副本今天仍可还原；restore_drill 计划任务从未运行在册（267011），演练零产物。",
        build_status="pending",
        wiring_status="wired_manual",
        slot_source="manual",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="terminal",
        source_anchors=["file:scripts/ch/archiver.py", "file:scripts/backup/restore_drill.py"],
        store_refs=[
            {
                "artifact": "缺口登记",
                "location": f"{BOOK_DIR}/04_冷备灾备与分层.md §末B P-2",
                "key": "obs_id",
                "retention": "抽检常态化＋端到端 restore 通过后退役",
            }
        ],
        gaps=[
            {
                "anchor": "slot:ZEPHYR-RESTORE-DRILL",
                "symptom": "never_run",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §2.5",
                "note_zh": "本车道实跑 Get-ScheduledTaskInfo：LastRun 为空、LastTaskResult=267011（从未运行）",
            }
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §1.7/§2.5"],
    ),
    _n(
        "DSC-11",
        _C,
        "stage",
        "灾备双链备份（CH 增量 + 版本化代码快照 + VM，F→G 镜像）",
        "今天真的备份成功了吗？下一次备份会不会把最后一份副本删掉？",
        note_zh="OS 计划任务（daily 6AM + post-commit reconciler 8h 撞闸即写 skipped 案卷）；CH 真值口径唯一=system.backup_log（不是 backups 目录、不是 state 文件）；代码快照为 09-14 /MIR 事故后的版本化+硬链接去重形态。",
        build_status="built",
        wiring_status="wired_os_task",
        slot_source="schtasks",
        slot_refs=["ZephyrAlpha-DailyBackup"],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="production",
        module_ref="scripts/backup/backup_reconciler.py",
        source_anchors=[
            "file:scripts/backup/backup.ps1",
            "file:scripts/backup/backup_reconciler.py",
            "file:scripts/backup/backup_config.yaml",
        ],
        store_refs=[
            {
                "artifact": "备份报告",
                "location": "logs/backup_report_*.json + data/databases/backup_state.json",
                "key": "run_timestamp",
                "retention": "滚动（cadence 24h/8h 闸）",
            },
            {
                "artifact": "CH 备份真值",
                "location": "ClickHouse system.backup_log（只读）",
                "key": "name+start_time",
                "retention": "服务端保留",
            },
        ],
        fallback=[
            {
                "kind": "skip_not_fail",
                "when": "CH 不可达/配置缺失 → skip 不算失败；post-commit 撞 8h 闸写 skipped 案卷",
                "residual": "skip 语义显式化但今天没备与备了没成功要读不同案卷",
            },
            {
                "kind": "mirror_delete",
                "when": "STAGE 3c/3d robocopy /MIR 镜像",
                "residual": "删除类退出码 2/3 仍落 status=ok 分支＝删除无 fail-loud、目标级无白名单闸",
            },
        ],
        gap_refs=["DSC-GAP-MIRROR", "DSC-GAP-CODEBACKUP"],
        task_family="四阶段备份链",
        gaps=[
            {
                "anchor": "file:scripts/backup/backup_config.yaml",
                "symptom": "guard_revived",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §2.3",
                "note_zh": "P0：g_mirror 的 ch_vm_backup 目标摘除只在登记册与一个被后续提交反向恢复的 commit 里成立；F 侧原件已瘦，下一次 /MIR 会删掉 G 侧唯一全量镜像且报告零红字（Owner 门位，不由本图代答）",
            },
            {
                "anchor": "task:ZephyrAlpha-DailyBackup",
                "symptom": "nonterminal_result",
                "measured_on": "2026-09-25",
                "pointer": "本车道实跑 Get-ScheduledTaskInfo + logs/backup_report_20260925_060007.json",
                "note_zh": "今晨 06:00:01 那次 LastTaskResult=267014（运行中/未回收，复跑时点已 17h+）、报告 duration=32,796s；CH 腿 BACKUP_CREATED 成功不能替整条链背书",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/04_冷备灾备与分层.md §2.2（四源互证）",
            "本车道 09-25 复跑 schtasks + system.backup_log + 当日报告",
        ],
        freshness_evidence=_FRESHNESS["DSC-11"],
    ),
    _n(
        "DSC-GAP-CODEBACKUP",
        _C,
        "gap",
        "断供：今晨备份的代码快照腿 status=failed",
        "报告里 CH 成功，就等于所有阶段都成功吗？",
        note_zh="本车道读 logs/backup_report_20260925_060007.json：databases.clickhouse.status=ok 且 verified=True，但 code_backup.status=failed（failures=1、vanished=5）；OS 任务态未回收。灾备段的 ✅ 因此带限定。",
        build_status="pending",
        wiring_status="wired_os_task",
        slot_source="schtasks",
        slot_refs=[],
        downstream_action="alert_only",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=["file:scripts/backup/backup.ps1", "file:logs/backup_report_20260925_060007.json"],
        store_refs=[
            {
                "artifact": "版本化快照",
                "location": "G:/backup/working_vault/<yyyymmdd>",
                "key": "run_date",
                "retention": "14 天滚动",
            }
        ],
        gaps=[
            {
                "anchor": "file:G:/backup/working_vault/20260925",
                "symptom": "run_failing",
                "measured_on": "2026-09-25",
                "pointer": "backup_report_20260925_060007.json（本车道实读）",
                "note_zh": "prev_snapshot=20260924、rotated=[]⇒09-25 快照未成，回退窗口只剩 09-24 一份",
            }
        ],
        evidence=["本车道 09-25 只读复跑：报告 JSON（utf-8-sig）逐字段实读"],
    ),
    _n(
        "DSC-12",
        _C,
        "stage",
        "冷热分层 / 压缩决策（契约驱动，结构上不可能产数 ✅）",
        "分层决策的真源件还活着吗？压缩比数据在哪里？",
        note_zh="本环节是 DSC-10B 的输入节点（决策 vs 执行），不是并列环节；真源=data_retention_contract.yaml §rolling_archive + INV-RET-003/005。骨架原指真源 storage_tiering.py 已被裁定#383 判纸面退役（零触发零消费、文件在盘未摘），data_compression_archiver.py 实测零调用方——两件的建成/在盘都不等于在岗。",
        build_status="partial",
        wiring_status="decision_only",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        module_ref=None,
        source_anchors=[
            "file:docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml",
            "file:src/zephyr/data/storage_tiering.py",
            "file:src/zephyr/data/data_compression_archiver.py",
        ],
        store_refs=[
            {
                "artifact": "压缩比度量",
                "location": "archive_manifest.jsonl 字段 compress_ratio（archiver 顺带产出）",
                "key": "table+partition",
                "retention": "同归档清单",
            }
        ],
        fallback=[
            {
                "kind": "decision_only",
                "when": "契约参数缺失即拒绝启动（load_contract_params）",
                "residual": "本环节永远不可能用产数新鲜度标 ✅——它是决策件",
            }
        ],
        gaps=[
            {
                "anchor": "file:src/zephyr/data/storage_tiering.py",
                "symptom": "retired_not_removed",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §3.1",
                "note_zh": "裁定#383 判退役、物理摘除归后续批次⇒图12 不得再当活件画",
            },
            {
                "anchor": "file:src/zephyr/data/data_compression_archiver.py",
                "symptom": "unwired",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §3.1",
                "note_zh": "头注 CONSUMERS 是期望消费者，全仓 grep 零调用方＝建好未接线",
            },
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §3（真源换挂逐件实测）"],
    ),
    _n(
        "DSC-HB",
        _C,
        "handoff",
        "交接 B：主库热数据 → 冷备段（超线分区 + 当日备份回执）",
        "热库的哪一部分交给冷备、按什么线交？",
        note_zh="超保留线分区（契约分层线）＋当日备份成功回执是准入门；本点是 S2/S3 产物进入不可逆段的唯一通道。",
        build_status="built",
        wiring_status="wired_event",
        slot_source="event",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="scripts/ch/archiver.py",
        source_anchors=[
            "file:docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml",
            _tbl("market_kline_1min"),
        ],
        data_refs=[_tbl("market_kline_1min")],
        store_refs=[
            {
                "artifact": "分层线参数",
                "location": "data_retention_contract.yaml（retention_lines_months/§rolling_archive）",
                "key": "contract_section",
                "retention": "规则真源 YAML",
            }
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §1.5/§3.2"],
    ),
    _n(
        "DSC-HC",
        _C,
        "handoff",
        "交接 C：冷库/备份件 → 恢复侧",
        "冷备产物交给谁验？验过的证据在哪里？",
        note_zh="恢复侧消费方=archiver restore / restore.ps1 / restore_drill.py / _recovery_drill.py；本交接今天只有人工案卷，无机生闭环（演练任务从未运行）。",
        build_status="partial",
        wiring_status="wired_manual",
        slot_source="manual",
        slot_refs=[],
        downstream_action="none",
        confidence="proposed",
        verified_scope="structure",
        red_reason="terminal",
        module_ref=None,
        source_anchors=["file:scripts/ch/archiver.py", "file:scripts/backup/restore.ps1"],
        store_refs=[
            {
                "artifact": "演练案卷",
                "location": "logs/dr_drill_*.json",
                "key": "drill_date",
                "retention": "人工班次留档",
            }
        ],
        gap_refs=["DSC-GAP-ARCHIVE-AUDIT"],
        gaps=[
            {
                "anchor": "file:logs/dr_drill_20260915.json",
                "symptom": "manual_only",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §1.7/§2.5",
                "note_zh": "归档件从未被端到端 restore 验证覆盖；VM 导入演练因盘容量留档跳过",
            }
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §1.7/§2.5"],
    ),
    # ── S5 对账修复 ──────────────────────────────────────────────────────────
    _n(
        "DSC-GAP-L2TICK",
        _S,
        "gap",
        "断供：l2_tick / suspend 双 0 行（L2 权限=💰-4 花钱可解）",
        "表在、任务在、行数为零——这种静默空转该记在谁账上？",
        note_zh="三任务写同一 suspend 表、l2_tick 需 L2 行情权限且原降级腿 09-09 被清（循环自引用）。本车道 09-25 fail-visible 复跑：两表 count=0 仍在。属花钱可解（💰-4），不列 🌑。",
        build_status="pending",
        wiring_status="wired_cron",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=[_tbl("market_l2_tick"), _tbl("market_suspend"), "slot:intraday_realtime"],
        data_refs=[_tbl("market_l2_tick"), _tbl("market_suspend")],
        store_refs=[
            {
                "artifact": "断供登记",
                "location": f"{BOOK_DIR}/01_采集三段与源熔断.md §2 内表",
                "key": "table",
                "retention": "权限到位并产数后本节点退役",
            }
        ],
        gaps=[
            {
                "anchor": _tbl("market_l2_tick"),
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §2",
                "note_zh": "本车道复跑仍 0 行",
            },
            {
                "anchor": _tbl("market_suspend"),
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/01_采集三段与源熔断.md §2",
                "note_zh": "三任务同写一表、0 行＝从未产数",
            },
        ],
        evidence=[f"{BOOK_DIR}/01_采集三段与源熔断.md §2", f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §5-2"],
    ),
    _n(
        "DSC-GAP-REPLAY",
        _I,
        "gap",
        "不可证：local_fallback 回灌是否真排空过（测量腿未接）",
        "落盘件有没有被回灌干净？凭哪条读数说它干净？",
        note_zh="回灌排水在 resource_profile_registry 登记为 planned/dynamic，samples 落点在本 worktree 不可见；DSC-04/05/FB 三条边都指向此不可证面，故单列缺口而非三处各写一遍散文。",
        build_status="pending",
        wiring_status="running_unregistered",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=["file:src/zephyr/data/local_replay.py", "file:config/resource_profile_registry.yaml"],
        store_refs=[
            {
                "artifact": "回灌测量样本",
                "location": ".runtime/logs/resource_samples/（本 worktree 不可见）",
                "key": "task_id+ts",
                "retention": "待接测量腿",
            }
        ],
        gaps=[
            {
                "anchor": "task:dynamic_local_replay",
                "symptom": "unregistered_running",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/02_入库单通道与幂等判重.md §1 下",
                "note_zh": "登记侧滞后＋测量样本零落点＝排空与否无读据（残余 🌑-1 两点之一）",
            }
        ],
        evidence=[f"{BOOK_DIR}/02_入库单通道与幂等判重.md §1"],
    ),
    _n(
        "DSC-GAP-MIRROR",
        _C,
        "gap",
        "P0：g_mirror 的 ch_vm_backup 目标防护只在未提交工作树里成立",
        "下一次 /MIR 会不会删掉全机唯一一份全量镜像，而且报告零红字？",
        note_zh="在册摘除 commit 的防护被后续提交反向恢复（dev HEAD 仍含该目标），F 侧原件已瘦；删除类 robocopy 退出码 2/3 仍落 status=ok 分支⇒不会报红。系 Owner 门位，不由施工件代答。",
        build_status="pending",
        wiring_status="wired_os_task",
        slot_source="schtasks",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="broken_supply",
        source_anchors=["file:scripts/backup/backup.ps1", "file:scripts/backup/backup_config.yaml"],
        store_refs=[
            {
                "artifact": "镜像目标清单",
                "location": "scripts/backup/backup_config.yaml §g_mirror.targets",
                "key": "target_name",
                "retention": "配置真源",
            }
        ],
        gaps=[
            {
                "anchor": "file:scripts/backup/backup_config.yaml",
                "symptom": "guard_revived",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/04_冷备灾备与分层.md §2.3（99_pending_owner.md 已在报）",
                "note_zh": "WB12-44 P0；本车道 09-25 报告实读 g_mirror.targets 只余 zephyr_cold 一项且 robocopy_exit=1/status=ok",
            }
        ],
        evidence=[f"{BOOK_DIR}/04_冷备灾备与分层.md §2.3（全证据链 git log -p 实见）"],
    ),
    _n(
        "DSC-13",
        _R,
        "stage",
        "完整性巡检 + 新鲜度哨兵（四检核器，只检测不回补）",
        "数据该新没新、该全没全？检出来的缺口谁来修？",
        note_zh="integrity_check(23:00 达标检测) + supply_sentinel(06:50 业务新鲜度阈值/切片/行数地板，并托管 quality_sentinel 变异巡检) + calendar_coverage(07:10 日历×表日期差集)。全族只检测+告警，回补由 DSC-14 按各自口径独立发现。任务级对账已于批次4 独立成行（DSC-20）。",
        build_status="built",
        wiring_status="wired_special_branch",
        slot_source="schedule",
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/integrity_checker.py",
        source_anchors=[
            "slot:integrity_check",
            "slot:data_supply_sentinel",
            "slot:calendar_coverage_check",
            "file:src/zephyr/data/integrity_checker.py",
            "file:src/zephyr/data/supply_sentinel.py",
            "file:src/zephyr/data/config/data_supply_sentinel.yaml",
        ],
        store_refs=[
            {
                "artifact": "告警件",
                "location": "data/failures/*.json",
                "key": "yyyymmdd+check+time",
                "retention": "落盘即止（无确认/销项字段）",
            },
            {
                "artifact": "巡检台账",
                "location": "data/integrator_progress.db task_progress",
                "key": "task_id",
                "retention": "常驻",
            },
        ],
        fallback=[
            {
                "kind": "alert_only",
                "when": "CRITICAL 才 webhook 外发，其余等级静默落盘",
                "residual": "连续多日数十个告警件无人消解即无人知晓",
            },
            {
                "kind": "empty_string_as_pass",
                "when": "CH 查询 404/500 → 空串",
                "residual": "读不到被读成没缺口＝假绿（逐阈值分支未逐条审计）",
            },
        ],
        gap_refs=["DSC-GAP-RECDIFF", "DSC-GAP-MACRO"],
        task_family="四检核器（23:00/06:50/07:10）",
        gaps=[
            {
                "anchor": "slot:integrity_check",
                "symptom": "detection_no_repair",
                "measured_on": "2026-09-23",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §1.2",
                "note_zh": "案卷坐实 20 个衍生/财务任务漏跑＋19 失败，含 consensus_daily_build/financial_derived_build——检出来了但无自动补跑通道",
            },
            {
                "anchor": "slot:integrity_check",
                "symptom": "slot_run_missing",
                "measured_on": "2026-09-25",
                "pointer": "本车道 09-25T15:2xZ 复跑（task_progress + data/failures 双向）",
                "note_zh": "23:00 档在复跑时点（slot 后约 25min）无当日案卷、台账仍停在 09-24T15:01:36Z＝当日缺跑疑点（历史案卷 09-21~24 四日连产为反证）",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/05_对账修复六环.md §1.2（台账 last_run/status/rows＋按日告警计数实测）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2（D12-13 🔨→✅ 三证）",
        ],
        freshness_evidence=_FRESHNESS["DSC-13"],
    ),
    _n(
        "DSC-14",
        _R,
        "stage",
        "缺口回补三通道（行数缺口 / 档期打卡 / 已知缺口台账）",
        "哪一类缺口由哪一条通道捞？通道自己不跑了谁会知道？",
        note_zh="三通道口径互不重叠：weekend_backfill（过去 7 天行数缺口）/ daily_backfill（当日全表缺口）/ catchup_guard（档期 vs 打卡对账，不看行数）。第 4 通道（事件自动回填）单列 DSC-14D 并已判死⇒行级状态=分面。catchup_guard 从 DSC-13 去重移归本环节（WB12-27）。",
        build_status="partial",
        wiring_status="wired_cron",
        slot_source="schedule",
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/catchup_guard.py",
        source_anchors=[
            "slot:weekend_backfill",
            "slot:daily_backfill",
            "slot:catchup_guard",
            "file:src/zephyr/data/backfill_checker.py",
            "file:src/zephyr/data/catchup_guard.py",
        ],
        store_refs=[
            {
                "artifact": "补跑台账",
                "location": "data/integrator_progress.db（键=被补任务原 task_id）",
                "key": "task_id",
                "retention": "常驻",
            },
            {
                "artifact": "缺口台账",
                "location": "src/zephyr/data/config/known_data_gaps.yaml",
                "key": "gap_id",
                "retention": "规则真源 YAML",
            },
        ],
        fallback=[
            {
                "kind": "catchup_bounded",
                "when": "单批补跑限量＋trading_day_only 顺延＋RUNNING 跳过防撞车",
                "residual": "补跑走 scheduler.run_task＝与被补任务同写手同表，合并前立刻按行数判据会飘（须 FINAL）",
            },
            {
                "kind": "no_channel_name",
                "when": "通道自身不留 progress 键（记在被补任务名下）",
                "residual": "通道健康度不可直接观测——只能从告警变多反推它不补了",
            },
        ],
        gap_refs=["DSC-GAP-RECDIFF"],
        task_family="三活通道 + 一死通道",
        facets=[
            {
                "leg_id": "weekend",
                "name_zh": "weekend_backfill 行数缺口腿",
                "status": "🔨",
                "evidence": ["05 簿 §2.1 分派行号在册；档期留痕按被补任务名记账，通道自身健康度不可直接观测"],
            },
            {
                "leg_id": "daily",
                "name_zh": "daily_backfill 当日缺口腿",
                "status": "🔨",
                "evidence": ["同上（17:00 档在册）"],
            },
            {
                "leg_id": "catchup",
                "name_zh": "catchup_guard 档期对账腿",
                "status": "🔨",
                "evidence": [
                    "本车道复跑 task_progress 末次 2026-09-25T01:24:20Z（=北京 09:24）PARTIAL rows=15",
                    "非声明的 05:30 档⇒自动档期留痕缺（批次4 停 09-21 的读数此后有推进，判词改、红不减）",
                ],
            },
            {
                "leg_id": "auto4",
                "name_zh": "第四通道（事件自动回填）",
                "status": "⬜",
                "evidence": ["死结论见 DSC-14D（零生产实例化＋无槽＋无分派分支）"],
            },
        ],
        gaps=[
            {
                "anchor": "slot:catchup_guard",
                "symptom": "stale_slot_run",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §2.2 ＋ 本车道复跑",
                "note_zh": "末次打卡 09:24 非 05:30 档；schedule.yaml 自述该槽被当成周末校准槽的过渡补丁——③ 兜 ① 的前提今天不成立",
            },
            {
                "anchor": "status:open",
                "symptom": "unresolved_gaps",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §4.2",
                "note_zh": "known_data_gaps 仍有 open/monitoring 未了账，与漏跑清单交叉才是缺口 vs 坏数据判据分界",
            },
        ],
        evidence=[f"{BOOK_DIR}/05_对账修复六环.md §2.1/§2.2（三通道分派行号＋台账读数）"],
    ),
    _n(
        "DSC-14D",
        _R,
        "channel",
        "第四通道：事件自动回填（auto_backfiller）——建好未接线",
        "新因子/公式升级/源修复之后的历史重刷，今天由谁触发？",
        note_zh="设计=按日期分片规划回填＋10% 随机抽样验证＋更新血缘并触发 auto-retrain；实测=既不在任何调度分派、也不在任何事件订阅，只有包级 re-export 与单测。骨架 §1 D12-14 的第 4 腿即此件（分面 ⬜）。",
        build_status="pending",
        wiring_status="unwired_exempt_bypass",
        slot_source="none",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        module_ref="src/zephyr/data/auto_backfiller.py",
        source_anchors=[
            "file:src/zephyr/data/auto_backfiller.py",
            "file:docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml",
        ],
        store_refs=[
            {
                "artifact": "豁免登记",
                "location": "wiring_registry.yaml CAND-DAT-014（wiring_class: pure_library / wiring_status: exempt）",
                "key": "candidate_id",
                "retention": "注册表在册",
            }
        ],
        fallback=[
            {
                "kind": "fall_back_manual",
                "when": "三类事件语义回填全部落回 DSC-16 的手动/留盘脚本",
                "residual": "人记得才补；且回填通过后的血缘前推与 auto-retrain 断链＝因子重刷后模型仍是旧的",
            }
        ],
        gaps=[
            {
                "anchor": "file:src/zephyr/data/auto_backfiller.py",
                "symptom": "unwired",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §2.3",
                "note_zh": "死结论：零生产实例化（AutoBackfiller( 只出现在测试）＋特殊槽全集无此分支＋schedule.yaml 无对应槽",
            },
            {
                "anchor": "file:docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml",
                "symptom": "gate_bypassed",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §2.3 第 3 条",
                "note_zh": "以 pure_library/exempt 分类合法绕过接线门＝建好未接线长期隐身的机制因",
            },
            {
                "anchor": "file:docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md",
                "symptom": "doc_contradiction",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §2.3 第 4 条",
                "note_zh": "SOP 把它写成常态在岗，与代码/注册表三说不一＝文档矛盾=事故型，禁按文档标 ✅",
            },
        ],
        evidence=[f"{BOOK_DIR}/05_对账修复六环.md §2.3（四条可复跑证据链：grep/特殊槽全集/注册表/SOP）"],
    ),
    _n(
        "DSC-15",
        _R,
        "stage",
        "日终三账对账（回测 vs 模拟盘 L1/L2/L3）——未接线",
        "回测与柜台今天还对得上吗？——这一问目前无人问",
        note_zh="设计正确（L1 交易级、L2 持仓零容差、L3 PnL 0.1%、A/B/C 归因三分类、差异 append-only 落库）；实测未接线：15:40 槽在 schedule.yaml 挂着但 scheduler 无该槽分派分支、tasks.yaml 无同名任务、run_daily_reconciliation 零生产调用方（模块自述本模块不挂调度与 schedule 口径相反）。行级状态 ⬜（批次4 自 🔨 下调）。",
        build_status="pending",
        wiring_status="unwired_slot_hollow",
        slot_source="schedule",
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/trading/recon_runner.py",
        source_anchors=[
            "slot:eod_reconciliation",
            "file:src/zephyr/trading/recon_runner.py",
            "file:src/zephyr/ex_core/eod_reconciliation.py",
        ],
        data_refs=["table:reconciliation_differences"],
        store_refs=[
            {
                "artifact": "三账差异台账",
                "location": "governance.db:reconciliation_differences（append-only 仅 INSERT）",
                "key": "trade_date+recon_layer",
                "retention": "永久（实测 0 行）",
            }
        ],
        fallback=[
            {
                "kind": "silent_empty_slot",
                "when": "槽名无任务无分派 → 交常规 DAG 后跑 0 任务、静默返回成功",
                "residual": "R-021 假通道形态：槽位拼错一个字母＝永不触发且零报错（唯一拼写防线只覆盖 miniqmt/qmt_bridge 两类源）",
            },
            {
                "kind": "no_idempotency_key",
                "when": "差异表无 run_id/无 upsert",
                "residual": "接线后补跑同日会双计差异行，污染趋势统计",
            },
        ],
        gap_refs=["DSC-GAP-TERMINUS", "DSC-GAP-RECDIFF"],
        task_family="三账 diff（未接线）",
        gaps=[
            {
                "anchor": "slot:eod_reconciliation",
                "symptom": "unwired",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §3.3",
                "note_zh": "运行台账在结构上不存在（只有差异表、没有跑了几次/哪次全绿的 run 表）⇒不是拿不到日志，是无从取证",
            },
            {
                "anchor": "table:reconcile_execution_log",
                "symptom": "false_green_trap",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §3.3 第 4 条",
                "note_zh": "近亲名、本车道复跑 89,115 行且当天仍在写，但属图11 提交自愈环台账——按名字相似认领证据必假绿（列名集双向核对已入骨架 ★坑7）",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/05_对账修复六环.md §3.3（零调用方＋无分派分支＋0 行三项实测）",
            "本图 machine.scheduler_dispatch.slots_hollow（槽在、零任务、无分派分支，机械可判）",
        ],
    ),
    _n(
        "DSC-GAP-TERMINUS",
        _R,
        "gap",
        "缺口：域终点（数据达标 PASS）今天不可证",
        "这张图宣称的终点，凭哪一条读数成立？",
        note_zh="骨架 §0 门① 于批次4 改写：可证终点=归档清单（DSC-10B）＋任务级对账案卷（DSC-20）双实锚；对账 PASS 语义的唯一实现 DSC-15 未接线，故达标面今天由本缺口承担，不许冒充。red_reason 取 terminal 为主（unwired 为并发标，取一为主的终裁在总包）。",
        build_status="pending",
        wiring_status="unwired_slot_hollow",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="terminal",
        source_anchors=["slot:eod_reconciliation", "file:src/zephyr/trading/recon_runner.py"],
        store_refs=[
            {
                "artifact": "终点判据缺口登记",
                "location": f"{BOOK_DIR}/05_对账修复六环.md §末A OBS-WF-8",
                "key": "obs_id",
                "retention": "接线＋运行留痕补齐后本节点退役",
            }
        ],
        fallback=[
            {
                "kind": "substitute_terminal",
                "when": "以 DSC-10B archive_manifest / DSC-11 backup_log / DSC-17 cross_validation_log / DSC-20 案卷作留痕型终点",
                "residual": "四者只证明产出与检测发生过，不证明数据达标",
            }
        ],
        gaps=[
            {
                "anchor": "node:DSC-15",
                "symptom": "terminal_unprovable",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §末A OBS-WF-8",
                "note_zh": "图级问题非环节级问题：挂槽≠在跑须进封矿判据，否则图13 的 15:40 槽会以同形态被误标",
            }
        ],
        evidence=[
            f"{BOOK_DIR}/05_对账修复六环.md §末A OBS-WF-8（P0 上报）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §5-1（终点改写条款）",
        ],
    ),
    _n(
        "DSC-GAP-RECDIFF",
        _R,
        "gap",
        "等未产表：reconciliation_differences（消费方已按空表设计降级）",
        "一张 0 行的表被下游当成可信输入，这个降级设计本身该不该亮红？",
        note_zh="与 DSC-GAP-TERMINUS 同一根因、不同账面：终点不可证记在 TERMINUS，本节点记消费侧受损事实——backtest_backlog 判据 c 明写空表不阻断，即消费方已知晓并容忍永久为空。",
        build_status="pending",
        wiring_status="unwired_slot_hollow",
        slot_source="schedule",
        slot_refs=[],
        downstream_action="none",
        confidence="verified",
        verified_scope="structure",
        red_reason="unwired",
        source_anchors=[
            "file:src/zephyr/trading/recon_runner.py",
            "file:docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml",
        ],
        data_refs=["table:reconciliation_differences"],
        store_refs=[
            {
                "artifact": "三账差异表",
                "location": "governance.db:reconciliation_differences",
                "key": "trade_date+recon_layer",
                "retention": "永久（实测 0 行）",
            }
        ],
        gaps=[
            {
                "anchor": "table:reconciliation_differences",
                "symptom": "zero_rows",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/11_消费端需求反查.md §1-C/§4-N5",
                "note_zh": "本车道经 DatabaseService 治理库只读复跑 count=0；0 行不可读成全对，等价于从未跑过",
            }
        ],
        evidence=[f"{BOOK_DIR}/11_消费端需求反查.md §1-C（N5 加证）", "本车道 09-25 治理库只读复跑"],
    ),
    _n(
        "DSC-16",
        _R,
        "stage",
        "坏数据修复与回补器族（手动/留盘为主）",
        "发现的是缺口还是坏数据？修它有没有正门、正门在不在版本控制里？",
        note_zh="修复纪律四条（污染判据先行/FINAL 逐位验证/勿物理删事实走 valid_to·fact_close/并发写表先 claim）＋ RULE-DATA-OPS 三步验证；判重正门与修复配对方才闭环（判门缺陷见 DSC-GAP-DUPGUARD）。",
        build_status="partial",
        wiring_status="wired_manual",
        slot_source="manual",
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/c4_history_repair.py",
        source_anchors=[
            "file:scripts/data/repair_kline_degraded_pull.py",
            "file:src/zephyr/data/c4_history_repair.py",
            "file:src/zephyr/data/config/known_data_gaps.yaml",
        ],
        store_refs=[
            {
                "artifact": "缺口台账",
                "location": "src/zephyr/data/config/known_data_gaps.yaml",
                "key": "gap_id",
                "retention": "规则真源 YAML（三渠道实证不可恢复→转 accepted）",
            }
        ],
        fallback=[
            {
                "kind": "accept_gap",
                "when": "源侧永久消失的缺口三渠道实证后转 accepted，勿留悬账反复重试",
                "residual": "若误判可补→反复重试与配额/熔断互相打架",
            },
            {
                "kind": "manual_script",
                "when": "事件回填通道死（DSC-14D）→ 全部走一次性脚本",
                "residual": "零隐式范围是脚本侧纪律，无门禁兜底",
            },
        ],
        task_family="政策 §3 回补器七件 + 修复两件",
        gaps=[
            {
                "anchor": "file:scripts/data/backfill_tick_depth5.py",
                "symptom": "untracked",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §4.1",
                "note_zh": "政策点名的 7 个回补器中 4 个不在 VCS（仅主区磁盘）⇒任何 worktree/新克隆 ls 不到；未纳管即无 INVARIANTS/无 gate/无测试，改数据行为不可审",
            },
            {
                "anchor": "file:scripts/ch/c4_history_repair.py",
                "symptom": "path_ghost",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §末A OBS-WF-12",
                "note_zh": "骨架原路径写错，真身在 src/zephyr/data/（本图已按真身挂锚）",
            },
        ],
        evidence=[f"{BOOK_DIR}/05_对账修复六环.md §4（逐个纳管态实测＋缺口台账 status 分布）"],
    ),
    _n(
        "DSC-17",
        _R,
        "stage",
        "一致预期管线双向互验（自建聚合 vs 同花顺快照）",
        "两个独立真源互相打不打脸？用哪一列判它新鲜？",
        note_zh="检查族＝秩相关/新鲜度/结构断言/PIT 零修正率；23:30 交易日档期由特殊槽分派；本图唯一能用产出表新鲜度当执行见证的检核器（骨架 ⬜ 已被实测改判 ✅：表在位、非空、末写与 cron 精确吻合）。",
        build_status="built",
        wiring_status="wired_special_branch",
        slot_source="schedule",
        downstream_action="detect_only",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/consensus_crosscheck.py",
        source_anchors=[
            "slot:consensus_crosscheck",
            _tbl("market_cross_validation_log"),
            "file:src/zephyr/data/consensus_crosscheck.py",
        ],
        data_refs=[_tbl("market_cross_validation_log")],
        store_refs=[
            {
                "artifact": "互验台账",
                "location": _tbl("market_cross_validation_log"),
                "key": "check_date+metric+symbol",
                "retention": "随 CH 表",
            }
        ],
        fallback=[
            {
                "kind": "disabled_flag",
                "when": "服务总闸 data/runtime/consensus_crosscheck.disabled",
                "residual": "关闸即整环停，无独立健康度指标",
            }
        ],
        gap_refs=["DSC-GAP-CONSENSUSCHAIN"],
        task_family="互验四检查族",
        gaps=[
            {
                "anchor": _tbl("market_cross_validation_log"),
                "symptom": "epoch_sentinel_column",
                "measured_on": "2026-09-21",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §5.3",
                "note_zh": "check_time 自 09-21 起恒为 epoch⇒用 max(check_time) 判新鲜必误报停更；新鲜度口径必须钉在 check_date",
            },
            {
                "anchor": "slot:consensus_crosscheck",
                "symptom": "coverage_shrink",
                "measured_on": "2026-09-23",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §5.3 / §末B P-7",
                "note_zh": "按日行量从 ~27 项缩到 4 项，是有意收窄还是配置漂移实测不可判；与 DSC-08 预期腿停更交叉是本图最有价值的待查线索",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/05_对账修复六环.md §5.1（列名实测＋行集读数）",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §2（三验复跑）",
        ],
        freshness_evidence=_FRESHNESS["DSC-17"],
    ),
    _n(
        "DSC-18",
        _R,
        "stage",
        "CH 存储维护 OPTIMIZE / 合并（周度 OS 任务）",
        "合并真的发生了吗？失败 0 算不算效果证据？",
        note_zh="存在理由＝ReplacingMergeTree 去重是异步的，本工具是三防线（读侧 FINAL / 归档 FINAL 导出 / 物理去重）的最后一道；表清单自发现，无硬编码。判词=已运行 OS 周任务、登记侧滞后、计数不可信。",
        build_status="partial",
        wiring_status="running_unregistered",
        slot_source="schtasks",
        slot_refs=["ZephyrAlpha-CH-OptimizeMerge-Weekly"],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="scripts/ch/optimize_merge.py",
        source_anchors=[
            "file:scripts/ch/optimize_merge.py",
            "file:config/resource_profile_registry.yaml",
            _tbl("market_tick"),
        ],
        data_refs=[_tbl("market_tick")],
        store_refs=[
            {
                "artifact": "维护日志",
                "location": "logs/ch_optimize_merge_weekly.log（UTF-16LE）",
                "key": "run_date",
                "retention": "追加式日志",
            }
        ],
        fallback=[
            {
                "kind": "empty_string_as_success",
                "when": "ch_reader.query 失败返回空串不抛 → 记 optimize 完成 (0.0s)",
                "residual": "同帧日志可见 HTTP 500 与成功并存；[ERROR_CONTRACT] 承诺的 exit 1 兑现不了＝写/维护侧假成功，比读侧假绿更危险",
            },
            {
                "kind": "outside_resource_gate",
                "when": "OS 计划任务不进 APScheduler 的 exclusive_group 判定",
                "residual": "与 weekend_calibration 同窗但互不可见＝资源闸对 OS 任务盲区",
            },
        ],
        gap_refs=["DSC-GAP-REPLAY"],
        task_family="周度维护（OS 侧）",
        gaps=[
            {
                "anchor": "task:ops_ch_optimize_merge_weekly",
                "symptom": "unregistered_running",
                "measured_on": "2026-09-20",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §6.2",
                "note_zh": "开工了但没登记：本车道独立复跑 schtasks LastRun=09-20 03:30:00 Result=0 NextRun=09-27 03:30，登记册仍 planned/manual/samples=0（samples 零是测量腿未接，不是没跑）",
            },
            {
                "anchor": "file:scripts/ch/optimize_merge.py:138",
                "symptom": "false_success",
                "measured_on": "2026-09-20",
                "pointer": f"{BOOK_DIR}/05_对账修复六环.md §6.3",
                "note_zh": "失败 0 不可信：唯一可信效果证据=合并前后逐位比对或 system.parts 冗余率复测；周批 659 分区不足以覆盖事故分区",
            },
        ],
        evidence=[f"{BOOK_DIR}/05_对账修复六环.md §6.2/§6.3", "本车道 09-25 独立复跑 schtasks"],
    ),
    _n(
        "DSC-19",
        _R,
        "stage",
        "破损 part 自愈探测器（CHECKSUM 隔离环，进程内常驻）",
        "部件级损坏被谁抓住？抓住之后是谁动手、动了有没有留痕？",
        note_zh="调度器进程内常驻守护线程：每 5min 扫 system.text_log 的 CHECKSUM_DOESNT_MATCH → STOP MERGES → DETACH PART → 审计 jsonl。全仓唯一具备 DETACH 隔离能力的环节。批次4 新增行：它是入库段的自愈腿、也是对账修复段的反馈环，不产数故永不 ✅。",
        build_status="partial",
        wiring_status="wired_stream",
        slot_source="none",
        slot_refs=[],
        downstream_action="auto_remediate",
        confidence="verified",
        verified_scope="structure",
        module_ref="src/zephyr/data/scheduler.py",
        source_anchors=["file:src/zephyr/data/scheduler.py", "file:src/zephyr/data/ch_writer.py"],
        store_refs=[
            {
                "artifact": "隔离审计件",
                "location": "data/local_fallback/corrupted_parts_audit.jsonl",
                "key": "table+part",
                "retention": "append（本车道复跑：文件不存在）",
            }
        ],
        fallback=[
            {
                "kind": "detach_isolate",
                "when": "CHECKSUM 命中 → DETACH PART 隔离坏件保读路径",
                "residual": "检测口径只覆盖 CHECKSUM_DOESNT_MATCH，抓不到装载期 0-byte parts 族（本役 09-25 事故即其漏网实例）",
            }
        ],
        gap_refs=["DSC-GAP-MACRO"],
        task_family="常驻探测器（零档期）",
        invalidation="若扩口径条款（0 字节部件族 + 装载期错误码）落地并首次留痕，本格状态判词应重估",
        gaps=[
            {
                "anchor": "file:src/zephyr/data/scheduler.py:1081",
                "symptom": "detector_scope_gap",
                "measured_on": "2026-09-25",
                "pointer": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.2",
                "note_zh": "现役事故不在其检测口径内；且事故同时打掉它判新鲜度所依赖之外的 parts 面——零触发不等于零风险",
            },
            {
                "anchor": "file:data/local_fallback/corrupted_parts_audit.jsonl",
                "symptom": "zero_fire_no_audit",
                "measured_on": "2026-09-25",
                "pointer": "本车道只读复跑（主区该路径不存在）",
                "note_zh": "自 07-16 上线零触发实证；退役资格按内收判据季度审（零触发但有消费面＝不退役，消费=40 表读路径可用性前提）",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.2/§5-2",
            f"{BOOK_DIR}/11_消费端需求反查.md §2-2（双锚 grep 实证）",
        ],
    ),
    _n(
        "DSC-20",
        _R,
        "stage",
        "任务级对账（档期应跑集合 vs task_runs 打卡集合差四计数）",
        "今天该跑的有没有真跑？漏的那几个是谁？后果落在哪张表上？",
        note_zh="integrity_checker 的第 4 类检核独立成行：产出应跑/成功/漏跑/失败四计数案卷，与逐表行数/新鲜度（DSC-13）和补执行动作（DSC-14）是三个正交完备性轴。全图唯一能机械证明漏跑真实存在的机生件；下游=catchup_guard 基准 + CLI status + 告警件三族。批次4 新增行。",
        build_status="built",
        wiring_status="wired_special_branch",
        slot_source="schedule",
        downstream_action="alert_only",
        confidence="verified",
        verified_scope="production",
        module_ref="src/zephyr/data/integrity_checker.py",
        source_anchors=[
            "slot:integrity_check",
            "file:src/zephyr/data/progress_store.py",
            "file:src/zephyr/data/integrity_checker.py",
        ],
        store_refs=[
            {
                "artifact": "任务级对账案卷",
                "location": "data/failures/<ds>_integrity_check_task_reconcile_<hhmmss>.json",
                "key": "yyyymmdd",
                "retention": "按日落盘（无销项字段）",
            },
            {
                "artifact": "打卡台账",
                "location": "data/integrator_progress.db task_runs",
                "key": "run_id/task_id",
                "retention": "常驻",
            },
        ],
        fallback=[
            {
                "kind": "alert_only",
                "when": "四计数差 > 0 即产 ERROR 级案卷",
                "residual": "无人消解即无人知晓；补跑通道只兜档期类漏跑（且 catchup 自身未落 05:30 档）",
            }
        ],
        gap_refs=["DSC-GAP-RECDIFF"],
        task_family="第 4 检核（档期执行完整性）",
        gaps=[
            {
                "anchor": "slot:integrity_check",
                "symptom": "slot_run_missing",
                "measured_on": "2026-09-25",
                "pointer": "本车道 09-25T15:2xZ 复跑（data/failures 与 task_progress 双向）",
                "note_zh": "09-21~24 四日案卷连产为在册证，但当日 23:00 档在复跑时点未落地⇒按日连产读数带一日缺口，禁写成全绿",
            },
            {
                "anchor": "task:consensus_daily_build",
                "symptom": "detection_no_repair",
                "measured_on": "2026-09-24",
                "pointer": f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.3（09-24 件读数 183/149/19/15）",
                "note_zh": "漏跑清单含 consensus_daily_build/financial_derived_build/kline_sector_*——本行正是这些改判的下修依据，无此行则改判无处引证",
            },
        ],
        evidence=[
            f"{BOOK_DIR}/05_对账修复六环.md §1.2/§末 OBS-WF-13",
            f"{BOOK_DIR}/12_扩行提案与封顶重宣.md §1.3（三问裁定）",
            "本车道 09-25 只读复跑：案卷四件齐 + task_runs 188,702 行",
        ],
        freshness_evidence=_FRESHNESS["DSC-20"],
    ),
]
_HUMAN["nodes"] = _NODES

_EDGES: list[dict[str, Any]] = [
    {"from": "DSC-SRC", "to": "DSC-01", "kind": "data_flow", "note_zh": "盘后批式源"},
    {"from": "DSC-SRC", "to": "DSC-02", "kind": "data_flow", "note_zh": "盘中/竞价流"},
    {"from": "DSC-SRC", "to": "DSC-03", "kind": "data_flow", "note_zh": "事件/另类流"},
    {"from": "DSC-01", "to": "DSC-04", "kind": "data_flow", "note_zh": "normalized rows→写通道"},
    {"from": "DSC-02", "to": "DSC-05", "kind": "data_flow", "note_zh": "tick 段落 WAL"},
    {"from": "DSC-02", "to": "DSC-04", "kind": "data_flow", "note_zh": "盘中快照批量写"},
    {"from": "DSC-03", "to": "DSC-04", "kind": "data_flow", "note_zh": "新闻/宏观攒批写"},
    {"from": "DSC-04", "to": "DSC-FB", "kind": "degrade", "note_zh": "HTTP 废→本地 TSV 落盘（两条入边之一）"},
    {"from": "DSC-05", "to": "DSC-FB", "kind": "degrade", "note_zh": "WAL 段复用同一落盘袋（两条入边之二，WB12-26）"},
    {"from": "DSC-FB", "to": "DSC-04", "kind": "control", "note_zh": "replay_batch 回灌（同段不触发反向边规则）"},
    {"from": "DSC-04", "to": "DSC-06", "kind": "data_flow", "note_zh": "写入后幂等/判重口径生效"},
    {"from": "DSC-05", "to": "DSC-06", "kind": "data_flow", "note_zh": "tick 幂等靠引擎"},
    {"from": "DSC-GAP-DUPGUARD", "to": "DSC-06", "kind": "gap", "note_zh": "准入闸缺陷挂在判重环节上"},
    {"from": "DSC-GAP-REPLAY", "to": "DSC-FB", "kind": "gap", "note_zh": "回灌排空不可证挂在汇聚节点"},
    {"from": "DSC-GAP-L2TICK", "to": "DSC-02", "kind": "gap", "note_zh": "双 0 行断供挂在盘中采集腿"},
    {"from": "DSC-GAP-MACRO", "to": "DSC-03", "kind": "gap", "note_zh": "运行事故挂在事件采集腿"},
    {"from": "DSC-GAP-NEWSGHOST", "to": "DSC-03", "kind": "gap", "note_zh": "幽灵库名指向真身所在采集环节（防再引）"},
    {"from": "DSC-06", "to": "DSC-07", "kind": "data_flow", "note_zh": "原始表就绪→衍生"},
    {"from": "DSC-06", "to": "DSC-08", "kind": "data_flow", "note_zh": "三大报表/研报就绪→派生"},
    {"from": "DSC-06", "to": "DSC-09", "kind": "data_flow", "note_zh": "行情/打板就绪→派生"},
    {
        "from": "DSC-03",
        "to": "DSC-08",
        "kind": "data_flow",
        "note_zh": "research_report→consensus_daily_build 上游边（断链见 gap）",
    },
    {"from": "DSC-GAP-CONSENSUSCHAIN", "to": "DSC-08", "kind": "gap", "note_zh": "预期链停摆挂在此环节"},
    {"from": "DSC-07", "to": "DSC-HA", "kind": "handoff_out", "note_zh": "出图12 域（交图13/图9）"},
    {"from": "DSC-08", "to": "DSC-HA", "kind": "handoff_out", "note_zh": "预期因子地基"},
    {"from": "DSC-09", "to": "DSC-HA", "kind": "handoff_out", "note_zh": "L2 门/plan_engine 供料"},
    {
        "from": "DSC-21",
        "to": "DSC-HA",
        "kind": "handoff_out",
        "note_zh": "进程内派生表同样出图被消费（11 卷 174 点分母）",
    },
    {"from": "DSC-GAP-NAV", "to": "DSC-21", "kind": "gap", "note_zh": "等未产表挂在本环节（写器零接线）"},
    {"from": "DSC-GAP-EXECEP", "to": "DSC-21", "kind": "gap", "note_zh": "等未产表挂在本环节（实盘链未接）"},
    {"from": "DSC-GAP-FFVAL", "to": "DSC-21", "kind": "gap", "note_zh": "等未产表挂在本环节（DDL 未 apply）"},
    {"from": "DSC-GAP-FFSIG", "to": "DSC-21", "kind": "gap", "note_zh": "等未产表挂在本环节（未建表）"},
    {"from": "DSC-GAP-RECDIFF", "to": "DSC-15", "kind": "gap", "note_zh": "消费侧受损挂在未接线对账环节"},
    {"from": "DSC-06", "to": "DSC-13", "kind": "data_flow", "note_zh": "被检对象=在库数据"},
    {
        "from": "DSC-13",
        "to": "DSC-20",
        "kind": "control",
        "note_zh": "同宿主进程两轴检核：表数据完整性 vs 档期执行完整性",
    },
    {
        "from": "DSC-20",
        "to": "DSC-14",
        "kind": "control",
        "note_zh": "漏跑清单=catchup 的基准输入（批次4 移交后唯一路径）",
    },
    {"from": "DSC-14", "to": "DSC-16", "kind": "control", "note_zh": "补不回的转修复/转 accepted"},
    {
        "from": "DSC-14D",
        "to": "DSC-14",
        "kind": "gap",
        "status": "unwired",
        "note_zh": "事件回填通道设计上归此、实测无触发源⇒边不成立",
    },
    {"from": "DSC-16", "to": "DSC-18", "kind": "control", "note_zh": "修复后 OPTIMIZE 逐位验证"},
    {"from": "DSC-13", "to": "DSC-17", "kind": "control", "note_zh": "只检测族协同"},
    {"from": "DSC-15", "to": "DSC-GAP-TERMINUS", "kind": "gap", "note_zh": "终点语义由缺口节点承担"},
    {"from": "DSC-19", "to": "DSC-06", "kind": "gap", "note_zh": "入库自愈腿边注：探测器保的是读/判口径可用性"},
    {"from": "DSC-04", "to": "DSC-HB", "kind": "handoff_out", "note_zh": "热库分区交冷备"},
    {"from": "DSC-06", "to": "DSC-HB", "kind": "handoff_out", "note_zh": "幂等就绪表进不可逆段唯一通道"},
    {"from": "DSC-HB", "to": "DSC-10A", "kind": "data_flow", "note_zh": "人工批量归档入口"},
    {"from": "DSC-HB", "to": "DSC-10B", "kind": "data_flow", "note_zh": "事件触发滚动归档入口"},
    {"from": "DSC-HB", "to": "DSC-11", "kind": "data_flow", "note_zh": "增量备份链"},
    {
        "from": "DSC-12",
        "to": "DSC-10B",
        "kind": "control",
        "note_zh": "契约参数（分层线/批限量/excluded_tables）驱动执行——决策是执行的输入节点，非并列环节",
    },
    {
        "from": "DSC-11",
        "to": "DSC-10B",
        "kind": "trigger",
        "note_zh": "备份成功事件→滚动归档（五阀，backup.ps1 STAGE 4b）",
    },
    {"from": "DSC-GAP-MIRROR", "to": "DSC-11", "kind": "gap", "note_zh": "P0 防护失效挂在灾备环节"},
    {"from": "DSC-GAP-CODEBACKUP", "to": "DSC-11", "kind": "gap", "note_zh": "今晨代码快照腿失败挂灾备环节"},
    {"from": "DSC-10A", "to": "DSC-HC", "kind": "handoff_out", "note_zh": "冷档→恢复侧"},
    {"from": "DSC-10B", "to": "DSC-HC", "kind": "handoff_out", "note_zh": "滚动归档清单→恢复侧"},
    {"from": "DSC-11", "to": "DSC-HC", "kind": "handoff_out", "note_zh": "备份件→恢复侧"},
    {
        "from": "DSC-GAP-ARCHIVE-AUDIT",
        "to": "DSC-HC",
        "kind": "gap",
        "note_zh": "零抽检/从未端到端 restore 挂在恢复交接面",
    },
    {"from": "DSC-18", "to": "DSC-06", "kind": "feedback", "note_zh": "合并效果回判重口径（未合并冗余是同源病灶两端）"},
    {"from": "DSC-14", "to": "DSC-01", "kind": "feedback", "note_zh": "补跑=重放盘后采集任务"},
    {"from": "DSC-14", "to": "DSC-02", "kind": "feedback", "note_zh": "补跑=重放盘中任务"},
    {"from": "DSC-14", "to": "DSC-03", "kind": "feedback", "note_zh": "补跑=重放事件档期任务"},
    {"from": "DSC-16", "to": "DSC-01", "kind": "feedback", "note_zh": "修复回灌后由采集段重产"},
    {"from": "DSC-16", "to": "DSC-14", "kind": "feedback", "note_zh": "修复结论回写缺口台账，反哺回补判据"},
    {"from": "DSC-19", "to": "DSC-16", "kind": "feedback", "note_zh": "DETACH 隔离=修复段的兜底动作（自愈反馈环）"},
    {
        "from": "DSC-13",
        "to": "DSC-01",
        "kind": "feedback",
        "note_zh": "告警面反馈源侧健康与停源决策（downstream_action=detect_only⇒无自动闭环）",
    },
    {"from": "DSC-20", "to": "DSC-13", "kind": "feedback", "note_zh": "四计数回写巡检台账（同宿主进程，结果互标）"},
]
_HUMAN["edges"] = _EDGES

_FEEDBACK: list[dict[str, Any]] = [
    {"from": "DSC-14", "to": "DSC-01", "note_zh": "缺口回补→重放采集（行数缺口/档期漏跑两类口径各自捞）"},
    {"from": "DSC-14", "to": "DSC-02", "note_zh": "盘中腿缺口同样由补跑通道重放"},
    {"from": "DSC-14", "to": "DSC-03", "note_zh": "事件档期补跑"},
    {"from": "DSC-16", "to": "DSC-01", "note_zh": "坏数据修复后回采集段重产，结论回写 known_data_gaps.yaml"},
    {"from": "DSC-16", "to": "DSC-14", "note_zh": "修复与回补互为替代（事件通道一旦接线，手动重刷降为兜底）"},
    {"from": "DSC-13", "to": "DSC-01", "note_zh": "哨兵告警回采源侧决策；downstream_action=detect_only⇒无自动闭环"},
    {"from": "DSC-18", "to": "DSC-06", "note_zh": "合并效果回判重口径（读侧 FINAL / 归档 FINAL / 物理去重三防线）"},
    {"from": "DSC-19", "to": "DSC-16", "note_zh": "探测器 DETACH 隔离回修复段（批次4 新增反馈环）"},
    {
        "from": "DSC-19",
        "to": "DSC-06",
        "note_zh": "自愈腿回读/判口径可用性：隔离坏 part 是为让 FINAL/FINAL 双版读数不挂起（批次4 新增）",
    },
    {"from": "DSC-20", "to": "DSC-13", "note_zh": "任务级四计数回巡检台账（批次4 新增，两轴互补不可互替）"},
]
_HUMAN["feedback_loops"] = _FEEDBACK
# ══════════════════════════════════════════════════════════════════════════
# 机生层
# ══════════════════════════════════════════════════════════════════════════
_HUMAN_KEYS = (
    "schema_version",
    "map_id",
    "name_zh",
    "nickname",
    "ttl",
    "effective_from",
    "ssot_note_zh",
    "laws",
    "boundary",
    "segments",
    "nodes",
    "edges",
    "feedback_loops",
)

# scheduler 分派面：`schedule_name == "<槽名>"` 与 `schedule_name in ("a", "b")` 两种写法
_DISPATCH_EQ_RE = re.compile(r'schedule_name\s*==\s*"([a-z0-9_]+)"')
_DISPATCH_IN_RE = re.compile(r"schedule_name\s+in\s+\(([^)]*)\)")
_DISPATCH_IN_ITEM_RE = re.compile(r'"([a-z0-9_]+)"')
# 骨架 §1 状态格：编号 | 环节名 | 段 | 状态（首字符=行级符号 ✅/🔨/⬜ 或 `分面`）
_SKELETON_ROW_RE = re.compile(r"^\|\s*(D12-\d{2}[ab]?)\s*\|([^|]*)\|([^|]*)\|\s*([✅🔨⬜]|分面)", re.M)


def _load_yaml(path: Path) -> Any:
    """读 YAML 真源；失败即抛（禁静默产半图）。"""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def scan_tasks(root: Path) -> dict[str, Any]:
    """扫 tasks.yaml：任务全集/源分布/韧性配置/依赖 DAG 面。"""
    tasks = _load_yaml(root / TASKS_YAML_REL)["tasks"]
    ids = [t.get("task_id") for t in tasks]
    dup_ids = sorted({i for i in ids if ids.count(i) > 1})
    slot_of = {t.get("task_id"): t.get("schedule") for t in tasks}
    edges = [(t.get("task_id"), d) for t in tasks for d in (t.get("dependencies") or [])]
    tables = sorted({t["table"] for t in tasks if t.get("table")})
    return {
        "path": TASKS_YAML_REL,
        "tasks_total": len(tasks),
        "unique_task_ids": len(set(ids)),
        "duplicate_task_ids": dup_ids,
        "distinct_sources": len({t.get("source") for t in tasks}),
        "distinct_target_tables": len(tables),
        "target_tables": tables,
        "incremental_true": sum(1 for t in tasks if t.get("incremental") is True),
        "fallback_nonempty": sum(1 for t in tasks if t.get("fallback_sources")),
        "schedule_disabled": sum(1 for t in tasks if t.get("schedule") == "disabled"),
        "with_date_col": sum(1 for t in tasks if t.get("date_col")),
        "tasks_with_buffer": sum(1 for t in tasks if t.get("buffer_max_seconds")),
        "dep_edges": len(edges),
        "tasks_with_deps": sum(1 for t in tasks if t.get("dependencies")),
        "dep_edges_cross_slot": sum(1 for a, _b in edges if slot_of.get(_b) != slot_of.get(a)),
        "per_source_task_counts": _count(tasks, "source"),
        "per_slot_task_counts": _count(tasks, "schedule"),
    }


def _count(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    """按字段计数的稳定序版本（按计数降序、同数按名升序，保证幂等）。"""
    acc: dict[str, int] = {}
    for r in rows:
        val = r.get(key)
        if val is None:
            continue
        acc[str(val)] = acc.get(str(val), 0) + 1
    return {k: v for k, v in sorted(acc.items(), key=lambda kv: (-kv[1], kv[0]))}


def scan_schedule(root: Path) -> dict[str, Any]:
    """扫 schedule.yaml：cron 槽全集/执行器池/"一任务只属一槽"匹配面（正反两向）。"""
    sched = _load_yaml(root / SCHEDULE_YAML_REL)["schedules"]
    task_slots = set(scan_tasks(root)["per_slot_task_counts"])
    slot_names = sorted(sched)
    return {
        "path": SCHEDULE_YAML_REL,
        "slots_total": len(slot_names),
        "slots": slot_names,
        "executors": _count(list(sched.values()), "executor"),
        "slots_without_tasks": sorted(s for s in slot_names if s not in task_slots),
        "task_slots_unmatched": sorted(task_slots - set(slot_names)),
    }


def scan_scheduler_dispatch(root: Path) -> dict[str, Any]:
    """扫 scheduler.py 分派面——判「挂槽≠在跑」的机械尺（本图最硬的一族结论由此来）。"""
    text = (root / SCHEDULER_PY_REL).read_text(encoding="utf-8", errors="replace")
    dispatched = set(_DISPATCH_EQ_RE.findall(text))
    for grp in _DISPATCH_IN_RE.findall(text):
        dispatched.update(_DISPATCH_IN_ITEM_RE.findall(grp))
    slots = scan_schedule(root)
    task_slots = set(scan_tasks(root)["per_slot_task_counts"])
    hollow = sorted(s for s in slots["slots"] if s not in task_slots and s not in dispatched)
    return {"path": SCHEDULER_PY_REL, "dispatched_slots": sorted(dispatched), "slots_hollow": hollow}


def scan_asset_registry(root: Path) -> dict[str, Any]:
    """扫 data_asset_registry：declared entry_counts vs 实际列表长度（静态清单漂移尺）。"""
    doc = _load_yaml(root / ASSET_REGISTRY_REL)
    declared = {k: int(v) for k, v in (doc.get("entry_counts") or {}).items()}
    actual = {k: len(doc.get(k) or []) for k in ("sources", "datasets", "jobs")}
    return {
        "path": ASSET_REGISTRY_REL,
        "declared": declared,
        "actual": actual,
        "drift": {k: actual[k] - declared.get(k, 0) for k in actual if declared.get(k) != actual[k]},
    }


def scan_executors(root: Path) -> dict[str, Any]:
    """五段执行体文件实存性（含退役/未接线件的在盘证据——存在≠在岗，在岗判据在节点字段）。"""
    out: dict[str, dict[str, Any]] = {}
    for node_id, files in sorted(_EXECUTOR_FILES.items()):
        entries = []
        for rel in files:
            p = root / rel
            entries.append(
                {"path": rel, "exists": p.exists(), "label": get_module_name_bilingual(rel) if p.exists() else ""}
            )
        out[node_id] = {
            "executors": entries,
            "present": sum(1 for e in entries if e["exists"]),
            "missing": [e["path"] for e in entries if not e["exists"]],
        }
    return out


def scan_skeleton_status(root: Path) -> dict[str, str]:
    """骨架 §1 状态列实扫——verified_scope 的**唯一**外部对照物（同一张表同一个列，两侧不各自漂移）。

    返回 {node_id: "✅"|"🔨"|"⬜"|"分面"}。骨架不可读/表形变更 ⇒ 返回空表，调用侧降 warn。
    """
    p = root / SKELETON_REL
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    parts = text.split("## §1 环节全集", 1)
    if len(parts) != 2:
        return {}
    body = parts[1].split("## §2", 1)[0]
    out: dict[str, str] = {}
    for m in _SKELETON_ROW_RE.finditer(body):
        node_id = "DSC-" + m.group(1).split("-", 1)[1].upper()
        out[node_id] = m.group(4)
    return out


def _internal_task_ids(tasks_yaml: list[dict[str, Any]]) -> list[str]:
    """internal 派生任务全集（标识符，非正文）——衍生段节点的反查锚。"""
    return sorted({t["task_id"] for t in tasks_yaml if t.get("source") == "internal"})


def _process_in_product_ids(root: Path) -> dict[str, Any]:
    """第四枚举源=任务表外进程内写手（D12-21 的机械尺）：六表在 tasks.yaml 的命中数。"""
    text = (root / TASKS_YAML_REL).read_text(encoding="utf-8", errors="replace")
    wanted = [
        "regime_snapshot_history",
        "strategy_screen",
        "account_nav_daily",
        "execution_report",
        "factor_feature_value",
        "factor_signal",
    ]
    return {
        "tables": {t: len(re.findall(rf"\b{t}\b", text)) for t in wanted},
        "note_zh": "命中数全 0 ⇒ 该批表的生产者不在 tasks.yaml 面内（DSC-21 立行的机械尺）",
    }


def _canonicalize(node: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """existing 节点的 L0/L1 统一名迁移：旧别名一律丢弃并 WARN（内容以统一名在 _HUMAN 承载）。"""
    legacy = (
        "semantics_zh",
        "mech_note_zh",
        "clock_semantics_zh",
        "degradation",
        "miss_fallback_zh",
        "silent_failover",
        "data_anchors",
        "detection_only",
        "design_refs",
        "doc_ref",
    )
    dropped = [k for k in legacy if k in node]
    clean = {k: v for k, v in node.items() if k not in legacy}
    return clean, dropped


def build_document(root: Path, as_of: str | None) -> dict[str, Any]:
    """合成图：人工层 existing-wins + 机生层全量重建（含双轴与总线号的机生推导）。"""
    tasks = scan_tasks(root)
    schedule = scan_schedule(root)
    dispatch = scan_scheduler_dispatch(root)
    registry = scan_asset_registry(root)
    executors = scan_executors(root)
    skeleton_status = scan_skeleton_status(root)
    module_index = scan_module_id_index(root)
    in_product = _process_in_product_ids(root)
    internal_ids = _internal_task_ids(_load_yaml(root / TASKS_YAML_REL)["tasks"])

    out_path = root / OUTPUT_REL
    existing: dict[str, Any] = {}
    dropped_legacy: dict[str, list[str]] = {}
    schema_migrated: str | None = None
    if out_path.exists():
        loaded = _load_yaml(out_path)
        if isinstance(loaded, dict):
            # 跨 schema 版本不做 existing-wins：L0/L1 统一名与双轴键以本件 _HUMAN 为准
            # （盘上旧键 semantics_zh/degradation/data_anchors 与旧 edges/laws 若被保留，
            #   CV-L0/CV-DUAL 必红且是"生成器与图脱节"的静默分叉）。同版本内仍 existing-wins。
            if str(loaded.get("schema_version")) != str(_HUMAN["schema_version"]):
                schema_migrated = f"{loaded.get('schema_version')}→{_HUMAN['schema_version']}"
            else:
                existing = loaded

    def human(key: str) -> Any:
        return existing[key] if key in existing else _HUMAN[key]

    defaults_by_id = {n["node_id"]: n for n in _HUMAN["nodes"]}
    raw_existing = [n for n in human("nodes") if isinstance(n, dict)]
    existing_by_id: dict[str, dict[str, Any]] = {}
    for n in raw_existing:
        clean, dropped = _canonicalize(n)
        nid = clean.get("node_id")
        if isinstance(nid, str) and dropped:
            dropped_legacy[nid] = dropped
        existing_by_id[nid] = clean
    # 盘上有、契约无的历史节点＝已随批次4 拆行/改画法退役（如 DSC-10→DSC-10A/10B），
    # 一律丢弃并记账——留着就是伪环节（禁"契约外 stage 节点"混进图）
    retired = sorted(i for i in existing_by_id if i not in defaults_by_id and i not in NODE_ORDER)
    order = [n["node_id"] for n in _HUMAN["nodes"]] + [
        i for i in existing_by_id if i not in defaults_by_id and i in NODE_ORDER
    ]
    nodes: list[dict[str, Any]] = []
    for nid in order:
        default_node = defaults_by_id.get(nid)
        existing_node = existing_by_id.get(nid)
        if default_node is None:
            base = dict(existing_node or {})
        elif existing_node is None:
            base = dict(default_node)
        else:
            # 逐键合并=生成器新增键会落地、已存在键以盘上为准（existing-wins 只到键级）
            base = {**default_node, **existing_node}
            base["node_id"] = nid
        # 双轴与总线号一律由真源推导，existing-wins 不得覆盖（否则人工层可随手改出谎）
        base["module_ref"] = default_node["module_ref"] if default_node else base.get("module_ref")
        base["module_id"] = module_index.get(str(base.get("module_ref") or "")) or None
        base["verified_scope"] = _derive_scope(base, skeleton_status, default_node)
        machine = _node_machine_with(root, tasks, schedule, dispatch, executors, nid)
        if nid in ("DSC-07", "DSC-08", "DSC-09", "DSC-21"):
            machine["internal_task_ids"] = internal_ids
            machine["process_in_product_tables"] = in_product
        base["machine"] = machine
        nodes.append(base)

    missing_contract = sorted(set(STAGE_TO_SKELETON) - {n["node_id"] for n in nodes})
    if missing_contract:
        raise RuntimeError(f"骨架契约环节未入图（生成器缺陷，禁产半图）: {missing_contract}")
    prod_ids = sorted(n["node_id"] for n in nodes if n.get("verified_scope") == "production")
    skel_ok = sorted(nid for nid, sym in skeleton_status.items() if sym == "✅")
    if skeleton_status and prod_ids != skel_ok:
        raise RuntimeError(
            f"双轴与骨架不一致（生成期硬失败，禁产出自粉饰的图）：production={prod_ids} 骨架✅={skel_ok}"
        )

    labels = {src: get_zh(src, "data_source") for src in tasks["per_source_task_counts"]}
    doc: dict[str, Any] = {
        "schema_version": human("schema_version"),
        "map_id": human("map_id"),
        "name_zh": human("name_zh"),
        "nickname": human("nickname"),
        "ttl": human("ttl"),
        "effective_from": human("effective_from"),
        "generator": _HUMAN["generator"],
        "ssot_note_zh": human("ssot_note_zh"),
        "laws": human("laws"),
        "boundary": human("boundary"),
        "segments": human("segments"),
        "nodes": nodes,
        "edges": human("edges"),
        "feedback_loops": human("feedback_loops"),
        "counts": _build_counts(nodes, human("edges"), skeleton_status),
        "machine": {
            "as_of": as_of,
            "sources": {
                "tasks_yaml": tasks_without_tables(tasks),
                "schedule_yaml": schedule,
                "scheduler_dispatch": dispatch,
                "asset_registry": registry,
                "skeleton_status": {
                    "path": SKELETON_REL,
                    "rows_scanned": len(skeleton_status),
                    "by_symbol": _count([{"s": v} for v in skeleton_status.values()], "s"),
                    "production_nodes": skel_ok,
                },
                "module_id_projection": {
                    "path": PATH_OWNERSHIP_REL,
                    "claims_scanned": len(module_index),
                    "nodes_with_module_id": sum(1 for n in nodes if n.get("module_id")),
                    "nodes_with_module_ref": sum(1 for n in nodes if n.get("module_ref")),
                    "nodes_null_module_id": sum(1 for n in nodes if not n.get("module_id")),
                },
                "process_in_product": in_product,
            },
            "source_task_labels": labels,
            "edge_kind_labels": {e.get("kind", ""): get_zh(e.get("kind", ""), "edge_type") for e in human("edges")},
            "internal_task_ids": internal_ids,
            "target_table_count": tasks["distinct_target_tables"],
        },
    }
    if dropped_legacy:
        doc["machine"]["legacy_aliases_dropped"] = dict(sorted(dropped_legacy.items()))
    if retired:
        doc["machine"]["retired_existing_nodes"] = retired
    return doc


def _derive_scope(
    node: dict[str, Any], skeleton_status: dict[str, str], default_node: dict[str, Any] | None
) -> str | None:
    """verified_scope 推导（口径真源=骨架 §1 状态列 + 六图终局卷 §3）：

    production ⇔ 骨架行级 ✅ ∧ 非分面 ∧ 有 freshness_evidence ∧ 无 probe_failed verdict。
    查不到骨架行（辅助/缺口节点或骨架不可读）⇒ 一律 structure（禁凭人工字段蒙混上 production）。
    """
    nid = node.get("node_id")
    sym = skeleton_status.get(nid) or (default_node or {}).get("_skeleton_symbol")
    if sym != "✅":
        return "structure"
    if node.get("facets"):
        return "structure"  # 行级 ✅ 仅当全腿 ✅：分面行永不 production
    fe = node.get("freshness_evidence") or []
    if not fe:
        return "structure"  # 缺新鲜度证据=不敢宣在产（宁欠不谎）
    if any(str(e.get("verdict")) == "probe_failed" for e in fe if isinstance(e, dict)):
        return "structure"  # 探测失败不得放行 production（多判=谎）
    if any(str(e.get("verdict")) not in ("fresh", "lagging") for e in fe if isinstance(e, dict)):
        return "structure"
    return "production"


def _node_machine_with(
    root: Path,
    tasks: dict[str, Any],
    schedule: dict[str, Any],
    dispatch: dict[str, Any],
    executors: dict[str, Any],
    node_id: str,
) -> dict[str, Any]:
    """带上下文的节点机生块（避免重复全量扫描）。"""
    owned = _SLOT_OWNERSHIP.get(node_id, [])
    slot_facts: dict[str, dict[str, Any]] = {}
    for slot in sorted(owned):
        slot_facts[slot] = {
            "in_schedule": slot in schedule["slots"],
            "task_count": tasks["per_slot_task_counts"].get(slot, 0),
            "special_dispatch": slot in dispatch["dispatched_slots"],
        }
    block: dict[str, Any] = {}
    if slot_facts:
        block["slots"] = slot_facts
        block["hollow_slots"] = sorted(
            s for s, f in slot_facts.items() if f["task_count"] == 0 and not f["special_dispatch"]
        )
    facts = executors.get(node_id)
    if facts:
        block["executors"] = facts["executors"]
        block["executors_missing"] = facts["missing"]
    return block


def tasks_without_tables(tasks: dict[str, Any]) -> dict[str, Any]:
    """机生层不外联目标表全清单（图里按环节挂锚即可，散文与清单都不写字面数）。"""
    return {k: v for k, v in tasks.items() if k != "target_tables"}


def _build_counts(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], skeleton_status: dict[str, str] | None = None
) -> dict[str, int]:
    """机生计数（静态清单禁手维——所有计数由节点/边集合现算，键序稳定）。"""
    counts: dict[str, int] = {"nodes": len(nodes), "edges": len(edges)}
    for seg in _SEGMENTS:
        counts[f"segment_{seg['segment_id']}"] = sum(1 for n in nodes if n.get("segment") == seg["segment_id"])
    counts["unwired_or_hollow"] = sum(
        1 for n in nodes if str(n.get("wiring_status", "")).startswith(("unwired", "running_unregistered"))
    )
    counts["gaps_registered"] = sum(len(n.get("gaps") or []) for n in nodes)
    counts["proposed_semantics"] = sum(1 for n in nodes if n.get("confidence") == "proposed")
    counts["verified_semantics"] = sum(1 for n in nodes if n.get("confidence") == "verified")
    for key, field in (
        ("gap_nodes", "node_type"),
        ("built_nodes", "build_status"),
        ("pending_nodes", "build_status"),
        ("partial_nodes", "build_status"),
        ("production_nodes", "verified_scope"),
        ("structure_nodes", "verified_scope"),
        ("facet_nodes", "__facets"),
        ("stage_nodes", "__stage"),
    ):
        counts[key] = 0
    for n in nodes:
        nt = n.get("node_type")
        if nt == "gap":
            counts["gap_nodes"] += 1
        if nt == "stage":
            counts["stage_nodes"] += 1
        if n.get("facets"):
            counts["facet_nodes"] += 1
        bs = n.get("build_status")
        if bs == "built":
            counts["built_nodes"] += 1
        elif bs == "pending":
            counts["pending_nodes"] += 1
        elif bs == "partial":
            counts["partial_nodes"] += 1
        vs = n.get("verified_scope")
        if vs == "production":
            counts["production_nodes"] += 1
        elif vs == "structure":
            counts["structure_nodes"] += 1
    counts["skeleton_ok_rows"] = sum(1 for v in (skeleton_status or {}).values() if v == "✅")
    counts["nodes_with_module_id"] = sum(1 for n in nodes if n.get("module_id"))
    counts["gap_ref_edges"] = sum(1 for e in edges if e.get("kind") == "gap")
    return counts


def render(doc: dict[str, Any]) -> str:
    """稳定渲染（禁 timestamp 进默认输出；行尾 LF；键序由构造顺序决定）。"""
    header = (
        "# 图12 数据供给链图（data_supply_chain_map）真源——机生层＋人工语义层双层\n"
        "# 由 scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py 生成/刷新\n"
        "# 人工语义层（nodes/edges/laws/segments/boundary）existing-wins；machine/counts 每次重建\n"
        "# 血肉源：docs/_working/map_build/fig12_datachain/{00_skeleton.md,01~05 作业簿,11/12 两卷}（实测结论已作节点字段）\n"
        "# 纪律：INV-1 只存标识符与指针｜挂槽≠在跑｜空串≠无数据｜production 必带 freshness_evidence｜"
        "缺口不冒充 built｜双轴与骨架 §1 同源（production 数==✅ 数）\n"
    )
    body = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=118)
    return header + body


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="图12 数据供给链图生成器（双层，幂等，双轴同源）")
    ap.add_argument("--root", default=str(REPO_ROOT), help="仓库根（默认=本文件所在 worktree）")
    ap.add_argument("--out", default=None, help=f"输出路径（默认 {OUTPUT_REL}）")
    ap.add_argument(
        "--as-of", default=None, help="机生层时间戳唯一注入口（禁内部取时；缺省=null 以保证同输入两次逐字节等）"
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要，零写入")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    doc = build_document(root, args.as_of)
    legacy = doc["machine"].get("legacy_aliases_dropped")
    if legacy:
        print(f"WARN: 已丢弃旧别名字段（L0/L1 统一名迁移，内容以 note_zh/fallback/source_anchors 承载）: {legacy}")
    payload = render(doc)
    out = Path(args.out) if args.out else root / OUTPUT_REL
    summary = doc["counts"]
    print("counts:", ", ".join(f"{k}={v}" for k, v in summary.items()))
    print("hollow_slots:", doc["machine"]["sources"]["scheduler_dispatch"]["slots_hollow"])
    print("registry_drift:", doc["machine"]["sources"]["asset_registry"]["drift"] or "none")
    print(
        "skeleton:",
        doc["machine"]["sources"]["skeleton_status"]["rows_scanned"],
        "行 ✅=",
        summary["skeleton_ok_rows"],
        "production=",
        summary["production_nodes"],
    )
    if args.dry_run:
        print("[dry-run] 零写入")
        return 0
    from zephyr.shared.io.file_utils import safe_write_text

    result = safe_write_text(out, payload, repo_root=root)
    if not getattr(result, "written", False):
        print(f"[ERROR] 写入失败（CAS 冲突？）: {out}", file=sys.stderr)
        return 1
    print(f"written: {out}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 本件=离线机生器（六图族）——对齐台/人工显式触发再生产物，非 cron/daemon/常驻服务；判据面由 validators+对抗尺承载（同款豁免先例=generate_connection_matrix.py:1480, 8454beec5a）
    sys.exit(main())
