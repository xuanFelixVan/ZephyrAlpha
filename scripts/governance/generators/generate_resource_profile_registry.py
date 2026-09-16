# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md | §
# [MODULE] scripts.governance.generators.generate_resource_profile_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml,hashlib; scripts.backtest.compute_window_gate（只读引用 NODE_CLASS_WEIGHT 映射口径）;
#   zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts（--check --publish-alerts
#   自检臂出口，函数级延迟 import——本模块不得因告警线缺席而崩）
# [CONSUMERS] zephyr.infrastructure.system_telemetry.resource_sampler（实体清单+观测模式）;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（真源漂移检测复用本模块抽取函数）;
#   scripts/governance/generators/generate_resource_week_view.py（实体+窗档入图）;
#   scripts/register_resource_regen_check_task.ps1（每小时自检+自动再生计划任务宿主）;
#   scripts/register_resource_view_publish_task.ps1（每日视图重渲+告警发布任务宿主）;
#   docs/registry_of_registries.yaml REG-RESCHED-001
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 静态清单生成器产出禁手工维护——条目增删只经本模块再生;
#   自检臂只读（除 --auto-regen 再生与 --publish-alerts 落板外零写入），且健康码
#   检测不得依赖闸本体（闸缺席时正是它唯一能开口的时候）;
#   人填字段合并保全（module_id/map_node_id/pool/peak_mem_gb申报/est_duration_min申报/
#   exclusive_group/status/notes_zh/measured.* 再生不丢）;
#   时间值不搬家——window_expr 从真源抽取（ps1 触发器/schedule.yaml cron），人禁填;
#   resource_class→E0 映射层在本模块，E0 真源（compute_window_gate.py）不动;
#   阈值不收编——mem_ceiling_gb 仅引用 process_reaper _DANGEROUS_MEM_GB 红线
# [MODIFY-GUARD] config/resource_profile_registry.yaml schema（18 字段）变更须同步采样器+闸+视图生成器
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失=跳过该实体并记 warnings; schedule.yaml 损坏=YAML 异常上抛（fail-closed）
# [TESTS] tests/scripts/test_generate_resource_profile_registry.py
# [A_module] module_id=MOD-RESCHED-PROFILE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Windows 计划任务真源
#   fields: scripts/register_*.ps1（任务名/触发器/时限/DISABLED）
#   code: parse_ps1_entities
# - id: I2
#   name: 数据槽位真源
#   fields: src/zephyr/data/config/schedule.yaml 21 槽位 cron
#   code: parse_schedule_slots
# - id: I3
#   name: 手动/事件实体种子
#   fields: 方案 §3.C 盲区清单（MANUAL_ENTITY_SEED）
#   code: manual_entities
# - id: I4
#   name: 排产链健康真源（只读探针）
#   fields: 闸模块/E0 模块/闸注册目录/周历视图 rw-data.js
#   code: check_gate_availability, check_view_freshness
# 层: 算法
# - id: A1
#   name_zh: ① 三源实体化
#   name_en: build_entities
#   intro: ps1 触发器→cron/事件窗档；槽位 cron 原样；手动实体窗档=manual/event/dynamic
#   desc: resource_class 初值+trading_sensitive 按 E0 四值映射推导（local→light，local_gpu/mixed→heavy）
#   inputs: I1, I2, I3
#   outputs: 18 字段实体草稿
# - id: A2
#   name_zh: ② 合并保全再生
#   name_en: merge_preserve
#   intro: 按 task_id 合并旧档——人填/采样字段保全，生成器字段刷新
#   desc: 防再生清空人复核成果；新源消失实体保留并标 status=orphaned_source
#   inputs: A1, 磁盘现有注册表
#   outputs: 全量实体
# - id: A3
#   name_zh: ③ CAS 落盘
#   name_en: main
#   intro: safe_write_text CAS 写注册表（热文件纪律），头部 groups/ceiling/计数刷新
#   desc: 计数=entities 条目数机生；ROOR counting_rule 对账口径同源
#   inputs: A2
#   outputs: config/resource_profile_registry.yaml
# - id: A4
#   name_zh: ④ 排产链自检
#   name_en: collect_check_findings
#   intro: --check 臂：现盘漂移比对 + 闸/E0/闸注册在场性 + 视图指纹新鲜度
#   desc: 闸缺席=block（C-5，原先静默）；视图过期=warn（C-10）；漂移=warn 可 --auto-regen 就地再生
#   inputs: A1, I4
#   outputs: sched_* findings
# 层: 输出
# - id: O1
#   name_zh: 资源画像单一真源
#   name_en: resource profile registry
#   intro: 全项目耗资源实体 18 字段画像（库），供器/闸/图/晨审消费
#   downstream: resource_sampler; resource_schedule_gate; generate_resource_week_view
# - id: O2
#   name_zh: 排产链告警条目
#   name_en: ops notification findings
#   intro: --publish-alerts 经告警桥落 .runtime/ops_notifications/notifications.jsonl
#   downstream: resource_schedule_alerts → OpsAlertFeed（promotion 页/晨审）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
# A1 --> A4
# I4 --> A4
# A4 --> O2
# A4 --> A3
"""generate_resource_profile_registry — 资源画像注册表生成器（MOD-RESCHED-PROFILE，B1 库）。

资源排班全景四件套之"库"的产出器（方案 §2.1 十八字段总表/§3 三层地图）。
把排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历）收敛为单一真源：
config/resource_profile_registry.yaml（ROOR tier0 REG-RESCHED-001）。

三输入：
1. scripts/register_*.ps1 —— Windows 计划任务（任务名/触发器/时限/DISABLED 解析）；
2. src/zephyr/data/config/schedule.yaml —— DataScheduler 21 槽位（cron 原样抽取）；
3. MANUAL_ENTITY_SEED —— 方案 §3.C 手动/事件盲区实体清单（生成器内种子，时间真源
   指向方案文档直至有更正式真源）。

合并保全（A2）：再生按 task_id 合并——module_id/map_node_id/pool/peak_mem_gb/
est_duration_min/exclusive_group/status/notes_zh（人复核字段）与 measured.*/samples_uri
（采样器独占）原样保留；生成器自有字段（resource_class 初值/window_type/window_expr/
schedule_truth_source/trading_sensitive）刷新。真源消失的旧实体保留并标
status=orphaned_source（不静默删——删除是 Owner 门位）。

排产链自检臂（2026-09-17 P0，v2 方案 L-2/C-5/C-10——"再生"本身也是排产对象）：
`--check` 除比对三真源与现盘注册表，还顺带自检整条链是否活着：
- C-5 闸/E0/闸注册缺席 → `sched_gate_absent`（block；原先整条告警链在闸缺席时
  静默，本检测刻意放在闸之外——闸无法自证在场）；
- C-10 周历视图 rw-data.js 内嵌 registry_sha256 ≠ 注册表现盘指纹 →
  `sched_view_stale`（warn，下次日视图任务自愈）；
- `--publish-alerts` 经告警桥落 `.runtime/ops_notifications/notifications.jsonl`
  （发布方 module_id=`resource-schedule-regen`，与闸/视图发布方划界，互不解除）；
- `--auto-regen` 检出漂移→就地全量再生（"改真源→表跟上"零人工）。

用法:
  python scripts/governance/generators/generate_resource_profile_registry.py            # 生成
  python scripts/governance/generators/generate_resource_profile_registry.py --check    # 漂移+链健康自检
  python ... --check --publish-alerts --auto-regen                                       # 计划任务体（每小时）
  python scripts/governance/generators/generate_resource_profile_registry.py --output <path>

退出码（register_resource_regen_check_task.ps1 消费契约）：
  0=健康；2=注册表与真源漂移（--auto-regen 后仍漂移才留 2）；
  3=无漂移但有健康码（闸缺席/视图过期——不触发再生，只告警）。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import safe_write_text, content_sha256  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT = REPO_ROOT / "config" / "resource_profile_registry.yaml"
SCHEDULE_YAML = REPO_ROOT / "src" / "zephyr" / "data" / "config" / "schedule.yaml"
PS1_GLOB = "register_*.ps1"  # 用法：(REPO_ROOT/"scripts").glob(PS1_GLOB)
PLAN_DOC_REL = "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md"

# ── 排产链自检探针（2026-09-17 P0：C-5 闸缺席 / C-10 视图新鲜度）───────────────
GATE_MODULE_RELPATH = "src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py"
E0_MODULE_RELPATH = "scripts/backtest/compute_window_gate.py"
GATE_REGISTRATION_RELPATH = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"
GATE_ID = "RESOURCE-SCHEDULE"  # 在册性判定键（真源=in_process_gate_registry.yaml）
DEFAULT_VIEW = (
    REPO_ROOT / "src" / "zephyr" / "frontend" / "dashboard" / "web" / "features" / "resourceweek" / "rw-data.js"
)
VIEW_SHA_KEY = "registry_sha256"
_RE_VIEW_SHA = re.compile(r'"' + VIEW_SHA_KEY + r'"\s*:\s*"([0-9a-f]+)"')

# 自检臂理由码字面量——清单真源=resource_schedule_gate（六码），此处必须自带字面量：
# C-5 的因果就是"闸不在场时还要能报警"，import 闸取码会让告警链在自己该说话的
# 那一刻哑火。一致性由 tests/infrastructure/test_resource_schedule_regen_check.py 锁死。
REASON_DRIFT = "sched_truth_drift"
REASON_GATE_ABSENT = "sched_gate_absent"
REASON_VIEW_STALE = "sched_view_stale"
# 告警板发布方身份（与闸/视图发布方划界：OpsAlertFeed 解除联动按 module_id 分域）
REGEN_PUBLISHER_MODULE_ID = "resource-schedule-regen"

# 内存天花板：引用 process_reaper._DANGEROUS_MEM_GB 红线（仅引用不收编——阈值三口径
# 统一是 v2 挂起议题，方案 §2.1 裁决③）
MEM_CEILING_GB = 10.0

# 互斥组枚举收口（方案 §2.1/§5-3，自实证归纳）
GROUPS: dict[str, str] = {
    "ch_bulk_write": "CH 大 DELETE+INSERT 互斥（亿行级写库族）",
    "tick_drain": "tick 排水 vs 回补互斥（local_replay 排水/大回补族）",
    "mine_vs_exam": "周六挖掘→考尺串行（成功先例：10:00→14:00）",
    "repair_passport": "亿行级修复=护照登记+窗口+白名单三件套",
    "gpu_default": "GPU 显存互斥（Kronos/Ollama/SFT/转换）",
    "llm_local": "本地 LLM 推理批互斥（qwen3:8b 单实例）",
}

# E0 四值映射层（方案 §2.1：local→light，local_gpu/mixed→heavy，api→按用途拆；
# 映射在本模块，E0 真源 scripts/backtest/compute_window_gate.py 不动）
E0_CLASS_TO_RESOURCE: dict[str, str] = {
    "local": "light",
    "local_gpu": "cpu_heavy",
    "mixed": "cpu_heavy",
    "api": "llm_api_paid",
}

# resource_class → 是否 E0 管辖（trading_sensitive 推导基；light/network_download/llm_api_paid 免）
TRADING_SENSITIVE_CLASSES = {"cpu_heavy", "gpu", "llm_api_local", "db_heavy"}

# pool 四档（schedule.yaml executor 六值裁剪：realtime/intraday_minute/intraday_sector→realtime）
EXECUTOR_TO_POOL = {
    "heavy": "heavy",
    "default": "default",
    "realtime": "realtime",
    "intraday_minute": "realtime",
    "intraday_sector": "realtime",
    "light": "light",
}

DOW_PS1_TO_CRON = {  # ps1 DaysOfWeek → cron dow（0/7=周日…6=周六，APScheduler/croniter 口径）
    "Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
    "Thursday": 4, "Friday": 5, "Saturday": 6,
}

# ---------------------------------------------------------------------------
# §3.C 手动/事件实体种子（方案 §3.C 盲区清单；时间真源=方案文档直至有更正式真源）
# 字段语义：class=resource_class 初值；dmin=est_duration_min 申报初值（人可复核改）；
# mem=peak_mem_gb 申报初值；grp=exclusive_group；wt=window_type
# ---------------------------------------------------------------------------
MANUAL_ENTITY_SEED: list[dict] = [
    {"task_id": "manual_factory_grid_executor", "cn": "工厂网格执行器（单批最大算力实体，2万配方）", "class": "cpu_heavy", "dmin": 240, "mem": 4.0, "grp": [], "wt": "manual"},
    {"task_id": "manual_kronos_adapter", "cn": "Kronos 适配器（CUDA auto，GPU 与 Ollama/桌面抢显存）", "class": "gpu", "dmin": 60, "mem": 6.0, "grp": ["gpu_default"], "wt": "manual"},
    {"task_id": "manual_kronos_finetune", "cn": "Kronos 两段式微调（tokenizer→predictor，torchrun 单卡；2026-09-16 实测 GPU 峰值~7GB、两段各 0.5-2h，kronos_small bs=128）", "class": "gpu", "dmin": 240, "mem": 8.0, "grp": ["gpu_default"], "wt": "manual"},
    {"task_id": "manual_run_sentiment_batch", "cn": "情绪批量（2010-2026 全历史，llm_api_local 小时级）", "class": "llm_api_local", "dmin": 180, "mem": 3.0, "grp": ["llm_local"], "wt": "manual"},
    {"task_id": "manual_run_sft_train", "cn": "SFT 手动重训（GPU 小时级）", "class": "gpu", "dmin": 240, "mem": 8.0, "grp": ["gpu_default"], "wt": "manual"},
    {"task_id": "manual_convert_gguf", "cn": "GGUF 转换（GPU 手动）", "class": "gpu", "dmin": 60, "mem": 6.0, "grp": ["gpu_default"], "wt": "manual"},
    {"task_id": "manual_lane_c_agentic_miner", "cn": "Lane-C agentic 挖掘（llm_api_local+cpu，分钟-十几分钟）", "class": "llm_api_local", "dmin": 30, "mem": 2.0, "grp": ["llm_local"], "wt": "manual"},
    {"task_id": "manual_hypothesis_translator", "cn": "假设翻译器（llm_api_local 手动/夜批）", "class": "llm_api_local", "dmin": 15, "mem": 1.5, "grp": ["llm_local"], "wt": "manual"},
    {"task_id": "manual_mcts_miner", "cn": "MCTS 挖掘（llm_api_local+cpu 手动）", "class": "llm_api_local", "dmin": 30, "mem": 2.0, "grp": ["llm_local"], "wt": "manual"},
    {"task_id": "manual_lane_b_miner", "cn": "Lane-B 挖掘（llm_api_local 手动/夜批）", "class": "llm_api_local", "dmin": 20, "mem": 2.0, "grp": ["llm_local"], "wt": "manual"},
    {"task_id": "manual_factory_grid_anova", "cn": "网格 ANOVA/E4 考尺/DSR 重算（cpu 分钟级手动）", "class": "light", "dmin": 15, "mem": 1.0, "grp": [], "wt": "manual"},
    {"task_id": "manual_bdpan_tick_backfill", "cn": "bdpan tick 大回补（全手动，与 heavy 槽互不可见）", "class": "network_download", "dmin": 1440, "mem": 4.0, "grp": ["tick_drain", "ch_bulk_write"], "wt": "manual"},
    {"task_id": "manual_bse_minute_backfill", "cn": "BSE 分钟回补（死线 2026-09-17，手动）", "class": "network_download", "dmin": 720, "mem": 3.0, "grp": ["tick_drain", "ch_bulk_write"], "wt": "manual"},
    {"task_id": "manual_tick_depth5_backfill", "cn": "tick 五档深度回补（水位 7600 万行，手动）", "class": "network_download", "dmin": 720, "mem": 3.0, "grp": ["tick_drain"], "wt": "manual"},
    {"task_id": "manual_lof_minute_backfill", "cn": "LOF 分钟回补（手动）", "class": "network_download", "dmin": 360, "mem": 2.0, "grp": ["tick_drain"], "wt": "manual"},
    {"task_id": "manual_sector880_backfill", "cn": "880 板块分钟回补（手动）", "class": "network_download", "dmin": 240, "mem": 2.0, "grp": ["tick_drain"], "wt": "manual"},
    {"task_id": "manual_repair_kline_tz", "cn": "K线时区修复月务（15.6亿行 DELETE+回插=全库最大破坏性负载，护照级）", "class": "db_heavy", "dmin": 2880, "mem": 6.0, "grp": ["repair_passport", "ch_bulk_write"], "wt": "manual"},
    {"task_id": "event_dashboard_backtest_run", "cn": "面板 backtest-run 端点（无 E0 远程重算入口→B2 已纳管）", "class": "cpu_heavy", "dmin": 60, "mem": 2.0, "grp": [], "wt": "event"},
    {"task_id": "event_dashboard_services_control", "cn": "面板服务编排端点（重启/停止控制面，轻载触发器）", "class": "light", "dmin": 5, "mem": 0.5, "grp": [], "wt": "event"},
    {"task_id": "dynamic_local_replay", "cn": "local_replay 排水（事件突发 replay_batch，与 tick 回补互斥）", "class": "db_heavy", "dmin": 120, "mem": 3.0, "grp": ["tick_drain"], "wt": "dynamic"},
    # --- ops_* 补注册批（2026-09-17，st-autolnk-20260917）：Task Scheduler 直注册、
    # 无 register_*.ps1 真源的系统运维任务（I1 解析盲区：dash 命名/非 register 脚本）。
    # 触发时间=实测 StartBoundary 记入备注；window_expr 留空，待立 register ps1 后由真源重抽。
    {"task_id": "ops_ch_optimize_merge_weekly", "cn": "CH 周度优化合并（实测周六 03:30；ch_bulk_write 族，与 weekend_calibration 03:00+180min 同窗——补注册后冲突闸首次可见）", "class": "db_heavy", "dmin": 120, "mem": 3.0, "grp": ["ch_bulk_write"], "wt": "manual"},
    {"task_id": "ops_daily_backup", "cn": "全量日备份 backup.ps1 -Mode all（实测每日 06:00；F 盘增量，磁盘 I/O 主导）", "class": "light", "dmin": 60, "mem": 1.0, "grp": [], "wt": "manual"},
    {"task_id": "ops_weekly_vm_backup", "cn": "CH VM VHDX 周备份 backup_ch_vm.ps1（实测周六 06:00，与日备份同刻叠 I/O）", "class": "light", "dmin": 240, "mem": 1.0, "grp": [], "wt": "manual"},
    {"task_id": "ops_io_check_monthly", "cn": "磁盘 IO 月检 io_check_task.bat（实测每月 13 日 09:00）", "class": "light", "dmin": 30, "mem": 0.5, "grp": [], "wt": "manual"},
    {"task_id": "ops_tilib_indicator_backfill_nightly", "cn": "指标库夜间回填 backfill_night.bat（实测每日 02:30；tilib 线资产，cpu+db）", "class": "cpu_heavy", "dmin": 120, "mem": 2.0, "grp": [], "wt": "manual"},
    {"task_id": "ops_bdpan_tick_watch", "cn": "bdpan tick 兜底回灌守望 bdpan_tick_watch.py（实测每日 08:00；tick_drain 族）", "class": "network_download", "dmin": 30, "mem": 1.0, "grp": ["tick_drain"], "wt": "manual"},
    {"task_id": "ops_board_index_realtime", "cn": "板块指数实时采集 board_index_realtime.py（实测每日 09:20）", "class": "network_download", "dmin": 15, "mem": 1.0, "grp": [], "wt": "manual"},
    {"task_id": "ops_sector_snapshot", "cn": "板块快照 run_sector_snapshot.py（实测每日 16:40）", "class": "network_download", "dmin": 15, "mem": 1.0, "grp": [], "wt": "manual"},
    {"task_id": "ops_qmt_watchdog", "cn": "QMT 行情桥看门狗 qmt_watchdog.ps1（实测每日 08:45）", "class": "light", "dmin": 5, "mem": 0.5, "grp": [], "wt": "manual"},
    {"task_id": "ops_ttl_rejudge_daily", "cn": "TTL 日重判 run_ttl_rejudge_daily.ps1（实测每日 18:05；治理清理）", "class": "light", "dmin": 15, "mem": 0.5, "grp": [], "wt": "manual"},
    {"task_id": "ops_ai_wrapper_inject", "cn": "AI Wrapper 注入保活 ensure_ai_wrapper_injection.ps1（实测每日 12:41；开发工具链）", "class": "light", "dmin": 5, "mem": 0.5, "grp": [], "wt": "manual"},
]

# schedule.yaml 槽位 → resource_class/申报时长 特化映射（executor 兜底，槽位覆写）
SLOT_OVERRIDES: dict[str, dict] = {
    "pre_market": {"class": "network_download", "dmin": 15, "mem": 1.5},
    "intraday_realtime": {"class": "light", "dmin": 2, "mem": 1.0},
    "intraday_minute": {"class": "light", "dmin": 2, "mem": 1.0},
    "intraday_sector": {"class": "light", "dmin": 2, "mem": 1.0},
    "event_driven": {"class": "network_download", "dmin": 3, "mem": 1.0},
    "news_slow": {"class": "network_download", "dmin": 180, "mem": 2.0},
    "daily_crypto": {"class": "network_download", "dmin": 10, "mem": 1.0},
    "daily_kline": {"class": "db_heavy", "dmin": 90, "mem": 3.0},
    "daily_capital": {"class": "network_download", "dmin": 45, "mem": 2.0},
    "daily_event": {"class": "network_download", "dmin": 45, "mem": 2.0},
    "research_nightly": {"class": "network_download", "dmin": 120, "mem": 2.5},
    "consensus_crosscheck": {"class": "db_heavy", "dmin": 60, "mem": 2.5},
    "nightly_financial": {"class": "db_heavy", "dmin": 120, "mem": 3.0},
    "weekend_calibration": {"class": "db_heavy", "dmin": 180, "mem": 4.0, "grp": ["ch_bulk_write"]},
    "monthly_static": {"class": "network_download", "dmin": 60, "mem": 1.5},
    "weekend_backfill": {"class": "network_download", "dmin": 240, "mem": 3.0, "grp": ["tick_drain"]},
    "daily_backfill": {"class": "network_download", "dmin": 120, "mem": 2.5, "grp": ["tick_drain"]},
    "integrity_check": {"class": "light", "dmin": 15, "mem": 1.0},
    "catchup_guard": {"class": "light", "dmin": 30, "mem": 1.0},
    "nightly_sentiment": {"class": "light", "dmin": 20, "mem": 1.0},
    "auction_highfreq": {"class": "light", "dmin": 10, "mem": 1.0},
}

# ps1 触发解析失败的兜底提示表（真源仍是 ps1 文本；此处仅已知触发器的人类可读备注）
PS1_FALLBACK_HINTS: dict[str, dict] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _base_entity(task_id: str, cn: str) -> dict:
    """18 字段骨架（§2.1 顺序）。"""
    return {
        "task_id": task_id,
        "module_id": None,
        "map_node_id": None,
        "resource_class": "light",
        "pool": "default",
        "peak_mem_gb": None,
        "est_duration_min": None,
        "exclusive_group": [],
        "window_type": "manual",
        "window_expr": None,
        "schedule_truth_source": PLAN_DOC_REL,
        "trading_sensitive": False,
        "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0, "last_at": None},
        "samples_uri": f".runtime/logs/resource_samples/{task_id}.jsonl",
        "status": "planned",
        "notes_zh": cn,
    }


# ---------------------------------------------------------------------------
# ① ps1 解析（Windows 计划任务真源）
# 任务名捕获：$TaskName = "..." / TaskName = "..."（hashtable）/ -TaskName "..." / -Name "..."
# ---------------------------------------------------------------------------
_RE_TASKNAME = re.compile(r'(?:\$TaskName\s*=\s*|TaskName\s*=\s*|-TaskName\s+|-Name\s+)"?(ZephyrAlpha_[A-Za-z0-9_]+)')
_RE_TIME_LIMIT = re.compile(r"-ExecutionTimeLimit\s+\(?New-TimeSpan\s+-Hours\s+(\d+)")
_RE_TIME_LIMIT_MIN = re.compile(r"-ExecutionTimeLimit\s+\(?New-TimeSpan\s+-Minutes\s+(\d+)")
_RE_WEEKLY = re.compile(r"-Weekly(?:\s+-DaysOfWeek\s+([\w,]+))?\s+-At\s+\"?(\d{1,2}:\d{2})\"?")
_RE_DAILY = re.compile(r"-Daily\s+-At\s+\"?(\d{1,2}:\d{2})\"?")
_RE_ONCE_REP = re.compile(r"-Once\s+-At\s+\(Get-Date\)|-Once\s+-At\s+\"?(\d{1,2}:\d{2})\"?[\s\S]{0,200}?-RepetitionInterval\s+\(?New-TimeSpan\s+-Minutes\s+(\d+)")
_RE_TIMES_LIST = re.compile(r"-Times\s+@\(([^)]*)\)")
_RE_ATLOGON = re.compile(r"-AtLogOn\b")
_RE_TIME_STR = re.compile(r'"(\d{1,2}:\d{2})"')

# 计划任务 → 分类特化（类/池/申报初值；窗档仍从 ps1 文本抽取，不在此维护时间值）
PS1_TASK_OVERRIDES: dict[str, dict] = {
    "FactoryLaneC": {"class": "cpu_heavy", "pool": "heavy", "mem": 2.0, "dmin": 240, "grp": ["mine_vs_exam"], "status": "active"},
    "C4Exam": {"class": "cpu_heavy", "pool": "heavy", "mem": 2.0, "dmin": 240, "grp": ["mine_vs_exam"], "status": "active"},
    "F06Grid": {"class": "cpu_heavy", "pool": "heavy", "mem": 4.0, "dmin": 240, "grp": [], "status": "active",
                "note": "周六 14:00 批 A census+批 B subspace（factory_grid_executor×2，4ea29d816f；与 C4Exam 同刻——错窗处置待 Owner/资源线裁）"},
    "OllamaServe": {"class": "llm_api_local", "pool": "light", "mem": 8.0, "dmin": 0, "grp": ["gpu_default"], "status": "active", "wt": "event",
                    "note": "AtLogOn 常驻（est=0 表示常驻）；qwen3:8b 显存/内存驻留"},
    "PatternMining": {"class": "light", "pool": "light", "mem": 1.0, "dmin": 5, "status": "active"},
    "PaperSession": {"class": "light", "pool": "light", "mem": 1.0, "dmin": 30, "status": "active"},
    "IntradayFundFlow": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 10, "status": "active"},
    "IndexMinuteEOD": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 10, "status": "active"},
    "PostSettlement": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 10, "status": "active"},
    "DataScheduler": {"class": "light", "pool": "light", "mem": 1.5, "dmin": 0, "status": "active", "wt": "event", "note": "AtLogOn 常驻守护（est=0 表示常驻）"},
    "TickSubscriber": {"class": "light", "pool": "light", "mem": 1.5, "dmin": 0, "status": "active", "wt": "event", "note": "AtLogOn 常驻（est=0）；盘中高频 WAL 写"},
    "CHHealthProbe": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "DeadmanSwitch": {"class": "light", "pool": "light", "mem": 0.3, "dmin": 1, "status": "active", "wt": "event"},
    "ProcessReaper": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "WorktreeDriftWatchdog": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "RSSHub": {"class": "light", "pool": "light", "mem": 0.8, "dmin": 0, "status": "active", "wt": "event", "note": "AtLogOn 常驻（pm2 resurrect，est=0 表示常驻）"},
    "TraeCacheCleanup": {"class": "light", "pool": "light", "mem": 0.3, "dmin": 5, "status": "active", "wt": "event"},
    "TradingWatchdog": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 5, "status": "retired", "wt": "event",
                        "note": "注册为 DISABLED（裁定 INT-03：Owner 手动启用才生效）"},
    "ResourceSamplerScan": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event",
                            "note": "AtLogOn+PT10M one-shot 采样扫描（2026-09-16 生产接线：register_resource_sampler_scan_task.ps1）"},
    "ResourceSamplerWriteback": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 1, "status": "active",
                                 "note": "日 05:40 measured 回写（git 跟踪文件日更一次，derived-sync 例行吸收）"},
    # 2026-09-17 P0（v2 方案 L-2 再生排产化）：把"再生"本身排进班次——两个新任务
    # 由本生成器自己的 ps1 真源源物化为实体（吃自己狗粮，active 计入闸内存求和）
    "ResourceRegenCheck": {"class": "light", "pool": "light", "mem": 0.5, "dmin": 2, "status": "active", "wt": "event",
                           "note": "每小时排产自检+漂移就地再生+C-5/C-10 告警发布（register_resource_regen_check_task.ps1；"
                                   "cadence=注册后 Post-Registration 补 PT1H 重复，ps1 静态文本无 cron 可抽→event，"
                                   "与 ResourceSamplerScan 同型先例）"},
    "ResourceViewPublish": {"class": "light", "pool": "light", "mem": 1.0, "dmin": 5, "status": "active",
                            "note": "日 05:50 周历重渲+闸 findings 告警发布（register_resource_view_publish_task.ps1；"
                                    "排在采样器回写 05:40 之后——视图吃 measured 回写结果）"},
}


def parse_ps1_entities(ps1_paths: list[Path] | None = None) -> tuple[list[dict], list[str]]:
    """解析 register_*.ps1 → sch_* 实体草稿（任务名集合+逐任务分段触发器抽取）。

    返回 (实体, 警告)；跨文件同名任务取首见并告警。
    """
    warnings: list[str] = []
    entities: list[dict] = []
    seen_tasks: dict[str, str] = {}
    for ps1 in sorted(ps1_paths or (REPO_ROOT / "scripts").glob(PS1_GLOB)):
        try:
            text = ps1.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"ps1 不可读 {ps1.name}: {exc}")
            continue
        # 只在登记语境匹配（跳过注释行里的 Verify/schtasks 提示）
        code_lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
        code = "\n".join(code_lines)
        task_names = sorted(set(_RE_TASKNAME.findall(code)))
        if not task_names:
            continue
        time_limit_h = _RE_TIME_LIMIT.search(code)
        time_limit_m = _RE_TIME_LIMIT_MIN.search(code)
        limit_min = int(time_limit_h.group(1)) * 60 if time_limit_h else (
            int(time_limit_m.group(1)) if time_limit_m else None)
        for name in task_names:
            short = name.replace("ZephyrAlpha_", "", 1)
            tid = "sch_" + _snake(short)
            if tid in seen_tasks:
                warnings.append(f"duplicate_task {tid}: {ps1.name} 与 {seen_tasks[tid]} 重复，取首见")
                continue
            seen_tasks[tid] = ps1.name
            ov = PS1_TASK_OVERRIDES.get(short, {})
            ent = _base_entity(tid, ov.get("note", short))
            ent["schedule_truth_source"] = str(ps1.relative_to(REPO_ROOT)).replace("\\", "/")
            ent["resource_class"] = ov.get("class", "light")
            ent["pool"] = ov.get("pool", "light")
            ent["peak_mem_gb"] = ov.get("mem", 0.5)
            ent["exclusive_group"] = list(ov.get("grp", []))
            ent["status"] = ov.get("status", "active")
            ent["window_type"] = ov.get("wt", "cron")
            exprs = _extract_trigger_exprs(code, name)
            if exprs:
                ent["window_expr"] = "|".join(exprs) if len(exprs) > 1 else exprs[0]
                if limit_min:
                    ent["est_duration_min"] = limit_min
                elif len(exprs) == 1:
                    ent["est_duration_min"] = ov.get("dmin", limit_min or 10)
                else:
                    ent["est_duration_min"] = ov.get("dmin", limit_min or 10)
            else:
                ent["est_duration_min"] = ov.get("dmin", limit_min or 5)
            if ov.get("dmin") is not None and not exprs:
                ent["est_duration_min"] = ov["dmin"]
            ent["trading_sensitive"] = ent["resource_class"] in TRADING_SENSITIVE_CLASSES
            entities.append(ent)
    return entities, warnings


def _snake(name: str) -> str:
    """CamelCase→snake_case（缩写词 runs 正确切分：CHHealthProbe→ch_health_probe）。"""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return re.sub(r"_+", "_", s).lower()


def _extract_trigger_exprs(code: str, task_name: str) -> list[str]:
    """从 ps1 代码抽单任务的 cron 表达式集合（多触发点 '|'-连接；AtLogOn/常驻返回空）。"""
    exprs: list[str] = []
    # 任务名各出现位置向后分段（-Times/-Trigger 都在 -TaskName 之后；回看 0 防吞上一任务的
    # -Times；前向截至下一个 ZephyrAlpha_ 任务名，防串到下一任务的触发器）
    all_name_starts = [m.start() for m in re.finditer(r"ZephyrAlpha_[A-Za-z0-9_]+", code)]
    segments: list[str] = []
    for m in re.finditer(re.escape(task_name), code):
        end = m.start() + 1500
        for s in all_name_starts:
            if s > m.end() and s < end:
                end = s
                break
        segments.append(code[m.start(): end])
    segments.append(code)
    for seg in segments:
        m_times = _RE_TIMES_LIST.search(seg)
        if m_times:
            for t in _RE_TIME_STR.findall(m_times.group(1)):
                hh, mm = t.split(":")
                exprs.append(f"{int(mm)} {int(hh)} * * *")
        for m in _RE_WEEKLY.finditer(seg):
            dows = [DOW_PS1_TO_CRON.get(d.strip(), 6) for d in (m.group(1) or "Saturday").split(",")]
            hh, mm = m.group(2).split(":")
            dow_expr = ",".join(str(d) for d in sorted(set(dows)))
            exprs.append(f"{int(mm)} {int(hh)} * * {dow_expr}")
        if not m_times:
            for m in _RE_DAILY.finditer(seg):
                hh, mm = m.group(1).split(":")
                exprs.append(f"{int(mm)} {int(hh)} * * *")
        if exprs:
            break
    if not exprs:
        # AtLogOn / Once+Repetition 兜底：event 或周期分钟
        for seg in segments:
            if _RE_ATLOGON.search(seg):
                return []  # event（window_type 由覆写表/缺省承载）
            m = _RE_ONCE_REP.search(seg)
            if m and m.group(2):
                exprs.append(f"*/{int(m.group(2))} * * * *")
                break
    seen: set[str] = set()
    return [e for e in exprs if not (e in seen or seen.add(e))]


# ---------------------------------------------------------------------------
# ② schedule.yaml 槽位
# ---------------------------------------------------------------------------
def _aps_dow_to_standard(field: str) -> str:
    """APScheduler dow（0=周一）→ 标准 cron dow（0=周日，croniter 口径）逐元素平移。

    schedule.yaml 真源是 APScheduler 语义（其注释自证"APScheduler 0=周一"）；
    注册表统一标准 cron 语义（生成器=映射层），gate/视图 croniter 消费零二次转换。
    支持 *、*/n、列表、范围（含开区间范围）。
    """
    field = field.strip()
    if field == "*":
        return field

    def shift_int(d: int) -> int:
        return (d + 1) % 7  # APScheduler 0=周一 → 标准 cron 0=周日：+1 平移

    def shift_tok(tok: str) -> list[str]:
        """单个元素平移；范围展开成列表（dow 全周最多 7 元素，防端点平移越周反转）。"""
        if tok.lstrip("-").isdigit():
            return [str(shift_int(int(tok)))]
        if "/" in tok:
            base, step = tok.split("/", 1)
            inner = shift_tok(base)
            return [f"{inner[0]}/{step}"]
        if "-" in tok:
            lo, hi = tok.split("-", 1)
            lo_i, hi_i = int(lo), int(hi)
            if hi_i < lo_i:  # 环周范围（如 5-1=周六..周一）：先展开再平移
                seq = [d % 8 for d in range(lo_i, lo_i + 7)] if False else [d % 7 for d in list(range(lo_i, 7)) + list(range(0, hi_i + 1))]
            else:
                seq = list(range(lo_i, hi_i + 1))
            return sorted({str(shift_int(d)) for d in seq}, key=int)
        return [tok]

    vals: list[int] = []
    steps: list[str] = []
    for part in field.split(","):
        for x in shift_tok(part):
            if "/" in x:
                steps.append(x)  # 步长语义（如 */2）不平展
            else:
                vals.append(int(x))
    vals = sorted(set(vals))
    # 连续段压缩回区间（1,2,3,4,5 → 1-5；可读性）
    runs: list[str] = []
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] == vals[j] + 1:
            j += 1
        runs.append(str(vals[i]) if j == i else f"{vals[i]}-{vals[j]}")
        i = j + 1
    return ",".join(runs + steps) if runs else (steps[0] if steps else field)


def parse_schedule_slots(path: Path | None = None) -> tuple[list[dict], list[str]]:
    """schedule.yaml 21 槽位 → data_slot_* 实体（cron 原样抽取+dow 语义归一，人禁填时间值）。"""
    warnings: list[str] = []
    p = path or SCHEDULE_YAML
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    slots = data.get("schedules") or {}
    entities: list[dict] = []
    for name, slot in slots.items():
        if not isinstance(slot, dict):
            continue
        ov = SLOT_OVERRIDES.get(name, {})
        cron = str(slot.get("cron") or "")
        fields = cron.split()
        if len(fields) == 6:
            # 6 段（秒 分 时 日 月 周，auction）：剥离秒段+归一 dow
            fields = fields[1:]
        if len(fields) == 5:
            fields[4] = _aps_dow_to_standard(fields[4])
            cron = " ".join(fields)
        executor = str(slot.get("executor") or "default")
        ent = _base_entity(f"data_slot_{name}", str(slot.get("description") or name)[:80])
        ent["schedule_truth_source"] = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        ent["window_type"] = "cron"
        ent["window_expr"] = cron or None
        ent["resource_class"] = ov.get("class", "db_heavy" if executor == "heavy" else "light")
        ent["pool"] = EXECUTOR_TO_POOL.get(executor, "default")
        ent["peak_mem_gb"] = ov.get("mem", 2.0)
        ent["est_duration_min"] = ov.get("dmin", 30)
        ent["exclusive_group"] = list(ov.get("grp", []))
        ent["status"] = "active"
        desc = str(slot.get("description") or name)
        ent["notes_zh"] = (desc[:70] + "…") if len(desc) > 70 else desc
        ent["trading_sensitive"] = ent["resource_class"] in TRADING_SENSITIVE_CLASSES
        entities.append(ent)
    return entities, warnings


# ---------------------------------------------------------------------------
# ③ 手动/事件实体（§3.C 种子）
# ---------------------------------------------------------------------------
def manual_entities() -> list[dict]:
    """§3.C 盲区实体 → manual_*/event_*/dynamic_* 实体（时间真源=方案文档）。"""
    out: list[dict] = []
    for seed in MANUAL_ENTITY_SEED:
        ent = _base_entity(seed["task_id"], seed["cn"])
        ent.update(
            resource_class=seed["class"],
            pool="heavy" if seed["class"] in ("cpu_heavy", "gpu", "db_heavy") else "default",
            peak_mem_gb=seed["mem"],
            est_duration_min=seed["dmin"],
            exclusive_group=list(seed["grp"]),
            window_type=seed["wt"],
            window_expr=None,
            status="planned",  # 手动实体=画像已登记、行为零变更（方案 §8）
        )
        if seed["wt"] == "dynamic":
            ent["status"] = "planned"
        ent["trading_sensitive"] = ent["resource_class"] in TRADING_SENSITIVE_CLASSES
        out.append(ent)
    return out


# ---------------------------------------------------------------------------
# ④ 合并保全 + 落盘
# ---------------------------------------------------------------------------
# 人填字段（再生保全；消费者=对齐机制/闸/图）+采样器独占字段
_HUMAN_FIELDS = ("module_id", "map_node_id", "pool", "peak_mem_gb", "est_duration_min",
                 "exclusive_group", "status", "notes_zh")
_SAMPLER_FIELDS = ("measured", "samples_uri")


def merge_preserve(fresh: list[dict], existing: list[dict] | None) -> tuple[list[dict], list[str]]:
    """按 task_id 合并：人填/采样字段保全，生成器字段刷新。返回 (合并实体, 警告)。"""
    warnings: list[str] = []
    old_by_id = {str(e.get("task_id")): e for e in (existing or []) if isinstance(e, dict)}
    merged: list[dict] = []
    seen: set[str] = set()
    for ent in fresh:
        tid = str(ent["task_id"])
        seen.add(tid)
        old = old_by_id.get(tid)
        if old:
            for f in _HUMAN_FIELDS + _SAMPLER_FIELDS:
                if f in old and old[f] is not None:
                    ent[f] = old[f]
            # 申报初值防回退：旧档人已填（非 None）则不覆盖初值
            merged.append(ent)
        else:
            merged.append(ent)
    for tid, old in old_by_id.items():
        if tid not in seen:
            old["status"] = "orphaned_source"
            old["notes_zh"] = str(old.get("notes_zh") or "") + "；[生成器] 真源消失，待 Owner 裁定删除"
            warnings.append(f"orphaned_source: {tid}")
            merged.append(old)
    return merged, warnings


def build_registry(existing_path: Path | None = None, output_path: Path | None = None) -> dict:
    """三源实体化+合并保全 → 注册表 dict（不落盘，测试可断言）。"""
    existing: list[dict] = []
    out = output_path or DEFAULT_OUTPUT
    if existing_path and existing_path.exists():
        try:
            data = yaml.safe_load(existing_path.read_text(encoding="utf-8")) or {}
            existing = list(data.get("entities") or [])
        except yaml.YAMLError:
            existing = []
    elif out.exists():
        try:
            data = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
            existing = list(data.get("entities") or [])
        except yaml.YAMLError:
            existing = []
    ps1_ents, w1 = parse_ps1_entities()
    slot_ents, w2 = parse_schedule_slots()
    ents, w3 = merge_preserve(ps1_ents + slot_ents + manual_entities(), existing)
    ents.sort(key=lambda e: (str(e.get("task_id", "")).split("_")[0], str(e.get("task_id"))))
    registry = {
        "schema_version": "1.0.0",
        "doc_type": "register",
        "ttl": "permanent",
        "title": "资源画像注册表（resource profile registry）",
        "status": "active",
        "generated_at": _now_iso(),
        "generated_by": "scripts/governance/generators/generate_resource_profile_registry.py",
        "maintenance": "auto",
        "counting_rule": "entities 数组条目数（生成器三源全量再生；条目禁手工增删）",
        "total_entities": len(ents),
        "field_count": 18,
        "mem_ceiling_gb": MEM_CEILING_GB,
        "mem_ceiling_source": "src/zephyr/trading/process_reaper.py _DANGEROUS_MEM_GB（引用不收编）",
        "groups": GROUPS,
        "cron_convention": "标准 cron（0=周日，croniter 口径）；schedule.yaml 的 APScheduler dow（0=周一）由生成器归一——生成器=映射层",
        "e0_mapping_note": "resource_class←E0 compute_class 映射层在本生成器（local→light，local_gpu/mixed→heavy，api→llm_api_*）；E0 真源 scripts/backtest/compute_window_gate.py 不动",
        "plan_ref": PLAN_DOC_REL,
        "entities": ents,
    }
    return registry


def registry_text(registry: dict) -> str:
    header = (
        "# [GENERATED] 本文件由生成器产出，禁手工增删条目（静态清单生成器产出红线）。\n"
        "# 人可复核字段（module_id/map_node_id/pool/peak_mem_gb/est_duration_min/\n"
        "# exclusive_group/status/notes_zh）可改，再生时合并保全；时间值（window_expr）\n"
        "# 人禁填——再生自真源重抽。\n"
    )
    return header + yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=120)


def registry_content_sha(path: Path | str) -> str:
    """注册表内容指纹（周历视图内嵌 registry_sha256 同口径）。

    口径 = sha256(bytes，先把 CRLF 归一为 LF)[:12]。归一化不是洁癖：视图内嵌指纹与
    现盘指纹只差一个字节就报 sched_view_stale，而 git stash/checkout、网关回写、
    编辑器另存都会把整份 YAML 的行尾在 CRLF/LF 之间翻转——内容一字未改却被误判过期
    （2026-09-17 实测踩过：行尾归一后的 sha 恰等于视图内嵌值）。

    写侧真源=generate_resource_week_view.build_view_data；读侧本函数。两侧各留一行
    实现是刻意的（自检不得依赖视图生成器可装载——视图缺席正是它要报的警），
    口径一致性（含行尾归一）由单测
    test_freshness_sha_recipe_matches_view_writer 锁死。
    """
    raw = Path(path).read_bytes()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:12]


def detect_registry_drift(disk_entities: list[dict], fresh_entities: list[dict]) -> list[str]:
    """现盘注册表实体 vs 三真源重抽实体逐字段比对 → 漂移描述清单（空=无漂移）。

    口径（既有设计不动）：实体缺失/窗档三字段（window_expr/window_type/
    schedule_truth_source）不一致=漂移；磁盘多出的非 orphaned 实体=ghost。
    """
    disk_map = {str(e.get("task_id")): e for e in disk_entities if isinstance(e, dict)}
    new_map = {str(e.get("task_id")): e for e in fresh_entities if isinstance(e, dict)}
    drifts: list[str] = []
    for tid, ent in new_map.items():
        old = disk_map.get(tid)
        if old is None:
            drifts.append(f"missing_on_disk: {tid}")
            continue
        for k in ("window_expr", "window_type", "schedule_truth_source"):
            if str(old.get(k)) != str(ent.get(k)):
                drifts.append(f"{tid}.{k}: disk={old.get(k)!r} fresh={ent.get(k)!r}")
    for tid in disk_map:
        if tid not in new_map and disk_map[tid].get("status") != "orphaned_source":
            drifts.append(f"ghost_on_disk: {tid}")
    return drifts


def check_gate_availability(repo_root: Path | None = None) -> list[str]:
    """C-5：E0 日历/排班闸在场性探针 → 缺席原因清单（空=健康）。

    病灶（v2 方案 C-5）：闸/E0 缺席时三检查臂整体哑火——commit gate fail-closed 只在
    有人提交时叫，api_server fail-open，resource_schedule_alerts 静默。本探针由再生
    计划任务每小时自证"守卫还在岗"，且刻意不 import 闸取理由码（闸不在时取不到）。

    三层判定（层层依赖，前层失败即短路——后面判了也没意义）：
    ① 文件在场：闸模块 + E0 模块；
    ② 注册在册且 enabled：以 in_process_gate_registry.yaml 条目为真源（在册但
       enabled=false = gateway 永不加载，文件在场也是死闸）；
    ③ 可导入且符号齐备：按注册声明的 module_path/factory_function 经
       importlib.import_module 装载——与 GitCommitGateway 的加载方式同一口径，
       语法破损/依赖缺失在这里显形为 gate_import_failed（等同缺席，不静默）。
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    problems: list[str] = []
    if not (root / E0_MODULE_RELPATH).exists():
        problems.append(f"e0_module_missing: {E0_MODULE_RELPATH}")
    if not (root / GATE_MODULE_RELPATH).exists():
        problems.append(f"gate_module_missing: {GATE_MODULE_RELPATH}")
    if problems:  # 文件都不在，装载/注册层判定无意义（fail-closed 面不缩）
        return problems
    entry: dict | None = None
    try:
        data = yaml.safe_load((root / GATE_REGISTRATION_RELPATH).read_text(encoding="utf-8")) or {}
        hits = [g for g in (data.get("gates") or [])
                if isinstance(g, dict) and str(g.get("gate_id")) == GATE_ID]
        if not hits:
            problems.append(f"gate_unregistered: {GATE_ID} 不在 {GATE_REGISTRATION_RELPATH}（gateway 永不加载）")
        else:
            entry = hits[0]
            if not bool(entry.get("enabled", True)):
                problems.append(f"gate_disabled: {GATE_ID} 注册 enabled=false（在册但停用=死闸）")
    except Exception as exc:  # noqa: BLE001 — 注册目录读不动=无法自证在册，等同缺席
        problems.append(f"gate_registry_unreadable: {str(exc)[:160]}")
    if problems or not entry:
        return problems
    try:
        mod = importlib.import_module(str(entry.get("module_path")))
    except Exception as exc:  # noqa: BLE001 — gateway 装不上=缺席
        return problems + [f"gate_import_failed: {entry.get('module_path')}: {str(exc)[:160]}"]
    for sym in (str(entry.get("factory_function") or ""), "run_all_checks", "expand_windows"):
        if sym and not hasattr(mod, sym):
            problems.append(f"gate_symbol_missing: {sym}")
    try:
        e0 = mod._load_e0_module()  # E0 装载复用闸自己的通道（不另起炉灶防口径分裂）
        for sym in ("classify_window", "gate_decision"):
            if not hasattr(e0, sym):
                problems.append(f"e0_symbol_missing: {sym}")
    except Exception as exc:  # noqa: BLE001 — E0 装载失败=检查③ fail-closed 的那条腿也断了
        problems.append(f"e0_module_unloadable: {str(exc)[:160]}")
    return problems


def check_view_freshness(view_path: Path | str | None = None, registry_path: Path | str | None = None) -> list[str]:
    """C-10：周历视图新鲜度 → 过期原因清单（空=新鲜）。

    视图缺席/无指纹字段/指纹不符一律按过期报（"看不到"不等于"没问题"）。
    视图真渲染由日视图任务负责（24h 内自愈），故本码=warn 非 block。
    """
    vp = Path(view_path) if view_path else DEFAULT_VIEW
    rp = Path(registry_path) if registry_path else DEFAULT_OUTPUT
    label = str(vp)
    if not rp.exists():
        return [f"registry_missing_for_freshness: {rp}"]
    if not vp.exists():
        return [f"view_missing: {label}"]
    try:
        text = vp.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"view_unreadable: {label}: {exc}"]
    m = _RE_VIEW_SHA.search(text)
    if not m:
        return [f"view_no_{VIEW_SHA_KEY}_field: {label}（视图未内嵌真源指纹，新鲜度不可判）"]
    current = registry_content_sha(rp)
    if m.group(1) != current:
        return [
            f"view_stale: 视图内嵌 {VIEW_SHA_KEY}={m.group(1)} 现盘注册表={current}"
            "（待日视图发布任务重渲，24h 内自愈）"
        ]
    return []


def collect_check_findings(
    drifts: list[str],
    gate_problems: list[str],
    view_problems: list[str],
) -> list[SimpleNamespace]:
    """自检结果 → 告警桥 finding 对象（duck-typed，见下）。"""
    findings: list[SimpleNamespace] = []
    for p in gate_problems:
        findings.append(
            SimpleNamespace(reason_code=REASON_GATE_ABSENT, severity="block",
                            task_ids=["<schedule_chain>"], detail=f"排班闸缺席/不可解析：{p}", at=None)
        )
    for p in view_problems:
        findings.append(
            SimpleNamespace(reason_code=REASON_VIEW_STALE, severity="warn",
                            task_ids=["<resource_week_view>"], detail=p, at=None)
        )
    if drifts:
        head = "; ".join(drifts[:5])
        more = f" …（共 {len(drifts)} 条）" if len(drifts) > 5 else ""
        findings.append(
            SimpleNamespace(reason_code=REASON_DRIFT, severity="warn", task_ids=["<registry>"],
                            detail=f"注册表与三真源漂移 {len(drifts)} 条：{head}{more}", at=None)
        )
    return findings


def publish_check_findings(findings: list, board_dir: str | None = None) -> dict:
    """自检 findings → ops 告警板（唯一出口=OpsAlertFeed，本模块零通道自建）。

    告警线本身缺席时降级记日志不抛（INVARIANTS：告警线不得成为故障源）。
    空 findings 也必须调用——告警桥的解除联动正是靠"本轮未再触发"这一信号
    （提前 return 会让上一次报过的 stale 告警永远挂在板上）。
    """
    try:
        from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import publish_findings
    except Exception as exc:  # noqa: BLE001 — 告警桥缺席：退化为 stderr 留痕，绝不抛崩计划任务
        logger.warning("resource_schedule_alerts 不可用，告警降级留痕: %s", exc)
        return {"ops": [], "active_keys": [], "failed": str(exc)[:160]}
    try:
        return publish_findings(findings, board_dir=board_dir, module_id=REGEN_PUBLISHER_MODULE_ID)
    except Exception as exc:  # noqa: BLE001
        logger.warning("自检告警发布失败: %s", exc)
        return {"ops": [], "active_keys": [], "failed": str(exc)[:160]}


def main() -> int:  # noqa: C901
    ap = argparse.ArgumentParser(description="资源画像注册表生成器（MOD-RESCHED-PROFILE）")
    ap.add_argument("--check", action="store_true",
                    help="自检臂：漂移检测（实体集/window_expr 与磁盘比对）+C-5 闸在场性+C-10 视图新鲜度，不写")
    ap.add_argument("--publish-alerts", action="store_true",
                    help="与 --check 同用：自检 findings 落 ops 告警板（缺省 .runtime/ops_notifications/"
                         "，测试经 ZEPHYR_OPS_NOTIFICATION_DIR 重定向——不加旗标，板路径单源）")
    ap.add_argument("--auto-regen", action="store_true",
                    help="与 --check 同用：检出注册表漂移→就地全量再生（排产化零人工）")
    ap.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    ap.add_argument("--view", type=str, default=str(DEFAULT_VIEW), help="周历视图路径（新鲜度自检注入用）")
    ap.add_argument("--existing", type=str, default=None, help="合并保全的旧档路径（测试注入；缺省=output）")
    args = ap.parse_args()
    out = Path(args.output)
    existing_path = Path(args.existing) if args.existing else out
    registry = build_registry(existing_path=existing_path, output_path=out)
    if args.check:
        if not out.exists():
            print("DRIFT: 磁盘无注册表")
            return 2
        disk = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
        drifts = detect_registry_drift(list(disk.get("entities") or []), list(registry["entities"]))
        gate_problems = check_gate_availability()
        # 视图新鲜度只在被测注册表=生产注册表时判（临时注册表无视图，比了指纹也是噪音）
        view_problems = check_view_freshness(args.view, out) if out == DEFAULT_OUTPUT else []
        if drifts:
            print("DRIFT:")
            for d in drifts:
                print(" ", d)
        regen_summary: dict = {}
        if drifts and args.auto_regen:
            text = registry_text(registry)
            expected = content_sha256(out.read_text(encoding="utf-8")) if out.exists() else None
            out.parent.mkdir(parents=True, exist_ok=True)
            safe_write_text(out, text, expected_base_sha256=expected)
            disk_after = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
            drifts_after = detect_registry_drift(list(disk_after.get("entities") or []),
                                                 list(build_registry(existing_path=out, output_path=out)["entities"]))
            regen_summary = {
                "attempted": True,
                "drift_before": len(drifts),
                "drift_after": len(drifts_after),
                "total_entities": len(disk_after.get("entities") or []),
            }
            drifts = drifts_after
            # 再生改了注册表指纹→视图新鲜度必须重判（拿修复后的事实报警，不报旧账）
            if out == DEFAULT_OUTPUT:
                view_problems = check_view_freshness(args.view, out)
            print(f"AUTO-REGEN: {regen_summary}")
        findings = collect_check_findings(drifts, gate_problems, view_problems)
        for p in gate_problems:
            print(f"HEALTH[{REASON_GATE_ABSENT}]: {p}")
        for p in view_problems:
            print(f"HEALTH[{REASON_VIEW_STALE}]: {p}")
        if args.publish_alerts:
            pub = publish_check_findings(findings, board_dir=None)
            print(f"PUBLISH-ALERTS: ops={len(pub.get('ops', []))} keys={pub.get('active_keys')}")
        if not drifts and not findings:
            print(f"OK: 无漂移（{len(registry['entities'])} 实体）")
            return 0
        if drifts:
            return 2
        print(f"HEALTH: 注册表无漂移（{len(registry['entities'])} 实体），但 {len(findings)} 条健康码")
        return 3
    text = registry_text(registry)
    expected = None
    if out.exists():
        expected = content_sha256(out.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out, text, expected_base_sha256=expected)
    print(json.dumps({"ok": True, "total_entities": registry["total_entities"], "output": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
