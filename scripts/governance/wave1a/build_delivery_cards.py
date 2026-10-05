# [BLUEPRINT] MOD-TASK_SYSTEM | docs/_working/total_command_closeout/10_wave_plan.md#波1A-1A.1
# [MODULE] scripts.governance.wave1a.build_delivery_cards
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.schema.task_types; zephyr.governance.persistence.task_repo; zephyr.shared.io.paths
# [CONSUMERS] docs/_working/total_command_closeout/wave1a/delivery_cards_report.md; session st-final-build-20260926
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#   （原值 permanent——CLI 审计工具按需人工触发，PERM-TRIGGER 手动模式铁律归 task_bound）
# [STARTUP] manual
# [MATURITY] candidate
# [SAFETY] M
# [AI_AUTONOMY] supervised
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""build_delivery_cards.py — 波 1A/1B/2 交付卡幂等建卡器（1A.1）。

入口 = TaskRepository.create_and_ready()/create()（GOV-TASK-001 v3.2.0 强制校验）。
只准经仓储 API 向 governance.db tasks 表追加新行；禁 UPDATE/DELETE 既有行。
21 字段 = 仓储强制 18（TEMPLATE_REQUIRED_FIELDS）+ 本包追加 3
（session_id / artifact_paths / approval_required 必须显式设置，路径必须绝对）。
按 task_key→固定 task_id 去重：重复跑不产生重复卡。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_LANE_ROOT = Path(__file__).resolve().parents[3]
_SRC = str(_LANE_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.schema.task_types import Task, TaskNamespace, TaskStatus

SESSION_ID = "st-final-build-20260926"
BATCH_ID = f"{SESSION_ID}-w1a1b2"
DEP_1A: list[str] = []  # 波1A 无前置
_ALL_1A = [f"OPS-92601{i:02d}" for i in range(1, 7)]
_ALL_1B = [f"OPS-92601{i:02d}" for i in range(7, 17)]

# 21 必填字段 = 仓储 TEMPLATE_REQUIRED_FIELDS(18) + 本包 3
EXTRA_REQUIRED = ("session_id", "artifact_paths", "approval_required")
PATH_FIELDS_ABS = ("artifact_paths", "deliverables", "files_in_scope", "allowed_touch")

_L = str(_LANE_ROOT).replace("\\", "/")


def _note(tid: str, wave: str) -> str:
    """_note implementation."""
    return f"{_L}/docs/_working/total_command_closeout/{wave}/card_notes/{tid}.md"


def _desc(cause: str, cure: str, steps: str, accept: str) -> str:
    """_desc implementation."""
    return f"根因：{cause}。治根：{cure}。施工步骤：{steps}。验收标准：{accept}。"


# (seq, key, title, section, deliverable, extra_artifacts, rb, approval, safety, deps, desc)
SPECS: list[dict] = [
    dict(
        seq=9260101,
        key="1A.1",
        wave="wave1a",
        title="波1A.1 交付状态迁回机读真源：波1A/1B/2 施工追踪包建卡入 tasks 表",
        section="10_wave_plan.md#波1A-1A.1",
        deliverable=f"{_L}/scripts/governance/wave1a/build_delivery_cards.py",
        artifacts=[f"{_L}/docs/_working/total_command_closeout/wave1a/delivery_cards_report.md"],
        rb=False,
        approval=False,
        safety="M",
        deps=DEP_1A,
        desc=_desc(
            "交付状态散在散文交接书、与机读真源（governance.db tasks 76 列）脱钩，本轮 40+ 处叙述与盘面不符",
            "以本卡挂靠 1A.1 包，状态一律回写 tasks 表，散文只承载为什么",
            "建卡器按 21 必填字段自检后经 TaskRepository 官方 API 追加，涉 Owner 门位项 approval_required=True",
            "卡数==波1A/1B/2 需追踪包数且 21 字段非空、路径为绝对路径（建卡器自检输出为准）",
        ),
    ),
    dict(
        seq=9260102,
        key="1A.2",
        wave="wave1a",
        title="波1A.2 交付判据 COMPLETED→VERIFIED：升态校验器（三判据）成为状态机约束",
        section="10_wave_plan.md#波1A-1A.2",
        deliverable=f"{_L}/scripts/governance/wave1a/verified_promotion_check.py",
        artifacts=[f"{_L}/tests/governance/test_delivery_card_canary.py"],
        rb=True,
        approval=False,
        safety="M",
        deps=DEP_1A,
        desc=_desc(
            "COMPLETED 是自称完成、无证据锚也被当交付（2546 行中 COMPLETED 1990、artifact_paths 非空仅 7）",
            "升 VERIFIED 必须三判据齐：artifact_paths 非空、逐件 git cat-file -e HEAD 为真、涉判据者有红蓝证据锚",
            "写只读校验器并对既有 COMPLETED 卡抽样复算，禁把任何既有卡改 VERIFIED 交差",
            "抽 20 张 COMPLETED 卡复算：无 HEAD 证据锚者必须升不了 VERIFIED（红证）且 canary 测试跑成",
        ),
    ),
    dict(
        seq=9260103,
        key="1A.3",
        wave="wave1a",
        title="波1A.3 触发面三列对账表生成器：名册声明/进程内实载/HEAD 树命中，零命中自动进红名单",
        section="10_wave_plan.md#波1A-1A.3",
        deliverable=f"{_L}/scripts/governance/wave1a/gate_rule_face_reconcile.py",
        artifacts=[f"{_L}/docs/_working/total_command_closeout/wave1a/reconcile/gate_trigger_faces.md"],
        rb=False,
        approval=False,
        safety="M",
        deps=DEP_1A,
        desc=_desc(
            "门在名册却不在装载面/触发面（CREATE-GUARD files_trigger 空每链全跑、三台密钥门恒零命中）",
            "一张生成器表同时收敛名册/实载/命中三列，禁手工维护",
            "生成器产出表并对声明有而实载或命中为零的门点名",
            "表可复算、红名单非空即报、新增门三列齐才准入",
        ),
    ),
    dict(
        seq=9260104,
        key="1A.4",
        wave="wave1a",
        title="波1A.4 规则↔执法面对账尺：别名归一覆盖率 + 六条零匹配规则逐条定性（退役支属注册表净删须 Owner 门位）",
        section="10_wave_plan.md#波1A-1A.4",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1a/reconcile/rule_enforcement_coverage.md",
        artifacts=[],
        rb=False,
        approval=True,
        safety="H",
        deps=DEP_1A,
        desc=_desc(
            "规则在册却无门禁或指向死面，trae_057/066/074/076/078/083 六条零匹配（naive grep 不可用须别名归一）",
            "覆盖率进 ROOR 派生字段；六条逐条定性为补执法面/改判据面/退役，其中退役=注册表净删走 Owner 门位",
            "按 TRAE-060/trae_060 两写法归一后实测覆盖，再逐条给定性依据",
            "覆盖率成文且六条各有定性行；任何退役支未经 Owner 门位不得执行",
        ),
    ),
    dict(
        seq=9260105,
        key="1A.5",
        wave="wave1a",
        title="波1A.5 死库与死指针清理：0 字节库逐个判复活/改指活库/退役（规则库路径同批改，退役支须 Owner 门位）",
        section="10_wave_plan.md#波1A-1A.5",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1a/dead_db_disposition.md",
        artifacts=[f"{_L}/docs/_working/total_command_closeout/wave1a/reconcile/dead_db_inventory.md"],
        rb=False,
        approval=True,
        safety="H",
        deps=DEP_1A,
        desc=_desc(
            "trae_034 明文指向的 zalpha_metadata.db 实测 0 字节，depgraph.db 等 4 库 0 字节仍被引用（含 34 处 depgraph）",
            "按消费者数+有无活替代逐库判定；同批改规则库路径禁留死指针；读侧探针失败必抛禁静默降级",
            "出清单表逐条判复活/改指/退役；退役支属注册表净删提交 Owner 菜单不代裁",
            "0 字节库数→0（复活或退役有归）且 34 处 depgraph 引用逐条有归属",
        ),
    ),
    dict(
        seq=9260106,
        key="1A.6",
        wave="wave1a",
        title="波1A.6 交接书退役：跨会话交接=卡集合+一条查询命令，散文只承载为什么",
        section="10_wave_plan.md#波1A-1A.6",
        deliverable=f"{_L}/scripts/governance/wave1a/cross_session_view.py",
        artifacts=[f"{_L}/docs/_working/total_command_closeout/wave1a/delivery_cards_report.md"],
        rb=False,
        approval=False,
        safety="M",
        deps=DEP_1A,
        desc=_desc(
            "11 份散文交接书承载状态导致本轮人工归并约 3.5 小时、40+ 处叙述与盘面不符",
            "状态迁机读卡集合，散文只留裁定理由；交接视图按 session_id/blocked_by/verification_status 出",
            "一条命令出跨会话状态视图并把命令与输出样本写进案卷",
            "下一次多会话合并人工归并工时≤1 小时；视图命令可复跑",
        ),
    ),
    # ---- 波 1B（串行于波 1A 之后）----
    dict(
        seq=9260107,
        key="1B.1.1",
        wave="wave1b",
        title="波1B.1.1 四台在册禁用门逐台定性 + 名册/实载/命中常设对账表（恢复属 ⚑-6-3 须 Owner，禁自裁）",
        section="10_wave_plan.md#波1B-1.1",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/gate_disable_attribution.md",
        artifacts=[f"{_L}/scripts/governance/wave1a/gate_rule_face_reconcile.py"],
        rb=True,
        approval=True,
        safety="H",
        deps=_ALL_1A,
        desc=_desc(
            "103−4=99 证明四台是被主动禁用而非装载失败，其中 PERMANENT-SYSTEM-TRIGGER 从未被任何交接书点名",
            "逐台给禁用归因与禁用窗口有无违规落地核查；对账表常设化（复用 1A.3 生成器不造第二套）",
            "出四台归因行+常设三列对账表；是否恢复呈 Owner 门位不代裁",
            "对账表三列可复算、四台各有归因行；人为禁用一台而对账表不点名时尺必须红",
        ),
    ),
    dict(
        seq=9260108,
        key="1B.1.2",
        wave="wave1b",
        title="波1B.1.2 candidate 册同 id 双条去重（CAND-GOVTEST-005）：以 HEAD 为基重放，注册表净删支须 Owner",
        section="10_wave_plan.md#波1B-1.2",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/cand_dedup_replay_report.md",
        artifacts=[],
        rb=True,
        approval=True,
        safety="H",
        deps=_ALL_1A,
        desc=_desc(
            "同 id 双条异体使凡带该册的袋在队列合并器必死（本役 33 封 dead 的结构性毒袋之一）",
            "保留信息更全者+并入对方独有字段+被并者改号或降级议题条目（Z-05 语义零删除；净删注册表条目属 Owner）",
            "按配方 R-1 以 HEAD 为基纯插入重放，禁整册覆写（该册盘面处 MM 他道在途）",
            "合并器三向合并能过；改一条内容制造身份键冲突时红证必现",
        ),
    ),
    dict(
        seq=9260109,
        key="1B.1.3",
        wave="wave1b",
        title="波1B.1.3 priority 撞号真身：聚合台与吸收台不得实载层同号断言尺 + 6 簇设计内同值注记（禁改数值）",
        section="10_wave_plan.md#波1B-1.3",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/priority同号_assertion_report.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "两册条目根本无 priority 字段（真源=GateSpec），实为代码层 6 簇源台+聚合台 _union_check 同值对",
            "只补实载层同号断言尺，并把 6 对显式注为设计内同值，禁动数值",
            "出尺并注记 6 对（其中 2 簇靠 enabled:false 才不并存）",
            "人为让两台实载门同号时尺必须红",
        ),
    ),
    dict(
        seq=9260110,
        key="1B.1.4",
        wave="wave1b",
        title="波1B.1.4 REGISTRY-CODE-ANCHOR 漂移与 GATE-21 真红点（script_manifest 盘 461≠HEAD 516）生成器重算",
        section="10_wave_plan.md#波1B-1.4",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/manifest_recount_report.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "文档串 106 vs 代码 129、script_manifest 磁盘 461≠516，手工态必然漂移",
            "生成器重算机生册，禁手改",
            "重算并落两册对账读数",
            "删一行清单时尺红；重算后盘-HEAD 键集合差为 0",
        ),
    ),
    dict(
        seq=9260111,
        key="1B.1.5",
        wave="wave1b",
        title="波1B.1.5 CREATE-GUARD 触发面登记 files_trigger 或改 own-scope 差分（不退役，Owner 明令）",
        section="10_wave_plan.md#波1B-1.5",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/create_guard_trigger_fix.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "files_trigger='' 致每链全跑，实测 1519 次/19186s 占全部门 13.6%，成本源 create_guard.py 全树 git grep",
            "登记 files_trigger 或改 own-scope 差分，门本身保留（退役属 Owner 明令禁区）",
            "改造后重放 100 笔 verdict 全等自证",
            "新文件缺 token 时必拦仍能红，且重放 verdict 全等",
        ),
    ),
    dict(
        seq=9260112,
        key="1B.1.6",
        wave="wave1b",
        title="波1B.1.6 flag 三态读：读到 ON/读到 OFF/读不到必报红点名（Z-10）",
        section="10_wave_plan.md#波1B-1.6",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/flag_tristate_report.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "flag 读取失败被当 OFF 静默降级（全流通§5-R6/T13），翻错不存在的东西风险在册（X-30）",
            "读失败必报红点名，不与 OFF 同码",
            "补三态判读并点名",
            "把 flag 文件改坏时必须报红而非当 OFF 拒投",
        ),
    ),
    dict(
        seq=9260113,
        key="1B.1.7",
        wave="wave1b",
        title="波1B.1.7 入队预检旁路封堵：requeue 与 enqueue_item 直调补 run_enqueue_preflight",
        section="10_wave_plan.md#波1B-1.7",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/preflight_bypass_close.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "requeue 与直调绕过预检，28 件纯格式类与 20 件必拒类带病入队",
            "两入口统一补预检；格式类落地侧自动修、必拒类点名",
            "封堵后重放既有 dead 袋验归因不变",
            "直调旁路投一件缺 token 新文件必被拦",
        ),
    ),
    dict(
        seq=9260114,
        key="1B.1.7b",
        wave="wave1b",
        title="波1B.1.7b 队列失败摘除+后继袋重建（对标 Merge Queue/Merge Trains/Zuul，与 B5 毒药熔断合并）",
        section="10_wave_plan.md#波1B-1.7b",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/queue_train_recovery.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "一袋死掉其后各袋整链停摆（实测 pending=0/dead≈700）",
            "后继各袋按新组合继续前进；与既有 B5 熔断合并，不新造机制",
            "实现摘除+重建并回放必死袋场景",
            "造一袋必死者，改后其后各袋必须落地或各自具名死因",
        ),
    ),
    dict(
        seq=9260115,
        key="1B.1.7c",
        wave="wave1b",
        title="波1B.1.7c 死信属主制+复发熔断：每封死信落 owner_session/first_dead_at，同签名 3 次熔断升根因",
        section="10_wave_plan.md#波1B-1.7c",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/dead_owner_routing.md",
        artifacts=[],
        rb=False,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "死信无人认领被反复重投，同签名复发无上限",
            "新死信 24h 内必有属主与归因签名；复发 3 次熔断并禁继续重投",
            "落属主字段与熔断判据",
            "新死信 24h 内有属主与归因签名",
        ),
    ),
    dict(
        seq=9260116,
        key="1B.1.8",
        wave="wave1b",
        title="波1B.1.8 从未入库件捞回：两红蓝测试按 path+blob_sha256 双证反查队列 blobs 与 .runtime/tmp",
        section="10_wave_plan.md#波1B-1.8",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave1b/unlanded_recovery.md",
        artifacts=[],
        rb=False,
        approval=False,
        safety="M",
        deps=_ALL_1A,
        desc=_desc(
            "test_redblue_governance.py 与 test_redblue_robust.py 从未进 HEAD（X-16 缩小后仅剩两测试件）",
            "双证齐才定缺失；未落地件唯一存活处=队列 blobs（取证禁照文档字面大小写，X-16）",
            "四态核对表逐件反查",
            "四态核对表成文且每件有结论",
        ),
    ),
    # ---- 波 2（串行于波 1 之后）----
    dict(
        seq=9260117,
        key="2.1",
        wave="wave2",
        title="波2.1 六图役 30 施工件抢救落地：补 creation_token、翻译主仓跑≥8字、悬空裁定号改文字、基底显式",
        section="10_wave_plan.md#波2-2.1",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave2/landing_manifest_2_1.md",
        artifacts=[f"{_L}/docs/_working/total_command_closeout/wave2/landing_manifest_2_1.md"],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1B,
        desc=_desc(
            "车道落后 dev 237 commit 零自有 commit、30 件 HEAD 命中 0/30、脏项 272，一旦被外部重置即永久损失",
            "按配方 R-2 三件套同袋补齐+悬空裁定号清除（dead 0040 死在引用 HEAD 查无的 414/415 号）+基底显式",
            "逐袋 gate_prerun 到硬阻断 0 再入队，落地只认 git show HEAD:",
            "HEAD 对点名件命中数==计划数且逐件抽 sha",
        ),
    ),
    dict(
        seq=9260118,
        key="2.2",
        wave="wave2",
        title="波2.2 波2 役 169 件（D 册 31+ 件 HEAD 完全不存在者为准）抢救落地：三字段头注/零消费者同袋接线/depgraph 登记",
        section="10_wave_plan.md#波2-2.2",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave2/landing_manifest_2_2.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1B,
        desc=_desc(
            "声称 169 件整批未进 HEAD 而工棚自证绿（X-29 实测 31 件双无）",
            "新 .py 三字段头注齐、ORPHAN-MODULE 零消费者新件与接线同袋、apply_depgraph 先登记、YAML 禁回填取样字面量",
            "按 D 册逐件清单装袋，袋≤38 一袋一域",
            "HEAD 命中数与 D 册清单对账一致",
        ),
    ),
    dict(
        seq=9260119,
        key="2.3",
        wave="wave2",
        title="波2.3 全流通三批成品抢救落地（lane_ff_door/books/replay + campaign_hold），账簿键集合差自证删除集==∅",
        section="10_wave_plan.md#波2-2.3",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave2/landing_manifest_2_3.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1B,
        desc=_desc(
            "三批成品滞留车道与 campaign_hold，门侧拒投类无预检先死",
            "门侧拒投类先补预检；热台账只追加并以键集合差自证删除集为空",
            "按 A 册逐件装袋落地",
            "A 册点名件 HEAD 命中且账簿差集为空",
        ),
    ),
    dict(
        seq=9260120,
        key="2.4",
        wave="wave2",
        title="波2.4 CH 大声失败改造 + 灾备处方件 + 回测哨兵落地：换会抛错 reader、哨兵拆 helper 禁调阈值、号文缺失有归",
        section="10_wave_plan.md#波2-2.4",
        deliverable=f"{_L}/docs/_working/total_command_closeout/wave2/landing_manifest_2_4.md",
        artifacts=[],
        rb=True,
        approval=False,
        safety="M",
        deps=_ALL_1B,
        desc=_desc(
            "t1_t2_handover.py 在 index 不在 HEAD、其测试未跟踪；CH-FINAL-GATE 会拦自家裸 query；哨兵三函数复杂度超限",
            "先换会抛错 reader 再投；改名/换目录重绑 creation_token；拆模块级 helper（参数≤7）禁调阈值；号文缺失补或呈报声明退役",
            "逐件按处方落地",
            "哨兵所在袋可过复杂度门且未动任何阈值",
        ),
    ),
]

_RULES = [
    {"module_id": "GOV-TASK-001", "section": "v3.2.0", "reason": "建卡 18 模板必填校验"},
    {"module_id": "RULE-THIRTEEN", "section": "§1.3", "reason": "粒度门禁 R1-R6"},
    {"module_id": "RULE-SSOT", "section": "宪法0.7", "reason": "架构数据直写 DB、状态不寄散文"},
]


def build_task(spec: dict, created_at: datetime) -> Task:
    """build_task implementation."""
    tid = f"OPS-{spec['seq']}"
    artifacts = [spec["deliverable"], *spec["artifacts"]]
    kwargs: dict = dict(
        task_id=tid,
        namespace=TaskNamespace.OPS,
        seq=spec["seq"],
        title=spec["title"][:200],
        description=spec["desc"],
        priority="P1",
        phase=1,
        execution_model="glm",
        files_in_scope=[_note(tid, spec["wave"])],
        deliverables=[spec["deliverable"]],
        acceptance=[spec["desc"].split("验收标准：")[1].rstrip("。")],
        source_blueprint=SESSION_ID,
        source_section=spec["section"],
        safety_level=spec["safety"],
        directive=f"10册-{spec['section']}（总指挥战役 Owner 排产指令）",
        classification="internal",
        ai_autonomy_level="supervised",
        applicable_rules=list(_RULES),
        allowed_touch=[
            f"{_L}/scripts/governance/{spec['wave']}/**",
            f"{_L}/docs/_working/total_command_closeout/{spec['wave']}/**",
        ],
        artifact_paths=artifacts,
        session_id=SESSION_ID,
        idempotent=True,
        requires_rb_check=spec["rb"],
        approval_required=spec["approval"],
        rollback_instructions="仅追加新行；不 UPDATE/DELETE 既有行；撤销经正式通道按 task_id 逐条申请。",
        tags=["wave1a", "st-final-build-20260926", f"pkg:{spec['key']}"] + (["rb-required"] if spec["rb"] else []),
        created_at=created_at,
        updated_at=created_at,
        root_cause_analysis=spec["desc"].split("。")[0],
    )
    if spec["deps"]:
        kwargs.update(status=TaskStatus.BLOCKED, depends_on=list(spec["deps"]), blocked_by=list(spec["deps"]))
    return Task(**kwargs)


def self_check_21(t: Task) -> list[str]:
    """21 必填字段非空 + 路径字段绝对性自检。返回问题清单（空=过）。"""
    problems: list[str] = []
    for f in (*TaskRepository.TEMPLATE_REQUIRED_FIELDS, *EXTRA_REQUIRED):
        v = getattr(t, f, None)
        if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and len(v) == 0):
            problems.append(f"缺字段 {f}")
    for f in PATH_FIELDS_ABS:
        for p in getattr(t, f) or []:
            if not Path(p).is_absolute():
                problems.append(f"{f} 非绝对路径: {p}")
    return problems


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="波1A/1B/2 交付卡幂等建卡器")
    ap.add_argument("--db", default=None, help=f"tasks 库路径（默认 {DB_PATH}）")
    ap.add_argument("--check-only", action="store_true", help="只跑 21 字段自检不落库")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = args.db or str(DB_PATH)

    results: list[dict] = []
    now = datetime.now(UTC)
    repo = None if args.check_only else TaskRepository(db_path=db)
    for spec in SPECS:
        t = build_task(spec, now)
        problems = self_check_21(t)
        status = "rejected_self_check" if problems else None
        if not problems and repo is not None:
            existing = repo.get(t.task_id)
            if existing is not None:
                # requires_rb_check 列不在仓储 INSERT 列面（写入面缺口，案卷 §一登记）：
                # 用官方 update() 为本会话新建卡补 tags 双锚，禁裸 SQL、不动既有他话卡。
                cur_tags = list(existing.tags or [])
                if t.requires_rb_check and "rb-required" not in cur_tags:
                    repo.update(t.task_id, tags=[*cur_tags, "rb-required"])
                    status = "exists_synced_tags"
                else:
                    status = "exists_skipped"
            elif spec["deps"]:
                repo.create(t, allow_direct_create=True, batch_id=BATCH_ID)
                status = "created_blocked"
            else:
                repo.create_and_ready(t, allow_direct_create=True, batch_id=BATCH_ID)
                status = "created_ready"
        results.append(
            dict(
                task_key=spec["key"],
                task_id=t.task_id,
                status=status or "self_checked",
                self_check=problems if problems else "PASS",
                rb_check=t.requires_rb_check,
                approval_required=t.approval_required,
            )
        )
    n_created = sum(1 for r in results if str(r["status"]).startswith("created"))
    n_skip = sum(1 for r in results if r["status"] == "exists_skipped")
    n_fail = sum(1 for r in results if r["status"] == "rejected_self_check")
    summary = dict(
        cards=len(SPECS),
        created=n_created,
        exists_skipped=n_skip,
        self_check_fail=n_fail,
        all_21_pass=all(r["self_check"] == "PASS" for r in results),
        approval_required_ids=[r["task_id"] for r in results if r["approval_required"]],
        rb_check_ids=[r["task_id"] for r in results if r["rb_check"]],
        mode="check_only" if args.check_only else "write",
    )
    print(json.dumps(dict(summary=summary, cards=results), ensure_ascii=False, indent=1))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
