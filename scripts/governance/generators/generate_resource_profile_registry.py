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
#   exclusive_group/status/notes_zh/measured.* 再生不丢）——唯一例外：pool 磁盘值不在执行器
#   词表（幽灵池/串维度）时回落本批派生值，人复核不得让幽灵池永生（C-7/R-C）;
#   pool 必在执行器实测泳道词表内（词表实测提取，禁硬编码；未知池阻断写出）;
#   C-15 实测对账臂只读且永不阻断再生（改表改不动操作系统任务表，差集只落健康码）;
#   L-5 演练臂只读真源：缺席/损坏=降级留痕（extraction_warnings），绝不让其余三源再生崩掉;
#   C-11 声明↔代码反查臂只读源码，finding 码 sched_gate_declaration_gap 仅出 stdout +
#   notes_zh 幂等哨兵标注（不入告警板/不计退出码，合流归主会话）;
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
# - id: I5
#   name: 执行器泳道词表真源（C-7）
#   fields: src/zephyr/data/scheduler.py executors 字典（池名+worker 数）; gov_audit/resource_aware_pool 空间维池
#   code: extract_executor_vocabulary, extract_audit_pool_namespace
# - id: I6
#   name: Windows 计划任务实测态（C-15，只读）
#   fields: schtasks /query /fo CSV（TaskName/Status）
#   code: query_schtasks, parse_schtasks_csv
# - id: I7
#   name: 应急演练排程真源（L-5，第 4 源）
#   fields: scripts/governance/meta/drill_schedule.yaml（frequency/day_of_month/months 第三种日期法）
#   code: parse_drill_entities
# - id: I8
#   name: 执行体源码（C-11 反查输入，只读）
#   fields: schedule_truth_source 直指 .py / ps1 动作链一跳 / data_slot_* 归 DataScheduler 宿主
#   code: resolve_executor_sources
# 层: 算法
# - id: A1
#   name_zh: ① 四源实体化
#   name_en: build_entities
#   intro: ps1 触发器→cron/事件窗档；槽位 cron 原样；演练排程（第三种日期法）→归一 cron；
#          手动/事件实体窗档=manual/event/dynamic
#   desc: resource_class 初值+trading_sensitive 按 E0 四值映射推导（local→light，local_gpu/mixed→heavy）；
#         演练无自动触发器→status=planned（R-D 不占闸内存和），起跑档先过备份窗避让
#   inputs: I1, I2, I3, I7
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
# - id: A5
#   name_zh: ⑤ 池词表校验（C-7/R-C）
#   name_en: check_pool_vocabulary
#   intro: 实体 pool 必须在执行器实测词表内；resource_class→pool 映射规则在本模块
#   desc: 幽灵池（历史 21 实体挂 light）与串用审计空间维池（cpu/gpu）=sched_pool_undeclared
#         block；合并保全对此开唯一例外（磁盘幽灵值回落派生值，人填其余字段照旧保全）；
#         写盘前置同一守卫，未知池阻断再生（宁可留漂移也不写脏词表）
#   inputs: I5, A1
#   outputs: sched_pool_undeclared findings
# - id: A6
#   name_zh: ⑥ 计划任务实测对账（C-15）
#   name_en: reconcile_sched_tasks
#   intro: 注册表 active 声明 ↔ schtasks 实测任务表差集
#   desc: active 但系统 Disabled=sched_task_disabled；有源无任务=sched_task_missing；
#         系统里有而表里没有=sched_task_orphan；探针读不动=sched_task_probe_unavailable
#         （降级不静默）；已登记待裁差集走 SCHED_TASK_EXEMPTIONS 豁免留痕（stdout 打印、
#         不落告警板）；本臂只读、永不阻断再生（改表改不动操作系统任务）
#   inputs: I6, A2
#   outputs: sched_task_* findings + 豁免留痕
# - id: A7
#   name_zh: ⑦ 声明↔代码受闸反查（C-11 第二半）
#   name_en: check_gate_declaration_gaps
#   intro: active 且申报 trading_sensitive 的实体 ↔ 其执行体源码是否真调用 E0 闸（纯存在性）
#   desc: 三态台账 gated/gap/unresolved（"查不动"与"查过没问题"分开留痕）；gap=纸面受管、
#         裸奔执行（lane_b 型）。finding 码 sched_gate_declaration_gap 只打 stdout + 幂等
#         notes_zh 哨兵标注（闸/告警桥的理由码清单归 P2-a，本会话禁自加码）——不入告警板、
#         不计退出码，待主会话合流后升格为健康码；本臂只读源码，永不阻断再生
#   inputs: A2, I8
#   outputs: gap findings（stdout）+ notes_zh 机器标注
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
# I7 --> A1
# I5 --> A5
# I6 --> A6
# A1 --> A2
# A2 --> A3
# A2 --> A6
# A2 --> A7
# I8 --> A7
# A7 --> O1
# A5 --> A3
# A6 --> A4
# A3 --> O1
# A1 --> A4
# I4 --> A4
# A4 --> O2
# A4 --> A3
"""generate_resource_profile_registry — 资源画像注册表生成器（MOD-RESCHED-PROFILE，B1 库）。

资源排班全景四件套之"库"的产出器（方案 §2.1 十八字段总表/§3 三层地图）。
把排班真源散落四处（register_*.ps1 / schedule.yaml / drill_schedule.yaml / E0 日历）收敛为
单一真源：config/resource_profile_registry.yaml（ROOR tier0 REG-RESCHED-001）。

四输入：
1. scripts/register_*.ps1 —— Windows 计划任务（任务名/触发器/时限/DISABLED 解析）；
2. src/zephyr/data/config/schedule.yaml —— DataScheduler 21 槽位（cron 原样抽取）；
3. MANUAL_ENTITY_SEED —— 方案 §3.C 手动/事件盲区实体清单（生成器内种子，时间真源
   指向方案文档直至有更正式真源；L-8 收编的触发型实体用可选键 `src` 把真源指针钉在
   自己的触发代码上）；
4. scripts/governance/meta/drill_schedule.yaml —— 应急演练定期排程（MOD-INF-005 §13.4，
   L-5 第 4 真源源：第三种日期法 frequency/day_of_month/months 在此归一为标准 cron）。

合并保全（A2）：再生按 task_id 合并——module_id/map_node_id/pool/peak_mem_gb/
est_duration_min/exclusive_group/status/notes_zh（人复核字段）与 measured.*/samples_uri
（采样器独占）原样保留；生成器自有字段（resource_class 初值/window_type/window_expr/
schedule_truth_source/trading_sensitive）刷新。真源消失的旧实体保留并标
status=orphaned_source（不静默删——删除是 Owner 门位）。

排产链自检臂（2026-09-17 P0，v2 方案 L-2/C-5/C-10——"再生"本身也是排产对象）：
`--check` 除比对四真源与现盘注册表，还顺带自检整条链是否活着：
- C-5 闸/E0/闸注册缺席 → `sched_gate_absent`（block；原先整条告警链在闸缺席时
  静默，本检测刻意放在闸之外——闸无法自证在场）；
- C-10 周历视图 rw-data.js 内嵌 registry_sha256 ≠ 注册表现盘指纹 →
  `sched_view_stale`（warn，下次日视图任务自愈）；
- `--publish-alerts` 经告警桥落 `.runtime/ops_notifications/notifications.jsonl`
  （发布方 module_id=`resource-schedule-regen`，与闸/视图发布方划界，互不解除）；
- `--auto-regen` 检出漂移→就地全量再生（"改真源→表跟上"零人工）。

池词表守卫（2026-09-17 P1-a，v2 方案 C-7/裁定 R-C）：pool 的合法值只有 DataScheduler
APScheduler 执行器字典里真实存在的泳道（实测提取，禁硬编码）。历史 21 实体挂的 `light`
是幽灵池——daily_crypto 事故自证：不存在的 executor 注册时不报错、触发时 job 被摘除，
该槽位自上线从未自动跑成过（见 src/zephyr/data/config/schedule.yaml:72 注释）。
幽灵池上的班次在闸的同窗求和里根本不存在，故 `sched_pool_undeclared`=block 且**写盘前置
同一守卫**：未知池绝不进注册表（合并保全为此开唯一例外，其余人填字段照旧不丢）。

计划任务实测对账（2026-09-17 P1-a，v2 方案 C-15，第 5 真源=Windows Task Scheduler）：
`schtasks /query /fo CSV` 只读拉实测任务表，与注册表"在册声明"作差集——
`sched_task_disabled`（声明 active 系统却禁用）/`sched_task_missing`（有源无任务）/
`sched_task_orphan`（系统里有而表里没有）/`sched_task_probe_unavailable`（探针降级，
不静默）。已登记待裁的差集走 SCHED_TASK_EXEMPTIONS 豁免表（stdout 打 EXEMPT 行留痕、
不落告警板）。本臂只读、永不阻断再生——注册表改不动操作系统的任务表。

演练排程收编（2026-09-17 P4-α，v2 方案 L-5，第 4 真源源）：MOD-INF-005 §13.4 的三类定期
演练本就是排班表，却用**第三种日期法**（frequency/day_of_month/months）在表外自转。本臂
把它归一为标准 cron（`parse_drill_entities`），实体 `drill_*` 与三源同权——合并保全、幂等
再生、孤儿标记、`--check` 漂移比对一视同仁。起跑档 04:00 由 `avoid_backup_window` 对备份
禁排窗（06:00-10:00 上包络）判避让；无法归一的频率降级为 `window_type=manual` 并出告警，
**不猜时间**。演练无自动触发器 → status=planned（R-D：未排产不占闸内存和）。

声明↔代码受闸反查（2026-09-17 P4-α，v2 方案 C-11 第二半）：C-15 治的是"ps1 声称↔系统
实际"，本臂治"注册表申报 trading_sensitive ↔ 执行体代码真问过闸吗"。执行体定位口径
（`resolve_executor_sources`）：真源直指 .py → ps1 动作链一跳 → data_slot_* 归 DataScheduler
宿主；源码里找不到闸调用形态（check_gate(/gate_decision(/runtime_e0_decision(）即
gap。**finding 码 `sched_gate_declaration_gap` 只打 stdout + 再生 notes_zh 幂等标注**——
闸与告警桥的理由码清单归 P2-a 所有，合流前不入告警板、不计退出码（不自加码造私码）。

用法:
  python scripts/governance/generators/generate_resource_profile_registry.py            # 生成
  python scripts/governance/generators/generate_resource_profile_registry.py --check    # 漂移+链健康自检
  python ... --check --publish-alerts --auto-regen                                       # 计划任务体（每小时）
  python ... --check --skip-schtasks                                                     # 离线/非 Windows 跳过实测臂
  python ... --check --schtasks-csv <path>                                               # 实测表以 CSV 注入（对账取证）
  python scripts/governance/generators/generate_resource_profile_registry.py --output <path>

退出码（register_resource_regen_check_task.ps1 消费契约）：
  0=健康；2=注册表与真源漂移（--auto-regen 后仍漂移才留 2；池词表守卫阻断写出时也留 2，
  此时不写盘——宁可带可见漂移也不把幽灵池写进表）；
  3=无漂移但有健康码（闸缺席/视图过期/幽灵池/实测差集——不触发再生，只告警）。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import logging
import re
import subprocess
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

# 自检臂理由码字面量——清单真源=resource_schedule_gate，此处必须自带字面量：
# C-5 的因果就是"闸不在场时还要能报警"，import 闸取码会让告警链在自己该说话的
# 那一刻哑火。一致性由 tests/infrastructure/test_resource_schedule_regen_check.py 锁死。
REASON_DRIFT = "sched_truth_drift"
REASON_GATE_ABSENT = "sched_gate_absent"
REASON_VIEW_STALE = "sched_view_stale"
# C-7（2026-09-17 P1-a）：pool 词表违规（幽灵池/串审计空间维池/词表真源读不动）
REASON_POOL_UNDECLARED = "sched_pool_undeclared"
# C-15（2026-09-17 P1-a）：schtasks 实测对账三码 + 探针缺席降级码
REASON_TASK_DISABLED = "sched_task_disabled"
REASON_TASK_MISSING = "sched_task_missing"
REASON_TASK_ORPHAN = "sched_task_orphan"
REASON_TASK_PROBE = "sched_task_probe_unavailable"
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

# pool 词表治理（2026-09-17 P1-a，v2 方案 C-7/裁定 R-C）——执行器真实词表**实测提取**，
# 不硬编码：真源=DataScheduler 的 APScheduler 执行器字典（src/zephyr/data/scheduler.py
# init_scheduler）。历史事故自证（daily_crypto）：schedule.yaml 把 executor 写成不存在
# 的 `light`，APScheduler 注册时不校验、触发时 "Executor lookup failed" 直接摘除 job，
# 该槽位自上线从未自动跑成过（水位全靠手动）——真源注释见
# src/zephyr/data/config/schedule.yaml:72。故 light 是**幽灵池**：注册表里挂它的实体
# 等于在一条不存在的泳道上排班（v2 裁定 R-C：幽灵池先治再排班，P3 前置）。
#
# 另一套同名池词表在 zephyr.gov_audit.resource_aware_pool（cpu/gpu 双池）——那是审计
# 准入的**空间维**池（v2 方案 C-6 同名认知风险），永不作为排班泳道值，故列入
# AUDIT_POOL_NAMESPACE 反向校验（注册表出现 cpu/gpu=把空间维当时间维，同样是词表违规）。
EXECUTOR_SOURCE_RELPATH = "src/zephyr/data/scheduler.py"
AUDIT_POOL_SOURCE_RELPATH = "src/zephyr/gov_audit/resource_aware_pool.py"
AUDIT_POOL_NAMESPACE = frozenset({"cpu", "gpu"})
# 兜底词表：仅在执行器真源不可读时用于**不阻断再生**（同时必发 sched_pool_vocab_unreadable
# 健康码——降级永不静默）
FALLBACK_POOL_VOCAB = ("default", "heavy", "realtime", "intraday_minute", "intraday_sector")

# schedule.yaml executor → pool：五档真池原样（不再裁剪 intraday_*→realtime，
# 泳道=真实争抢组；未知值→default 且必发词表 finding）
EXECUTOR_TO_POOL: dict[str, str] = {name: name for name in FALLBACK_POOL_VOCAB}

# resource_class → pool 映射规则（v1 公理：映射层在本生成器，E0/执行器真源不动）。
# 盘中高频/常驻轻守护统一落 default（8 线程通用池=无争抢档）；重算力落 heavy；
# 真·盘中实时槽位由 executor 原值承载（EXECUTOR_TO_POOL 直通），不走本表。
RESOURCE_CLASS_TO_POOL: dict[str, str] = {
    "cpu_heavy": "heavy",
    "gpu": "heavy",
    "db_heavy": "heavy",
    "llm_api_local": "heavy",
    "llm_api_paid": "default",
    "network_download": "default",
    "light": "default",
}
DEFAULT_POOL = "default"

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
    # --- L-8 收编（2026-09-17 P4-α）：唯一漏网的"自动触发重活"——新模型入库即 Quick 考试 ---
    {"task_id": "event_model_exam_trigger", "cn": "触发式考试调度器（ModelDiscovery 见新模型→自动 Quick 考试 39 次推断，经本地 Ollama 吃 GPU）"
                                                 "｜窗档=event 参照 sch_resource_regen_check 先例（无 cron 可抽，触发即开工）"
                                                 "｜盘中拒跑守卫自 v2 C-3 起单源引 E0 compute_window_gate"
                                                 "｜申报=单批 3 模型上限（每模型 Quick 约 6-8min）",
     "class": "llm_api_local", "dmin": 30, "mem": 2.0, "grp": ["llm_local"], "wt": "event",
     "src": "src/zephyr/intelligence/model_profiling/exam_trigger_scheduler.py"},
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
        # measured 段真源=采样器（本模块只声明骨架，值由 writeback CAS 写入并合并保全）
        # no_sample_reason_zh（2026-09-17 L-1）：零样本实体的如实原因——"取不到实测"是
        # 事实、不是缺陷，编造数值才是缺陷；采样器 [MODIFY-GUARD] 双向同步此子键。
        "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0,
                     "last_at": None, "no_sample_reason_zh": None},
        "samples_uri": f".runtime/logs/resource_samples/{task_id}.jsonl",
        "status": "planned",
        "notes_zh": cn,
    }


# ---------------------------------------------------------------------------
# ①′ 池词表（C-7/裁定 R-C）：执行器真实泳道词表实测提取 + 校验
# ---------------------------------------------------------------------------
def _balanced_brace_block(text: str, open_idx: int) -> str:
    """从 text[open_idx]=='{' 起取配对大括号体（不含外层括号）。"""
    depth = 0
    for i in range(open_idx, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : i]
    return ""


_RE_EXECUTOR_NAME = re.compile(r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*:\s*\w*Executor\s*\(\s*(\d+)')


def extract_executor_vocabulary(path: Path | None = None) -> tuple[dict[str, int], list[str]]:
    """C-7 词表实测提取：DataScheduler APScheduler 执行器字典 → {池名: worker 数}。

    真源=src/zephyr/data/scheduler.py init_scheduler 的 executors={...} 块。读侧只读、
    且用文本解析而非 import——scheduler.py 一装载就拉起 APScheduler/CH 依赖，自检臂必须
    在最脏的环境里也能跑。返回 (词表, 问题清单)；提取失败=空表+问题，调用方降级到
    FALLBACK_POOL_VOCAB 并**必发** sched_pool_undeclared 健康码（降级永不静默）。
    """
    problems: list[str] = []
    p = Path(path) if path else REPO_ROOT / EXECUTOR_SOURCE_RELPATH
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {}, [f"executor_source_unreadable: {p}: {exc}"]
    i = text.find("executors=")
    if i < 0:
        return {}, [f"executor_source_no_match: {p} 未见 executors= 字典（执行器词表口径变更须同步本生成器）"]
    j = text.find("{", i)
    if j < 0:
        return {}, [f"executor_source_no_match: {p} executors= 后无字典体"]
    body = _balanced_brace_block(text, j)
    pairs = _RE_EXECUTOR_NAME.findall(body)
    if not pairs:
        return {}, [f"executor_source_no_match: {p} executors 字典内无可识别 *Executor(n) 条目"]
    return {name: int(n) for name, n in pairs}, problems


_RE_AUDIT_POOL = re.compile(r"self\._([a-z]+)_pool\s*=\s*ThreadPoolExecutor")


def extract_audit_pool_namespace(path: Path | None = None) -> tuple[set[str], list[str]]:
    """提取审计准入侧的**空间维**池名（gov_audit/resource_aware_pool 的 cpu/gpu 双池）。

    v2 方案 C-6 同名认知风险的机检化：这套池回答"任务落到哪台算力"，排班 pool 回答
    "时间窗落在哪条泳道"——两套词表永不相同，注册表出现其中之一=串维度（违规）。
    """
    p = Path(path) if path else REPO_ROOT / AUDIT_POOL_SOURCE_RELPATH
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return set(AUDIT_POOL_NAMESPACE), [f"audit_pool_source_unreadable: {p}: {exc}"]
    names = {m for m in _RE_AUDIT_POOL.findall(text)}
    return (names or set(AUDIT_POOL_NAMESPACE)), []


def pool_vocabulary() -> tuple[set[str], list[str]]:
    """排班 pool 合法词表（执行器实测提取）+ 提取问题清单（降级时非空）。"""
    vocab, problems = extract_executor_vocabulary()
    if not vocab:
        vocab = {name: 0 for name in FALLBACK_POOL_VOCAB}
    return set(vocab), problems


def derive_pool(resource_class: str, declared: str | None = None, executor: str | None = None) -> str:
    """pool 派生规则（映射层在本生成器——v1 公理：E0/执行器真源不动，表与模块不互抄）。

    优先序：显式声明（人复核/ps1 特化表）→ schedule.yaml executor 原值 → 类映射 → 兜底。
    刻意**不洗值**：未知声明原样透传，让 check_pool_vocabulary 抓到并阻断再生——
    在这里悄悄改成合法池等于把违规抹平，词表校验就永远只对着空气报警。
    """
    if declared:
        return str(declared)
    if executor:
        mapped = EXECUTOR_TO_POOL.get(executor)
        if mapped:
            return mapped
        return str(executor)  # 未知 executor 原样透传（daily_crypto 的 light 就是这样混进来的）
    return RESOURCE_CLASS_TO_POOL.get(resource_class, DEFAULT_POOL)


def check_pool_vocabulary(entities: list[dict]) -> list[dict]:
    """C-7 词表校验：实体 pool 不在执行器真实词表（或串用审计空间维池）→ finding。

    幽灵池（历史 21 实体挂 `light`）=在一条不存在的泳道上排班，同窗并发求和全错，
    故本码 severity=block；main() 写盘前置同一函数——未知池阻断再生。
    """
    vocab, problems = pool_vocabulary()
    audit_ns, audit_problems = extract_audit_pool_namespace()
    out: list[dict] = []
    for p in problems:  # 词表读不动也必须能报警（降级不静默）
        out.append({"reason_code": REASON_POOL_UNDECLARED, "severity": "warn",
                    "task_ids": ["<executor_vocabulary>"], "detail": p})
    for p in audit_problems:
        out.append({"reason_code": REASON_POOL_UNDECLARED, "severity": "warn",
                    "task_ids": ["<audit_pool_vocabulary>"], "detail": p})
    for e in entities:
        if not isinstance(e, dict):
            continue
        pool = str(e.get("pool") or "")
        if pool in vocab:
            continue
        tid = str(e.get("task_id") or "?")
        cls = str(e.get("resource_class") or "")
        if pool in audit_ns:
            detail = (f"{tid}.pool={pool!r} 串用了审计准入的空间维池（{AUDIT_POOL_SOURCE_RELPATH} "
                      f"{sorted(audit_ns)} 双池）——排班泳道词表={sorted(vocab)}（v2 C-6/C-7）")
        else:
            detail = (f"{tid}.pool={pool!r} 不在执行器真实词表 {sorted(vocab)}"
                      f"（幽灵池；daily_crypto 事故实证=不存在的 executor 在触发时 job 被摘除，"
                      f"排班等于没排；class={cls} 应挂 {derive_pool(cls)!r}，v2 C-7/R-C）")
        out.append({"reason_code": REASON_POOL_UNDECLARED, "severity": "block",
                    "task_ids": [tid], "detail": detail})
    return out


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
#
# pool 值纪律（2026-09-17 P1-a，v2 方案 C-7/裁定 R-C）：本表历史上给 20 个任务填了
# `light`——执行器字典里根本没有这条泳道。事故自证（daily_crypto）：schedule.yaml 的
# executor 写成不存在的 `light`，APScheduler 注册不校验、每日 08:30 触发时
# "Executor lookup failed" 并摘除 job——该槽位自上线从未自动跑成过（水位全靠手动），
# 2026-09-16 才治本（真源注释 src/zephyr/data/config/schedule.yaml:72）。
# 幽灵池上的排班=纸面排班，同窗求和必错，故 R-C 把 C-7 列为 P3 重排班的前置。
# 改挂规则（映射规则归本生成器，v1 公理；词表实测提取见 pool_vocabulary）：
#   重算力/常驻本地 LLM（cpu_heavy/gpu/db_heavy/llm_api_local）→ heavy（2 线程串行档）
#   真·盘中会话争抢（贯穿交易时段的采集/模拟盘）→ realtime
#   其余轻守护与 one-shot 批 → default（8 线程通用池）
# 新填未知池由 check_pool_vocabulary 阻断再生并出健康码（sched_pool_undeclared）。
PS1_TASK_OVERRIDES: dict[str, dict] = {
    "FactoryLaneC": {"class": "cpu_heavy", "pool": "heavy", "mem": 2.0, "dmin": 240, "grp": ["mine_vs_exam"], "status": "active"},
    "C4Exam": {"class": "cpu_heavy", "pool": "heavy", "mem": 2.0, "dmin": 240, "grp": ["mine_vs_exam"], "status": "active"},
    "F06Grid": {"class": "cpu_heavy", "pool": "heavy", "mem": 4.0, "dmin": 240, "grp": [], "status": "active",
                "note": "周六 14:00 批 A census+批 B subspace（factory_grid_executor×2，4ea29d816f；与 C4Exam 同刻——错窗处置待 Owner/资源线裁）"},
    "OllamaServe": {"class": "llm_api_local", "pool": "heavy", "mem": 8.0, "dmin": 0, "grp": ["gpu_default"], "status": "active", "wt": "event",
                    "note": "AtLogOn 常驻（est=0 表示常驻）；qwen3:8b 显存/内存驻留"},
    "PatternMining": {"class": "light", "pool": "default", "mem": 1.0, "dmin": 5, "status": "active"},
    "PaperSession": {"class": "light", "pool": "realtime", "mem": 1.0, "dmin": 30, "status": "active",
                     "note": "09:25 起贯穿盘中时段的模拟盘会话 → realtime 泳道（live_strategy_biz 第 4 通道）"},
    "IntradayFundFlow": {"class": "light", "pool": "realtime", "mem": 0.5, "dmin": 10, "status": "active"},
    "IndexMinuteEOD": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 10, "status": "active",
                       "note": "15:10 收盘后 EOD，不与盘中争抢 → default"},
    "PostSettlement": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 10, "status": "active",
                       "note": "工作日 15:30 盘后结算 → default"},
    "DataScheduler": {"class": "light", "pool": "default", "mem": 1.5, "dmin": 0, "status": "active", "wt": "event",
                      "note": "AtLogOn 常驻守护（est=0 表示常驻）；21 个 data_slot 的宿主进程——"
                              "采样器宿主归因锚点=SLOT_HOST_TASK_ID（L-1 pid join）"},
    "TickSubscriber": {"class": "light", "pool": "realtime", "mem": 1.5, "dmin": 0, "status": "active", "wt": "event",
                       "note": "AtLogOn 常驻（est=0）；盘中高频 WAL 写 → realtime"},
    "CHHealthProbe": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "DeadmanSwitch": {"class": "light", "pool": "default", "mem": 0.3, "dmin": 1, "status": "active", "wt": "event"},
    "ProcessReaper": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "WorktreeDriftWatchdog": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event"},
    "RSSHub": {"class": "light", "pool": "default", "mem": 0.8, "dmin": 0, "status": "active", "wt": "event", "note": "AtLogOn 常驻（pm2 resurrect，est=0 表示常驻）"},
    "TraeCacheCleanup": {"class": "light", "pool": "default", "mem": 0.3, "dmin": 5, "status": "active", "wt": "event"},
    "TradingWatchdog": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 5, "status": "retired", "wt": "event",
                        "note": "注册为 DISABLED（裁定 INT-03：Owner 手动启用才生效）——"
                                "C-15 schtasks 实测臂的现役对账样本（实测确为 Disabled，与退役一致=零告警）"},
    "ResourceSamplerScan": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 1, "status": "active", "wt": "event",
                            "note": "AtLogOn+PT10M one-shot 采样扫描（2026-09-16 生产接线：register_resource_sampler_scan_task.ps1）"},
    "ResourceSamplerWriteback": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 1, "status": "active",
                                 "note": "日 05:40 measured 回写（git 跟踪文件日更一次，derived-sync 例行吸收）"},
    # 2026-09-17 P0（v2 方案 L-2 再生排产化）：把"再生"本身排进班次——两个新任务
    # 由本生成器自己的 ps1 真源源物化为实体（吃自己狗粮，active 计入闸内存求和）
    "ResourceRegenCheck": {"class": "light", "pool": "default", "mem": 0.5, "dmin": 2, "status": "active", "wt": "event",
                           "note": "每小时排产自检+漂移就地再生+C-5/C-10/C-7/C-15 告警发布（register_resource_regen_check_task.ps1；"
                                   "cadence=注册后 Post-Registration 补 PT1H 重复，ps1 静态文本无 cron 可抽→event，"
                                   "与 ResourceSamplerScan 同型先例）"},
    "ResourceViewPublish": {"class": "light", "pool": "default", "mem": 1.0, "dmin": 5, "status": "active",
                            "note": "日 05:50 周历重渲+闸 findings 告警发布（register_resource_view_publish_task.ps1；"
                                    "排在采样器回写 05:40 之后——视图吃 measured 回写结果）"},
}


def _iter_ps1_code(ps1_paths: list[Path] | None = None) -> list[tuple[Path, str | None, str]]:
    """register_*.ps1 → [(路径, 去注释正文, 读失败原因)]（I1 实体臂与 C-15 对账臂共用口径）。

    "只在登记语境匹配（跳过注释行里的 Verify/schtasks 提示）"这条规则必须单源：两臂各扫
    各的会口径分裂，注释里的示例任务名会被其中一臂当成真实声明。
    """
    out: list[tuple[Path, str | None, str]] = []
    for ps1 in sorted(ps1_paths or (REPO_ROOT / "scripts").glob(PS1_GLOB)):
        try:
            text = ps1.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            out.append((ps1, None, str(exc)))
            continue
        # 只在登记语境匹配（跳过注释行里的 Verify/schtasks 提示）
        code_lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
        out.append((ps1, "\n".join(code_lines), ""))
    return out


def parse_ps1_entities(ps1_paths: list[Path] | None = None) -> tuple[list[dict], list[str]]:
    """解析 register_*.ps1 → sch_* 实体草稿（任务名集合+逐任务分段触发器抽取）。

    返回 (实体, 警告)；跨文件同名任务取首见并告警。
    """
    warnings: list[str] = []
    entities: list[dict] = []
    seen_tasks: dict[str, str] = {}
    for ps1, code, err in _iter_ps1_code(ps1_paths):
        if code is None:
            warnings.append(f"ps1 不可读 {ps1.name}: {err}")
            continue
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
            ent["pool"] = derive_pool(ent["resource_class"], ov.get("pool"))
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
# ①‴ C-15 实测对账臂（第 5 真源=Windows Task Scheduler，只读）
# 病灶（v2 方案 C-15）：注册表过去只对 **文本真源**（ps1/schedule.yaml）负责，而"任务是否
# 真的挂在系统里、是否被禁用"从无第二方核验——register_*.ps1 写得再漂亮，任务被
# 禁用/被删/从未注册，排班就是纸面文章（实测 2026-09-17：系统共 229 条任务、其中
# ZephyrAlpha_* 37 条，ps1 声称 22 条里 1 条查无此任务（PatternMining），另有 5 条系统在册
# 而注册表完全不认识（4 条实验遗留 + WeeklyRest），6 条处于 Disabled）。
# 纪律：本臂**只读**（schtasks /query，零写系统），且永不阻断再生（再生改不动操作系统的
# 任务表）——差集全落 check 臂健康码，复用 P0 的 collect_check_findings/告警码机制。
# 任务名 → 实体 task_id 的推导与 I1 实体臂同源（_RE_TASKNAME + _snake），不另立第二套
# 命名规则；无 register_*.ps1 真源的直注册任务（dash 命名/launch_hidden.vbs 直挂）由
# OPS_TASK_ALIASES 显式收编——这是"抽取知识"（与 PS1_TASK_OVERRIDES 同类），不是清单副本。
# ---------------------------------------------------------------------------
ZA_TASK_PREFIXES = ("ZephyrAlpha_", "ZephyrAlpha-")

# 实测任务名 → 注册表 task_id（I1 正则看不到的直注册任务；ops_* 种子实体的系统侧锚点）
OPS_TASK_ALIASES: dict[str, str] = {
    "ZephyrAlpha-DailyBackup": "ops_daily_backup",
    "ZephyrAlpha-WeeklyVMBackup": "ops_weekly_vm_backup",
    "ZephyrAlpha-CH-OptimizeMerge-Weekly": "ops_ch_optimize_merge_weekly",
    "ZephyrAlpha-IOCheck-Monthly": "ops_io_check_monthly",
    "ZephyrAlpha-AI-Wrapper-Inject": "ops_ai_wrapper_inject",
    "ZephyrAlpha_TTLRejudgeDaily": "ops_ttl_rejudge_daily",
    "ZephyrAlpha_QMTWatchdog": "ops_qmt_watchdog",
    "ZephyrAlpha_BdpanTickWatch": "ops_bdpan_tick_watch",
    "ZephyrAlpha_BoardIndexRealtime": "ops_board_index_realtime",
    "ZephyrAlpha_SectorSnapshot": "ops_sector_snapshot",
    # 注意：**不**收编 ZephyrAlpha_NightlySentiment——该 job 的现役真源是 schedule.yaml:169
    # （cron 20 8 * * *，executor default）在数据调度器进程内触发，挂 OS 任务名上去会让
    # 对账臂误报"active 却 Disabled=纸面班次"。那条已退役 OS 残余见 SCHED_TASK_EXEMPTIONS。
}

# 已知差集豁免（留痕，不静默：main 仍打 EXEMPT 行到 stdout，只是不落告警板/不计入退出码）。
# 判据：登记在方案文档且处置权在本臂之外（Owner 门位/他会话线），本会话禁改活任务。
SCHED_TASK_EXEMPTIONS: dict[str, dict] = {
    "ZephyrAlpha_C4Exam_Full0916": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "2026-09-16 全量重跑实验遗留（每日 17:30 调 run_c4_exam.ps1 全量），"
                     "禁用/删除/转正=Owner 门位（docs/_working/automation/"
                     "20260917_automation_linkage_plan_v1.md §待裁-4）",
    },
    "ZephyrAlpha_C4Exam_OneShot0915": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "2026-09-15 一次性重跑实验遗留（每日 17:30），同上 §待裁-4",
    },
    "ZephyrAlpha_FactoryLaneC_Full0916": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "2026-09-16 全量重跑实验遗留（每日 15:35 调 run_factory_lane_c.ps1 全量），"
                     "与正式 sch_factory_lane_c 重复跑同一条线，同上 §待裁-4",
    },
    "ZephyrAlpha_FactoryLaneC_OneShot0915": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "2026-09-15 一次性重跑实验遗留（每日 15:35），同上 §待裁-4",
    },
    # 有源无任务：ps1 在、实体 active，系统里没有——报警是它的本职，但已登记给图形库线核对
    # （§待裁-5），此处豁免到该线回复；删掉本行即恢复每小时告警（不留静默黑洞）。
    "ZephyrAlpha_PatternMining": {
        "reason_code": REASON_TASK_MISSING,
        "reason_zh": "register_pattern_mining_task.ps1 在、注册表实体 active，Task Scheduler 无此任务"
                     "（20260917 联动方案 §待裁-5 已登记图形库线核对是否重挂）",
    },
    # OPS_TASK_ALIASES 注释承诺的"已退役 OS 残余"落地点（2026-09-17 P1-a 补：注释在册、
    # 表内缺条目=孤儿误报，且 --check 永远退不出 0）。
    "ZephyrAlpha_NightlySentiment": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "OS 侧已退役残余（实测 Disabled）：该 job 的现役真源是 schedule.yaml:169"
                     "（cron 20 8 * * *，executor default），由数据调度器进程内触发，注册表已以"
                     " data_slot_nightly_sentiment(active) 在册。不收编进别名（否则 active 实体挂"
                     "Disabled OS 名=误报纸面班次，见 OPS_TASK_ALIASES 注释），删除本条 OS 任务即"
                     "可彻底销项——删任务=Owner 门位，本会话禁改活任务",
    },
    "ZephyrAlpha_WeeklyRest": {
        "reason_code": REASON_TASK_ORPHAN,
        "reason_zh": "真孤儿但**不在本臂销项**：scripts/ops/weekly_rest_guard.ps1 周日 05:00 关机"
                     "（Owner 2026-09-17 全批点头，docs/_working/automation/20260917_fullauto_"
                     "skeleton_v1.md 要求「排班表登记」），无 register_*.ps1 真源故 I1 抽不到。"
                     "不随手挂 ops_* 种子：关机房保养窗在现模型里无法如实表达——它是全机 "
                     "blackout（谁都不许跑），而 GROUPS 无 rest/blackout 档、peak_mem_gb 求和"
                     "会把「关机」当成「零内存占用的普通班次」，登记错比不登记更危险（闸会据此"
                     "放行同窗重活）。移交 P3 全局重排班：先定 blackout 窗建模（新增 "
                     "exclusive_group 档或独立 rest 实体语义），再由落地线登记",
    },
}

_RE_DISABLED_TOKEN = re.compile(r"(?i)^(disabled|disable)|禁用|已停止")


def _schtasks_norm_name(raw: str) -> str:
    """CSV TaskName 单元格 → 规范任务名（去引号/去根目录前缀 `\\`/去空白）。"""
    s = str(raw or "").strip().strip('"').strip()
    s = re.sub(r"^[\\/]+", "", s)
    return s


def parse_schtasks_csv(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """`schtasks /query /fo CSV` 正文 → ({任务名: [状态,…]}, 问题清单)。

    真实形态的三个坑（实测 2026-09-17）：① 每个目录块都重印一遍表头，表头必须按内容
    判定跳过而不是只跳第 0 行；② TaskName 带根目录前缀 `\\`；③ 状态列随系统显示语言
    变化（EN=Ready/Running/Disabled，ZH=…/已禁用），故禁用判定按多样 token，未知状态
    一律按"未禁用"处理（宁可漏报也不误报停用——停用的判据必须肯定）。
    """
    problems: list[str] = []
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or not rows[0] or str(rows[0][0]).strip().strip('"').lower() != "taskname":
        problems.append("schtasks_csv_unparsed: 首行不是 TaskName 表头（输出形态变更须同步本解析器）")
    live: dict[str, list[str]] = {}
    short_rows = 0
    for r in rows:
        if not r or not str(r[0]).strip():
            continue
        if str(r[0]).strip().strip('"').lower() == "taskname":  # 每目录块重印表头
            continue
        if len(r) < 3:
            short_rows += 1
            continue
        name = _schtasks_norm_name(r[0])
        if not name:
            continue
        status = str(r[2]).strip().strip('"')
        if status not in live.setdefault(name, []):
            live[name].append(status)
    if short_rows:
        problems.append(f"schtasks_csv_short_rows: {short_rows} 行列数不足已跳过")
    return live, problems


def query_schtasks(timeout_s: float = 60.0) -> tuple[dict[str, list[str]], list[str]]:
    """只读探针：PowerShell 包裹的 `schtasks /query /fo CSV` → 实测任务表。

    必须经 PowerShell 包裹并把 [Console]::OutputEncoding 强制为 UTF-8：Git Bash 直调会把
    `/fo` 当路径改写，且默认代码页(GBK) 会同时乱码状态列与把 Disabled 译成中文。
    探针失败（非 Windows/无权限/超时）=返回问题清单并由调用方降级——**降级永不静默**
    （C-15 的意义就是"有人在替排班表看门"，看门人缺席必须吭声）。
    """
    cmd = [
        "powershell", "-NoProfile", "-Command",
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; schtasks /query /fo CSV",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout_s)
    except FileNotFoundError:
        return {}, ["schtasks_probe_unavailable: 无 powershell 可执行（非 Windows 环境）"]
    except Exception as exc:  # noqa: BLE001 — 探针任何异常都必须降级成健康码，不得抛崩计划任务
        return {}, [f"schtasks_probe_unavailable: {str(exc)[:160]}"]
    live, problems = parse_schtasks_csv(r.stdout or "")
    if r.returncode != 0 and not live:
        return {}, problems + [f"schtasks_probe_failed: rc={r.returncode} {str(r.stderr)[:160]}"]
    if r.returncode != 0:
        problems.append(f"schtasks_probe_partial: rc={r.returncode} 但取到 {len(live)} 条（差集判定按不完整表处理）")
    if not live:
        problems.append("schtasks_probe_empty: 实测任务表为空（不可能，判探针失效）")
        return {}, problems
    return live, problems


def collect_ps1_task_claims(ps1_paths: list[Path] | None = None) -> dict[str, str]:
    """register_*.ps1 声称的任务名 → 实体 task_id（与 I1 实体臂同规则，跨文件取首见）。"""
    claims: dict[str, str] = {}
    for _ps1, code, _err in _iter_ps1_code(ps1_paths):
        if not code:
            continue
        for name in _RE_TASKNAME.findall(code):
            short = name.replace("ZephyrAlpha_", "", 1)
            claims.setdefault(name, "sch_" + _snake(short))
    return claims


def reconcile_sched_tasks(
    entities: list[dict],
    live: dict[str, list[str]],
    claims: dict[str, str] | None = None,
    aliases: dict[str, str] | None = None,
    exemptions: dict[str, dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    """实测任务表 ↔ 注册表在册声明 对账 → (findings, 豁免留痕)。

    三类差集（v2 方案 C-15）：
    - `sched_task_disabled`：声明 active 却在系统里被禁用（排了班但没人开门）；
    - `sched_task_missing`：声明 active 且 ps1/别名在册，系统里查无此任务（纸面排班）；
    - `sched_task_orphan`：系统里在跑，注册表完全不认识（闸/视图/求和全都看不见它）。
    planned（画像已登记、行为零变更，方案 §8）与 retired/orphaned_source 实体**不期待**
    任务存在；退役实体挂 Disabled=一致，挂 Ready=孤儿（退役了还在跑）。
    """
    claims = collect_ps1_task_claims() if claims is None else claims
    aliases = OPS_TASK_ALIASES if aliases is None else aliases
    exemptions = SCHED_TASK_EXEMPTIONS if exemptions is None else exemptions
    by_tid = {str(e.get("task_id")): e for e in entities if isinstance(e, dict)}
    declared: dict[str, str] = {}
    for name, tid in list(claims.items()) + list(aliases.items()):
        declared.setdefault(name, tid)

    def _status_of(name: str) -> list[str]:
        return list(live.get(name) or [])

    def _disabled(names: list[str]) -> bool:
        return bool(names) and all(_RE_DISABLED_TOKEN.search(s or "") for s in names)

    findings: list[dict] = []
    exempted: list[dict] = []

    def _emit(code: str, name: str, tid: str, detail: str) -> None:
        ex = exemptions.get(name)
        if ex and str(ex.get("reason_code") or code) == code:
            exempted.append({"task_name": name, "task_id": tid, "reason_code": code,
                             "reason_zh": str(ex.get("reason_zh") or "")})
            return
        findings.append({"reason_code": code, "severity": "warn",
                         "task_ids": [tid if tid in by_tid else name], "detail": detail})

    for name, tid in sorted(declared.items()):
        ent = by_tid.get(tid)
        if ent is None:  # 声称在册但实体不在表里=表自己漏了（真源消失/命名漂移）
            _emit(REASON_TASK_MISSING, name, tid,
                  f"{name}: 真源声称实体 {tid} 不在注册表（再生未物化，须查 _RE_TASKNAME 命名口径）")
            continue
        status = str(ent.get("status") or "")
        if status not in ("active",):
            if status in ("retired", "orphaned_source") and name in live and not _disabled(_status_of(name)):
                _emit(REASON_TASK_ORPHAN, name, tid,
                      f"{name}: 注册表 status={status}（退役/真源消失）但系统实测 {sorted(_status_of(name))} 仍在跑"
                      "——纸面退役、现实在跑，闸与求和都看不见它")
            continue
        if name not in live:
            _emit(REASON_TASK_MISSING, name, tid,
                  f"{name}: 注册表 active（真源={ent.get('schedule_truth_source')}）但 Task Scheduler 查无此任务"
                  "——排了班却没开门，daily_crypto 型纸面排班（v2 C-15）")
            continue
        if _disabled(_status_of(name)):
            _emit(REASON_TASK_DISABLED, name, tid,
                  f"{name}: 注册表 active 但系统实测 Disabled——班次存在却永不触发（v2 C-15）")
    known = set(declared)
    for name in sorted(live):
        if not name.startswith(ZA_TASK_PREFIXES) or name in known:
            continue
        _emit(REASON_TASK_ORPHAN, name, name,
              f"{name}: 系统实测在注册（状态 {sorted(live[name])}）但注册表不认识它"
              "——无 ps1 真源/无别名收编，资源画像与冲突闸双双失明（v2 C-15）")
    return findings, exempted


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
        ent["pool"] = derive_pool(ent["resource_class"], executor=executor)
        if executor not in EXECUTOR_TO_POOL:
            warnings.append(
                f"undeclared_executor {name}: schedule.yaml executor={executor!r} 不在执行器真实词表"
                f"（daily_crypto 先例=APScheduler 触发时摘 job，任务从未自动跑成）"
            )
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
# ②‖ drill_schedule.yaml 排程（L-5：第 4 真源源=应急演练日程，2026-09-17 P4-α）
# 病灶（v2 方案 L-5）：MOD-INF-005 §13.4 的三类定期演练本来就是一张排班表（DOM+月列表
# 结构），但它在注册表之外自转——既不占预算也不进冲突视野，而且它用的是**第三种日期法**
# （frequency/day_of_month/months 三元组，既非 cron 也非 ps1 触发器）。不收编，就会有
# 第四、第五种日期法在别处野长（每种野法=一处永不与表对账的排班真源）。
# 纪律：与 I1/I2 同规——时间值只从真源抽、归一为标准 cron，人禁填；演练由人/Agent 按日程
# 执行、**无自动触发器**，故 status=planned（R-D：未排产不占闸内存和）。
# ---------------------------------------------------------------------------
DRILL_SCHEDULE_RELPATH = "scripts/governance/meta/drill_schedule.yaml"
# 演练起跑档：04:00 北京 wall time（与 ps1/schedule.yaml 同语义）。选此窗的三条理由全可判：
# ① 避开备份窗（BACKUP_WINDOW_GUARD）；② 落在 E0 盘外重算力黄金窗（00:00-09:00，
#    compute_window_gate.OPEN_BUFFER 口径）；③ 避开采样器回写 05:40 与视图发布 05:50。
DRILL_START_MINUTE_OF_DAY = 4 * 60
# 备份禁排窗——取上包络：日备份每日 06:00×60min、CH VM 周备份周六 06:00×240min（时刻真源
# =MANUAL_ENTITY_SEED 里 ops_daily_backup / ops_weekly_vm_backup 的实测备注）。按最坏那天
# 避总不会错（保守=宁可错避，不可错排：备份中途叠一份恢复演练会把演练变成真事故）。
BACKUP_WINDOW_GUARD: dict[str, int | str] = {
    "start_minute": 6 * 60,
    "end_minute": 10 * 60,
    "source_task_ids": "ops_daily_backup,ops_weekly_vm_backup",
}
# 逐演练申报特化（class/mem/dmin=申报初值，人可复核；与 PS1_TASK_OVERRIDES 同类抽取知识）
DRILL_OVERRIDES: dict[str, dict] = {
    "script_failure_drill": {"class": "light", "mem": 1.0, "dmin": 30},
    "emergency_bypass_drill": {"class": "light", "mem": 0.5, "dmin": 20},
    "recovery_drill": {"class": "light", "mem": 2.0, "dmin": 60},
}
_FREQUENCIES_WITH_DOM = ("monthly", "quarterly")


def avoid_backup_window(start_min: int, duration_min: int) -> tuple[int, bool]:
    """纯函数：演练窗 [start, start+duration) 落进备份禁排窗则整体移出。

    返回 (起始分钟, 是否发生避让)。避让方向=**后置到禁排窗尾之后**（盘外越晚越接近备份
    完成态，比提前更稳），并按 30min 档对齐。未落窗内原样返回——判得准才动，判不准不动。
    """
    lo = int(BACKUP_WINDOW_GUARD["start_minute"])  # type: ignore[arg-type]
    hi = int(BACKUP_WINDOW_GUARD["end_minute"])  # type: ignore[arg-type]
    dur = max(int(duration_min or 0), 0)
    if not (lo <= start_min < hi) and not (start_min < hi and start_min + dur > lo):
        return start_min, False
    return hi + (dur // 30) * 30, True


def normalize_drill_cron(spec: dict, start_min: int) -> tuple[str | None, str | None]:
    """演练排程（frequency/day_of_month/months 三元组）→ 标准 cron `m h dom mon dow`。

    第三种日期法在此收口成 cron（真源语义 1:1 平移，不发明时间值）。返回 (cron, 问题)：
    无法归一的频率（weekly/daily/未知/季频缺 months）→ (None, 说明)，由调用方降级为
    manual 窗档并出告警——**不猜时间**（猜出来的排班比没排班更危险）。
    """
    freq = str(spec.get("frequency") or "").strip().lower()
    hh, mm = divmod(int(start_min), 60)
    if freq not in _FREQUENCIES_WITH_DOM:
        return None, f"frequency={freq or '缺失'!r} 无法归一为 cron（本臂只收 月/季×DOM 法）"
    dom = spec.get("day_of_month")
    if dom is None:
        dom_field = "*"
    elif isinstance(dom, (list, tuple)):
        dom_field = ",".join(str(int(x)) for x in dom)
    else:
        dom_field = str(int(dom))
    months = spec.get("months")
    if isinstance(months, (list, tuple)) and months:
        mon_field = ",".join(str(int(x)) for x in months)
    elif freq == "monthly":
        mon_field = "*"
    else:
        return None, "quarterly 但未声明 months（季频无月列表=无法归一）"
    return f"{mm} {hh} {dom_field} {mon_field} *", None


def parse_drill_entities(path: Path | None = None) -> tuple[list[dict], list[str]]:
    """drill_schedule.yaml → drill_* 实体（L-5 第 4 真源源；文件缺席=告警不静默）。"""
    warnings: list[str] = []
    p = Path(path) if path else REPO_ROOT / DRILL_SCHEDULE_RELPATH
    if not p.exists():
        return [], [f"drill_source_missing: {p}（第 4 真源源缺席，演练排程不在视野）"]
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        # 本臂是新加的，缺席/损坏一律降级留痕（不抛崩既有三源再生——排产自检必须能说话）
        return [], [f"drill_source_unreadable: {p}: {str(exc)[:120]}"]
    drills = data.get("drills")
    if not isinstance(drills, dict) or not drills:
        return [], [f"drill_source_empty: {p} 无 drills 字典（结构变更须同步本解析器）"]
    entities: list[dict] = []
    for key, spec in drills.items():
        if not isinstance(spec, dict):
            warnings.append(f"drill_skipped {key}: 条目非 dict")
            continue
        ov = DRILL_OVERRIDES.get(str(key), {})
        cls = str(ov.get("class", "light"))
        dmin = int(ov.get("dmin", 30))
        start, shifted = avoid_backup_window(DRILL_START_MINUTE_OF_DAY, dmin)
        cron, why = normalize_drill_cron(spec, start)
        if why:
            warnings.append(f"drill_window_unnormalized {key}: {why}→窗档降级 manual（不猜时间）")
        ent = _base_entity("drill_" + _snake(re.sub(r"_drill$", "", str(key))),
                           str(spec.get("type") or key)[:40])
        ent["schedule_truth_source"] = DRILL_SCHEDULE_RELPATH
        ent["resource_class"] = cls
        ent["pool"] = derive_pool(cls, ov.get("pool"))
        ent["peak_mem_gb"] = ov.get("mem", 0.5)
        ent["est_duration_min"] = dmin
        ent["exclusive_group"] = list(ov.get("grp", []))
        ent["window_type"] = "cron" if cron else "manual"
        ent["window_expr"] = cron
        ent["status"] = "planned"  # 无自动触发器（按日程人工执行）→ R-D 不占闸内存和
        ent["trading_sensitive"] = cls in TRADING_SENSITIVE_CLASSES
        ent["notes_zh"] = (
            f"{spec.get('type') or key}｜排程真源 {DRILL_SCHEDULE_RELPATH}"
            f"（frequency={spec.get('frequency')}/day_of_month={spec.get('day_of_month')}"
            f"/months={spec.get('months')}→归一 cron）"
            f"｜时刻=生成器档 {DRILL_START_MINUTE_OF_DAY // 60:02d}:{DRILL_START_MINUTE_OF_DAY % 60:02d}"
            f"（避备份窗 {BACKUP_WINDOW_GUARD['source_task_ids']}）"
            + ("；已避让出备份窗" if shifted else "；未落备份窗")
            + f"｜源声明 module_id={data.get('module_id')}（L-6 map_node_id 灌数待挂）"
            + f"｜{str(spec.get('description') or '')[:60]}"
        )
        entities.append(ent)
    return entities, warnings


# ---------------------------------------------------------------------------
# ③ 手动/事件实体（§3.C 种子）
# ---------------------------------------------------------------------------
def manual_entities() -> list[dict]:
    """§3.C 盲区实体 → manual_*/event_*/dynamic_* 实体（时间真源=方案文档）。

    种子可选键 `src`=该实体自己的触发真源（缺省=方案文档）。L-8 收编的考试触发型实体用它
    把真源指针钉在触发代码上——C-11 声明↔代码反查臂据此定位执行体源码，不必另立第二套
    "实体→代码"映射（那会变成没人对账的私有清单）。
    """
    out: list[dict] = []
    for seed in MANUAL_ENTITY_SEED:
        ent = _base_entity(seed["task_id"], seed["cn"])
        ent.update(
            resource_class=seed["class"],
            pool=derive_pool(seed["class"]),
            peak_mem_gb=seed["mem"],
            est_duration_min=seed["dmin"],
            exclusive_group=list(seed["grp"]),
            window_type=seed["wt"],
            window_expr=None,
            schedule_truth_source=str(seed.get("src") or PLAN_DOC_REL),
            status="planned",  # 手动实体=画像已登记、行为零变更（方案 §8）
        )
        if seed["wt"] == "dynamic":
            ent["status"] = "planned"
        ent["trading_sensitive"] = ent["resource_class"] in TRADING_SENSITIVE_CLASSES
        out.append(ent)
    return out


# ---------------------------------------------------------------------------
# ③‖ C-11 声明↔代码反查臂（2026-09-17 P4-α，v2 方案 C-11 第二半）
# C-11 的两半：第一半"ps1 声称 ↔ schtasks 实际"差集已在 C-15 臂（本模块 A6）；本臂补
# 第二半——"申报受闸 ↔ 代码实闸"脱节。申报口径就是注册表自己的字段：
#   trading_sensitive=True ⟺ "本实体受 FAC-E0 算力窗闸管辖"（TRADING_SENSITIVE_CLASSES
#   映射出来的断言，方案 §2.1 定义）。断言写进了表，代码里却从没问过闸，那这一栏就是
#   自我安慰——lane_b 型事故的形状（纸面受管、裸奔执行）。
# 判定=纯存在性反查（grep 执行体源码是否调用所声明的闸），不做语义分析：报的是"根本没
# 问过闸"，不是"问得不对"（后者是 P2-c 运行时准入的活）。
# 纪律：本臂**只读源码、只出留痕**——finding 码 sched_gate_declaration_gap 尚未进闸/告警桥
#   的理由码清单（那两个文件归 P2-a 所有，本会话禁自加码），故 findings 只打生成器
#   stdout + 再生 notes_zh，不入告警板、不计退出码，移交主会话合流后再升格为健康码。
# ---------------------------------------------------------------------------
GAP_REASON_CODE = "sched_gate_declaration_gap"
# notes_zh 机器标注哨兵（幂等：每次反查先剥掉旧哨兵再按需追加，人写的正文永不被动）
GAP_NOTE_MARK = "〔生成器·C-11 声明↔代码反查〕"
_RE_GAP_NOTE = re.compile(r"\s*" + re.escape(GAP_NOTE_MARK) + r".*$", re.S)
# E0 闸的调用面——**只认调用形态，不认裸符号名**：注释/[DEPENDENCIES] 头里写一句
# "compute_window_gate" 就能把自己洗成已受闸的话，本臂就永远只对着空气点头（红蓝口径）。
_RE_GATE_CALL = re.compile(r"\bcheck_gate\s*\(|\bgate_decision\s*\(|\bruntime_e0_decision\s*\(")
_RE_SCRIPT_TOKEN = re.compile(r"[A-Za-z0-9_./\\-]+\.(?:py|ps1)")
_RE_DASH_M = re.compile(r"(?:^|\s)-m\s+([A-Za-z][A-Za-z0-9_.]*)")
_ROOT_TOKENS = ("scripts/", "src/")


def _norm_script_token(raw: str) -> str | None:
    """ps1 里的路径碎片 → 仓内相对路径（取最后一个 scripts//src/ 锚点，丢盘符/变量前缀）。

    `$RepoRoot\\scripts\\run_c4_exam.ps1`、`D:/ZephyrAlpha/scripts/x.py`、
    `scripts\\backtest\\y.py` 三种写法在此归一；锚点前的部分（变量名、盘符）一律是噪音。
    """
    s = str(raw or "").replace("\\", "/")
    cut = max((s.rfind(t) for t in _ROOT_TOKENS), default=-1)
    if cut < 0:
        return None
    rel = s[cut:]
    return rel if (REPO_ROOT / rel).exists() else None


def _ps1_chain_targets(text: str) -> list[str]:
    """一段 ps1/命令行文本 → 它拉起的仓内脚本清单（.py 直取 + .ps1 递归一跳 + -m 模块）。"""
    out: list[str] = []
    for tok in _RE_SCRIPT_TOKEN.findall(text):
        norm = _norm_script_token(tok)
        if norm and norm not in out:
            out.append(norm)
    for mod in _RE_DASH_M.findall(text):
        rel = "src/" + mod.replace(".", "/") + ".py"
        if (REPO_ROOT / rel).exists() and rel not in out:
            out.append(rel)
    for hop in [p for p in out if p.endswith(".ps1")]:
        try:
            sub = (REPO_ROOT / hop).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for tok in _RE_SCRIPT_TOKEN.findall(sub):
            norm = _norm_script_token(tok)
            if norm and norm.endswith(".py") and norm not in out:
                out.append(norm)
    return out


def resolve_executor_sources(ent: dict) -> tuple[list[str], str]:
    """实体 → (执行体源码仓内路径清单, 解析口径标签)。

    口径优先级：schedule_truth_source 直指 .py（L-8 收编实体走这条）→ ps1 真源动作链
    一跳（sch_* 全量）→ schedule.yaml 槽位归 DataScheduler 宿主（槽位的执行体就是它，
    21 槽位共用一个进程，逐槽找模块会找到天上去）→ 空表=反查不可达（不猜）。
    """
    src = str(ent.get("schedule_truth_source") or "")
    tid = str(ent.get("task_id") or "")
    if src.endswith(".py"):
        return ([src], "py_truth_source") if (REPO_ROOT / src).exists() else ([], "py_unreadable")
    if src.endswith(".ps1") and (REPO_ROOT / src).exists():
        try:
            text = (REPO_ROOT / src).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return [], "ps1_unreadable"
        targets = [p for p in _ps1_chain_targets(text) if p.endswith(".py")]
        return (targets, "ps1_chain") if targets else ([], "ps1_chain_empty")
    if tid.startswith("data_slot_"):
        host = EXECUTOR_SOURCE_RELPATH
        return ([host], "data_slot_host") if (REPO_ROOT / host).exists() else ([], "host_unreadable")
    return ([], "unresolved")


def check_gate_declaration_gaps(entities: list[dict]) -> tuple[list[dict], list[dict]]:
    """C-11 反查：active 且申报受闸（trading_sensitive）的实体 ↔ 执行体是否真问过闸。

    返回 (findings, 审计覆盖台账)。台账逐实体记 verdict∈{gated,gap,unresolved}——
    "查不动"与"查过没问题"必须分开留痕（降级不静默是本模块的一贯纪律）。
    """
    findings: list[dict] = []
    ledger: list[dict] = []
    for e in entities:
        if not isinstance(e, dict):
            continue
        if str(e.get("status")) != "active" or not bool(e.get("trading_sensitive")):
            continue
        tid = str(e.get("task_id") or "?")
        srcs, how = resolve_executor_sources(e)
        if not srcs:
            ledger.append({"task_id": tid, "verdict": "unresolved", "how": how, "sources": []})
            continue
        hits: list[str] = []
        unreadable: list[str] = []
        for rel in srcs:
            try:
                text = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                unreadable.append(rel)
                continue
            if _RE_GATE_CALL.search(text):
                hits.append(rel)
        if hits:
            ledger.append({"task_id": tid, "verdict": "gated", "how": how, "sources": hits})
            continue
        detail = (f"{tid}: 注册表申报 trading_sensitive=True（受 FAC-E0 算力窗闸管辖），"
                  f"但执行体源码未见闸调用（{'; '.join(srcs[:4])}"
                  + (f"，另有 {len(unreadable)} 个文件读不动" if unreadable else "")
                  + f"；解析口径={how}）——纸面受管、裸奔执行（v2 C-11，lane_b 型）。"
                  "修法=执行体开工前问 check_gate()，或如实改申报（trading_sensitive=false 须给理由）")
        findings.append({"reason_code": GAP_REASON_CODE, "severity": "warn",
                         "task_ids": [tid], "detail": detail})
        ledger.append({"task_id": tid, "verdict": "gap", "how": how, "sources": srcs})
    return findings, ledger


def annotate_gate_declaration_gaps(entities: list[dict], findings: list[dict]) -> None:
    """把反查结论幂等写进 notes_zh（就地改，无返回值）。

    notes_zh 是人复核字段（合并保全），所以本函数**先剥旧哨兵再按需追加**：人写的正文
    一字不动，机器尾巴随事实增删——闸补上了，哨兵下一轮自动消失；闸没补，哨兵年年重打。
    在 merge_preserve 之后调用（否则磁盘旧 notes_zh 会把标注盖回去，标注永远上不了表）。
    """
    gapped = {tid for f in findings for tid in (f.get("task_ids") or [])}
    for e in entities:
        if not isinstance(e, dict):
            continue
        notes = str(e.get("notes_zh") or "")
        stripped = _RE_GAP_NOTE.sub("", notes).rstrip()
        tid = str(e.get("task_id") or "")
        if tid in gapped:
            why = next((f.get("detail", "") for f in findings if tid in (f.get("task_ids") or [])), "")
            e["notes_zh"] = (stripped + " " if stripped else "") + GAP_NOTE_MARK + " " + why.split("——", 1)[-1][:180]
        elif GAP_NOTE_MARK in notes:  # 只剥旧哨兵：没标注的实体原样不动（None 不被改成空串）
            e["notes_zh"] = stripped


def report_gate_declaration_gaps(entities: list[dict]) -> int:
    """C-11 反查留痕（只打 stdout，不入 findings/告警板/退出码）→ gap 条数。

    为什么只到 stdout：`sched_gate_declaration_gap` 还没进闸与告警桥的理由码清单（那两份
    文件归 P2-a 所有，本会话禁自加码）——私码上板=造一条没人解除的哑警报。故这里只留痕，
    主会话合流后再升格为健康码（届时把它接进 collect_check_findings 即可，本函数不动）。
    """
    findings, ledger = check_gate_declaration_gaps(entities)
    for f in findings:
        print(f"GAP[{f['reason_code']}][{f['severity']}]: {f['detail']}")
    gated = sum(1 for l in ledger if l.get("verdict") == "gated")
    unresolved = sum(1 for l in ledger if l.get("verdict") == "unresolved")
    print(f"GAP-AUDIT: active 且申报受闸 {len(ledger)} 实体 → 代码实闸 {gated} / 声明缺口 {len(findings)}"
          f" / 反查不可达 {unresolved}（{GAP_REASON_CODE} 未入闸与告警桥清单：不计退出码，待主会话合流）")
    return len(findings)


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
    vocab, _vocab_problems = pool_vocabulary()  # 词表只读一次（实体循环内不重复开文件）
    merged: list[dict] = []
    seen: set[str] = set()
    for ent in fresh:
        tid = str(ent["task_id"])
        seen.add(tid)
        old = old_by_id.get(tid)
        if old:
            derived_pool = ent.get("pool")  # 本批派生值（合并前抓——下面会被磁盘值覆盖）
            for f in _HUMAN_FIELDS + _SAMPLER_FIELDS:
                if f in old and old[f] is not None:
                    ent[f] = old[f]
            # 唯一例外（2026-09-17 P1-a，v2 C-7/R-C）：pool 的"人复核保全"不能让
            # 幽灵池永生——磁盘挂 light/串维度池时回落到本批派生值并告警留痕。
            # 其余人填字段与 measured.* 双轨照旧原样保全（v1 公理不破）。
            preserved_pool = ent.get("pool")
            if preserved_pool is not None and str(preserved_pool) not in vocab:
                warnings.append(
                    f"ghost_pool_discarded: {tid} 保留值 pool={preserved_pool!r} 不在执行器词表"
                    f"→ 回落到派生值 {derived_pool!r}"
                )
                ent["pool"] = derived_pool if derived_pool else DEFAULT_POOL
            # 申报初值防回退：旧档人已填（非 None）则不覆盖初值
        merged.append(ent)
    for tid, old in old_by_id.items():
        if tid not in seen:
            old["status"] = "orphaned_source"
            old["notes_zh"] = str(old.get("notes_zh") or "") + "；[生成器] 真源消失，待 Owner 裁定删除"
            warnings.append(f"orphaned_source: {tid}")
            merged.append(old)
    return merged, warnings


def build_registry(existing_path: Path | None = None, output_path: Path | None = None) -> dict:
    """四源实体化+合并保全+C-11 反查标注 → 注册表 dict（不落盘，测试可断言）。"""
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
    drill_ents, w4 = parse_drill_entities()
    ents, w3 = merge_preserve(ps1_ents + slot_ents + drill_ents + manual_entities(), existing)
    # C-11 反查必须在合并保全**之后**：notes_zh 是人可复核字段，合并会用磁盘旧值覆盖机读值，
    # 标注写在前面就会被旧账吃掉（写在后面+哨兵幂等剥离 = 人写的正文永不被动）。
    gap_findings, _gap_ledger = check_gate_declaration_gaps(ents)
    annotate_gate_declaration_gaps(ents, gap_findings)
    workers, vocab_problems = extract_executor_vocabulary()
    audit_ns, audit_problems = extract_audit_pool_namespace()
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
        "counting_rule": "entities 数组条目数（生成器四源全量再生；条目禁手工增删）",
        "total_entities": len(ents),
        "field_count": 18,
        "mem_ceiling_gb": MEM_CEILING_GB,
        "mem_ceiling_source": "src/zephyr/trading/process_reaper.py _DANGEROUS_MEM_GB（引用不收编）",
        "groups": GROUPS,
        "pool_vocabulary": {
            "lanes": sorted(set(workers) or set(FALLBACK_POOL_VOCAB)),
            "workers": {k: int(v) for k, v in sorted(workers.items())},
            "source": EXECUTOR_SOURCE_RELPATH,
            "audit_namespace_excluded": sorted(audit_ns),
            "note": "pool=执行器真实泳道词表（实测提取，禁硬编码）；值不在 lanes 内即幽灵池"
                    "（daily_crypto 事故：不存在的 executor 在触发时被 APScheduler 摘 job，"
                    "任务从未自动跑成）——check 臂 sched_pool_undeclared 并阻断再生"
                    "（v2 方案 C-7/裁定 R-C）。audit_namespace_excluded=空间维池（回答"
                    "'落到哪台算力'），与时间维泳道同名不同物，注册表挂它=串维度（C-6）",
        },
        "extraction_warnings": sorted(
            list(w1) + list(w2) + list(w3) + list(w4) + list(vocab_problems) + list(audit_problems)
        ),
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
    """现盘注册表实体 vs 四真源重抽实体逐字段比对 → 漂移描述清单（空=无漂移）。

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


def to_findings(raw: list[dict]) -> list[SimpleNamespace]:
    """生成器内部 finding dict → 告警桥 duck-typed finding（SimpleNamespace）。

    刻意不 import 闸的 Finding：C-5 的教训——告警链不得依赖闸本体（闸不在场时正是它
    唯一能开口的时候），告警桥只 getattr 取值，SimpleNamespace 即契约。
    """
    return [
        SimpleNamespace(reason_code=str(f.get("reason_code")),
                        severity=str(f.get("severity") or "warn"),
                        task_ids=list(f.get("task_ids") or []),
                        detail=str(f.get("detail") or ""), at=None)
        for f in raw or []
    ]


def pool_block_violations(entities: list[dict]) -> list[dict]:
    """写盘前置守卫（C-7/R-C）：severity=block 的池违规——未知池不得进注册表。"""
    return [f for f in check_pool_vocabulary(entities) if str(f.get("severity")) == "block"]


def collect_check_findings(
    drifts: list[str],
    gate_problems: list[str],
    view_problems: list[str],
    pool_findings: list[dict] | None = None,
    sched_findings: list[dict] | None = None,
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
    findings.extend(to_findings(pool_findings or []))     # C-7 词表臂
    findings.extend(to_findings(sched_findings or []))    # C-15 实测对账臂
    if drifts:
        head = "; ".join(drifts[:5])
        more = f" …（共 {len(drifts)} 条）" if len(drifts) > 5 else ""
        findings.append(
            SimpleNamespace(reason_code=REASON_DRIFT, severity="warn", task_ids=["<registry>"],
                            detail=f"注册表与四真源漂移 {len(drifts)} 条：{head}{more}", at=None)
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
                    help="自检臂：漂移检测（实体集/window_expr 与磁盘比对）+C-5 闸在场性"
                         "+C-10 视图新鲜度+C-7 池词表+C-15 计划任务实测对账+C-11 受闸反查留痕，不写")
    ap.add_argument("--publish-alerts", action="store_true",
                    help="与 --check 同用：自检 findings 落 ops 告警板（缺省 .runtime/ops_notifications/"
                         "，测试经 ZEPHYR_OPS_NOTIFICATION_DIR 重定向——不加旗标，板路径单源）")
    ap.add_argument("--auto-regen", action="store_true",
                    help="与 --check 同用：检出注册表漂移→就地全量再生（排产化零人工）")
    ap.add_argument("--skip-schtasks", action="store_true",
                    help="自检臂跳过 C-15 实测对账（非 Windows/离线取证用；生产计划任务不带此旗标）")
    ap.add_argument("--schtasks-csv", type=str, default=None,
                    help="以 CSV 文件替代 schtasks 探针（单测/离线对账注入；仅 --check 生效）")
    ap.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    ap.add_argument("--view", type=str, default=str(DEFAULT_VIEW), help="周历视图路径（新鲜度自检注入用）")
    ap.add_argument("--existing", type=str, default=None, help="合并保全的旧档路径（测试注入；缺省=output）")
    args = ap.parse_args()
    out = Path(args.output)
    existing_path = Path(args.existing) if args.existing else out
    registry = build_registry(existing_path=existing_path, output_path=out)
    # C-7/R-C 写盘前置守卫：未知池（幽灵池/串审计空间维池）绝不进注册表——闸的并发求和
    # 按 pool 分组，幽灵池上的班次等于没排（daily_crypto 事故自证）。
    pool_findings = check_pool_vocabulary(list(registry["entities"]))
    pool_block = [f for f in pool_findings if str(f.get("severity")) == "block"]

    def _pool_blocked_print() -> None:
        print(f"POOL-BLOCK: 词表守卫阻断写出（{len(pool_block)} 项未知池，v2 C-7/R-C）")
        for f in pool_block[:20]:
            print("  ", f["detail"])

    # C-15 实测对账臂（只读）：与 C-10 视图新鲜度同一纪律——只有"被测表=生产注册表"时
    # 才对本机任务表负责（沙箱临时表拿去比操作系统任务表只能造噪音）。
    sched_findings: list[dict] = []
    exempt_lines: list[str] = []
    if out == DEFAULT_OUTPUT and not args.skip_schtasks:
        if args.schtasks_csv:
            try:
                live, probe_problems = parse_schtasks_csv(
                    Path(args.schtasks_csv).read_text(encoding="utf-8", errors="replace"))
            except OSError as exc:
                live, probe_problems = {}, [f"schtasks_csv_unreadable: {exc}"]
        else:
            live, probe_problems = query_schtasks()
        if live:
            sched_findings, exempted = reconcile_sched_tasks(list(registry["entities"]), live)
            exempt_lines = [f"{e['reason_code']}: {e['task_name']} → {e['task_id']}: {e['reason_zh']}"
                            for e in exempted]
            sched_findings.extend({"reason_code": REASON_TASK_PROBE, "severity": "warn",
                                   "task_ids": ["<task_scheduler>"], "detail": p} for p in probe_problems)
        else:
            sched_findings = [{"reason_code": REASON_TASK_PROBE, "severity": "warn",
                               "task_ids": ["<task_scheduler>"],
                               "detail": "；".join(probe_problems) or "实测任务表为空"}]
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
            if pool_block:
                _pool_blocked_print()  # 宁可留漂移，也不把幽灵池写进表（表可修，闸求和不可信）
                regen_summary = {"attempted": False, "blocked_by": REASON_POOL_UNDECLARED}
                drifts = drifts + [f"pool_guard_blocked: {f['detail']}" for f in pool_block]
            else:
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
        findings = collect_check_findings(drifts, gate_problems, view_problems,
                                          pool_findings=pool_findings, sched_findings=sched_findings)
        for p in gate_problems:
            print(f"HEALTH[{REASON_GATE_ABSENT}]: {p}")
        for p in view_problems:
            print(f"HEALTH[{REASON_VIEW_STALE}]: {p}")
        for f in pool_findings:
            print(f"HEALTH[{f['reason_code']}][{f['severity']}]: {f['detail']}")
        for f in sched_findings:
            print(f"HEALTH[{f['reason_code']}][{f['severity']}]: {f['detail']}")
        for line in exempt_lines:  # 豁免≠静默：stdout 留痕，只是不落告警板/不计退出码
            print(f"EXEMPT: {line}")
        report_gate_declaration_gaps(list(registry["entities"]))  # C-11：同上，只留痕不计码
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
    if pool_block:
        _pool_blocked_print()
        return 2
    text = registry_text(registry)
    expected = None
    if out.exists():
        expected = content_sha256(out.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out, text, expected_base_sha256=expected)
    print(json.dumps({"ok": True, "total_entities": registry["total_entities"], "output": str(out)}, ensure_ascii=False))
    report_gate_declaration_gaps(list(registry["entities"]))  # C-11 留痕（不进 JSON 结果契约，不动退出码）
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
