# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §trading_day_cycle_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_trading_day_cycle_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   （按需 CLI 再生成器；permanent 会触发 PERM-TRIGGER 手动模式铁律）
# create-guard-not-dup: 死车道抢救的FiveMaps生成器/校验器（字节代投非新能力），docstring描述读文本建图的既有动作，与canonical无重叠
# [DEPENDENCIES] yaml；ast；subprocess（只读 powershell Get-ScheduledTask 查询，禁 Register/Unregister/Change）；
#   scripts.governance._shared.terminology_loader（get_category_map）；
#   scripts.governance._shared.module_translation_loader（get_module_translation）；
#   zephyr.shared.io.file_utils（safe_write_text，热写通道复用）；git（只读 show 取 HEAD 提交时间派生时间戳）；
#   docs/03_modules/path_ownership_map.yaml（depgraph 派生在册投影 claim_type=depgraph_node，
#   路径→MOD-* 总线号只读面，禁自造号）；docs/_working/map_build/fig13_daycycle/00_skeleton.md
#   （§2 四张环节表状态列，verified_scope 双轴唯一同源口径）
# [CONSUMERS] config/trading_day_cycle_map.yaml（唯一产出物）；
#   scripts/governance/d5_architecture/validators/validate_trading_day_cycle_map.py（在册实存对照本生成器
#   写入的 machine_facts.trigger_surfaces）；
#   tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py（幂等实证直调 build_document）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 双层结构（GOMAP/图11 先例）：machine_facts 层每次全量重扫可执行真相源
# [MODIFY-GUARD] 环节契约全集/边/反馈环改动前先回写 docs/_working/map_build/fig13_daycycle/
#   00_skeleton.md（44 环节），gap 节点增删须同步校验器 NODE_UNIVERSE 与本件 NODE_ORDER；
#   产出 config/trading_day_cycle_map.yaml 禁手改后不回生成
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] production 环节缺 exec_evidence=raise KeyError；计划任务/热册不可读=对应面记
#   {"available": false}/{"exists": false} 降级不崩；写盘 CAS 失败=返回码 1；--dry-run 零写入；
#   --skip-schtasks=计划任务面显式降级（CI 用）
# [TESTS] tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py
#   （schedule.yaml 槽全集+tasks.yaml 挂载 join+_run_special_schedule 分支面+PHASE_STAGES 实扫+
#   TRADING_DAY_GUARDED_SCHEDULES+register_*.ps1 声明面+计划任务只读查询面+data/runtime 总闸实存面+
#   骨架 §2 状态列实扫+path_ownership depgraph_node 在册 module_id 面），
#   人工语义层（环节名/decision_question/laws/boundary/边/反馈环）取骨架与作业簿，
#   生成器内以契约常量承载且不擅改判据；
#   幂等=同输入两次产出逐字节等：时间戳必经 --as-of 入参或 HEAD 提交时间派生，生成器禁壁钟取时函数
#   （now/time 类）——RULE-SCHEMA-TZ；计划任务查询失败=available:false 降级，禁抛禁写空集合冒充真源；
#   INV-1 三条硬让渡（骨架 §0.2）：①时刻值不搬家（cron 字面量零复制，节点只存槽名/tn 名/entity_id/
#   段名/表名/路径）②决策内容不进图（节点禁 judgment_basis/factor_refs/strategy_refs，判据唯一出路
#   tdm_refs）③数据管线内部结构不重画（批次节点只挂计数与指针）；计数只进 counts 字段不进散文；
#   字段名一律 L0/L1 统一名（note_zh/doc_refs/cadence_zh/fallback/ready_gate+no_ready_gate_reason_zh/
#   wiring_status/gap_refs——同义异名四件与两指针别名已随三层字段裁定废止，残留由校验器 CV-L0 判红）；
#   verified_scope 与骨架 §2 状态列同源（✅→production、🔨/⬜→structure），production 数恒等骨架 ✅ 数，
#   本生成器不擅改任何判据口径；有实现代码的节点必经在册面核"已实现"后挂 MOD-*（CV-BUS），
#   查不到号=module_id null+red_reason 必填，禁自造号
# [MODIFY-GUARD] 环节契约全集/边/反馈环改动前必须先回写
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] 见同批 tests/ 下 canary 件
#   docs/_working/map_build/fig13_daycycle/00_skeleton.md（本图唯一收敛基准，44 环节）；
#   gap 节点（D13-G01..）是骨架外显性化缺口件，增删须同步校验器 NODE_UNIVERSE 与本件 NODE_ORDER；
#   产出物 config/trading_day_cycle_map.yaml 禁手改后不回生成（counts 一致性校验判红）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失=对应 machine_fact 记 {"exists": false} / {"available": false} 不崩溃；
#   safe_write_text CAS 失败=返回码 1；--dry-run 零写入；--skip-schtasks=计划任务面显式降级（CI 用）
# [TESTS] tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""generate_trading_day_cycle_map.py — 交易日循环全景图（图 13，trading_day_cycle_map）生成器。

域（骨架 §1 一句话）：一个交易日从夜窗闭合到次日交接，**什么时点必须发生什么、谁给它让路、
它没跑谁接、接不住当日算什么状态**。44 环节 D13-01..44（盘前 12／盘中 12／盘后 11／夜窗与贯穿 9）。

两层结构（照抄图 10 GOMAP 与图 11 dev_delivery_map 先例，机生优先+静态清单禁手工维护）：
  1. 机生层 machine_facts（每次全量重扫，本图最硬的一层——"槽位挂着但没跑"只有扫出来才算数）：
     - `src/zephyr/data/config/schedule.yaml`：槽全集（槽名/执行器池/节拍类别，**cron 字面量零复制**）
     - `src/zephyr/data/config/tasks.yaml`：槽×任务 join（过滤 extra.disabled 后的有效挂载数）+
       孤儿任务（schedule 值非槽名）+ 重复 task_id（"一任务只属一槽"的在册绕行）
     - `src/zephyr/data/scheduler.py`：`_run_special_schedule` 硬编码分支面（零任务槽是否真跑的唯一判据）
     - `src/zephyr/plan_engine/daily_loop_master_switch.py`：`PHASE_STAGES` 实扫段集（AST 字面量，不 import）
     - `src/zephyr/data/trading_calendar.py`：`TRADING_DAY_GUARDED_SCHEDULES` 日历守卫归属面
     - `scripts/register_*.ps1` 声明面 + Windows 计划任务只读查询面（Get-ScheduledTask，禁写操作）
     - `data/runtime/*.disabled` 服务总闸实存面（不存在=开着，存在=停用）
     - **骨架 §2 状态列实扫**（✅/🔨/⬜ 四张表逐环节取列——verified_scope 双轴的唯一同源口径）
     - **depgraph 在册 module_id 投影面**（path_ownership_map.yaml claim_type=depgraph_node 的
       路径→MOD-*，加源文件自身 `[BLUEPRINT] MOD-*` 头声明兜底；逐路径核"已实现"，查不到号
       =module_id null+red_reason 必填，禁自造号）
     - **TDM 节点号在册面**（config/trading_decision_map.yaml 的 node_id 全集，tdm_refs 逐条实存判定）
  2. 人工语义层：环节名/decision_question/note_zh（L0 统一名，废止三个同义异名注解字段与两个
     doc 指针别名）/laws/boundary/边/反馈环——逐条取自
     docs/_working/map_build/fig13_daycycle/00_skeleton.md §0/§1/§2 与十本作业簿（簿 10=外部对标三扫：
     表A 七条逐条落 L1/L2 字段或 gap 节点、表C 五条判据分歧只以 gap_refs 记入不自裁），状态口径
     ✅/🔨/⬜ 照用骨架 §2 状态列（判据不擅改；作业簿复判差异另记 mining_status 字段）。

CLI:
    python scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py
    python ... --dry-run                     # 只打印摘要
    python ... --as-of 2026-09-24T12:00:00+08:00   # 注入时间戳（幂等实证用；缺省=HEAD 提交时间派生）
    python ... --skip-schtasks               # 计划任务面显式降级（无 Windows 面环境）
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[4]
_GOV_DIR = str(next(p for p in _THIS.parents if (p / "_shared").exists()))
for _p in (_GOV_DIR, str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.module_translation_loader import get_module_translation  # noqa: E402
from _shared.terminology_loader import (
    get_category_map,  # noqa: E402  # noqa: import-integrity  sys.path 注入的 _shared 包
)
from d5_architecture.generators._common import (  # noqa: E402  # noqa: import-integrity  sys.path 注入的 governance 包
    anchor_label_bilingual,
    head_commit_time,
    serialize_map_document,
    tbl_name,
)

_tbl = tbl_name  # 表名取数单源化（_common.tbl_name，CR-15 同批收内）

OUTPUT_PATH = _REPO_ROOT / "config" / "trading_day_cycle_map.yaml"
_SKELETON = "docs/_working/map_build/fig13_daycycle/00_skeleton.md"
_BOOK_DIR = "docs/_working/map_build/fig13_daycycle"

# 真源坐标（全部只读）
_SCHEDULE_REL = "src/zephyr/data/config/schedule.yaml"
_TASKS_REL = "src/zephyr/data/config/tasks.yaml"
_SCHEDULER_REL = "src/zephyr/data/scheduler.py"
_DLOOP_REL = "src/zephyr/plan_engine/daily_loop_master_switch.py"
_CALENDAR_REL = "src/zephyr/data/trading_calendar.py"
_CATCHUP_REL = "src/zephyr/data/catchup_guard.py"
_REGISTRY_REL = "config/resource_profile_registry.yaml"
_REGISTER_GLOB = "scripts/register_*.ps1"
# depgraph 派生在册投影（claim_type=depgraph_node 的 路径→MOD-* 面；生成器只读，禁自造号）
_PATH_OWNERSHIP = "docs/03_modules/path_ownership_map.yaml"
# TDM 交叉引用真源（tdm_refs 的在册 node_id 面）
_TDM_REL = "config/trading_decision_map.yaml"
# 簿 10（外部对标三扫）——表A/表C 逐条出处的作业簿件
_EXT_BOOK = f"{_BOOK_DIR}/10_外部对标三扫.md"

# 作业簿归属（骨架 §5 簿号契约；环节编号→簿文件名）
_BOOK_OF: dict[str, str] = {
    **{f"{i:02d}": "01_盘前就绪链.md" for i in (1, 2, 3)},
    **{f"{i:02d}": "02_盘前元数据与竞价.md" for i in (4, 5, 6, 11, 12)},
    **{f"{i:02d}": "03_盘前编排与十源探针.md" for i in (7, 8, 9, 10)},
    **{f"{i:02d}": "04_盘中采集层群.md" for i in (13, 14, 15, 16, 17, 18)},
    **{f"{i:02d}": "05_盘中资金流与决策层.md" for i in (19, 20, 21, 22, 23)},
    **{f"{i:02d}": "06_盘后结算与三账.md" for i in (25, 26, 27, 28, 29)},
    **{f"{i:02d}": "07_dloop十六段解剖.md" for i in (24, 32, 33, 34)},
    **{f"{i:02d}": "08_盘后批次与当日回测.md" for i in (30, 31, 35)},
    **{f"{i:02d}": "09_夜窗与日界贯穿.md" for i in (36, 37, 38, 39, 40, 41, 42, 43, 44)},
}

# ---------------------------------------------------------------------------
# 人工语义层（骨架/作业簿契约常量）。SEGMENT_SEMANTIC_ZH 是骨架 §2 四段**人工语义契约件**
# （段名/界定语/交接语），不是英文枚举的翻译字典；英文枚举的中文标签一律走翻译 loader。
# ---------------------------------------------------------------------------

# 骨架 §0.2 三条硬让渡 + §3 两条禁则 —— 必须落成 laws（撞车判定的边界即图本体边界）
LAWS = [
    "让渡一·时刻值不搬家：节点只存槽名/tn 名/entity_id/段名等稳定标识符，cron 字面量与执行器线程数"
    "零复制（骨架 §0.2 硬让渡 1）",
    '让渡二·决策内容不进图：任何"怎么判"唯一出路是 tdm_refs 引 TDM 节点，本图节点禁带'
    " judgment_basis/factor_refs/strategy_refs（骨架 §3 禁则一，违者=第二动作流程真源）",
    "让渡三·管线内部结构不重画：有任务挂载的数据槽在本图只作批次节点（含有效挂载数与当日就绪判定），"
    "其源→库→衍生→冷备→对账内部结构归图 12，对账装配落点归 battle_map BM-REC-*（骨架 §0.2 硬让渡 3）",
    "槽位挂着≠真在跑：环节存在性判据=该时点的执行体是否被调用 + 该执行体产物表是否有行，"
    '禁以"槽 firing/APScheduler 记 success/表里有留痕"三点任一判绿（簿 04 §0.1、簿 06 假绿专段）',
    "缺席必须记账：每环节须声明 ready_gate（本节点是否就绪门格）与 fallback（没跑谁接）；"
    '无兜底不许留空，须写 fallback="none:<理由>"；非就绪门格须写 no_ready_gate_reason_zh（骨架 §1 门④，'
    "字段名一律取六图终局卷 §1 L1 统一名）",
    "看着≠动手：每环节 downstream_action 必须区分自动补跑/仅告警/仅检测/仅编排/执行五态，"
    "检出即蒸发（无落盘无消费者）不得记为有兜底（簿 01 三哨兵总裁定、簿 09 3.3）",
]

BOUNDARY = [
    '不画下单/撤单执行流——归 TDM L4/X-S2（骨架 §1 边界）；本图只画"该时点必须发生什么"',
    "不画因子与策略——归各库；本图节点无判据字段（让渡二）",
    "不画数据管线内部结构（源→库→衍生→冷备→对账）——归图 12；本图批次节点只挂有效挂载计数与就绪判定",
    "不画资源争抢与内存天花板——归排班三表（resource_profile_registry + schedule_overview + "
    'schedule_consistency_reconciler）；本图放弃"时刻值与资源档位"两项职责，只新增"时序与就绪"',
    "不画治理夜班（C4Exam/ModelExam/GateFullTreeAudit 等 schtasks 族）——主体让渡 GOMAP，"
    "本图只留守护接缝三点（骨架 §2 D13-42）",
    "不画开发时会话生命周期——归图 11；不画 24/7 三班制交接（shift_handover_checklist 面向连续市场，"
    "不覆盖 A 股日界，骨架 §2 D13-44 实证）",
]

# 段名全集经 SSoT 词表装载器动态加载（禁字面量/禁自写 yaml 读取——GATE-VOCAB+VOCAB-CHAIN 双治本）
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402 —— SSoT 唯一真源

SEGMENTS = tuple(sorted(load_vocabulary_values("governance_family_vocabulary.yaml")))
# gap 节点（骨架外显性化缺口件）——增删须同步校验器 NODE_UNIVERSE/SEGMENT_OF_INDEX 与本件 NODE_ORDER
GAP_ORDER: tuple[str, ...] = ("D13-G01", "D13-G02", "D13-G03", "D13-G04")

# 段名/界定语/交接语 = 骨架 §2 四段标题与 §2.1 机制三分的人工语义件（非英译中字典）
SEGMENT_SEMANTIC_ZH: dict[str, dict[str, str]] = {
    "A": dict(
        name_zh="盘前段",
        span_zh="05:30–09:30（骨架 §2 段 A）",
        handoff_zh="三连哨（05:30 档期对账→06:50 停更→07:10 逐日 diff）构成缺席兜底层，"
        "交 09:15 前就绪门编排；盘前段的部分语义由 16:45 dloop 圈预产（见 feedback_loops）",
    ),
    "B": dict(
        name_zh="盘中段",
        span_zh="09:30–15:00（骨架 §2 段 B）",
        handoff_zh="采集层群按 5 分钟槽滚动，dloop 唤醒词段与墙钟窗闸段在 16:45 圈被回头驱动；"
        "模拟盘 15:05 收口交盘后段",
    ),
    "C": dict(
        name_zh="盘后段",
        span_zh="15:00–20:00（骨架 §2 段 C）",
        handoff_zh="15:10 三件同分钟→15:30 结算单就绪→15:40 核对→16:30 日K线→16:45 dloop "
        '16 段→17:00 起批次群；本段是全图唯一"三机制同窗"密集段（簿 06 O-3）',
    ),
    "D": dict(
        name_zh="夜窗与贯穿段",
        span_zh="20:00–次日 05:30 + 周月批 + 全日不变量（骨架 §2 段 D）",
        handoff_zh="夜窗五槽收口后交日界；日历闸门与常驻守护贯穿全图；D13-44 完成 T→T+1 状态移交",
    ),
}

# 契约全集：44 环节（骨架 §2 四张表，编号一经定稿即契约）+ 4 个 gap 显性化缺口节点
# （簿 10 表A/表C 与图 12 侧跨图缺口，属骨架外件，待总包回写骨架 §2——本车道禁改骨架）。
NODE_ORDER: tuple[str, ...] = tuple(f"D13-{i:02d}" for i in range(1, 45)) + GAP_ORDER
# gap 节点的 doc_refs 出处（不在骨架 §2 表内，禁指骨架 §2——骨架无此行）
_GAP_DOC = {
    "D13-G01": (_EXT_BOOK, "六图终局卷 §4 图13 判据①（空转槽与落空对象全可查）"),
    "D13-G02": (
        "docs/_working/map_build/fig12_datachain/11_消费端需求反查.md",
        f"{_BOOK_DIR}/05_盘中资金流与决策层.md",
    ),
    "D13-G03": (f"{_BOOK_DIR}/06_盘后结算与三账.md", "docs/_working/map_build/fig12_datachain/11_消费端需求反查.md"),
    "D13-G04": ("docs/_working/map_build/fig12_datachain/11_消费端需求反查.md", _EXT_BOOK),
}

# ---------------------------------------------------------------------------
# 44 环节语义契约件（骨架 §2 四张表逐行 + 九本作业簿复判；status 照用骨架状态列）
# 字段：seg 段归属｜st 骨架状态｜recheck 作业簿复判（不改骨架口径，另字段承载）｜name 环节名
#       q decision_question（时序问题，非决策判据）｜mech 机制一句话｜clk 时点语义（无 cron 字面量）
#       src slot_source｜slot/entity/tn/stages 各类真源指针｜act downstream_action
#       gate ready_gate｜nrg 无前置声明理由｜fb miss_fallback｜ref module_ref｜anc/run/data/tdm/doc 指针
#       ev evidence（verified 必备）｜red 🌑 红条目｜dangling 落空对象指针｜extra 本图特有结构化字段
# ---------------------------------------------------------------------------
_SCHED = "schedule"
_SCHT = "schtasks"
_EVENT = "event"
_DLOOP = "dloop_stage"
_NONE = "none"

N: dict[str, dict[str, Any]] = {
    # ── 段 A 盘前 ──────────────────────────────────────────────────────
    "D13-01": dict(
        seg="A",
        st="🔨",
        name="调度对账补跑（错过档期自愈）",
        src=_SCHED,
        slot=["catchup_guard"],
        clk="每日 05:30（全周含周末：守卫本身须非交易日可跑）",
        act="auto_remediate",
        q="05:30 这一圈补跑跑完了吗？跑不完是谁的手被麻住？错过档期今天还有谁接？",
        mech="APScheduler 特殊槽硬编码分支驱动 catchup_guard；单批补跑上限与顺延纪律见实现，"
        "补跑宇宙=其档期分桶常量集（机生层 catchup_universe 实扫）",
        gate="无（本槽是兜底器，自身不设前置）",
        nrg="",
        fb="无（接不住即档期视角失效）",
        ref="src/zephyr/data/catchup_guard.py:42",
        anc=["src/zephyr/data/catchup_guard.py:42", "src/zephyr/data/scheduler.py:231"],
        run=["tmp/catchup_guard.lock", "tmp/scheduler_run.log"],
        doc=["docs/01_policies_and_standards/sop/data_ops_sop/"],
        ev=[
            "簿 01 §1：05:30 每日 firing 但自 09-21 后无一圈完成；task_progress 最后一次成功汇总"
            "非 05:30 档期时点且 rows 打满上限",
            "tmp/catchup_guard.lock 现值 PID 经 tasklist 实测已死（锁留死进程）",
            "特殊槽分发分支该腿无降级告警（对照哨兵两腿均有）→ 崩溃=静默",
        ],
        obs="每日 1 次 firing；自 09-21 起无一圈完成",
        extra=dict(remediation_broken=True, remediation_break_zh="晨间调度器重启风暴腰斩长批 + 锁留死 PID"),
    ),
    "D13-02": dict(
        seg="A",
        st="🔨",
        name="数据断供哨兵（含托管质量变异巡检）",
        src=_SCHED,
        slot=["data_supply_sentinel"],
        clk="每日 06:50（全周含周末：周末断供周一才报=重演两月盲区）",
        act="alert_only",
        q="06:50 这一巡检出几条红？红有没有落成可操作产物？谁的手去修？",
        mech="特殊槽分支 → supply_sentinel 三判据腿（业务新鲜度/行数地板/关键列填充率）+ 盲点出声 + "
        "托管 quality_sentinel 变异巡检；配置条目数与覆盖表集合以机生层为准，本图不抄清单",
        gate="无前置（自身是哨）",
        nrg="",
        fb="修复腿让渡 D13-01（档期）与 D13-35（行数）",
        ref="src/zephyr/data/supply_sentinel.py:11",
        anc=["src/zephyr/data/supply_sentinel.py:11", "src/zephyr/data/scheduler.py:238"],
        data=["src/zephyr/data/config/data_supply_sentinel.yaml", "config/quality_sentinel_tables.yaml"],
        run=["data/failures/", "data/quality_sentinel/"],
        ev=[
            "簿 01 §2：今晨 06:51 日志行 checked/breached/blind_spots 三计数在案，连续 6 日 ERROR 落盘文件",
            "只检测不修复写进其 INVARIANTS；检出条目共用同一 task_id 被 300 秒冷却折成 1 个 failures 文件"
            "（11 红只剩 1 痕）",
            "总闸 data/runtime/quality_sentinel.disabled 实存扫=不存在（机生层 service_flags）",
        ],
        obs="每日 1 拍；托管变异巡检另有 7 天节奏闸（未跑属正常）",
        extra=dict(alert_folding=True, alert_folding_zh="按 task_id 冷却去重致多红折叠成一痕"),
    ),
    "D13-03": dict(
        seg="A",
        st="🔨",
        name="交易日历逐日覆盖 diff",
        src=_SCHED,
        slot=["calendar_coverage_check"],
        clk="每日 07:10（全周）",
        act="detect_only",
        q="07:10 的逐日 diff 有没有检出缺日？检出之后动了谁的手？",
        mech='特殊槽分支 → 日历覆盖检查器：对在册表族逐日 diff，治"补 max(date) 原理性失明"；'
        "监控表名单以机生层 scanned 配置为准",
        gate="无前置",
        nrg="",
        fb="无（检出即蒸发）",
        ref="src/zephyr/data/calendar_coverage_checker.py:101",
        anc=["src/zephyr/data/calendar_coverage_checker.py:101", "src/zephyr/data/scheduler.py:255"],
        run=["tmp/scheduler_run.log"],
        ev=[
            "簿 01 §3：今晨 07:10 完成行 checked/breached 在日志（滞后 0）",
            "违规仅出 WARN 日志行：alerter 对 WARN 不落盘、特殊槽分支只回 bool 并丢弃报告 dict"
            '→ 既无人看也无人修（"嘴都没有对准人"）',
        ],
        obs="每日 1 拍",
        extra=dict(detection_evaporates=True, detection_evaporates_zh="WARN 不落盘 + 报告 dict 被特殊槽分支丢弃"),
    ),
    "D13-04": dict(
        seg="A",
        st="✅",
        name="夜间情绪窗结算（窗口 [T-1 18:00, T 08:00)）",
        src=_SCHED,
        slot=["nightly_sentiment"],
        clk="每日 08:20（全周）；窗口右端=T 日 08:00 → 段归属盘前成立，采集腿落夜窗（两腿跨段）",
        act="execute",
        q="08:20 结算的窗闭合了吗？窗内有没有产物行落到情绪窗口表？",
        mech="特殊槽分支 → 夜间情绪窗结算；总闸实存面见机生层 service_flags（存在=停用）",
        gate="T-1 18:00 至 T 08:00 新闻窗已闭合",
        nrg="",
        fb="无（窗不闭合则该拍产物缺）",
        ref="src/zephyr/data/scheduler.py:272",
        anc=["src/zephyr/data/scheduler.py:272", _SCHEDULE_REL],
        ev=[f"骨架 §2 D13-04 行：{_tbl('market_news_sentiment_window')} max(window_ts) 与全表行数读数在案（§7 C 组）"],
        obs="每日 1 拍",
        extra=dict(spans_segments=["A", "D"]),
    ),
    "D13-05": dict(
        seg="A",
        st="🔨",
        name="币圈日线（UTC 日界→北京晨间时点）",
        src=_SCHED,
        slot=["daily_crypto"],
        clk="每日 08:41（全周）",
        act="execute",
        q="08:41 的币圈日线跑了吗？水位是自动推进还是全靠手动？",
        mech="常规 DAG 槽（有任务挂载，挂载数见机生层）；执行器池历史幽灵池事故留痕见 schedule.yaml 注",
        gate="无前置",
        nrg="",
        fb="无（该槽不在补跑宇宙内，错过无人补）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:75", f"{_SCHEDULE_REL}:77"],
        ev=["骨架 §2 D13-05 行：该任务上线后从未自动跑成、水位全靠手动（槽注释自证）"],
        obs="每日 1 拍",
        dangling=["slot:daily_crypto"],
    ),
    "D13-06": dict(
        seg="A",
        st="🔨",
        name="L0.5 盘前元数据（universe 与撮合约束前提）",
        src=_SCHED,
        slot=["pre_market"],
        clk="交易日晨间 08:34（APScheduler 0-4 口径）",
        act="execute",
        q='08:34 五子源都到位了吗？有没有"任务 SUCCESS 而水位不动"的子源？',
        mech="常规 DAG 槽（有效挂载数见机生层）；五子源逐个读数归簿 02，本图只作盘前就绪腿",
        gate="无前置（盘前第一腿）",
        nrg="",
        fb="D13-01 档期对账（pre_market 在其 intraday 桶）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:24", "src/zephyr/data/scheduler.py:475"],
        data=["docs/03_modules/_domain_data/data_source_integrator_blueprint.md"],
        ev=[
            "簿 02 §D13-06：四子源有行、停复牌子源 0 行且水位停在纪元起点 → 子源断链，整槽不得判绿",
            "同一子源不在断供哨兵与日历覆盖检查的任何名单内（簿 01 O-4 / 簿 02 旁向）→ 双层哨兵共同盲区",
        ],
        obs="交易日每日 1 拍",
        extra=dict(subsource_hollow=True, subsource_hollow_zh="名义在产、一子源零行且不在任何哨兵名单"),
    ),
    "D13-07": dict(
        seg="A",
        st="✅",
        name="QMT 终端看门狗",
        src=_SCHT,
        tn=["ZephyrAlpha_QMTWatchdog"],
        entity=["ops_qmt_watchdog"],
        clk="交易日 08:45 与 12:55 两拍（Windows 计划任务；资源册 window_expr 未抽到该双时点=跨机制漏拍）",
        act="alert_only",
        q="08:45 与 12:55 两拍 QMT 进程在不在？不在时谁来登录？",
        mech="独立 ps1 脚本判进程存活并写留痕；不覆盖自动登录（🌑-1）",
        gate="无前置",
        nrg="",
        fb="无人接：登录只能人做（🌑 点名项，图不编造出处）",
        ref="scripts/qmt_watchdog.ps1:28",
        anc=["scripts/qmt_watchdog.ps1:28", "scripts/qmt_watchdog.ps1:11"],
        run=["data/runtime/qmt_watchdog.log"],
        ev=["骨架 §2 D13-07 行：留痕末六行=连续三交易日两拍均 OK 且带 pid（§2 表内实查）"],
        obs="交易日每日 2 拍",
    ),
    "D13-08": dict(
        seg="A",
        st="✅",
        name="十源健康探针（归档 57 号 C3 腿）",
        src=_NONE,
        slot=[],
        clk="每日一份日志（触发者未在排班真源定位：槽内不存在，只有日志面能发现）",
        act="detect_only",
        q="今日十源健康日志有没有产出？谁消费它？",
        mech="独立探针模块产日志，被调度器消费；不在 schedule.yaml 与计划任务任何名单内",
        gate="无前置",
        nrg="",
        fb="无（触发者待定位，属图照出来的洞）",
        ref="src/zephyr/data/source_health_check.py",
        anc=["src/zephyr/data/source_health_check.py", "src/zephyr/data/scheduler.py:1696"],
        run=["logs/"],
        ev=[
            "骨架 §2 D13-08 行：logs/source_health_YYYYMMDD.log 连续每日；执行体被调度器两处消费",
            "B4 案例批当场逼出（排班真源里不存在该腿）",
        ],
        obs="每日 1 份日志（触发者待定位）",
        extra=dict(trigger_owner_unlocated=True),
    ),
    "D13-09": dict(
        seg="A",
        st="⬜",
        name="开盘前就绪门（09:15 前 C1+C2+C3 合成→当日准入裁定）★一等门节点",
        src=_NONE,
        slot=[],
        clk="09:15 前（人工窗，无时点真源：排班三表与计划任务面均无该时刻）",
        act="none",
        q="09:15 前三个判据合成了吗？判不过当日算 SKIP 还是算照常跑？谁有权让下游拒绝准入？",
        mech="三判据（C1 QMT 进程在否 / C2 关键任务今日水位 / C3 探针 miniqmt connect_ok）合成→当日 SKIP"
        " 判定；合成器**零在位**（全仓检索无就绪门执行体，TDM 亦无该节点），故本格 ready_gate 的"
        "三源判据定义由本图钉死、实现交施工波：C1=watchdog 留痕末行日期==今日 ∧ C2=关键任务水位"
        "比对==今日（**禁沿用「最近运行 SUCCESS」字面口径**，已被 SUCCESS 而水位未动型假绿证伪）"
        " ∧ C3=source_health 当日在且 miniqmt 绿。三判据现行执行者逐个点名（簿 03 §2 死结论）："
        "C1=watchdog(查 XtItClient) 与 paper-session 拉起前查(查 XtMiniQmt) 双替身且进程名分裂、"
        "C2=纯人读 CLI 且口径已失真、C3=探针自动跑而结果不进任何裁定。「开不开市（日历腿 D13-43）"
        "」与「开不开得起（本门）」两问分居两格且后者无主（簿 03 O-16）："
        "ready_gate 与 calendar_gated 双字段禁合并",
        gate="本格即就绪门本体（不挂在他门下游）",
        nrg="",
        fb="none:无合成器⇒接不住当日算什么状态=默认全绿（本图最大空洞的显性化）",
        ref=None,
        anc=[
            "docs/_archive/57_daily_cycle_sop.md",
            "scripts/qmt_watchdog.ps1:43",
            "scripts/start_paper_session_daily.ps1:61",
            "src/zephyr/data/scheduler.py:1701",
        ],
        doc=["docs/_archive/57_daily_cycle_sop.md", _EXT_BOOK],
        ev=[
            "骨架 §2 D13-09 状态列 + 簿 03 §2 死结论「门该在、无主」（三判据执行者逐腿点名，合成器零）",
            "复跑: grep -rn 就绪门 src 与 grep -rn readiness src 均零业务命中；"
            "grep -c D13 config/trading_decision_map.yaml=0（TDM 无该裁定节点，"
            "骨架 §0.1-3 实证 activation 只有窗没有点）",
            "C2 字面口径已被证伪：盘前元数据一子源状态 SUCCESS 而水位未动（簿 02 §3 实测 11,106=2×5,553 行、"
            "无当日行）⇒ 照 57 号原文核 C2 会在红色天上判绿",
            "C1 失败的唯一真实强制点在 D13-12 拉起前查（日志反证两日 SKIP(QMT 未开)），只管模拟盘一条命",
            "C3 探针红时没有任何件据此把当日标 SKIP（scheduler 任务级源跳闸≠开盘准入裁定）",
        ],
        obs="0 拍（无合成器；三判据各自半自动且互不交集）",
        extra=dict(
            archived_ssot_only=True,
            archived_ssot_only_zh="唯一真源已归档且无接替件（57 号承诺并入 55 号监控体系未兑现）",
            admission_denied_zh="未过门=下游拒绝准入（本图唯一拒准入语义边，逐条列顶层 "
            "admission_edges；现行实况=08:45/09:25/09:30 各自到点自跑、无准入边）",
        ),
    ),
    "D13-10": dict(
        seg="A",
        st="🔨",
        name="板块状态盘前复制（close_final→pre_open + 偏好重映射）",
        src=_SCHED,
        slot=["sector_pre_open"],
        clk="交易日 09:15（与 D13-11 同分钟）",
        act="execute",
        q="09:15 的盘前复制产了吗？产物停在 T 日还是 T-1 日？",
        mech="特殊槽分支（sector 双槽合一）→ 板块状态管线；服务总闸实存见机生层",
        gate="D13-25 前一交易日 close_final 已定格",
        nrg="",
        fb="无（缺则该日无盘前板块态）",
        ref="src/zephyr/data/sector_state_pipeline.py:164",
        anc=["src/zephyr/data/sector_state_pipeline.py:164", "src/zephyr/data/scheduler.py:439"],
        ev=[
            "骨架 §2 D13-10 行：pre_open 态 max(trade_date) 滞后 1 交易日（当日未产）；该槽为新增后"
            "未热载（同文件在册先例：调度器重启后生效）"
        ],
        obs="交易日每日 1 拍",
        extra=dict(lag_trading_days=1),
    ),
    "D13-11": dict(
        seg="A",
        st="✅",
        name="集合竞价高频五档采集",
        src=_SCHED,
        slot=["auction_highfreq"],
        clk="交易日 09:15–09:25 每 10 秒（含秒槽；coalesce 理由见槽注释）",
        act="execute",
        q="竞价窗内每拍都采到了吗？窗内快照数够吗？",
        mech="六字段（含秒）间隔槽 + 日历守卫在册 9 槽之一；行数读数归图 12",
        gate="竞价窗开启（交易所时钟）",
        nrg="",
        fb="无（窗过不补）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:183", f"{_SCHEDULE_REL}:186"],
        ev=["骨架 §2 D13-11 行：当日竞价快照与档位表行数量级读数在案（§7 C 组）"],
        obs="窗内每 10 秒",
    ),
    "D13-12": dict(
        seg="A",
        st="✅",
        name="模拟盘会话拉起 + 交易日历闸",
        src=_SCHT,
        tn=["ZephyrAlpha_PaperSession"],
        entity=["sch_paper_session"],
        clk="交易日 09:25（Daily 触发，非 AtLogOn；包装层自带 is_trading_day 闸）",
        act="execute",
        q="09:25 会话拉起来了吗？非交易日与 QMT 未开各算哪种 SKIP？",
        mech="计划任务拉起包装脚本 → 常驻适配器；日历闸在包装层而非槽层",
        gate="D13-07 判 QMT 进程在 + 今日为交易日",
        nrg="",
        fb="D13-42 三路守护的心跳腿（陈旧则 schtasks 重跑）",
        ref="scripts/register_paper_session_task.ps1:67",
        anc=["scripts/register_paper_session_task.ps1:67", "scripts/start_paper_session_daily.ps1"],
        run=[".runtime/logs/paper_session.log"],
        ev=[
            "骨架 §2 D13-12 行：当日 09:25:03 起 + 非交易日 SKIP(is_trading_day=False) + QMT 未开 SKIP "
            "三态留痕各一条在案"
        ],
        obs="交易日每日 1 次拉起",
    ),
    # ── 段 B 盘中 ──────────────────────────────────────────────────────
    "D13-13": dict(
        seg="B",
        st="🔨",
        recheck="🌑",
        name="竞价后档位一次性聚合（情绪指数竞价档）",
        src=_SCHED,
        slot=["post_auction"],
        clk="交易日 09:30（槽每日 firing）",
        act="none",
        q="09:30 这一拍真跑了吗？还是槽位挂着、APScheduler 记 success 而什么都没执行？",
        mech="机生判据：该槽有效挂载数与特殊槽分支存在性共同决定真伪——两者皆零=假通道槽，"
        '落到调度器"无任务"分支后静默返回空并被记为成功，日志轮转再自毁证据',
        gate="D13-11 竞价窗已收官",
        nrg="",
        fb="无（假通道槽：接不住也不会有人知道）",
        ref="src/zephyr/data/scheduler.py:2256",
        anc=["src/zephyr/data/scheduler.py:2256", f"{_SCHEDULE_REL}:34"],
        ev=[
            "簿 04 §1：注册证据与进程加载证据齐全，但 HEAD 无挂载任务且无特殊槽分支；"
            "09:30 那次实跑是死在导入异常上的在途 WIP，随后当日蒸发窗被灭未落 HEAD",
            '簿 04 §0.1 A 类：本槽与 eod_reconciliation 是全仓仅有的"零任务∧零分支"两槽=恒假成功',
        ],
        obs="名义每日 1 拍；实为 0 拍",
        dangling=["slot:post_auction"],
        extra=dict(idle_slot_expected=True),
    ),
    "D13-14": dict(
        seg="B",
        st="🔨",
        name="盘中实时层（Tick/L2/Greeks/IV/期货/涨跌停/港股K）",
        src=_SCHED,
        slot=["intraday_realtime"],
        clk="盘中每 5 分钟（交易时段窗 + 日历守卫在册）",
        act="execute",
        q="盘中每 5 分钟这一拍有没有真产出？各腿分别在产吗？",
        mech="实时执行器池 DAG 槽（有效挂载数见机生层，内部结构归图 12）",
        gate="QMT/行情通道可用",
        nrg="",
        fb="D13-01（intraday 桶在补跑宇宙内）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:39", "src/zephyr/data/trading_calendar.py:151"],
        ev=['簿 04 环节段：多腿实测零产（在册定性），本图取"层在产但腿不齐"的时序事实'],
        obs="盘中每 5 分钟",
    ),
    "D13-15": dict(
        seg="B",
        st="🔨",
        name="盘中分钟K线滚动层",
        src=_SCHED,
        slot=["intraday_minute"],
        entity=["data_slot_intraday_minute"],
        clk="盘中每 5 分钟（交易时段窗 + 日历守卫在册）",
        act="execute",
        q="分钟K滚动有没有落到当日？60 分钟K唤醒词腿是否由它喂？",
        mech="独立执行器池 DAG 槽；其产出的 60 分钟K是 dloop 盘中族唤醒词来源",
        gate="无前置（与实时层并采）",
        nrg="",
        fb="D13-01（intraday 桶）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:45", "src/zephyr/plan_engine/daily_loop_master_switch.py:68"],
        ev=["骨架 §2 D13-15 行：实测挂载任务数量级在案；簿 04 复判补第三证后升为在产"],
        obs="盘中每 5 分钟",
    ),
    "D13-16": dict(
        seg="B",
        st="🔨",
        name="盘中板块分钟K线层（独立直连池）",
        src=_SCHED,
        slot=["intraday_sector"],
        clk="盘中每 5 分钟（独立执行器避开全市场慢任务）",
        act="execute",
        q="板块分钟K独立池在产吗？断供几个交易日？",
        mech="独立执行器池 DAG 槽（与 miniqmt 全市场慢任务隔离）",
        gate="无前置",
        nrg="",
        fb="无（该槽不在补跑宇宙内）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:50"],
        ev=["簿 04 环节段：该层实测断供 2 交易日（在册定性）"],
        obs="盘中每 5 分钟",
    ),
    "D13-17": dict(
        seg="B",
        st="🔨",
        name="事件驱动快新闻 + EDB 轮询",
        src=_SCHED,
        slot=["event_driven"],
        clk="7×24 每 3 分钟",
        act="execute",
        q="快新闻轮询在转吗？全局 3 分钟与盘后多跑的取舍是什么？",
        mech='DAG 槽；"一任务只属一槽"由调度器精确字符串匹配强制，故无法做盘中/盘后双节拍（结构约束）',
        gate="无前置",
        nrg="",
        fb="D13-01（always_on 桶）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:57", f"{_SCHEDULE_REL}:59", "src/zephyr/data/scheduler.py:491"],
        ev=["骨架 §2 D13-17 行：提速理由是单轮耗时留余量（槽注释自证）"],
        obs="每 3 分钟",
    ),
    "D13-18": dict(
        seg="B",
        st="🔨",
        name="慢新闻/研报独立队列（限流分池）",
        src=_SCHED,
        slot=["news_slow"],
        clk="每日 17 分与 47 分（7×24）",
        act="execute",
        q="共享额度下的分池节拍成立吗？研报腿断供几个交易日？",
        mech="DAG 槽；单例限流额度共享致并行总时间与串行相同（分池理由见槽注释）",
        gate="无前置",
        nrg="",
        fb="无（该槽不在补跑宇宙内）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:66", f"{_SCHEDULE_REL}:68"],
        ev=["簿 04 环节段：研报腿实测断供 4 交易日；断供哨兵配置不含该表（配置面事实，簿 09）"],
        obs="每小时 2 拍",
    ),
    "D13-19": dict(
        seg="B",
        st="✅",
        name="板块资金流日内五快照",
        src=_SCHT,
        tn=["ZephyrAlpha_IntradayFundFlow"],
        entity=["sch_intraday_fund_flow"],
        clk="交易日五拍（上午两拍、下午两拍、收盘后一拍；时点语义见 ps1 声明面）",
        act="execute",
        q="日内五快照都落库了吗？段内快照数够下跌段差分吗？",
        mech="独立 ps1 注册的计划任务（完全不在 APScheduler 视野内）；差分需段内至少 1 快照",
        gate="无前置",
        nrg="",
        fb="无（错过即缺拍，段内差分退化）",
        ref="scripts/register_counter_trend_feeder_tasks.ps1:80",
        anc=[
            "scripts/register_counter_trend_feeder_tasks.ps1:11",
            "scripts/register_counter_trend_feeder_tasks.ps1:80",
        ],
        run=["logs/fundflow_collect.log"],
        ev=["骨架 §2 D13-19 行：留痕两拍各 90 个行业、落库各 90 行 + 表侧 max 为当日（三证齐）"],
        obs="交易日每日 5 拍",
    ),
    "D13-20": dict(
        seg="B",
        st="🔨",
        name="竞价命中判定（日内唯一带墙钟窗闸的段）",
        src=_DLOOP,
        stages=["auction_hit"],
        clk="dloop 段内；代码内墙钟窗闸限上午 10:00–10:30（非排班槽）",
        act="execute",
        q="窗闸在自动圈下开过吗？窗外 skipped 与窗内命中在这张图上能区分吗？",
        mech="dloop 段 + 墙钟窗闸；只被 16:45 圈或人工逃生口调用 → 自动圈下恒在窗外=结构性失效",
        gate="D13-32 的 16:45 圈（或人工逃生口）+ 墙钟落窗",
        nrg="",
        fb="无（能力活在事件链，不在排班链）",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:294",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:73",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:294",
        ],
        ev=[
            "簿 07 §1.4 段 11：自动但恒不产出（结构性）——16:45 恒在窗外→永久 skipped",
            "骨架 §2 D13-20 行已把该处标为实证设计缺口",
        ],
        obs="自动圈下 0 拍（恒 skipped）",
        extra=dict(window_gate_dead_under_auto_loop=True),
    ),
    "D13-21": dict(
        seg="B",
        st="✅",
        name="盘中 L1 市场状态跟踪",
        src=_DLOOP,
        stages=["intraday_l1"],
        clk="60 分钟K唤醒词驱动（dloop 盘中族）",
        act="execute",
        q="当日有没有产出行？每交易日几行？",
        mech="dloop 段：唤醒词过滤通过才跑；产物按上海日读数",
        gate="60 分钟K到位（D13-15）",
        nrg="",
        fb="D13-32 的 16:45 圈兜底重放（幂等全命中则空转）",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:211",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:211",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:68",
        ],
        tdm=["TDM-P-P2"],
        ev=["骨架 §2 D13-21 行：按上海日实测当日内在产、近日逐日行数在案（三证齐）"],
        obs="唤醒词驱动（当日数拍）",
    ),
    "D13-22": dict(
        seg="B",
        st="🔨",
        name="盘中情景归类",
        src=_DLOOP,
        stages=["classify"],
        clk="同上唤醒词驱动（dloop 段内）",
        act="execute",
        q="归类段被谁调用？调用方只有 dloop 吗？",
        mech="dloop 段 → 情景归类器；本段无独立排班",
        gate="D13-21 产出为输入",
        nrg="",
        fb="同 D13-21",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:218",
        anc=["src/zephyr/plan_engine/daily_loop_master_switch.py:218"],
        ev=["骨架 §2 D13-22 行：调用方实测仅 dloop 一处"],
        obs="唤醒词驱动",
    ),
    "D13-23": dict(
        seg="B",
        st="🔨",
        name="盘中情绪环单拍（有节拍席位、无节拍）",
        src=_DLOOP,
        stages=["sentiment_loop"],
        clk="dloop 段内，非独立排班",
        act="execute",
        q="盘中有没有拍？每日几拍？拍落在什么时刻？",
        mech="dloop 段 → 盘中情绪环单拍：无业务日记号，每次调用即一拍；唯一调用方是 dloop",
        gate="D13-32 的 16:45 圈",
        nrg="",
        fb="无（盘中零拍，无兜底器）",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:274",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:274",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:285",
        ],
        ev=[
            "簿 07 1.6 表段 10：自动圈下每交易日只 1 拍且落收盘后 16:45–16:50 窗；人工日另有盘中三拍",
            '该段注释自陈"单拍就绪没节拍——本段=节拍席位"',
        ],
        obs="每日恰 1 拍（收盘后）；盘中零拍",
        cad_declared="段注释自陈的盘中连续节拍（本段=节拍席位）",
        extra=dict(cadence_gap=True),
    ),
    "D13-24": dict(
        seg="B",
        st="✅",
        name="模拟盘保活与成交回路",
        src=_SCHT,
        tn=["ZephyrAlpha_PaperSession"],
        entity=["sch_paper_session"],
        clk="09:25 拉起后常驻至收盘后 15:05 收口",
        act="execute",
        q="保活到收口了吗？退出码与成交落盘对不对？尾段成交归属谁裁？",
        mech="常驻适配器：交易时段保活、收口撤未成交单；成交持久化在位态",
        gate="D13-12 拉起成功",
        nrg="",
        fb="D13-42 DeadmanSwitch 陈旧重跑",
        ref="src/zephyr/ex_core/live_strategy_adapter.py",
        anc=["src/zephyr/ex_core/live_strategy_adapter.py", "scripts/register_paper_session_task.ps1:47"],
        run=[".runtime/logs/paper_session.log", "data/fills/"],
        ev=[
            "骨架 §2 D13-24 行：保活至 15:05 收口、exit_code=0、slot started/slots_running=1 三证在案",
            "🌑-5：尾段成交完整捕获口径无外部规范可依（图不编造）",
        ],
        obs="常驻",
    ),
    # ── 段 C 盘后 ──────────────────────────────────────────────────────
    "D13-25": dict(
        seg="C",
        st="🔨",
        name="板块状态盘后定格（真源态）",
        src=_SCHED,
        slot=["sector_close_final"],
        clk="交易日 15:10（与 D13-26 同分钟）",
        act="execute",
        q="15:10 定格的态是 T 日还是 T-1 日？",
        mech="特殊槽分支（sector 双槽合一）→ 板块状态管线盘后腿；服务总闸实存见机生层",
        gate="当日日线已入库（16:30 才产）→ 实测系统性定格 T-1",
        nrg="",
        fb="无（缺则 D13-10 次日无源）",
        ref="src/zephyr/data/sector_state_pipeline.py:164",
        anc=["src/zephyr/data/sector_state_pipeline.py:164", "src/zephyr/data/scheduler.py:439"],
        ev=[
            '簿 06 §D13-25：15:10 时今日日线未入库 ⇒ 定格恒 T-1（改判"恒 T-1"而非"偶发滞后"）',
            "骨架 §2 D13-25 行：close_final 态窗内行数只覆盖 2 个交易日、缺 1 日",
        ],
        obs="交易日每日 1 拍",
        extra=dict(locks_t_minus_1=True),
    ),
    "D13-26": dict(
        seg="C",
        st="✅",
        name="指数分钟K日终补拉（峰谷下跌段探测器供料）",
        src=_SCHT,
        tn=["ZephyrAlpha_IndexMinuteEOD"],
        entity=["sch_index_minute_eod"],
        clk="交易日 15:10（计划任务；主源失败另有降级源腿）",
        act="execute",
        q="15:10 拉到根数了吗？主源失败降级有没有留痕？",
        mech="独立 ps1 注册计划任务 → 分钟K补拉落行情表",
        gate="收盘（交易所时钟）",
        nrg="",
        fb="无（缺则下跌段探测器无料）",
        ref="scripts/register_counter_trend_feeder_tasks.ps1:86",
        anc=[
            "scripts/register_counter_trend_feeder_tasks.ps1:14",
            "scripts/register_counter_trend_feeder_tasks.ps1:86",
        ],
        run=["logs/index_minute_eod.log"],
        ev=["骨架 §2 D13-26 行：末次拉取根数与源标注留痕在案，上一行为源失败降级记录"],
        obs="交易日每日 1 拍",
    ),
    "D13-27": dict(
        seg="C",
        st="🔨",
        name="盘中持仓对账事件入口（与 D13-29 分工）",
        src=_EVENT,
        slot=[],
        clk="无槽：position 事件驱动（真跑的另一腿是进程内定时器，非注释自证的事件入口）",
        act="execute",
        q="对账到底由事件触发还是定时器触发？事件入口腿今天醒过吗？",
        mech="持仓对账器两条腿：事件入口腿（零调用方）+ 定周期腿（真跑）；与 D13-29 三账是两条链不合并",
        gate="成交回报事件面（实测行数极低）",
        nrg="",
        fb="无",
        ref="src/zephyr/ex_core/position_reconciler.py",
        anc=[f"{_SCHEDULE_REL}:204", "src/zephyr/ex_core/position_reconciler.py"],
        ev=[
            "簿 06 硬实查⑤：两条链拆开——事件入口腿零调用、定周期腿真跑；排班注释的两句自辩与实态方向相反",
            '骨架 §2 D13-27 行：注释自证"本槽位是定时事实核对，非自愈 reconciler 环路"',
        ],
        obs="定周期腿每若干分钟；事件入口腿 0 次",
        extra=dict(entry_leg_unwired=True),
    ),
    "D13-28": dict(
        seg="C",
        st="✅",
        name="盘后结算管线（T+1 结算单就绪硬时点）",
        src=_SCHT,
        tn=["ZephyrAlpha_PostSettlement"],
        entity=["sch_post_settlement"],
        clk="交易日 15:30（计划任务，含补火设置；同一硬时点在代码常量另有一处真源=INV-1 撞车面）",
        act="execute",
        q="15:30 结算单就绪了吗？QMT 离线时是降级还是伪造券商比对？",
        mech="计划任务 → 结算管线（系统侧核对 + 日终审计）；柜台侧真实结算单为 🌑-3（模拟账户无经纪商文件）",
        gate="收盘后券商侧回报可得（推定，外部真源=🌑-4）",
        nrg="",
        fb="QMT 离线→显式降级为仅系统侧核对（不伪造）",
        ref="src/zephyr/trading/post_settlement_pipeline.py:43",
        anc=[
            "scripts/register_post_settlement_task.ps1:42",
            "scripts/register_post_settlement_task.ps1:26",
            "src/zephyr/trading/post_settlement_pipeline.py:43",
            "scripts/run_post_settlement.py",
        ],
        run=["data/runtime/post_settlement_last_run.log"],
        ev=[
            "骨架 §2 D13-28 行：当日 trade_date/audit_status=OK/errors 空/exit_code=0 留痕在案",
            "簿 06：OK-over-zero 形态登记（空快照最小输入下的 OK 须标注，不得升格为三账证据）",
        ],
        obs="交易日每日 1 拍",
        extra=dict(clock_dual_source_zh="15:30 同时存在于 ps1 触发器与代码常量两处真源（簿 06 O 向）"),
    ),
    "D13-29": dict(
        seg="C",
        st="🔨",
        recheck="🌑",
        name="日终三账核对（柜台/内部/持仓 L1+L2+L3）",
        src=_SCHED,
        slot=["eod_reconciliation"],
        clk="交易日 15:40（槽每日 firing）",
        act="none",
        q="15:40 这一拍真跑了三账吗？还是假通道槽又记了一次 success？",
        mech="机生判据同 D13-13（零有效任务∧零特殊槽分支=假通道槽）；三件三账实现全零调用方",
        gate="D13-28 结算单就绪（等待边）",
        nrg="",
        fb="无（假通道槽）",
        ref="src/zephyr/trading/recon_runner.py:392",
        anc=["src/zephyr/trading/recon_runner.py:392", f"{_SCHEDULE_REL}:202", "src/zephyr/data/scheduler.py:2256"],
        data=["docs/03_modules/_domain_trading/"],
        ev=[
            '簿 06 §D13-29 三证互不依赖：15:40:03 现场捕获"无任务→APScheduler success"；'
            "两件三账实现（MOD-TRADING-013/MOD-L06-003）全仓零调用方；差异表全表 0 行",
            "假绿源划清：门禁/自愈环留痕表有约 8.8 万行且当日在写，列语义全是提交侧（gate_id/commit_message），"
            '与资金/持仓/柜台三账零关系——按"有留痕=在跑"判绿即中招',
            '该模块头仍自陈"本模块不挂调度"，与已挂 15:40 槽冲突=文档滞后',
        ],
        obs="名义每日 1 拍；实为 0 拍",
        dangling=["slot:eod_reconciliation"],
        extra=dict(idle_slot_expected=True, false_green_source_zh="reconcile_execution_log 行数强阳性与本环节无关"),
    ),
    "D13-30": dict(
        seg="C",
        st="✅",
        name="盘后日K线层（当日主行情落库=下游全链就绪门）",
        src=_SCHED,
        slot=["daily_kline"],
        clk="交易日 16:30（heavy 池串行）",
        act="execute",
        q="16:30 批次收口了吗？标的数看门铃响了吗？本图全链就绪门成立否？",
        mech="DAG 槽（有效挂载数见机生层）+ 批后标的数看门铃；内部结构归图 12",
        gate="交易所日终批处理推定完成（🌑-4：无外部真源）",
        nrg="",
        fb="D13-01 档期对账 + D13-35 行数视角补下载",
        ref="src/zephyr/data/scheduler.py:2265",
        anc=[f"{_SCHEDULE_REL}:79", "src/zephyr/data/scheduler.py:2265"],
        ev=[
            "骨架 §2 D13-30 行：日K线索表 max 为前一交易日（当日未到点属正常）+ 实测挂载任务数量级在案",
            '簿 08 X-11：16:30 heavy 批未收口时 17:00 补下载把"仍在跑"误判为"缺"，'
            "同一任务两实例并发写同一表、flush 行序交错",
        ],
        obs="交易日每日 1 批",
        dangling=["task:cohort_ledger_daily"],
        extra=dict(readiness_gate_for=("D13-32", "D13-33", "D13-35")),
    ),
    "D13-31": dict(
        seg="C",
        st="⬜",
        name="当日回测跑批（对账 L1 基准腿）",
        src=_NONE,
        slot=[],
        clk="16:30 之后，无槽（在位排班=零）",
        act="none",
        q="当日回测今天有人排班吗？没有的话 L1 基准腿从哪来？",
        mech="唯一真源=已归档日循环 SOP 的库级调用与显式落盘约定；产物落回测工件目录",
        gate="D13-30 日K线已落库",
        nrg="",
        fb="无（无排班=无缺席告警）",
        ref=None,
        anc=["docs/_archive/57_daily_cycle_sop.md"],
        data=["docs/_archive/57_daily_cycle_sop.md"],
        ev=["骨架 §2 D13-31 行：在位排班零；归档件记 GAP-5 转候选件（编号以归档件为准，本图不复制正文）"],
        obs="无",
        extra=dict(archived_ssot_only=True),
    ),
    "D13-32": dict(
        seg="C",
        st="✅",
        name="日循环总扳手（全链多段排班编排）★本图最大节点",
        src=_SCHED,
        slot=["dloop_post"],
        clk="交易日 16:45（原仅人工、后解禁；服务总闸实存见机生层）",
        act="orchestrate",
        q="16:45 这一圈把几段跑完了？哪几段是空转？输入日是 T 还是 T-1？",
        mech='特殊槽分支 → run_daily_loop(full)：段序与幂等/fail-open 纪律进本图，各段"判什么"引用 TDM'
        "（让渡二）；实扫段集与四相成员见机生层 dloop_phases",
        gate="D13-30 日K线到位（缺则整圈在 T-1 上重放且仍记 SUCCESS）",
        nrg="",
        fb="无（fail-open 逐段留痕；唯二 fail-closed 在段内）",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:337",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:337",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:402",
            f"{_SCHEDULE_REL}:242",
        ],
        run=["data/runtime/daily_loop_master.disabled"],
        tdm=["TDM-E-L0-03"],
        ev=[
            "骨架 §2 D13-32 行：三证齐（槽+段序实扫+当日拍板表在产）；总闸实存扫=不存在（机生层 service_flags）",
            '簿 07 §1.6：两圈耗时差一个量级=幂等全命中空转的量化实证（"跑了"≠"重算了"）',
        ],
        obs="交易日每日 1 圈",
        extra=dict(orchestrates_stages=True),
    ),
    "D13-33": dict(
        seg="C",
        st="🔨",
        name="收盘验证→三表结算（段序契约：verify 恒先于 settle）",
        src=_DLOOP,
        stages=["close_verify", "settle"],
        clk="dloop 段内（无独立时点）",
        act="execute",
        q="verify 与 settle 的先后守住了吗？结算今天扫到几行？",
        mech="dloop 相邻两段 + 钩子序契约（注释自证）；结算腿按判定表族遍历",
        gate="D13-30 日K线 + D13-32 圈已跑到该段",
        nrg="",
        fb="无",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:225",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:225",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:335",
        ],
        ev=[
            "骨架 §2 D13-33 行：验证表 scenario_hits 带触发时刻读数在案",
            '簿 09 §9.3：结算腿扫到 0 行时静默空转，不区分"本无事"与"该有活却扑空"',
        ],
        obs="每圈 1 次",
    ),
    "D13-34": dict(
        seg="C",
        st="✅",
        name="日度拍板（安全态：毕业包恒空→结构性无实盘）",
        src=_DLOOP,
        stages=["decision"],
        clk="dloop 末段",
        act="execute",
        q="今天这一拍出了日度判定吗？判定产物落库了吗？",
        mech="dloop 末段 → 日度决策编排器；下单动作归 TDM L4/X-S2（边界），本图只记时点与产物",
        gate="D13-33 verify→settle 已完成",
        nrg="",
        fb="无",
        ref="src/zephyr/plan_engine/daily_loop_master_switch.py:239",
        anc=[
            "src/zephyr/plan_engine/daily_loop_master_switch.py:239",
            "src/zephyr/plan_engine/daily_loop_master_switch.py:44",
        ],
        tdm=["TDM-E-L0-03"],
        ev=["骨架 §2 D13-34 行：日度判定表 max(trade_date)=当日 + 全表行数量级在案"],
        obs="每圈 1 次",
    ),
    "D13-35": dict(
        seg="C",
        st="✅",
        name="盘后数据批次群（资金面·事件·当日补下载）",
        src=_SCHED,
        slot=["daily_backfill", "daily_capital", "daily_event"],
        clk="交易日 17:00 / 18:00 / 19:00 三拍",
        act="auto_remediate",
        q='三拍各自动手了吗？17:00 补下载有没有把"仍在跑"误判为"缺"？',
        mech='三槽合并为一个批次节点（内部结构归图 12，让渡三）；17:00 是行数视角补下载（本段唯一"有手"腿）',
        gate="D13-30 批次已收口（今日它实际没有=结构性缺陷）",
        nrg="",
        fb="D13-01 档期视角 / D13-38 仅告警",
        ref="src/zephyr/data/backfill_checker.py",
        anc=["src/zephyr/data/scheduler.py:219", f"{_SCHEDULE_REL}:148", f"{_SCHEDULE_REL}:85"],
        ev=[
            "簿 08 X-11：17:00 补下载于 16:30 批未收口时二次开同一任务 → 同表两实例并发写、flush 行序交错",
            "骨架 §2 D13-35 行：三槽挂载任务数量级在案 + 资金面表侧 max 为前一交易日（昨日已产=正常）",
        ],
        obs="交易日每日 3 拍",
        dangling=["task:cohort_ledger_daily"],
        extra=dict(ready_gate_absent_zh='17:00 腿缺"daily_kline 批次已收口"前置（本图可红用例）'),
    ),
    # ── 段 D 夜窗与贯穿 ────────────────────────────────────────────────
    "D13-36": dict(
        seg="D",
        st="🔨",
        name="研报明细增量层（全市场逐股长批）",
        src=_SCHED,
        slot=["research_nightly"],
        clk="交易日 20:30（单实例上限 1）",
        act="execute",
        q="夜窗长批起跑了吗？增量窗补上几行？",
        mech="DAG 槽（有效挂载数见机生层）；历史回补量大、日度仅补增量窗（槽注释自证）",
        gate="无前置",
        nrg="",
        fb="无（该槽不在补跑宇宙内=错过无人补）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:96"],
        ev=[
            "簿 09 §3.2：本格断供 4 交易日而断供哨兵配置不含该表 ⇒ 唯一覆盖者是 23:00 巡检行数阈值（检测真空是配置面事实）"
        ],
        obs="交易日每日 1 拍",
        dangling=["slot:research_nightly"],
    ),
    "D13-37": dict(
        seg="D",
        st="🔨",
        name="夜间财务层（财报/十大股东/融资融券）",
        src=_SCHED,
        slot=["nightly_financial"],
        clk="交易日 22:00（heavy 串行）",
        act="execute",
        q="22:00 夜窗跑到几个任务？当夜漏跑名单有多大？",
        mech="DAG 槽（有效挂载数见机生层）；22:00 由因=次日披露口径此时已发布",
        gate="无前置",
        nrg="",
        fb="D13-01（daily 桶在册）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:113"],
        ev=['簿 09 §3.1：23:01 巡检"漏跑"名单同时出现本槽多数任务，与表侧 max 停在数日前同向（两条独立证据互指）'],
        obs="交易日每日 1 拍",
    ),
    "D13-38": dict(
        seg="D",
        st="🔨",
        name="每日完整性巡检（只检测+告警，不补跑）",
        src=_SCHED,
        slot=["integrity_check"],
        clk="交易日 23:00",
        act="alert_only",
        q="23:00 巡检检出几条不达标？它自己动手吗？三路兜底边界谁在守？",
        mech="特殊槽分支 → 全表达标巡检（动态发现真源清单）；三路分工=档期视角(D13-01)/行数视角(D13-35)/"
        "只告警(本腿)，其真源至今是排班文件散文注释，本图把它变成三条边",
        gate="当日各批次已跑完（否则误判缺）",
        nrg="",
        fb="无（只告警不动手）",
        ref="src/zephyr/data/integrity_checker.py",
        anc=["src/zephyr/data/scheduler.py:225", f"{_SCHEDULE_REL}:153", f"{_SCHEDULE_REL}:159"],
        ev=[
            "骨架 §2 D13-38 行：三路分工真源=散文注释（本图要变成可查边）",
            "簿 09 3.3：四路检测里只有 17:00 动手，23:00/23:30/06:50 一律落表/落文件",
        ],
        obs="交易日每日 1 拍",
    ),
    "D13-39": dict(
        seg="D",
        st="🔨",
        name="一致预期管线双向验证",
        src=_SCHED,
        slot=["consensus_crosscheck"],
        clk="交易日 23:30（单实例）",
        act="detect_only",
        q="23:30 双向对答案了吗？不一致时谁被通知？总闸开着吗？",
        mech="特殊槽分支 → 交叉验证（秩相关/新鲜度/结构断言/PIT 修正率四查），产物落交叉验证日志表",
        gate="自建聚合与外部快照两侧均已落库",
        nrg="",
        fb="无（落表即止）",
        ref="src/zephyr/data/consensus_crosscheck.py:62",
        anc=["src/zephyr/data/consensus_crosscheck.py:14", "src/zephyr/data/scheduler.py:341", f"{_SCHEDULE_REL}:103"],
        run=["data/runtime/consensus_crosscheck.disabled"],
        ev=[
            "骨架 §2 D13-39 行：源污染事件治本配套（槽注释自证）",
            "服务总闸实存扫=不存在（机生层 service_flags，不存在即开着）",
        ],
        obs="交易日每日 1 拍",
    ),
    "D13-40": dict(
        seg="D",
        st="🔨",
        name="另类宏观日频（假日缺价保守游标自愈）",
        src=_SCHED,
        slot=["daily_alt_fx"],
        clk="交易日 23:35",
        act="execute",
        q="23:35 这一拍的游标自愈了吗？它是 L1 上架流水线的首个正门槽位，排班外它归谁？",
        mech="DAG 槽（有效挂载数见机生层）；保守游标治假日缺价",
        gate="外部参考汇率可得",
        nrg="",
        fb="无（该槽不在补跑宇宙内）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:194"],
        ev=["骨架 §2 D13-40 行：槽注释自证为 L1 上架流水线首个正门槽位"],
        obs="交易日每日 1 拍",
        dangling=["slot:daily_alt_fx"],
    ),
    "D13-41": dict(
        seg="D",
        st="🔨",
        name="周批与月批（跨过日界的重活）",
        src=_SCHED,
        slot=["weekend_backfill", "weekend_calibration", "monthly_static"],
        clk="周初凌晨两拍 + 月初一拍（同文件内两条互斥的星期口径注释在册，须机械判定）",
        act="execute",
        q="周窗真在意图中的那天 firing 吗？口径注释互斥时以哪条为准？",
        mech="三槽（特殊槽分支 + 两 DAG 槽）；dow 口径互斥属时钟事故族，判定归机生层与实查，图不裁",
        gate="QMT 可达 + 避开晨维护窗",
        nrg="",
        fb="D13-01（weekly/monthly 桶在册）",
        ref=_SCHEDULER_REL,
        anc=[f"{_SCHEDULE_REL}:119", f"{_SCHEDULE_REL}:125", f"{_SCHEDULE_REL}:136"],
        ev=[
            '骨架 §2 D13-41 行：实测在册时钟事故两起——同一文件内两条互斥星期口径断言（一条"0=周日"、'
            '一条"0=周一"），且周窗未 firing 已咬过一次（上游链断多日）'
        ],
        obs="周 1 拍 + 月 1 拍",
        extra=dict(dow_semantics_conflict=True),
    ),
    "D13-42": dict(
        seg="D",
        st="🔨",
        name="常驻守护三路（reaper / deadman 心跳 / guard 三件套）",
        src=_SCHT,
        tn=[
            "ZephyrAlpha_ProcessReaper",
            "ZephyrAlpha_DeadmanSwitch",
            "ZephyrAlpha_DataScheduler",
            "ZephyrAlpha_TickSubscriber",
            "ZephyrAlpha_TradingWatchdog",
        ],
        entity=["sch_trading_watchdog"],
        clk="登录时 + 每 5 分钟重点火（主体让渡 GOMAP，本图只留日序接缝三点）",
        act="auto_remediate",
        q="09:25 前谁必须活着？15:05 后谁该退？心跳缺失算不算当日 FAIL？",
        mech="ps1 注册守护族：单实例唯一真源=脚本级 PID 锁 + 心跳判定（计划任务必须不参与单实例决策）；"
        "看门狗一台按裁定注册于禁用态",
        gate="无前置（贯穿全日）",
        nrg="",
        fb="心跳陈旧→计划任务重跑",
        ref="scripts/register_guard_tasks.ps1:20",
        anc=[
            "scripts/register_guard_tasks.ps1:46",
            "scripts/register_guard_tasks.ps1:33",
            "scripts/deadman_switch.ps1:138",
        ],
        run=[".runtime/"],
        ev=[
            '骨架 §2 D13-42 行：两日静默死亡根因已锁在"让计划任务参与单实例决策"上；一台看门狗按在册裁定处于禁用态',
            "簿 01 O-2：晨间重启风暴（当日多次重注册）与本图 D13-01 长批夭亡同时点——重启主体与节律归 GOMAP，"
            "日序风险本图记账",
        ],
        obs="每 5 分钟重点火",
    ),
    "D13-43": dict(
        seg="D",
        st="🔨",
        name="交易日历闸门（本图不变量载体：事件触发禁定时器）",
        src=_EVENT,
        slot=[],
        clk="每槽触发时实查（无独立时点）",
        act="execute",
        q="今天该不该跑？这一拍是被守卫跳掉还是被幂等吸收？",
        mech="日历守卫名单覆盖槽集见机生层 calendar_guard（实测少数槽受守卫，余下靠底层幂等吸收）；"
        "铁律真源=图 9 laws 第 3 条与运维红线（事件触发禁定时器），本图不复制正文",
        gate="交易日历本身可得（保守判据）",
        nrg="",
        fb="非交易日空跑由底层幂等闸吸收",
        ref="src/zephyr/data/trading_calendar.py:151",
        anc=["src/zephyr/data/trading_calendar.py:151", "src/zephyr/data/scheduler.py:184"],
        ev=[
            "簿 09 机械抽取：守卫成员数与排班槽总数比值在案（未守卫槽名单已逐名列出）",
            "生效实证=非交易日会话拉起腿显式 SKIP(is_trading_day=False)",
        ],
        obs="全日每拍实查",
        extra=dict(guards_only_subset=True),
    ),
    "D13-44": dict(
        seg="D",
        st="⬜",
        recheck="🔨",
        name="日界交接（T 日盘后 → T+1 日盘前的状态移交）",
        src=_DLOOP,
        stages=["next_day"],
        clk="夜窗收口 → 次日 05:30 重启（段界）",
        act="execute",
        q="T 日的判定与边界真的交给 T+1 了吗？交接件今天有几行？",
        mech="dloop 盘后段产次日预测 + 三件边界规划器；三班制交接件面向连续市场不覆盖 A 股日界",
        gate="D13-34 日度拍板已完成",
        nrg="",
        fb="次日 daily_plan 查不到即明写降级并折减置信度（不静默用旧值）",
        ref="src/zephyr/plan_engine/next_day_forecaster.py:268",
        anc=[
            "src/zephyr/plan_engine/intraday_tomorrow_forecast.py",
            "src/zephyr/plan_engine/tomorrow_boundary_planner.py",
            "src/zephyr/plan_engine/overnight_boundary_reviser.py",
            "src/zephyr/trading/shift_handover_checklist.py",
        ],
        data=["src/zephyr/plan_engine/next_day_forecaster.py"],
        ev=[
            "簿 09 硬实查③：交接产物表按业务日（藏在引用串里，表无交易日列）实测已断供多个已收盘交易日；"
            "根因锁定在发射件一处变量名错位→负值被产物校验器 fail-closed 拒发（按桶确定性杀掉多数交易日）",
            "真静默在编排层（段状态硬编码 ok）与校准腿（扫 0 行、样本冻结而聚合面照常出数）",
            "并发现象另记 D13-30/D13-35（同一任务两实例并发写一张表、行序交错）",
        ],
        obs="每圈 1 次（当日实为 0 产出）",
        extra=dict(
            supply_broken=True,
            business_date_anchor="inputs_ref 内嵌交易日串（表侧无交易日列）",
            silent_layer_zh="编排层段状态与校准腿聚合面掩盖断供",
        ),
    ),
    # ------------------------------------------------------------------
    # gap 节点（骨架外显性化缺口件：簿 10 表A/表C 与图 12 侧跨图缺口；六图终局卷 §1 裁定一
    # "gap 与聚合点是合法节点，但须带 red_reason「）。无实现代码可挂 ⇒ module_id=null +
    # red_reason 必填；代码坐标进 source_anchors（module_ref 留空，避免 CV-BUS 假矛盾）。
    # 增删须同步校验器 NODE_UNIVERSE 与本件 NODE_ORDER；待总包回写骨架 §2（本车道禁改骨架）。
    # ------------------------------------------------------------------
    "D13-G01": dict(
        gap=True,
        seg="A",
        st="⬜",
        name="无产出证据态缺位（「该产 N 条而实产 0」与「没跑」在图上同形）",
        src=_NONE,
        slot=[],
        clk="全图 44 格共有的表达缺口（无独立时点）",
        act="none",
        q="槽在 firing、任务记 SUCCESS、产物表 0 行——图上这算绿、算红，还是算不可确定？",
        mech="状态轴只有骨架 §2 三态（🌑 不占格），「无物化事件」被硬塞进 🔨/⬜。外部对标表A-A3 点名"
        "业界第四态 unknown（无物化事件时不判绿也不判红，判不可确定）；本车道**不改状态口径**"
        "（加态=改判据，触表C-C3 判据分歧，留总包复裁），只把缺格钉成 gap 节点。"
        "可机检的半边已在本图落地：expected_emits_per_trading_day（应产断言）∧ "
        "machine_facts.slot_facts.idle_slot（零任务零分支实扫）两条并读即可判「该产 N 而实产 0」，"
        "不加新态也能显红",
        gate="无前置",
        nrg="本格是表达缺口登记位，非就绪门格",
        fb="none:无第四态⇒不可确定形态混入绿/灰两态",
        ref=None,
        anc=["src/zephyr/data/scheduler.py:2256", f"{_SCHEDULE_REL}:34", f"{_SCHEDULE_REL}:202"],
        doc=[_EXT_BOOK],
        ev=[
            "簿 10 §1.2 与表A-A3（Dagster freshness 四态，一手页面已读到原文）+ 表C-C3"
            "（骨架状态四态封闭是批次志与封矿计数的算术基准，加态须总包落笔）",
            "复跑: 读 machine_facts.trigger_surfaces.dangling_objects.fake_channel_slots 非空"
            "（2 槽零任务零分支而被记 success）——现状以「假通道槽」承载同一事实，缺的是态不是证据",
        ],
        obs="0 拍（表达位不存在，非执行位）",
        red="unwired",
    ),
    "D13-G02": dict(
        gap=True,
        seg="B",
        st="⬜",
        name="成交回报桥面空转（消费方在等一条没有接线在写的表）",
        src=_NONE,
        slot=[],
        clk="随 D13-24 常驻（无独立时点）",
        act="none",
        q="成交→回报表→三账 L1 腿这条链今天有原料可流吗？下游按「永远为空」设计降级算不算供给？",
        mech="图 12 侧消费端反查在册的「在等没在产」五态中落到本图环节面的一条：本表近 7 日仅 1 行、"
        "当日 0 行；生产端仅对模拟桥可选接线，实盘链路在册原话为「未接线=零行为变更」。"
        "两条独立成因图上必须分列：①模拟盘无票池⇒0 成交（簿 05 下向）②回报表自上期后未再被写过"
        "（表侧读数）。写入通道与幂等归图 12（让渡三），本图只画「谁在等、等什么」，不重画其内部",
        gate="无前置",
        nrg="本格是跨图缺口登记位，非就绪门格",
        fb="none:桥面无料⇒三账 L1 基准腿今日无原料",
        ref=None,
        anc=["src/zephyr/ex_core/position_reconciler.py", "src/zephyr/trading/three_way_reconciliation.py"],
        doc=[f"{_BOOK_DIR}/05_盘中资金流与决策层.md", "docs/_working/map_build/fig12_datachain/11_消费端需求反查.md"],
        ev=[
            "图 12 簿 11 §1-C（消费方在等未产表 5 条之一，生产端实况逐条实测在册）",
            "簿 05 下向：本表全表 1 行、当日 0 行；盘后侧独立同证（结算留痕 fills=0 records=0 symbols=0）",
        ],
        obs="0 行/交易日（表在而链路无原料）",
        red="broken_supply",
    ),
    "D13-G03": dict(
        gap=True,
        seg="C",
        st="⬜",
        name="三账差异表恒空且消费方已按恒空设计降级",
        src=_NONE,
        slot=[],
        clk="随 D13-29 的 15:40 名义时点（该腿从未产出）",
        act="none",
        q="差异表 0 行是「今日无差异」还是「核对从未跑成」？下游拿「空表不阻断」当绿灯怎么办？",
        mech="自建表以来零行（写入侧全仓唯一一处 INSERT，其调用链零在位）；下游判据册已把「空表不阻断"
        "写死⇒ 恒空被固化为合规态，「跑过且无差异」与「没跑」不可区分——正是簿 10 表A-A7 点名的"
        "no-drift 留痕缺口。假绿温床另记：门禁/自愈环留痕表行数强阳性而列语义全是提交侧，"
        "与资金/持仓/柜台三账零关系（簿 06 假绿专段）",
        gate="无前置",
        nrg="本格是跨图缺口登记位，非就绪门格",
        fb="none:恒空即被下游读作「无差异」，无第二条证据路",
        ref=None,
        anc=["src/zephyr/trading/recon_runner.py:117", "src/zephyr/reporting/reconciliation_schema.py:42"],
        doc=[f"{_BOOK_DIR}/06_盘后结算与三账.md", _EXT_BOOK],
        ev=[
            "簿 06 §D13-29 三证互不依赖（15:40 现场捕获 + 两件同族实现零调用方 + 差异表全表 0 行）",
            "图 12 簿 11 §1-C 消费侧新证：回测待办册判据「空表不阻断」（恒空已进降级设计）",
        ],
        obs="0 行（自建表以来）",
        red="broken_supply",
    ),
    "D13-G04": dict(
        gap=True,
        seg="B",
        st="⬜",
        name="新闻产物表库名前缀写错的幽灵引用（改册面归图 12，本图只挂生产者腿）",
        src=_NONE,
        slot=[],
        clk="随 D13-17/D13-18 采集节拍（引用名与本图时序面无时刻关系）",
        act="none",
        q="被消费的表名在册吗？按错库名订阅的消费者会不会永远读到空而不报错？",
        mech="图 12 侧全库逐名核对：册面引用的 c1_market 前缀新闻表不存在，真身在 c3_fundamental"
        "（行数新鲜）。本图只登记「生产者腿在本图、幽灵名在册外」这一交叉事实，"
        "**不建图 12 的环节、不改册**（改册面属其车道与图 9 册的处置权）",
        gate="无前置",
        nrg="本格是跨图缺口登记位，非就绪门格",
        fb="none:错名订阅恒空返，与真表新鲜同形",
        ref=None,
        anc=["src/zephyr/data/scheduler.py:491", _SCHEDULE_REL],
        doc=["docs/_working/map_build/fig12_datachain/11_消费端需求反查.md", _EXT_BOOK],
        ev=[
            "图 12 簿 11 §1-D 幽灵引用（system.tables 逐名核对 exists:false；全库同名仅一表）",
            "簿 04 §D13-17 生产者腿三证齐（当日本槽千余次执行、真表当日 FINAL 千行级）"
            "⇒ 缺陷在引用名而不在供给，本图不得据此下调 D13-17 的态",
        ],
        obs="0（错名侧无供给，真表侧新鲜）",
        red="ghost_ref",
    ),
}

# L1 tdm_refs 补挂面（六图终局卷 §4 图13「还差的活」：填充率 <1/3 须补）。
# 每条挂载的**在册性判据**（校验器 CV-TDM 逐条比 TDM node_id 全集）+ **语义判据二选一**：
# ①TDM 节点的 module_ref 与本环节的实现代码同源，或 ②本环节产物表恰是该 TDM 节点的 data_refs
# （DS-* 解析见 config/trading_decision_map.yaml 与图 12 簿 11 §1 表→消费方反查）。
# 决策内容一律走本字段引用，节点内禁判据字段（让渡二/禁则一，违者 CV-DOMAIN 判红）。
TDMX: dict[str, list[str]] = {
    "D13-04": ["TDM-E-L0-04", "TDM-E-L1-S3", "TDM-E-L2-09", "TDM-E-L9-A09", "TDM-P-P1-03"],
    "D13-10": ["TDM-E-L9-V3"],
    "D13-11": ["TDM-E-L3-11-1"],
    "D13-13": ["TDM-E-L1-AGG"],
    "D13-14": ["TDM-E-L9-A02"],
    "D13-15": ["TDM-E-L9-A01"],
    "D13-16": ["TDM-E-L2-04"],
    "D13-17": ["TDM-E-L9-A09"],
    "D13-18": ["TDM-E-L9-A09"],
    "D13-19": ["TDM-E-L2-01-4"],
    "D13-21": ["TDM-E-L1-AGG"],
    "D13-25": ["TDM-E-L9-V3"],
    "D13-27": ["TDM-P-P1-01", "TDM-E-L4-13"],
    "D13-29": ["TDM-E-L4-13"],
    "D13-30": ["TDM-E-L3-12-3"],
    "D13-33": ["TDM-E-L9-V1", "TDM-E-L9-V3"],
    "D13-35": ["TDM-E-L2-01-4"],
    "D13-44": ["TDM-E-L0-03", "TDM-E-L0-04"],
}


# ---------------------------------------------------------------------------
# L1/L2 侧挂载表（与 N 同 key 空间；六图终局卷 §1 三层字段 + §2 CV-BUS + §3 双轴裁定，
# 以及簿 10 表A 七条落字段、表C 五条判据分歧留裁）。缺 production 节点的 exec_evidence
# =生成期硬失败（不产出自粉饰的图）。
# ---------------------------------------------------------------------------

# L1 wiring_status（缺省 wired）——"槽挂着但没跑「的统一表达位，三图共用这一个字段
WIRING: dict[str, str] = {
    "D13-01": "partial",  # 每日 firing 而自上期起无一圈完成（晨间重启风暴腰斩长批）
    "D13-05": "unwired_slot_hollow",  # 槽在册、任务上线后从未自动跑成（水位全靠手动）
    "D13-06": "partial",  # 四子源在产、一子源零行（SUCCESS 而水位不动型）
    "D13-08": "partial",  # 探针挂在调度器启动上，非独立时点（整天没重启=整天没探针）
    "D13-09": "unwired_no_caller",  # 门该在、无主：三判据无仲裁件、合成器零在位
    "D13-10": "partial",  # 新增槽未热载 + 产物停 T-1
    "D13-13": "unwired_slot_hollow",  # 零任务∧零特殊槽分支⇒恒假成功
    "D13-14": "partial",  # 层在拍而多腿零产
    "D13-16": "partial",  # 独立池断供
    "D13-18": "partial",  # 分池在转而研报腿断供
    "D13-20": "unwired_slot_hollow",  # 墙钟窗闸在 16:45 自动圈下恒 skipped
    "D13-23": "partial",  # 有节拍席位无节拍（每交易日 1 拍且落收盘后窗）
    "D13-25": "partial",  # 15:10 时当日日线未入库⇒定格恒 T-1（结构性）
    "D13-27": "partial",  # 事件入口腿零调用、定周期腿真跑（自陈与实际反向）
    "D13-29": "unwired_slot_hollow",  # 假通道槽第二例
    "D13-31": "unwired_no_caller",  # 无排班、无告警主体
    "D13-35": "partial",  # 缺"批次已收口「前置⇒同表两实例并发写
    "D13-36": "partial",  # 夜窗长批断供而不在任何哨兵名单
    "D13-41": "partial",  # 同文件两条互斥星期口径，周窗实测未 firing
    "D13-44": "partial",  # 名义在产、实测断链（编排层段状态硬编码 ok 掩盖）
    "D13-G01": "unwired_no_caller",
    "D13-G02": "unwired_no_caller",
    "D13-G03": "unwired_no_caller",
    "D13-G04": "unwired_no_caller",
}

# L1 red_reason（枚举 terminal/unwired/broken_supply/ghost_ref）；module_id 空者必填（CV-BUS）
RED: dict[str, str] = {
    "D13-01": "unwired",
    "D13-05": "broken_supply",
    "D13-06": "broken_supply",
    "D13-08": "unwired",
    "D13-09": "unwired",
    "D13-10": "broken_supply",
    "D13-13": "unwired",
    "D13-14": "broken_supply",
    "D13-16": "broken_supply",
    "D13-18": "broken_supply",
    "D13-20": "unwired",
    "D13-23": "unwired",
    "D13-25": "broken_supply",
    "D13-27": "unwired",
    "D13-29": "unwired",
    "D13-31": "unwired",
    "D13-35": "unwired",
    "D13-36": "broken_supply",
    "D13-41": "unwired",
    "D13-44": "broken_supply",
}

# L1 exec_evidence=production（骨架 ✅）环节的"真在产/真在跑「复跑口径（骨架 §7 + 各簿 §实查命令）。
# 观察数随并发漂移，故一律写"命令口径 + 断言 + 观察日「，不把静态计数钉进散文（根宪法 §9 条目 5）。
EXEC: dict[str, list[str]] = {
    "D13-04": [
        "复跑（骨架 §7 C 组，DatabaseService CH 只读）：情绪窗口表 max(window_ts) 与全表行数读数",
        "复跑: grep -n 'nightly_sentiment' src/zephyr/data/scheduler.py → 特殊槽分支在位（逐日产出行）",
    ],
    "D13-07": [
        "复跑（主区只读）: tail -6 data/runtime/qmt_watchdog.log → 连续交易日两拍 OK 且带 pid",
        "复跑: grep -n 'New-ScheduledTaskTrigger' scripts/qmt_watchdog.ps1 → 两拍时点在注册声明面",
    ],
    "D13-08": [
        "复跑（主区只读）: ls -1 logs/source_health_*.log → 逐日一份在盘（簿 03 纠正「连续每日」口径："
        "非交易日与未重启日可缺档，故本环 exec 半边为日志面而非排班面）",
        "复跑: grep -n source_health src/zephyr/data/scheduler.py → 消费点在调度器启动挂接",
    ],
    "D13-11": [
        "复跑（骨架 §7 C 组）: 竞价快照表与档位表 max(trade_date)=当日 + 行数量级",
        "复跑: grep -n 'auction_highfreq' src/zephyr/data/config/schedule.yaml → 含秒槽在册、"
        "且在日历守卫 9 槽名单内（src/zephyr/data/trading_calendar.py:151）",
    ],
    "D13-12": [
        "复跑（主区只读）: grep -n 'START\\|SKIP' .runtime/logs/paper_session.log → 交易日 09:25 起、"
        "非交易日 SKIP(is_trading_day=False)、QMT 未开 SKIP 三态留痕各在案",
        "复跑: grep -n '09:25\\|Daily' scripts/register_paper_session_task.ps1 → 触发器声明面在册",
    ],
    "D13-19": [
        "复跑（主区只读）: tail -6 logs/fundflow_collect.log → 逐拍采集行业数与落库行数同为正",
        "复跑（骨架 §7 A-4）: grep -n 'New-ScheduledTaskTrigger' "
        "scripts/register_counter_trend_feeder_tasks.ps1 → 五拍时点在声明面",
    ],
    "D13-21": [
        "复跑（骨架 §7 C 组，必按上海日聚合）: judgment_intraday_market_state 按 "
        "toDate(asof_ts,'Asia/Shanghai') 计数 → 当日在产、近日逐日为正",
        "复跑: grep -n '_stage_intraday_l1' src/zephyr/plan_engine/daily_loop_master_switch.py → 段在位",
    ],
    "D13-24": [
        "复跑（主区只读）: grep -n '保活至\\|exit_code' .runtime/logs/paper_session.log → 收口时刻与退出码留痕在案",
        "复跑: grep -n 'CONSUMERS' src/zephyr/ex_core/live_strategy_adapter.py → 归档件 GAP-2 "
        "接线已落的自证面（计划任务在册）",
    ],
    "D13-26": [
        "复跑（主区只读）: tail -4 logs/index_minute_eod.log → 末次拉取根数与源标注在案，"
        "上一行为源失败降级记录（降级腿亦有留痕=真在跑的第二证）",
        "复跑: grep -n 'IndexMinuteEOD' scripts/register_counter_trend_feeder_tasks.ps1 → tn 声明面",
    ],
    "D13-28": [
        "复跑（主区只读）: tail -20 data/runtime/post_settlement_last_run.log → 当日 trade_date、"
        "audit_status=OK、errors 空、exit_code=0 四件同 in",
        "复跑: grep -n 'StartWhenAvailable\\|15:30' scripts/register_post_settlement_task.ps1 → "
        "硬时点与补火设置在声明面（同值另有一处代码常量=INV-1 撞车面，见 node note）",
    ],
    "D13-30": [
        "复跑（骨架 §7 C 组）: kline_daily / kline_index max(trade_date) 读数"
        "（16:30 前显示 T-1 属正常，作废条件见本节点 invalidation）",
        "复跑: grep -n 'daily_kline' src/zephyr/data/config/schedule.yaml src/zephyr/data/scheduler.py "
        "→ 槽与批后标的数看门铃均在位",
    ],
    "D13-32": [
        '复跑: python -c "from zephyr.plan_engine.daily_loop_master_switch import PHASE_STAGES as P;'
        'print({k: len(v) for k, v in P.items()})" → 四相段数（本图机生层同口径）',
        "复跑（主区只读）: ls data/runtime/daily_loop_master.disabled → 不存在=总闸开着；"
        "再复跑骨架 §7 C 组日度判定表 max(trade_date)=当日",
    ],
    "D13-34": [
        "复跑（骨架 §7 C 组）: c1_backtest 日度判定表 max(trade_date) 与全表行数",
        "复跑: grep -n '_stage_decision' src/zephyr/plan_engine/daily_loop_master_switch.py → "
        "末段落位与 GRADUATED_PACKAGES 安全态常量同件在盘",
    ],
    "D13-35": [
        "复跑（骨架 §7 C 组）: 资金面表 max(trade_date) 读数（17/18/19 点批次昨日已产=正常）",
        "复跑: grep -n 'daily_backfill\\|daily_capital\\|daily_event' "
        "src/zephyr/data/config/schedule.yaml → 三拍槽在册；复跑 grep -n backfill_checker "
        "src/zephyr/data/scheduler.py → 行数视角补下载执行体在位",
    ],
}

# L1 invalidation=本节点结论的作废条件（时序图特有：同一读数在不同时刻语义相反）
INVALIDATION: dict[str, str] = {
    "D13-10": "T 日 09:15 前读数必然停在上期（当日尚未产），判「滞后」须在该拍之后复跑",
    "D13-19": "五拍未跑完前（15:05 前）快照数不足属正常，非断供",
    "D13-21": "asof_ts 为 UTC 存储——不按 Asia/Shanghai 日聚合会差 8 小时而误判（骨架 §7 复跑注意 2）",
    "D13-22": "同 D13-21 的时区作废条件",
    "D13-25": "15:10 定格时当日日线尚未入库（16:30 才产）⇒「恒 T-1」是结构结论，若在 16:30 后复跑该腿则本断言作废",
    "D13-29": "15:40 前该表恒空属预期，非断供证据（须 15:40 后复跑）",
    "D13-30": "16:30 批次收口前 max(trade_date)=T-1 属正常，不作断供判据（骨架 §7 复跑注意 1）",
    "D13-32": "16:45 圈之前本日无产物属正常；判「当日在产」须 16:45 后复跑",
    "D13-33": "同 D13-32：本段产物随 16:45 圈产生，圈前判「零产出」即作废",
    "D13-34": "同 D13-32：日度判定表在 16:45 圈末段落库，圈前无当日行属正常",
    "D13-35": "三拍各在其时点前无当日产物属正常；且 16:30 heavy 批未收口时本环「缺」判定作废"
    "（同表两实例并发写=真缺陷在另一腿）",
    "D13-36": "20:30 前无当日增量属正常；全市场逐股长批跨零点时「当日」须按北京日界判定",
    "D13-38": "23:00 巡检的「漏跑」名单以当日各批已跑完为前提，否则误判（与 D13-35 同族）",
    "D13-41": "周批按 dow 口径归属而本环 dow 语义在册互斥（机生层判定前，任何「周窗未 firing」结论作废）",
    "D13-44": "交接件的业务日藏在引用串里（表侧无交易日列）——不按上海日重算即差一天，"
    "任何「缺 N 交易日」结论在换算前作废",
}

# L1 ready_gate（本节点是否就绪门格；六图终局卷 §1 L1"就绪门是否成节点「）
READY_GATE: dict[str, bool] = {"D13-09": True, "D13-30": True}

# L2 簿 10 表A-A2 freshness_severity（业界两级、本仓一档；只记实测档位不造阈值——表C-C4 留裁）
FRESHNESS: dict[str, str] = {
    "D13-14": "一档实测：本层多腿零产仅进当日执行台账，无 warn/fail 分级（外部对标 A2 缺位）",
    "D13-16": "一档实测：断供若干交易日而不在断供哨兵名单⇒无级可言（A2 缺位的极端形态）",
    "D13-36": "一档实测：断供而唯一覆盖者是 23:00 巡检行数阈值（检测真空是配置面事实）",
    "D13-37": "一档实测：夜窗漏跑名单来自 23:00 巡检，与表侧水位两因不同级",
    "D13-39": "一档实测：双向验证落日志表即止，不一致不外发分级告警",
    "D13-44": "一档实测：断供由本车道人工复跑查出，无任何分级告警覆盖",
}

# L2 簿 10 表A-A4 expected_emits_per_trading_day（"该产 N 条、实产 0「的应产断言，缺产即事件级）
# N 的推导口径=骨架 §2 时点列与机生层 cadence_class（交易日一拍类槽 ⇒ 每交易日应产 1 次）
EMITS: dict[str, int] = {"D13-13": 1, "D13-18": 1, "D13-29": 1, "D13-31": 1, "D13-44": 1}

# L2 簿 10 表A-A5 ready_basis（推定时点 vs 确认事件在字段上分离；本仓恒 assumed 直到柜台侧接入）
READY_BASIS: dict[str, str] = {"D13-28": "assumed", "D13-29": "assumed"}

# L2 簿 10 表A-A6 miss_policy 显式覆盖（余者由 derive_miss_policy 从机生面算：
# 在补跑宇宙=rerun／只检不修=alert／槽在宇宙外=absorb／无槽=none）
MISS_POLICY: dict[str, str] = {
    "D13-01": "rerun",
    "D13-35": "rerun",
    "D13-38": "alert",
    "D13-02": "alert",
    "D13-03": "alert",
    "D13-09": "none",
    "D13-31": "none",
    "D13-G01": "none",
    "D13-G02": "none",
    "D13-G03": "none",
    "D13-G04": "none",
}

# L2 簿 10 表A-A7 no_drift_evidence（跳过也要落条；false=跑过且无差异与没跑不可区分）
NO_DRIFT: dict[str, bool] = {"D13-27": False, "D13-29": False, "D13-38": False}

# L1 failure_visibility_zh（downstream_action 的配套位：检出后痕迹去哪）
FAILURE_VISIBILITY: dict[str, str] = {
    "D13-01": "档期对账台账（task_progress 汇总）+ 锁文件；崩溃腿无降级告警=静默",
    "D13-02": "failures 案卷文件 + 哨兵日志行；同 task_id 冷却去重致多红折叠一痕",
    "D13-03": "仅 WARN 日志行（不落盘、报告 dict 被特殊槽分支丢弃）=检出即蒸发",
    "D13-13": "APScheduler 记 executed successfully（假通道槽的痕迹面就是它的反面）",
    "D13-29": "名义落差异表；实测零行⇒痕迹去向=无（另有同名门禁留痕表强阳性而语义不相干）",
    "D13-38": "巡检台账 + 告警通道（webhook 侧只认更高一级，故本腿落表即止）",
    "D13-39": "交叉验证日志表（落表即止，无第二消费者）",
    "D13-42": "心跳文件 + deadman 告警；陈旧则由计划任务重跑",
    "D13-09": "无落盘面——合成器不存在即无裁定产物，「接不住当日算什么」今天的答案是默认全绿"
    "（本图最大空洞，也是本格作为一等节点要钉住的唯一事实）",
    "D13-31": "无落盘面——无排班即无缺席告警主体（归档件的产物目录约定是唯一留痕），对账 L1 基准腿因此缺料",
}

# L1 gap_refs 手工腿（表C 判据分歧留裁 + 表A 未接线处方 + 跨图缺口交叉引用；
# 落空对象台账那半边由 node_gap_refs 机械分派，两半并集即完整缺口面）
_BENCH = "docs/_working/map_build/fig13_daycycle/10_外部对标三扫.md"
GAPREF: dict[str, list[str]] = {
    "D13-09": [
        "benchmark:A1-拒准入出边清单见顶层 admission_edges（本门唯一带拒准入语义的出边集）",
        "benchmark:C2-就绪门语义强度（是否允许持续重检/挂几次）留总包复裁——本图按骨架现文"
        "只立「当日一次判定」的门，未擅自加 re_check；D13-07 的 12:55 第二拍是否升为门内复检"
        "即此分歧的具体落点，故本图未给 D13-07 加拒准入出边",
    ],
    "D13-30": [
        "benchmark:C2-收盘就绪门与开盘就绪门同字不同轴（防后来者把两门合并成一格）",
        "benchmark:A1-就绪门语义的第二宿主（本格名即「下游全链就绪门」，"
        "与 D13-09 开盘前门一字之差两轴，防混淆点已实证钉死于 D13-09 注记）",
    ],
    "D13-01": [
        "benchmark:A6-miss_policy 落格（缺「每格声明」这一层，本图先按机生面派生）",
        "benchmark:C1-rerun 是否=给定时器补跑发准生证（措辞权在总包，本车道不改口径）",
    ],
    "D13-02": ["benchmark:C1-alert 腿与 rerun 腿分工真源至今是散文注释（三路兜底边已在本图落地）"],
    "D13-03": ["benchmark:C1-detect_only 无落盘面（检出即蒸发，表A-A7 同族）"],
    "D13-05": [
        "miss:slot:daily_crypto 全体有效任务在补跑宇宙外（错过无人补，逐任务标识见本条"
        "对侧的 task: 台账项；物理表名不在本图真源面内，故不写表名只写任务标识）"
    ],
    "D13-14": ["benchmark:A2-freshness_severity 两级未接线", "benchmark:C4-分级归告警系统还是图侧声明（留裁）"],
    "D13-16": ["benchmark:A2-freshness_severity 两级未接线", "benchmark:C4-分级归告警系统还是图侧声明（留裁）"],
    "D13-17": [
        "benchmark:A2-下游情绪窗原料新鲜度分级未接线",
        "xref:ghost-table-c1_market.news_data（真身 c3_fundamental 同名表；"
        "改册面归图 12 簿 11 §1-D，本图只挂生产者腿不建其环节）",
    ],
    "D13-18": [
        "benchmark:A4-expected_emits 应产断言未接线（本格先落应产数，缺产告警仍无主体）",
        "benchmark:A2-freshness_severity 两级未接线",
        "benchmark:C4-分级归告警系统还是图侧声明（留裁）",
    ],
    "D13-20": ["benchmark:A4-窗内应产 1 拍而实产 0（恒 skipped）"],
    "D13-23": ["benchmark:A4-盘中应产 N 拍而实产 0（席位在、节拍无）"],
    "D13-24": [f"table:{_tbl('market_execution_report')}（消费方在等未产表，环节面见 gap 节点 D13-G02）"],
    "D13-27": [
        "benchmark:A7-no_drift_evidence 缺位（matched 零留痕）",
        f"table:{_tbl('market_execution_report')}（消费方在等未产表，环节面见 gap 节点 D13-G02）",
    ],
    "D13-28": [
        "benchmark:A5-ready_basis=assumed（推定与确认已在字段上分离；外部真源=🌑-4）",
        "benchmark:C5-同硬时点两处真源（ps1 触发器与代码常量）待总包定唯一位",
    ],
    "D13-29": [
        "benchmark:A5-ready_basis=assumed",
        "benchmark:A7-no_drift_evidence 缺位",
        "benchmark:A2-freshness_severity 与本环无关但同级缺位",
        f"table:{_tbl('market_reconciliation_differences')}（环节面见 gap 节点 D13-G03）",
    ],
    "D13-31": ["benchmark:A4-应产 1 次日回测而排班侧恒 0（无缺席告警主体）"],
    "D13-35": ["benchmark:C1-rerun 措辞权留总包（17:00 补下载是「有手」腿）"],
    "D13-36": [
        "benchmark:A2-freshness_severity 两级未接线",
        "benchmark:A4-夜窗长批应产断言未接线",
        "benchmark:C4-分级归告警系统还是图侧声明（留裁）",
    ],
    "D13-37": ["benchmark:A2-freshness_severity 两级未接线", "benchmark:C4-分级归告警系统还是图侧声明（留裁）"],
    "D13-38": [
        "benchmark:C1-alert 腿（23:00 只检不修）与 rerun 腿边界=本图三条边",
        "benchmark:A7-no_drift_evidence 推广到巡检格",
    ],
    "D13-39": ["benchmark:A2-freshness_severity 两级未接线", "benchmark:C4-分级归告警系统还是图侧声明（留裁）"],
    "D13-43": [
        "benchmark:C5-calendar_gated 三值（true/false/null=未声明）的 null 语义与补填义务留总包；"
        "本图只登记「无守卫是有意还是漏配读不出」这一表达缺口，不改守卫名单"
    ],
    "D13-44": [
        "benchmark:A2-断供无分级覆盖",
        "benchmark:A4-应产 1 次日界件而实产 0",
        f"table:{_tbl('judgment_next_day_forecast')}（在册断供，环节面在本格、修复归图 12）",
    ],
    "D13-G01": ["benchmark:A3-unknown 第四显示态缺位", "benchmark:C3-加态=改判据口径（本车道未改，留总包）"],
    "D13-G02": [
        "xref:fig12-消费方在等未产表-5 条中涉及本图环节者 1 条（其余 3 条归属图 12/图 9，"
        "本图不建其节点：account_nav_daily、factor_feature_value、factor_signal）"
    ],
    "D13-G03": ["xref:fig12-消费方在等未产表-reconciliation_differences（生产者=D13-29 腿，消费侧新证在册）"],
    "D13-G04": ["xref:fig12-幽灵引用-news_data（改册面，非环节面；本图只挂生产者腿 D13-17/18）"],
}

# ---------------------------------------------------------------------------
# "未过门=拒绝准入"语义边（簿 10 表A-A1 + §1.1 K8s readiness 参照：门的出边语义不是"到点照跑"，
# 而是"未过门则下游不得准入"）。本表是**契约声明**，校验器 CV-ADMIT 双向反查：
# ①列出的每条边必须在 edges 里真实存在（声明而无边=假门）②门节点的出边里语义为准入者必须
# 全部在此登记（有边而无声明=拒准入语义不可查）。表C-C2（是否允许持续重检/挂几次）本车道
# 不自裁，只在 D13-09 的 gap_refs 留痕。
# ---------------------------------------------------------------------------
ADMISSION_EDGES = [
    {
        "from": "D13-09",
        "to": "D13-12",
        "kind": "admission",
        "note_zh": "09:25 模拟盘拉起须经 09:15 前就绪门准入——现行实况=拉起腿自带 QMT 与日历双查"
        "（只代管本门 C1 一条腿与「开不开市」判定），门体本身零在位（D13-09 red_reason=unwired）",
    },
    {
        "from": "D13-09",
        "to": "D13-15",
        "kind": "admission",
        "note_zh": "09:30 起盘中分钟K滚动层须经准入——本层是 60 分钟K唤醒词腿与 dloop 盘中族的原料源头，"
        "未过门照跑=把红色天的缺料往后透传三层（表A-A1 点名的第三类准入下游）",
    },
    {
        "from": "D13-09",
        "to": "D13-11",
        "kind": "admission",
        "note_zh": "09:15-09:25 竞价采集与本门同分钟窗：采集本身不等门（错过即无），"
        "但**其产物进情绪指数档（D13-13）与盘前选股链须经准入**，本边记的是这层等待语义，"
        "不是采集时刻本身",
    },
    {
        "from": "D13-30",
        "to": "D13-32",
        "kind": "admission",
        "note_zh": "收盘就绪门（与本图开盘前就绪门一字之差、轴不同）：16:45 dloop 圈的 data_readiness "
        "腿以当日主行情落库为前置，缺则整圈在 T-1 上重放且仍记 SUCCESS（fail-closed 唯二腿之一）",
    },
    {
        "from": "D13-30",
        "to": "D13-35",
        "kind": "admission",
        "note_zh": "17:00 行数视角补下载以「16:30 heavy 批已收口」为前置；实测该前置缺失⇒同表两实例并发写"
        "（簿 08 X-11；本边是应然而非实然，缺格事实记在 D13-35 的 ready_gate_absent_zh）",
    },
]

# 边=时点先后 + 事件驱动交接（骨架 §2 四段时点序 + §2.1 机制三分交接；反向一律走 feedback_loops）
EDGES = [
    # 段 A：缺席兜底三连哨 → 就绪门 → 拉起
    ["D13-01", "D13-02"],
    ["D13-02", "D13-03"],
    ["D13-03", "D13-04"],
    ["D13-04", "D13-06"],
    ["D13-05", "D13-06"],
    ["D13-06", "D13-09"],
    ["D13-07", "D13-09"],
    ["D13-08", "D13-09"],
    ["D13-09", "D13-10"],
    ["D13-09", "D13-12"],
    ["D13-09", "D13-11"],
    ["D13-09", "D13-15"],
    ["D13-10", "D13-11"],
    ["D13-11", "D13-13"],
    ["D13-12", "D13-24"],
    # 段 B：盘中采集与决策层
    ["D13-13", "D13-14"],
    ["D13-14", "D13-15"],
    ["D13-14", "D13-16"],
    ["D13-14", "D13-17"],
    ["D13-14", "D13-18"],
    ["D13-15", "D13-19"],
    ["D13-19", "D13-25"],
    ["D13-15", "D13-21"],
    ["D13-21", "D13-22"],
    ["D13-22", "D13-23"],
    ["D13-23", "D13-20"],
    ["D13-24", "D13-26"],
    ["D13-24", "D13-27"],
    ["D13-24", "D13-28"],
    # 段 C：盘后结算→三账→日K线→dloop→批次群
    ["D13-25", "D13-28"],
    ["D13-26", "D13-28"],
    ["D13-27", "D13-28"],
    ["D13-28", "D13-29"],
    ["D13-29", "D13-30"],
    ["D13-30", "D13-31"],
    ["D13-30", "D13-32"],
    ["D13-31", "D13-33"],
    ["D13-32", "D13-33"],
    ["D13-33", "D13-34"],
    ["D13-30", "D13-35"],
    ["D13-32", "D13-35"],
    ["D13-34", "D13-44"],
    # 段 D：夜窗收口与贯穿
    ["D13-35", "D13-36"],
    ["D13-36", "D13-37"],
    ["D13-37", "D13-38"],
    ["D13-38", "D13-39"],
    ["D13-39", "D13-40"],
    ["D13-40", "D13-44"],
    ["D13-41", "D13-44"],
    ["D13-42", "D13-43"],
    ["D13-43", "D13-44"],
    # 兜底器接原槽（档期视角/行数视角）
    ["D13-01", "D13-06"],
    ["D13-01", "D13-14"],
    ["D13-01", "D13-30"],
    ["D13-01", "D13-37"],
    ["D13-01", "D13-41"],
    # gap 节点显性化：边从"受影响环节"指向缺口（缺口不许画成孤岛；CV-GAP 逐节点反查）
    ["D13-13", "D13-G01"],
    ["D13-29", "D13-G01"],
    ["D13-24", "D13-G02"],
    ["D13-27", "D13-G02"],
    ["D13-29", "D13-G03"],
    ["D13-31", "D13-G03"],
    ["D13-17", "D13-G04"],
    ["D13-18", "D13-G04"],
]

FEEDBACK_LOOPS = [
    {
        "from": "D13-23",
        "to": "D13-20",
        "note": "intraday 相段序：PHASE_STAGES 实扫盘中族段序为 intraday_l1→classify→sentiment_loop→"
        "auction_hit，与本图环节编号（按墙钟时点排）逆向——段序契约边，非时点先后",
    },
    {
        "from": "D13-02",
        "to": "D13-01",
        "note": "断供→回补：哨兵检出档期错过后，修复腿让渡次日 05:30 档期对账（其 INVARIANTS 自陈只检测不修复）",
    },
    {
        "from": "D13-38",
        "to": "D13-35",
        "note": "巡检→补下载：23:00 只告警的行数缺口交给次日 17:00 行数视角补下载（三路兜底分工的第三条边）",
    },
    {
        "from": "D13-44",
        "to": "D13-01",
        "note": "日界交接回次日：T 日盘后状态移交 → T+1 日 05:30 重启（本图唯一的跨日闭环）",
    },
    {
        "from": "D13-32",
        "to": "D13-21",
        "note": "16:45 圈回头驱动盘中段（intraday 族唤醒词在自动圈内被伪造）——段界折叠，非时点先后",
    },
    {"from": "D13-32", "to": "D13-22", "note": "同上：归类段由 16:45 圈驱动，无独立盘中排班"},
    {
        "from": "D13-32",
        "to": "D13-23",
        "note": '同上：情绪环"有节拍席位无节拍"的机制来源——每交易日恰 1 拍且落在收盘后窗',
    },
    {
        "from": "D13-32",
        "to": "D13-20",
        "note": "同上且更硬：墙钟窗闸段在 16:45 圈恒窗外 → 自动驱动关系存在但产出恒为 skipped",
    },
    {
        "from": "D13-32",
        "to": "D13-09",
        "note": "盘前段盘后跑：盘前族段（含 T+1 预产腿）实跑在 16:45 圈，为次日窗先行产出（簿 07 溢出 E-3）",
    },
    {"from": "D13-42", "to": "D13-12", "note": "守护接缝：心跳陈旧则由计划任务重跑拉起腿——09:25 前必须活着是日序前置"},
]


# ---------------------------------------------------------------------------
# 机生层扫描（全部只读；禁写库/禁 OPTIMIZE/禁 DELETE；计划任务只查不注册）
# ---------------------------------------------------------------------------


def _read_text(root: Path, rel: str) -> str:
    p = root / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _ast_literal(root: Path, rel: str, name: str) -> Any:
    """从源文件 AST 取模块级字面量（不 import，避免施工期依赖运行时环境）。"""
    text = _read_text(root, rel)
    if not text:
        return None
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    try:
                        return ast.literal_eval(_unwrap_call(node.value))
                    except (ValueError, TypeError):
                        return None
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
            and node.value is not None
        ):
            try:
                return ast.literal_eval(_unwrap_call(node.value))
            except (ValueError, TypeError):
                return None
    return None


def _unwrap_call(node: ast.AST) -> ast.AST:
    """剥掉 frozenset(...)/Final[...] 包装，取内层字面量。"""
    while True:
        if isinstance(node, ast.Call) and node.args:
            node = node.args[0]
            continue
        return node


def _cadence_class(cron: str) -> str:
    """由 cron 派生**节拍类别**（标识符级语义，cron 字面量本身不进图——让渡一）。"""
    fields = str(cron or "").split()
    if len(fields) == 6:
        fields = fields[1:]
    if len(fields) != 5:
        return "unknown"
    minute, _hour, dom, _mon, dow = fields
    if minute.startswith("*/") or _hour.startswith("*/"):
        return "interval"
    if dom not in ("*", "?"):
        return "monthly"
    if dow == "*":
        return "all_week"
    if dow in ("0-4", "1-5"):
        return "trading_weekday"
    return "weekly"


def scan_schedule_slots(root: Path) -> dict[str, dict[str, Any]]:
    """schedule.yaml 槽全集：槽名 + 执行器池 + 节拍类别（无 cron 字面量、无 description 正文）。"""
    text = _read_text(root, _SCHEDULE_REL)
    if not text:
        return {}
    data = yaml.safe_load(text) or {}
    raw = data.get("schedules") or {}
    out: dict[str, dict[str, Any]] = {}
    for name, spec in raw.items():
        spec = spec or {}
        out[str(name)] = {
            "slot": str(name),
            "executor": str(spec.get("executor") or ""),
            "cadence_class": _cadence_class(spec.get("cron") or ""),
            "declared": True,
        }
    return out


def scan_task_mounts(root: Path, slot_names: set[str]) -> dict[str, Any]:
    """tasks.yaml × schedule join：有效挂载数（过滤 extra.disabled）+ 孤儿任务 + 重复 task_id。"""
    text = _read_text(root, _TASKS_REL)
    if not text:
        return {"exists": False}
    tasks = (yaml.safe_load(text) or {}).get("tasks") or []
    per_slot: dict[str, int] = {s: 0 for s in slot_names}
    tasks_by_slot: dict[str, list[str]] = {s: [] for s in slot_names}
    orphans: list[str] = []
    seen: dict[str, list[str]] = {}
    for t in tasks:
        if not isinstance(t, dict):
            continue
        sched = str(t.get("schedule") or "")
        tid = str(t.get("task_id") or "")
        disabled = bool((t.get("extra") or {}).get("disabled"))
        if sched not in slot_names:
            orphans.append(f"task:{tid}")
            continue
        if not disabled:
            per_slot[sched] = per_slot.get(sched, 0) + 1
            tasks_by_slot[sched].append(tid)
        seen.setdefault(tid, []).append(sched)
    duplicates = {tid: slots for tid, slots in seen.items() if len(slots) > 1}
    return {
        "exists": True,
        "per_slot_effective": per_slot,
        "tasks_by_slot": {k: sorted(v) for k, v in sorted(tasks_by_slot.items())},
        "orphan_task_refs": sorted(set(orphans)),
        "duplicate_task_ids": {k: sorted(v) for k, v in sorted(duplicates.items())},
        "total_declared_tasks": len(tasks),
    }


def scan_special_branches(root: Path) -> list[str]:
    """scheduler.py `_run_special_schedule` 硬编码分支面：零任务槽是否真跑的唯一机械判据。

    两种写法都要抽：`schedule_name == "x"` 与 `schedule_name in ("x", "y")`
    （sector 双槽合一即后者，漏抽会把真跑槽误判成假通道槽=反向假红）。
    """
    text = _read_text(root, _SCHEDULER_REL)
    if not text:
        return []
    body = _slice_function(text, "_run_special_schedule")
    found = set(re.findall(r'schedule_name\s*==\s*"([a-z0-9_]+)"', body))
    for tup in re.findall(r"schedule_name\s+in\s+\(([^)]*)\)", body):
        found |= set(re.findall(r'"([a-z0-9_]+)"', tup))
    return sorted(found)


def _slice_function(text: str, name: str) -> str:
    """取模块级函数体原文（把分支面限定在 `_run_special_schedule` 内，防他处同名比较误判）。"""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}("):
            start = i
            break
    if start is None:
        return ""
    for j in range(start + 1, len(lines)):
        if lines[j].startswith(("def ", "class ", "@")):
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


def scan_catchup_universe(root: Path) -> dict[str, Any]:
    """catchup_guard 档期分桶常量 = \"补跑宇宙\"：宇宙外槽的有效任务=错过无人补。"""
    buckets = (
        "_MONTHLY_SCHEDULES",
        "_WEEKLY_SCHEDULES",
        "_DAILY_SCHEDULES",
        "_INTRADAY_SCHEDULES",
        "_ALWAYS_ON_SCHEDULES",
        "_SKIP_SCHEDULES",
    )
    out: dict[str, Any] = {"source": _CATCHUP_REL, "exists": bool(_read_text(root, _CATCHUP_REL))}
    universe: set[str] = set()
    for b in buckets:
        v = _ast_literal(root, _CATCHUP_REL, b)
        members = sorted(str(x) for x in v) if isinstance(v, (set, frozenset)) else []
        out[b.lower().strip("_") + "_bucket"] = members
        if b != "_SKIP_SCHEDULES":
            universe |= set(members)
    out["universe"] = sorted(universe)
    return out


def scan_calendar_guard(root: Path) -> dict[str, Any]:
    """TRADING_DAY_GUARDED_SCHEDULES：日历守卫归属面（守卫是子集而非全集=本图不变量的空洞显性化）。"""
    v = _ast_literal(root, _CALENDAR_REL, "TRADING_DAY_GUARDED_SCHEDULES")
    members = sorted(str(x) for x in v) if isinstance(v, (set, frozenset)) else []
    return {"source": _CALENDAR_REL, "exists": bool(_read_text(root, _CALENDAR_REL)), "guarded_slots": members}


def scan_dloop_phases(root: Path) -> dict[str, Any]:
    """PHASE_STAGES 实扫（dloop_stage 归属节点的在册真源，AST 字面量不 import）。

    同时扫 `dispatch` 查表派发面的段名键集：实现自陈\"PHASE_STAGES 与派发表失同步时显式炸出\"，
    两处集合是否对齐是本图可机检的段序契约（不背段数、不抄段清单）。
    """
    v = _ast_literal(root, _DLOOP_REL, "PHASE_STAGES")
    phases: dict[str, list[str]] = {}
    if isinstance(v, dict):
        for k, seq in v.items():
            phases[str(k)] = [str(x) for x in (seq or [])]
    stages = sorted({s for seq in phases.values() for s in seq})
    text = _read_text(root, _DLOOP_REL)
    dispatched: list[str] = []
    lines = text.splitlines()
    try:
        i0 = next(i for i, ln in enumerate(lines) if ln.strip().startswith("dispatch: dict["))
    except StopIteration:
        i0 = None
    if i0 is not None:
        body: list[str] = []
        for ln in lines[i0 + 1 :]:
            if ln.strip() == "}":
                break
            body.append(ln)
        dispatched = sorted(set(re.findall(r'"([a-z0-9_]+)":', "\n".join(body))))
    return {
        "source": _DLOOP_REL,
        "exists": bool(text),
        "phases": phases,
        "stage_universe": stages,
        "dispatch_stages": dispatched,
        "dispatch_stage_sync": sorted(set(stages) ^ set(dispatched)) == [] and bool(dispatched),
        "sync_outliers": sorted(set(stages) ^ set(dispatched)),
    }


def scan_register_scripts(root: Path) -> dict[str, Any]:
    """`ZephyrAlpha_*` 任务名的脚本声明面（实存性扫描，全 ps1 面 + register_ 子集）。

    两圈都要扫：注册器 `scripts/register_*.ps1` 是主面，但 `qmt_watchdog.ps1` 这类
    自注册脚本同样在册（漏扫会让"计划任务未在册"判定在降级模式下假红）。
    """
    scripts: dict[str, list[str]] = {}
    for p in sorted(root.glob("scripts/*.ps1")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        tns = sorted(set(re.findall(r'["\'](ZephyrAlpha_[A-Za-z0-9_]+)["\']', text)))
        if tns:
            scripts[p.relative_to(root).as_posix()] = tns
    declared = sorted({tn for tns in scripts.values() for tn in tns})
    register_subset = sorted(k for k in scripts if Path(k).name.startswith("register_"))
    return {
        "script_count": len(register_subset),
        "register_scripts": register_subset,
        "declaring_scripts": scripts,
        "declared_task_names": declared,
    }


def scan_registered_schtasks(root: Path, *, skip: bool = False) -> dict[str, Any]:
    """Windows 计划任务表**只读查询**（Get-ScheduledTask，禁 Register/Unregister/Change/Enable/Disable）。

    查询失败或显式 skip → available:false + 空集：属输入差异，非错误；消费方（校验器）
    对不可用面降级跳过在册实存判定，禁把\"查不到\"冒充\"没注册\"。
    """
    if skip:
        return {"available": False, "reason": "explicit --skip-schtasks", "task_names": []}
    cmd = (
        "Get-ScheduledTask | Where-Object { $_.TaskName -like 'ZephyrAlpha_*' } "
        "| Select-Object -ExpandProperty TaskName | Sort-Object"
    )
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        r = run_subprocess_hidden(["powershell", "-NoProfile", "-Command", cmd], timeout=120)
    except Exception as e:  # noqa: BLE001 — 无 Windows 面/超时=available false（幂等仍可证）
        return {"available": False, "reason": f"{type(e).__name__}", "task_names": []}
    names = sorted({ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip().startswith("ZephyrAlpha_")})
    if r.returncode != 0 and not names:
        return {"available": False, "reason": f"exit={r.returncode}", "task_names": []}
    return {"available": True, "reason": "", "task_names": names}


def scan_service_flags(root: Path) -> dict[str, Any]:
    """`data/runtime/*.disabled` 服务总闸实存面（不存在=开着；存在=停用）——总闸真落空才看得见。"""
    rels = (
        "data/runtime/daily_loop_master.disabled",
        "data/runtime/quality_sentinel.disabled",
        "data/runtime/sector_state_pipeline.disabled",
        "data/runtime/consensus_crosscheck.disabled",
        "data/runtime/nightly_sentiment.disabled",
    )
    return {rel: {"present": (root / rel).exists()} for rel in rels}


def scan_registry_entities(root: Path, referenced: set[str]) -> dict[str, Any]:
    """排班资源册 entity_id 面：只回写**被引用**的 id + 总数（全量 81 清单属静态清单，归资源册自身）。"""
    text = _read_text(root, _REGISTRY_REL)
    if not text:
        return {"exists": False}
    entries = (yaml.safe_load(text) or {}).get("entities") or []
    ids = {str(e.get("task_id")) for e in entries if isinstance(e, dict) and e.get("task_id")}
    return {
        "exists": True,
        "total_entity_ids": len(ids),
        "referenced_entity_ids": sorted(r for r in referenced if r in ids),
        "unknown_refs": sorted(r for r in referenced if r not in ids),
    }


def scan_skeleton_status(root: Path) -> dict[str, str]:
    """骨架 §2 四张环节表状态列实扫（verified_scope 双轴的**唯一**外部同源口径）。

    与校验器同函数同口径（同一批表、同一个"状态"列），故两侧不会各自漂移。
    ✅=时点存在性+执行体存在性+最近执行证据三证齐｜🔨=有执行体而执行证据未取到｜⬜=空白格。
    文件不可读/表形变更 ⇒ 空表：调用方回落本件契约常量，校验器把该子检查降 warn（禁环境异常打死提交）。
    """
    p = root / _SKELETON
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    out: dict[str, str] = {}
    for m in re.finditer(r"^\|\s*(D13-\d{2})\s*\|[^|]*\|[^|]*\|[^|]*\|\s*([✅🔨⬜🌑])\s*\|", text, re.M):
        out[m.group(1)] = m.group(2)
    return out


def scan_module_id_index(root: Path) -> dict[str, str]:
    """depgraph 在册 module_id 面：路径 → MOD-*（两腿，逐路径核"已实现"，禁自造号）。

    腿 1：`docs/03_modules/path_ownership_map.yaml` 的 claim_type=depgraph_node 条目
          （depgraph 的仓内只读派生投影）；existence ∈ {未实现, deprecated} 者**不采信**
          ——在册面自称未实现的号不得被图引为"实现代码"总线号。
    腿 2：源文件自身 `# [BLUEPRINT] MOD-*` 头声明（depgraph 扫描器的输入面；腿 1 未覆盖该路径
          或该路径在册态为未实现时兜底），同样要求文件磁盘实存。
    两腿都查不到 ⇒ module_id=null，由校验器 CV-BUS 要求配 red_reason（有代码而无号=红，
    无代码而挂号=红，自造非 MOD-* 形态=红）。
    """
    out: dict[str, str] = {}
    p = root / _PATH_OWNERSHIP
    if p.exists():
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001 — 册不可解析=本面降级空表（CV-BUS 会报未挂全）
            data = {}
        for e in data.get("ownership") or []:
            if not isinstance(e, dict) or e.get("claim_type") != "depgraph_node":
                continue
            path = str(e.get("path") or "").replace("\\", "/")
            mid = str(e.get("owner_blueprint") or "")
            existence = str(e.get("existence") or "")
            if not path or not mid.startswith("MOD-") or existence in ("未实现", "deprecated"):
                continue
            out.setdefault(path, mid)
    for nid, spec in N.items():
        ref = spec.get("ref")
        if not ref:
            continue
        rel = _anchor_rel(ref)
        if rel in out or not (root / rel).exists():
            continue
        head = _read_text(root, rel).split("\n", 1)[0]
        m = re.match(r"^#\s*\[BLUEPRINT\]\s*(MOD-[^\s|]+)", head)
        if m:
            out[rel] = m.group(1)
    return out


def scan_roster_module_ids(root: Path) -> set[str]:
    """在册 MOD-* 全集（号段合法性判定用；生成器与校验器同口径，禁自造号）。"""
    ids = {m for m in scan_module_id_index(root).values()}
    p = root / _PATH_OWNERSHIP
    if p.exists():
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001
            data = {}
        for e in data.get("ownership") or []:
            mid = str((e or {}).get("owner_blueprint") or "") if isinstance(e, dict) else ""
            if mid.startswith("MOD-"):
                ids.add(mid)
    return ids


def scan_tdm_node_ids(root: Path) -> set[str]:
    """TDM 在册 node_id 全集（tdm_refs 的在册实存面；文件不可读=空集，调用方降 warn 跳过）。"""
    p = root / _TDM_REL
    if not p.exists():
        return set()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — TDM 不可解析=本面降级（不把热册可用性耦合进图门禁）
        return set()
    return {str(n.get("node_id")) for n in (data.get("nodes") or []) if isinstance(n, dict)}


def build_trigger_surfaces(root: Path, *, skip_schtasks: bool) -> dict[str, Any]:
    """一次全扫：三机制真源面（APScheduler 槽 / Windows 计划任务 / dloop 段）+ 落空对象台账。"""
    slots = scan_schedule_slots(root)
    slot_names = set(slots)
    mounts = scan_task_mounts(root, slot_names)
    branches = set(scan_special_branches(root))
    universe = set(scan_catchup_universe(root).get("universe") or [])
    guard = scan_calendar_guard(root)
    dloop = scan_dloop_phases(root)
    scripts = scan_register_scripts(root)
    registered = scan_registered_schtasks(root, skip=skip_schtasks)
    effective = (mounts.get("per_slot_effective") or {}) if mounts.get("exists") else {}

    for name, spec in slots.items():
        cnt = int(effective.get(name, 0))
        spec["effective_task_count"] = cnt
        spec["special_branch_exists"] = name in branches
        spec["calendar_guarded"] = name in set(guard.get("guarded_slots") or [])
        spec["in_catchup_universe"] = name in universe
        spec["idle_slot"] = cnt == 0 and name not in branches
    idle = sorted(s for s, v in slots.items() if v.get("idle_slot"))
    outside = sorted(
        s
        for s, v in slots.items()
        if v.get("declared") and not v.get("in_catchup_universe") and int(v.get("effective_task_count") or 0) > 0
    )
    orphans = sorted(set(mounts.get("orphan_task_refs") or []))
    dup_map = mounts.get("duplicate_task_ids") or {}
    by_slot = mounts.get("tasks_by_slot") or {}
    # 落空对象台账（逐条可查）：每条=标识符 + 类型 + 归属环节（owner_nodes）。
    # 任务级展开（补跑宇宙外按任务计数，与骨架 §7 A-3 的"任务数"口径一致），
    # 归属分派：槽名命中该环节的 slot_refs；孤儿任务归档期对账腿（三机制均看不见=唯一档期视角兜底者）。
    slot_owners: dict[str, list[str]] = {}
    for nid, spec in N.items():
        for s in spec.get("slot") or []:
            slot_owners.setdefault(s, []).append(nid)
    entries: list[dict[str, Any]] = []
    for s in idle:
        entries.append(
            {"id": f"slot:{s}", "kind": "fake_channel_slot", "owner_nodes": sorted(slot_owners.get(s) or [])}
        )
    for o in orphans:
        entries.append({"id": o, "kind": "orphan_task", "owner_nodes": ["D13-01"]})
    for s in outside:
        for tid in by_slot.get(s) or []:
            entries.append(
                {
                    "id": f"task:{tid}",
                    "kind": "task_outside_catchup_universe",
                    "slot": s,
                    "owner_nodes": sorted(slot_owners.get(s) or []),
                }
            )
    for tid, slot_list in sorted(dup_map.items()):
        owners = sorted({nid for s in slot_list for nid in (slot_owners.get(s) or [])})
        entries.append(
            {"id": f"task:{tid}", "kind": "double_slot_task", "slots": sorted(slot_list), "owner_nodes": owners}
        )
    entries.sort(key=lambda e: (e["kind"], e["id"]))
    dangling_total = len(entries)
    return {
        "scheduler_slots": {k: slots[k] for k in sorted(slots)},
        "slot_total": len([v for v in slots.values() if v.get("declared")]),
        "catchup_universe": scan_catchup_universe(root),
        "special_branch_slots": sorted(branches),
        "calendar_guard": guard,
        "dloop_phases": dloop,
        "register_scripts": scripts,
        "registered_schtasks": registered,
        "service_flags": scan_service_flags(root),
        "registry_entities": scan_registry_entities(
            root, {e for spec in N.values() for e in (spec.get("entity") or [])}
        ),
        "task_mount_facts": {k: v for k, v in mounts.items() if k != "per_slot_effective"},
        "dangling_objects": {
            "fake_channel_slots": idle,
            "orphan_tasks": orphans,
            "tasks_outside_catchup_universe": [
                {"slot": s, "effective_task_count": int(slots[s].get("effective_task_count") or 0)} for s in outside
            ],
            "double_slot_tasks": mounts.get("duplicate_task_ids") or {},
            "entries": entries,
            "total": dangling_total,
        },
    }


def idle_slot_facts(node_slots: list[str], surfaces: dict[str, Any]) -> dict[str, Any]:
    """空转槽判定（本图最该显性化的形态）：槽有效挂载数 + 特殊槽分支存在性 → 是否真落空。"""
    slots = surfaces.get("scheduler_slots") or {}
    picked = {s: slots.get(s) for s in node_slots if s in slots}
    counts = {s: int((picked[s] or {}).get("effective_task_count") or 0) for s in picked}
    return {
        "slot_effective_task_count": counts,
        "special_branch_exists": {s: bool((picked[s] or {}).get("special_branch_exists")) for s in picked},
        "calendar_guarded": {s: bool((picked[s] or {}).get("calendar_guarded")) for s in picked},
        "in_catchup_universe": {s: bool((picked[s] or {}).get("in_catchup_universe")) for s in picked},
        "idle_slot": bool(picked) and all((picked[s] or {}).get("idle_slot") for s in picked),
    }


def dloop_stage_facts(stages: list[str], surfaces: dict[str, Any]) -> dict[str, Any]:
    """dloop 段归属实存：逐段标注是否在 PHASE_STAGES 实扫全集内。"""
    universe = set((surfaces.get("dloop_phases") or {}).get("stage_universe") or [])
    return {"declared_stages": sorted(stages), "in_phase_stages": {s: s in universe for s in sorted(stages)}}


def schtasks_facts(tns: list[str], surfaces: dict[str, Any]) -> dict[str, Any]:
    """计划任务在册实存：已注册面 available=false 时标 unknown 而非 false（禁把查不到冒充没注册）。"""
    reg = surfaces.get("registered_schtasks") or {}
    names = set(reg.get("task_names") or [])
    declared = set((surfaces.get("register_scripts") or {}).get("declared_task_names") or [])
    return {
        "query_available": bool(reg.get("available")),
        "registered": {t: (t in names if reg.get("available") else None) for t in sorted(tns)},
        "declared_in_register_scripts": {t: t in declared for t in sorted(tns)},
    }


def _anchor_rel(ref: str) -> str:
    s = str(ref).rsplit(":", 1)[0] if str(ref).rsplit(":", 1)[-1].isdigit() else str(ref)
    return s if re.fullmatch(r"[\w./\-]+", s) else s


def derive_miss_policy(nid: str, spec: dict[str, Any], surfaces: dict[str, Any]) -> str:
    """簿 10 表A-A6：miss 策略是"格属性"不是"路径分工"——逐格派生（rerun/alert/absorb/none）。

    派生口径全部取机生面（禁手工清单）：槽在 catchup 宇宙内=rerun；只检不修格=alert；
    槽有任务而宇宙外=absorb（幂等空跑吸收，即 20 未守卫槽现状）；零任务零分支槽/无槽=none。
    **表C-C1 判据分歧（rerun 值是否=给定时器补跑发准生证）不在本函数处置范围**，
    由节点 gap_refs 记入留总包复裁——本图只登记"错过之后现实上谁接"，不改任何判据口径。
    """
    if nid in MISS_POLICY:
        return MISS_POLICY[nid]
    src = spec["src"]
    if src == _SCHED:
        info = surfaces.get("scheduler_slots") or {}
        slots = [info.get(s) or {} for s in (spec.get("slot") or [])]
        if any(s.get("in_catchup_universe") for s in slots):
            return "rerun"
        if any(s.get("idle_slot") for s in slots) or not slots:
            return "none"
        return "absorb"
    if spec.get("act") in ("alert_only", "detect_only"):
        return "alert"
    if src in (_SCHT, _DLOOP, _EVENT):
        return "absorb"
    return "none"


def status_to_build(status: str, spec: dict[str, Any]) -> tuple[str, str, str]:
    """状态口径**唯一同源**=骨架 §2 状态列实扫（判据不擅改）→ (build_status, confidence, verified_scope)。

    ✅→built+verified+production｜🔨→partial+verified+structure｜⬜→pending+verified+structure。
    双轴正交（六图终局卷 §3）：structure 只声明"这条边/这个槽名/这个负结论已核"，绝不冒充在产；
    production 数恒等骨架 ✅ 数（多了算谎、少了算欠，由校验器 CV-DUAL 计数判）。
    gap 节点不在骨架三态表内，其断言面只有"这条映射/这个键存在"=structure，永不 production。
    """
    if spec.get("gap"):
        return "pending", "verified", "structure"
    build = {"✅": "built", "🔨": "partial", "⬜": "pending"}[status]
    scope = "production" if status == "✅" else "structure"
    return build, "verified", scope


def build_semantic_layers() -> list[dict[str, Any]]:
    """四段层位（骨架 §2 段 A/B/C/D 标题与交接语义）。"""
    out: list[dict[str, Any]] = []
    for seg in SEGMENTS:
        spec = SEGMENT_SEMANTIC_ZH[seg]
        out.append(
            {
                "segment_id": seg,
                "name_zh": spec["name_zh"],
                "span_zh": spec["span_zh"],
                "handoff_zh": spec["handoff_zh"],
            }
        )
    return out


def node_gap_refs(nid: str, ledger: dict[str, Any]) -> list[str]:
    """缺口显性化指针（L1 gap_refs）=①落空对象台账认领 ②表C 判据分歧留裁 ③跨图缺口交叉引用。

    ①由台账机械分派（`owner_nodes` 按槽名/任务归属算出，孤儿任务按"档期视角唯一兜底腿"分派给
    D13-01）：16 条落空对象每条必落在某节点 gap_refs 内，校验器 CV-DANGLE 双向反查
    （台账有对象而无节点认领=红；节点引台账外对象=红），落空对象无一可隐身。
    """
    refs: list[str] = list(GAPREF.get(nid) or [])
    for entry in (ledger or {}).get("entries") or []:
        if nid in (entry.get("owner_nodes") or []):
            refs.append(str(entry.get("id")))
    return sorted(set(refs))


def build_nodes(
    surfaces: dict[str, Any], module_index: dict[str, str], skeleton_status: dict[str, str]
) -> list[dict[str, Any]]:
    """44 环节 + 4 gap 节点：人工语义层 ⊕ 机生面（三层字段名一律取六图终局卷 §1 统一名）。"""
    build_status_zh = get_category_map("build_status")
    ledger = surfaces.get("dangling_objects") or {}
    nodes: list[dict[str, Any]] = []
    for nid in NODE_ORDER:
        spec = N[nid]
        is_gap = bool(spec.get("gap"))
        # 三态口径唯一同源=骨架 §2 实扫（查无回落本件契约常量）；✅→production、其余→structure
        status = skeleton_status.get(nid) or spec["st"]
        build_status, confidence, verified_scope = status_to_build(status, spec)
        src = spec["src"]
        slot_refs = list(spec.get("slot") or [])
        tn_refs = list(spec.get("tn") or [])
        stages = list(spec.get("stages") or [])
        # entity_refs 原样承载（在册性由 registry_entities 台账与校验器判，生成器禁静默丢弃）
        entity_refs = list(spec.get("entity") or [])
        ref = spec.get("ref")
        rel = _anchor_rel(ref) if ref else None
        module_id = module_index.get(rel) if rel else None
        node: dict[str, Any] = {
            # ── L0 通用层（同语义必同名）──
            "node_id": nid,
            "name_zh": spec["name"],
            "segment": spec["seg"],
            "node_type": "gap" if is_gap else "stage",
            "decision_question": spec["q"],
            "note_zh": spec["mech"],
            "module_id": module_id,
            "source_anchors": list(spec.get("anc", [])),
            "doc_refs": sorted(
                ({f"{_SKELETON} §2 {nid}", f"{_BOOK_DIR}/{_BOOK_OF[nid[4:]]}"} | set(spec.get("doc") or []))
                if not is_gap
                else (
                    set(_GAP_DOC[nid])
                    | set(spec.get("doc") or [])
                    | {_SKELETON + " §2（44 环节契约，本格为骨架外 gap 件）"}
                )
            ),
            "runtime_refs": list(spec.get("run", [])),
            "data_refs": list(spec.get("data", [])),
            "store_refs": list(spec.get("stores") or []),
            "evidence": sorted(spec.get("ev", [])),
            "confidence": confidence,
            "verified_scope": None if verified_scope == "null" else verified_scope,
            "build_status": build_status,
            "build_status_zh": build_status_zh.get(build_status, build_status),
            "skeleton_status": status,
            # ── L1 纵轴流程专有层（本图按域取用；时点语义与节拍合并进 cadence_zh 双子键）──
            "slot_source": src,
            "slot_refs": slot_refs,
            "schtasks_refs": tn_refs,
            "entity_refs": entity_refs,
            "cadence_zh": {"declared": spec.get("cad_declared") or spec["clk"], "observed": spec.get("obs") or ""},
            "wiring_status": WIRING.get(nid, "wired"),
            "downstream_action": spec["act"],
            "failure_visibility_zh": spec.get("vis") or FAILURE_VISIBILITY.get(nid, ""),
            "fallback": spec.get("fb") or None,
            "miss_policy": derive_miss_policy(nid, spec, surfaces),
            "invalidation": INVALIDATION.get(nid),
            "ready_gate": bool(READY_GATE.get(nid)),
            "no_ready_gate_reason_zh": _no_gate_reason(nid, spec),
            "tdm_refs": sorted(set(spec.get("tdm") or []) | set(TDMX.get(nid) or [])),
            "gap_refs": node_gap_refs(nid, ledger),
            # ── L2 图专属层（六图终局卷 §1 L2 + 簿 10 表A 落字段；清单在图头 ssot_note_zh 声明）──
            "mechanism": {
                "schedule": "A_apscheduler",
                "schtasks": "B_windows_task",
                "dloop_stage": "C_inprocess_stage",
                "event": "C_inprocess_stage",
                "none": "D_unscheduled",
            }[src],
            "dloop_stages": stages,
        }
        red = spec.get("red") or RED.get(nid)
        if red:
            node["red_reason"] = red
        if ref:
            node["module_ref"] = ref
            node["module_label_bilingual"] = anchor_label_bilingual(rel)
        else:
            node["module_ref"] = None
        node["exec_evidence"] = sorted(EXEC.get(nid) or [])
        for key, table in (
            ("freshness_severity_zh", FRESHNESS),
            ("expected_emits_per_trading_day", EMITS),
            ("ready_basis", READY_BASIS),
            ("miss_policy", MISS_POLICY),
            ("no_drift_evidence", NO_DRIFT),
        ):
            if key == "expected_emits_per_trading_day":
                if nid in EMITS:
                    node[key] = EMITS[nid]
            elif table.get(nid) is not None:
                node[key] = table[nid]
        if spec.get("recheck"):
            node["mining_recheck_status"] = spec["recheck"]
        if spec.get("red") or spec.get("recheck") == "🌑":
            node["availability"] = "unreachable"
        node.update(spec.get("extra") or {})
        mf: dict[str, Any] = {}
        if src == _SCHED:
            mf["slot_facts"] = idle_slot_facts(slot_refs, surfaces)
        if src == _SCHT:
            mf["schtasks_facts"] = schtasks_facts(tn_refs, surfaces)
        if src == _DLOOP:
            mf["dloop_facts"] = dloop_stage_facts(stages, surfaces)
        if mf:
            node["machine_facts"] = mf
        nodes.append(node)
    return nodes


def _no_gate_reason(nid: str, spec: dict[str, Any]) -> str:
    """非就绪门格的理由（骨架 §1 门④"空值须有语义"；就绪门格本身返回空由校验器放行）。"""
    if READY_GATE.get(nid):
        return ""
    gate = spec.get("gate") or ""
    if gate and not gate.startswith("无"):
        return f'本格非就绪门格——前置"{gate}"由入边与本注记承载（就绪门格另置 ready_gate:true）'
    return spec.get("nrg") or "本格非就绪门格，无前置就绪判定"


def build_document(as_of: str, root: Path, *, skip_schtasks: bool = False) -> dict[str, Any]:
    """组装图文档：人工语义层 ⊕ 机生真源面（结构契约见 validate_trading_day_cycle_map）。

    生成期硬失败（禁产出自粉饰的图）：production（骨架 ✅）环节缺 exec_evidence=KeyError——
    宁可不产出，也不产出一张"双轴齐而证据空"的图。
    """
    surfaces = build_trigger_surfaces(root, skip_schtasks=skip_schtasks)
    module_index = scan_module_id_index(root)
    skeleton_status = scan_skeleton_status(root)
    nodes = build_nodes(surfaces, module_index, skeleton_status)
    missing_exec = [
        n["node_id"] for n in nodes if n.get("verified_scope") == "production" and not n.get("exec_evidence")
    ]
    if missing_exec:
        raise KeyError(f"EXEC 缺环节（production 环节必带 exec_evidence）: {missing_exec}")
    edges = [list(e) for e in EDGES]
    by_segment = {s: 0 for s in SEGMENTS}
    by_slot_source: dict[str, int] = {}
    by_scope: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_wiring: dict[str, int] = {}
    for node in nodes:
        by_segment[node["segment"]] += 1
        by_slot_source[node["slot_source"]] = by_slot_source.get(node["slot_source"], 0) + 1
        by_scope[str(node["verified_scope"])] = by_scope.get(str(node["verified_scope"]), 0) + 1
        by_type[node["node_type"]] = by_type.get(node["node_type"], 0) + 1
        by_wiring[node["wiring_status"]] = by_wiring.get(node["wiring_status"], 0) + 1
    idle = surfaces["dangling_objects"]["fake_channel_slots"]
    ledger = surfaces["dangling_objects"]
    unclaimed = sorted({str(e["id"]) for e in ledger["entries"] if not e.get("owner_nodes")})
    skeleton_counts: dict[str, int] = {}
    for sym in skeleton_status.values():
        skeleton_counts[sym] = skeleton_counts.get(sym, 0) + 1
    doc = {
        "schema_version": "0.2",
        "map_id": "trading_day_cycle_map",
        "name_zh": "交易日循环全景图",
        "nickname": "交易日循环",
        "effective_from": "2026-09-24",  # 骨架 §2 44 环节定稿日（人工层常量，非运行时取时）
        "markets": ["cn_a"],
        "generator": "scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py",
        "generated_at": as_of,
        "ssot_note_zh": (
            "环节契约真源=docs/_working/map_build/fig13_daycycle/00_skeleton.md §2（44 环节四段）+ 十本作业簿"
            "（簿 10=外部对标三扫：表A 七条逐条落 L1/L2 字段或 gap 节点、表C 五条判据分歧只以 gap_refs 记入"
            "不自裁）；machine_facts/trigger_surfaces 层每次全量重扫可执行真相源（排班槽面/任务挂载 join/"
            "特殊槽分支面/PHASE_STAGES 实扫/日历守卫面/计划任务只读查询面/服务总闸实存面/骨架状态列实扫/"
            "depgraph 在册 module_id 投影面），禁手工维护。\n"
            "三条硬让渡已落成 laws/boundary：时刻值不搬家（节点只存槽名/tn 名/entity_id/段名）、"
            "决策内容不进图（判据唯一出路 tdm_refs）、数据管线内部结构不重画。\n"
            "字段分层（六图终局卷 §1 裁定一「同语义必同名」）：L0 通用层统一名 note_zh/doc_refs"
            "（三个同义异名注解字段与两个 doc 指针别名已废止，残留由校验器 CV-L0 判红）；"
            "L1 纵轴层本图取用 slot_source/slot_refs/schtasks_refs/cadence_zh(declared+observed 双子键)/"
            "wiring_status/downstream_action/fallback/invalidation/ready_gate+no_ready_gate_reason_zh/"
            "tdm_refs/gap_refs+red_reason；L2 图专属层字段清单=dloop_stages（dloop 段归属）、mechanism"
            "（触发机制三分：A_apscheduler/B_windows_task/C_inprocess_stage/D_unscheduled）、"
            "skeleton_status（骨架态镜像，实扫得）、mining_recheck_status（作业簿复判另记）、"
            "availability（🌑 不可得）、entity_refs、miss_policy（表A-A6）、freshness_severity_zh（A2）、"
            "expected_emits_per_trading_day（A4）、ready_basis（A5）、no_drift_evidence（A7）、"
            "admission_denied_zh/ready_gate_absent_zh 等单格注记。\n"
            "双轴口径（六图终局卷 §3）：verified_scope=production ⇔ 骨架 §2 状态列 ✅（14 个，多了算谎"
            "少了算欠，校验器 CV-DUAL 计数判且 production 必带 exec_evidence）；structure=仅结构性事实"
            "（含「该在而无主」这类负结论）已核，覆盖 🔨/⬜ 与 gap 节点。本生成器不擅改任何判据与阈值。\n"
            "gap 节点 D13-G01..G04 是骨架外显性化缺口件（簿 10 表A/表C + 图 12 簿 11 消费端反查），"
            "无实现代码可挂 ⇒ module_id=null + red_reason 必填，待总包回写骨架 §2。"
        ),
        "laws": list(LAWS),
        "boundary": list(BOUNDARY),
        "segments": build_semantic_layers(),
        "admission_edges": [dict(a) for a in ADMISSION_EDGES],
        "nodes": nodes,
        "edges": edges,
        "feedback_loops": [dict(fl) for fl in FEEDBACK_LOOPS],
        "machine_facts": {
            "trigger_surfaces": surfaces,
            # 外部对标落地面（簿 10 表A 七条逐条可查：落在哪个字段/哪些环节/是否留裁）
            "external_benchmark_landing": {
                "source": _EXT_BOOK,
                "table_a_landed": [
                    {
                        "id": "A1",
                        "carrier": "nodes(D13-09).ready_gate + 顶层 admission_edges",
                        "nodes": ["D13-09", "D13-11", "D13-12", "D13-15", "D13-30", "D13-32", "D13-35"],
                    },
                    {
                        "id": "A2",
                        "carrier": "nodes(*).freshness_severity_zh",
                        "nodes": ["D13-14", "D13-16", "D13-36", "D13-37", "D13-39", "D13-44"],
                    },
                    {
                        "id": "A3",
                        "carrier": "gap 节点 D13-G01（状态口径未改，见 C3）",
                        "nodes": ["D13-G01", "D13-13", "D13-29"],
                    },
                    {
                        "id": "A4",
                        "carrier": "nodes(*).expected_emits_per_trading_day",
                        "nodes": ["D13-13", "D13-18", "D13-29", "D13-31", "D13-44"],
                    },
                    {"id": "A5", "carrier": "nodes(*).ready_basis", "nodes": ["D13-28", "D13-29"]},
                    {
                        "id": "A6",
                        "carrier": "nodes(*).miss_policy（机生面派生 + 显式覆盖）",
                        "nodes": ["D13-01", "D13-35", "D13-38", "全图 44 格"],
                    },
                    {"id": "A7", "carrier": "nodes(*).no_drift_evidence", "nodes": ["D13-27", "D13-29", "D13-38"]},
                ],
                # 判据分歧：本车道一律不自裁，只以 gap_refs/note 记入并留总包复裁
                "table_c_pending": [
                    {
                        "id": "C1",
                        "question_zh": "miss_policy=rerun 是否等于给定时器补跑发准生证",
                        "nodes": ["D13-01", "D13-02", "D13-03", "D13-35", "D13-38"],
                    },
                    {
                        "id": "C2",
                        "question_zh": "就绪门是否允许持续重检/挂几次（骨架定为当日一次）",
                        "nodes": ["D13-09", "D13-30"],
                    },
                    {
                        "id": "C3",
                        "question_zh": "unknown 第四显示态与骨架状态四态封闭口径能否并存",
                        "nodes": ["D13-G01", "全图 44 格"],
                    },
                    {
                        "id": "C4",
                        "question_zh": "freshness_severity 分级归告警系统引用还是图侧独立声明",
                        "nodes": ["D13-14", "D13-16", "D13-36", "D13-37", "D13-39", "D13-44"],
                    },
                    {
                        "id": "C5",
                        "question_zh": "calendar_gated 三值中 null（未声明理由）的语义与补填义务",
                        "nodes": ["D13-43"],
                    },
                ],
            },
            # 图 12 侧发现的"消费方在等未产表 5 + 幽灵引用 1"归属分派（涉及本图者已落环节/gap 节点，
            # 其余三条环节面归图 12，本图只交叉引用不建其节点）
            "cross_map_gap_inventory": {
                "source": "docs/_working/map_build/fig12_datachain/11_消费端需求反查.md §1-C/§1-D",
                "in_this_map": [
                    {
                        "artifact": _tbl("market_execution_report"),
                        "nodes": ["D13-24", "D13-27"],
                        "gap_node": "D13-G02",
                        "red_reason": "broken_supply",
                    },
                    {
                        "artifact": _tbl("market_reconciliation_differences"),
                        "nodes": ["D13-29", "D13-31"],
                        "gap_node": "D13-G03",
                        "red_reason": "broken_supply",
                    },
                    {
                        "artifact": "ghost:c1_market.news_data",
                        "nodes": ["D13-17", "D13-18"],
                        "gap_node": "D13-G04",
                        "red_reason": "ghost_ref",
                    },
                ],
                "owned_by_fig12": [
                    {
                        "artifact": _tbl("market_account_nav_daily"),
                        "reason_zh": "生产端零调用方，"
                        "环节面=写通道与消费方接线（图 12 域），本图无对应时点环节，仅交叉引用不建节点",
                    },
                    {
                        "artifact": "c1_market.factor_feature_value",
                        "reason_zh": "CH 表未建（DDL 在册未 apply），属工厂在线面供给，本图无时点环节",
                    },
                    {"artifact": "c1_market.factor_signal", "reason_zh": "同上（默认落点悬空）"},
                ],
            },
            "module_id_roster": {
                "source": _PATH_OWNERSHIP,
                "claims_scanned": len(module_index),
                "note_zh": "existence ∈ {未实现, deprecated} 的在册条目不采信；未被覆盖的路径退回"
                "源文件 [BLUEPRINT] 头声明（须磁盘实存）。在册面存在性与磁盘实存漂移时"
                "以磁盘为准并在环节 note 记事实（本车道不改 depgraph）。",
            },
            "tdm_roster_scanned": bool(scan_tdm_node_ids(root)),
        },
        "counts": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_feedback_loops": len(FEEDBACK_LOOPS),
            "by_segment": by_segment,
            "by_slot_source": by_slot_source,
            "by_node_type": {k: by_type[k] for k in sorted(by_type)},
            "by_verified_scope": {k: by_scope[k] for k in sorted(by_scope)},
            "by_wiring_status": {k: by_wiring[k] for k in sorted(by_wiring)},
            "machine": {
                "slot_total": surfaces["slot_total"],
                "special_branch_total": len(surfaces["special_branch_slots"]),
                "idle_slot_total": len(idle),
                "idle_slots": sorted(idle),
                "orphan_task_total": len(surfaces["dangling_objects"]["orphan_tasks"]),
                "double_slot_task_total": len(surfaces["dangling_objects"]["double_slot_tasks"]),
                "dangling_total": ledger["total"],
                "dangling_unclaimed": unclaimed,
                "calendar_guarded_slot_total": len(surfaces["calendar_guard"]["guarded_slots"]),
                "dloop_stage_universe": len(surfaces["dloop_phases"]["stage_universe"]),
                "register_script_total": surfaces["register_scripts"]["script_count"],
                "task_declaring_script_total": len(surfaces["register_scripts"]["declaring_scripts"]),
                "schtasks_query_available": surfaces["registered_schtasks"]["available"],
                "service_flag_present": sorted(k for k, v in surfaces["service_flags"].items() if v["present"]),
                "skeleton_status_scan": {
                    "source": _SKELETON,
                    "nodes_scanned": len(skeleton_status),
                    "by_symbol": {k: skeleton_counts[k] for k in sorted(skeleton_counts)},
                },
                "module_id_scan": {
                    "source": _PATH_OWNERSHIP,
                    "nodes_with_module_id": sum(1 for n in nodes if n.get("module_id")),
                    "nodes_with_module_ref": sum(1 for n in nodes if n.get("module_ref")),
                    "nodes_null_module_id": sum(1 for n in nodes if not n.get("module_id")),
                },
                "tdm_refs": {
                    "nodes_with_tdm_refs": sum(1 for n in nodes if n.get("tdm_refs")),
                    "roster_source": _TDM_REL,
                },
            },
        },
    }
    return doc


_MAP_HEADER = (
    "# 交易日循环全景图（trading_day_cycle_map，图 13）——由 generate_trading_day_cycle_map.py 机生。\n"
    "# 本文件禁手改后不回生成（counts 一致性校验判红）；环节契约真源="
    "docs/_working/map_build/fig13_daycycle/00_skeleton.md。\n"
    "# 三条硬让渡进 laws/boundary：时刻值不搬家（cron 字面量零复制）、决策内容不进图"
    "（判据走 tdm_refs）、管线内部不重画；machine_facts 层重扫即刷新。\n"
)


def serialize_document(doc: dict[str, Any]) -> str:
    """确定性序列化（键序=插入序，禁 sort_keys 打乱语义分组）——幂等实证的落点。"""
    return serialize_map_document(doc, _MAP_HEADER)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="交易日循环全景图（图 13）生成器（机生优先，幂等）")
    ap.add_argument(
        "--as-of", default=None, help="generated_at 注入值（ISO 字面串）；缺省=HEAD 提交时间派生；禁运行时取时"
    )
    ap.add_argument("--out", default=str(OUTPUT_PATH), help="产出路径（默认 config/trading_day_cycle_map.yaml）")
    ap.add_argument("--root", default=str(_REPO_ROOT), help="扫描根（默认仓库根；worktree 内跑=worktree 根）")
    ap.add_argument(
        "--skip-schtasks",
        action="store_true",
        help="计划任务面显式降级（无 Windows 面环境；available=false 而非冒充未注册）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要，零写入")
    args = ap.parse_args()

    root = Path(args.root)
    as_of = args.as_of or head_commit_time(root)
    doc = build_document(as_of=as_of, root=root, skip_schtasks=args.skip_schtasks)
    if args.dry_run:
        c = doc["counts"]
        print(
            f"dry-run: nodes={c['total_nodes']} edges={c['total_edges']} "
            f"segments={c['by_segment']} slot_source={c['by_slot_source']} "
            f"scope={c['by_verified_scope']} node_type={c['by_node_type']} "
            f"wiring={c['by_wiring_status']} "
            f"module_id={c['machine']['module_id_scan']} "
            f"dangling={c['machine']['dangling_total']} unclaimed={c['machine']['dangling_unclaimed']} "
            f"idle_slots={c['machine']['idle_slots']} generated_at={as_of}"
        )
        return 0
    payload = serialize_document(doc)
    out = Path(args.out)
    try:
        from zephyr.shared.io.file_utils import safe_write_text

        ok = safe_write_text(out, payload)
    except Exception:  # noqa: BLE001 — 非 zephyr 环境（tmp 测试根）降级直写，仍幂等
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8", newline="\n")
        ok = True
    if not ok:
        print(f"[ERROR] safe_write_text 失败（CAS 冲突？）: {out}", file=sys.stderr)
        return 1
    print(f"written: {out} (nodes={doc['counts']['total_nodes']} edges={doc['counts']['total_edges']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
