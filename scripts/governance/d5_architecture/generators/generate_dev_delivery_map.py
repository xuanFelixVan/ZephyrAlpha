# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §dev_delivery_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_dev_delivery_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# create-guard-not-dup: 本件=死车道抢救的 FiveMaps 生成器（字节代投非新能力），docstring 提及'scan gate registry'系描述扫描对象，非第二真源（canonical=reconciliation_registry 无重叠）
# [DEPENDENCIES] yaml；scripts.governance._shared.terminology_loader（get_category_map）；
#   scripts.governance._shared.module_translation_loader（get_module_translation）；
#   zephyr.shared.io.file_utils（safe_write_text，热写通道复用）；git（只读 show 取 HEAD 提交时间派生时间戳）；
#   docs/03_modules/path_ownership_map.yaml（depgraph_node 在册 module_id 派生面，只读）；
#   validate_dev_delivery_map（scan_skeleton_status 单源导入——CLONEGUARD 收内 2026-10-04，
#   先例 dc0bc34cff 家族方向：校验器=判据单一真源，生成器禁持副本）
# [CONSUMERS] config/dev_delivery_map.yaml（唯一产出物）；
#   tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py（幂等实证直调 build_document）；
#   总包排产：重生成/对齐（alignment_checklist 挂轴由总包落）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 双层结构（GOMAP 先例）：machine_facts 层每次全量重扫（门禁册/对账登记面/
# [MODIFY-GUARD] 环节契约全集/边/反馈环改动前先回写 fig11_delivery/00_skeleton.md；
#   产出 config/dev_delivery_map.yaml 禁手改后不回生成
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] production 节点缺 exec_evidence=raise KeyError；真源缺失=对应 machine_fact
#   记 {"exists": false} 不崩溃；写盘 CAS 失败=返回码 1；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py
#   四脚本公共函数与退出码面/.runtime/commit_queue 四态目录/骨架 §1 三态列/path_ownership
#   depgraph_node 在册 module_id 面/CommitStatus 生产者构造面/死因标记表条数），人工语义层（环节名/
#   decision_question/laws/boundary/边/反馈环/L2 退出码矩阵处方列）从骨架与作业簿取、生成器内以契约常量承载；
#   四态目录与一切 .runtime 面**只读扫**（禁写禁删禁调 commit_queue.py status/drain——二者触发自举排空）；
#   幂等=同输入两次产出逐字节等（时间戳必经 --as-of 入参或 HEAD 提交时间派生，生成器禁
#   壁钟取时函数（now/time 类）禁用——RULE-SCHEMA-TZ）；计数只进 counts 字段不进散文；节点只存稳定标识符与指针
#   （INV-1，门禁册条目正文禁入图）；中英标签必经既有翻译 loader（禁硬编码翻译字典）；
#   字段名一律 L0 统一名（note_zh/doc_refs，废止 mech_note_zh/design_refs 别名）；
#   verified_scope 与骨架 §1 三态列同源（✅→production、🔨→structure），生成器不擅改判据口径
# [MODIFY-GUARD] 环节契约全集/边/反馈环改动前必须先回写
#   docs/_working/map_build/fig11_delivery/00_skeleton.md（本图唯一收敛基准）；
#   产出物 config/dev_delivery_map.yaml 禁手改后不回生成（counts 一致性校验会判红）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失=对应 machine_fact 记 {"exists": false} 不崩溃；
#   safe_write_text CAS 失败=返回码 1；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""generate_dev_delivery_map.py — 交付流水线全景图（图 11，dev_delivery_map）生成器。

域（骨架一句话）：代码从会话诞生到落地 dev 主区的全部"开发时"流水线环节（不含运行时
模块归属——那是 GOMAP）。28 环节契约全集 D11-S01~S09/C01~C13/D01~D06 = 骨架 §6 封顶件，
另按六图终局卷 §4 图11 验收判据②补 2 个 gap 节点（D11-G01 退出码死分支 / D11-G02 precommit
回滚旗恒失效）——G01/G02 是**骨架外显性化缺口件**，待总包回写骨架 §1（本车道禁改骨架）。

两层结构（照抄 GOMAP generate_governance_map.py 先例，宪章机生优先 + 静态清单禁手工维护）：
  1. 机生层 machine_facts：扫可执行真相源——
     - in-process/pre-commit 两本门禁册（total_gates 字段与条目实数 + 通道分簇 gate_cluster，
       册自身有生成器真源，本图只挂指针与计数）
     - post-commit reconciler 登记面（网关 register( 调用动态计数）
     - git_commit.py / commit_queue.py / lock_files.py / session_worktree.py 公共函数与退出码面（AST）
     - **提交退出码全谱**：AST 读 _COMMIT_RESULT_MAP（状态→码）+ 全仓 `status=CommitStatus.X`
       生产者构造计数 ⇒ 专码零生产者者=死分支（机生判据，喂给 gap 节点 D11-G01）
     - **module_id 总线在册面**：docs/03_modules/path_ownership_map.yaml 的 claim_type=depgraph_node
       条目（depgraph 派生投影，路径→MOD-*），无代码节点 module_id=null+red_reason
     - **骨架三态列**：00_skeleton.md §1 表 ✅/🔨（verified_scope 双轴的唯一同源口径）
     - 死因标记表条数（env/item 两表元素数，只取计数不抄标记串——INV-1）
     - .runtime/commit_queue/{pending,processing,done,dead} 四态目录（只读 ls 计数；worktree/CI
       无 .runtime 面=exists:false，属输入差异不属非幂等）
  2. 人工语义层：环节名/decision_question/note_zh（L0 统一名，废止 mech_note_zh 别名）/
     laws/boundary/边/反馈环/L2 退出码矩阵的处方列——逐条取自
     docs/_working/map_build/fig11_delivery/00_skeleton.md（§0 四道门、§1 环节表、§2 车道交接）
     与八本作业簿（§末-3 实查命令=exec_evidence 口径真源）；
     状态/置信度口径照用骨架 ✅/🔨：✅→built+verified+production、🔨→partial+verified+structure，
     本生成器不擅改任何判据（production 数恒等骨架 ✅ 数，多了算谎少了算欠）。

CLI:
    python scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py            # 生成/刷新
    python scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py --dry-run  # 只打印摘要
    python ... --as-of 2026-09-24T12:00:00+08:00   # 注入时间戳（幂等实证用；缺省=HEAD 提交时间派生）
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
)
from d5_architecture.validators.validate_construction_steps import (  # noqa: E402  # noqa: import-integrity  sys.path 注入的 governance 包
    scan_module_id_index,
)
from d5_architecture.validators.validate_dev_delivery_map import (  # noqa: E402  # noqa: import-integrity  CLONEGUARD 单源化（先例 dc0bc34cff 家族方向：生成器改导入校验器判据件）
    scan_skeleton_status,
)

OUTPUT_PATH = _REPO_ROOT / "config" / "dev_delivery_map.yaml"
_SKELETON = "docs/_working/map_build/fig11_delivery/00_skeleton.md"
_BOOK_DIR = "docs/_working/map_build/fig11_delivery"
# depgraph 派生投影（claim_type=depgraph_node 的 路径→MOD-* 在册面；生成器只读）
_PATH_OWNERSHIP = "docs/03_modules/path_ownership_map.yaml"
# 两个 gap 节点的作业簿出处（骨架外显性化缺口件，禁指骨架§1——骨架无此行）
_GAP_BOOK_OF = {"D11-G01": "04_提交正门与全局锁.md", "D11-G02": "05_门禁链与precommit通道.md"}
# 作业簿编号→覆盖环节（骨架 §5 契约：01→S01-S03 … 08→D01-D06）
_BOOK_OF = {
    "S01": "01_会话启动与worktree池.md",
    "S02": "01_会话启动与worktree池.md",
    "S03": "01_会话启动与worktree池.md",
    "S04": "02_claim协议与暂存晋升.md",
    "S05": "02_claim协议与暂存晋升.md",
    "S06": "02_claim协议与暂存晋升.md",
    "S07": "03_merge回主区与收尾.md",
    "S08": "03_merge回主区与收尾.md",
    "S09": "03_merge回主区与收尾.md",
    "C01": "04_提交正门与全局锁.md",
    "C02": "04_提交正门与全局锁.md",
    "C03": "04_提交正门与全局锁.md",
    "C04": "04_提交正门与全局锁.md",
    "C05": "05_门禁链与precommit通道.md",
    "C06": "05_门禁链与precommit通道.md",
    "C07": "05_门禁链与precommit通道.md",
    "C08": "06_入队排空与真落盘.md",
    "C09": "06_入队排空与真落盘.md",
    "C10": "06_入队排空与真落盘.md",
    "C11": "07_对账观测与紧急车道.md",
    "C12": "07_对账观测与紧急车道.md",
    "C13": "07_对账观测与紧急车道.md",
    "D01": "08_死信全链.md",
    "D02": "08_死信全链.md",
    "D03": "08_死信全链.md",
    "D04": "08_死信全链.md",
    "D05": "08_死信全链.md",
    "D06": "08_死信全链.md",
}

_GW = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
_SW = "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"
_CQ = "scripts/commit_queue.py"
_LF = "scripts/lock_files.py"
_GC = "scripts/governance/commit_queue_landing.py"
_CLI = "scripts/git_commit.py"
_INPROC_REG = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"
_SHELL_REG = "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"
# 挂血肉四字段输入件（挂图SOP vertical_map_mounting_policy §4：purpose_tag/casebooks/trigger_facts/consumers）
# F5 机生四件（零判定装配）+ 总筹 addendum（判定件）；缺任一件=硬失败（血肉层不可静默降级）
_CURE_DIR = "docs/_working/commitmap_cure"
_F5_PURPOSE = f"{_CURE_DIR}/f5_purpose_tags.yaml"
_F5_CASEBOOKS = f"{_CURE_DIR}/f5_casebooks_mount.yaml"
_F5_TRIGGER = f"{_CURE_DIR}/f5_trigger_facts.yaml"
_F5_CONSUMERS = f"{_CURE_DIR}/f5_consumers_agg.yaml"
_CHIEF_ADDENDUM = f"{_CURE_DIR}/chief_purpose_addendum.yaml"

# ---------------------------------------------------------------------------
# 人工语义层（骨架/作业簿契约常量，全量按 NODE_ORDER 枚举——静态清单禁手工维护的是
# "条目+计数"型清单，本层是 28 环节的语义契约件，与图 9 母版的人工字段同性质）
# ---------------------------------------------------------------------------

LAWS = [
    "正门唯一：一切提交经 git_commit.py/GitCommitGateway 正门，禁裸 git commit 与 plumbing 绕过"
    "（骨架 §0 门① 三触发源终点同归正门）",
    "队列是正门：全局锁争用不空转，锁超时自动改道 pending；直连与队列不混抢（骨架 §0 门② 交接面 5）",
    "门禁一套不裁：队列落地仍走网关全门禁链（commit_queue_landing 头 INVARIANTS 原文声明）",
    "死信不卡队：落地普通 Exception→dead/ 队列继续排空；BaseException 留 processing 等回收（§1 D11-D01）",
    "跨车道交接必须有实体：三车道 10 个交接面逐一实证（§0 门②），无实证交接不许画边",
]

BOUNDARY = [
    "不画运行时治理流水线（孵化/监控/熔断/收割/自愈）——归 GOMAP；其 out_of_scope_refs 明示排除"
    "提交门禁体系（config/governance_operations_map.yaml），是本图立图正门依据",
    "不画交易决策逻辑——归 TDM（config/trading_decision_map.yaml），引用不吸收",
    "不画单施工任务 15 步生命周期——construction_workflow_policy Step10/Step12 自标"
    "「不重复，引用」转引本域真源（骨架 §3 撞车判定 #2）",
    "叶层清单（门禁条目正文/reconciler 条目/dead_reason 标记串）进作业簿不进图本体："
    "本图只挂计数与指针（INV-1 铁律，TDM 同款）",
]

NODE_ORDER = [
    f"D11-{x}"
    for x in (
        *[f"S{i:02d}" for i in range(1, 10)],
        *[f"C{i:02d}" for i in range(1, 14)],
        *[f"D{i:02d}" for i in range(1, 7)],
        # gap 节点殿后（契约序在其受影响环节之后，边 host→gap 恒前向）
        "G01",
        "G02",
    )
]

_LANES = {"S": "会话", "C": "提交", "D": "死信"}
# gap 节点车道归属（node_id 前缀 G 非车道字母，故 lane 由本表显式声明，校验器同口径豁免）
_GAP_LANE = {"D11-G01": "C", "D11-G02": "C"}

# 每节点：name/q/mech 语义；status ✅/🔨 照用骨架 §1 状态列（判据口径不擅改）；
# ev=实查坐标（verified 的 evidence）；ref=module_ref 代码锚；anc=source_anchors；
# run=运行时指针（磁盘豁免面）；data/gates/stores 见校验器字段契约。
N: dict[str, dict[str, Any]] = {
    "D11-S01": dict(
        status="✅",
        name="会话冷启动与开班检查",
        q="本会话该启动吗？启动前环境/守卫/隔离施工/能力反查就位了吗？",
        mech="冷启动序列钩子=phase_manager session_startup（环境切换→reaper 守卫存活→worktree 申请制→"
        "能力反查→depgraph 登记）；开班检查脚本 record_session_start_commit.py；同类半成品在途预查="
        "audit/reuse_scan（裁定#480 C-2「先查再建」：三源 fail-open 纯只读，session_worktree_start "
        "注册成功后打印同类半成品提示）。逐项守则归并行协调政策，图不复制",
        ref="src/zephyr/governance/ops_governance/phase_manager.py:248",
        anc=[
            "src/zephyr/governance/ops_governance/phase_manager.py:248",
            "scripts/record_session_start_commit.py",
            "src/zephyr/governance/audit/reuse_scan.py",
        ],
        run=[".runtime/session_registry.json"],
        ev=[
            "src/zephyr/governance/ops_governance/phase_manager.py:248 session_startup 在位",
            ".runtime/session_registry.json 实查在盘（2026-09-24）",
            "scripts/record_session_start_commit.py 实查在盘",
            "src/zephyr/governance/audit/reuse_scan.py 在位（裁定#480 C-2）；本会话 2026-10-04 启动实弹："
            "start 输出「reuse_scan: 未提供 task_files，跳过预查」=预查钩子活体",
        ],
        stores=[
            dict(
                artifact="会话注册表",
                location=".runtime/session_registry.json",
                key="session_id",
                retention="注销即移除",
            )
        ],
    ),
    "D11-S02": dict(
        status="✅",
        name="worktree 分配与池化",
        q="本会话 worktree 从哪来？池 lease 还是直接创建？并发阻断怎么判？",
        mech="session_worktree_start 优先 WorktreePool.lease（失败 fall back 直建，池永不阻断启动）+"
        "lease 后异步 prefetch 补池；breaking_change 双向并发阻断；"
        "新资产上户口合一命令=scripts/governance/register_asset.py（裁定#480 C-2：creation_token/大白话/"
        "depgraph 五道手续一条命令编排，纯编排零重写）；"
        "首 claim 指南路由=lock_files.py:1684 _deliver_first_acquire_guide"
        "（本会话首次 acquire 弹施工指路 playbook 锚点，已读留痕后零输出，fail-open 不绑架锁主流程）",
        ref=f"{_SW}:2607",
        anc=[
            f"{_SW}:2607",
            "src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:277",
            "scripts/governance/register_asset.py",
            "scripts/lock_files.py:1684",
        ],
        run=[".aidrafts/", ".aidrafts_pool/"],
        ev=[
            f"{_SW}:2607 session_worktree_start",
            "src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:277 lease（P3.3 池化+prefetch）",
            "本战役工作目录 .aidrafts/st-mapbuild-20260924 即活体",
            "scripts/governance/register_asset.py 在位（MOD-GOV-REGISTER-ASSET，裁定#480 C-2 上户口合一）",
            "首 claim 指南路由活体实弹（2026-10-04）：本会话首次 lock_files acquire 输出「首次施工指路」段"
            "（FT-new_script_py playbook 锚点递送）",
        ],
        stores=[
            dict(
                artifact="会话 worktree",
                location=".aidrafts/ + .aidrafts_pool/",
                key="session_id",
                retention="merge 后主仓吸收 / abort 自删",
            )
        ],
    ),
    "D11-S03": dict(
        status="✅",
        name="会话心跳与活性判定",
        q="会话还活着吗？新鲜窗与 idle 自退双轨怎么判死？",
        mech="heartbeat_daemon 30s 刷新+jsonl 审计；SessionRegistry 90s 新鲜窗+1800s idle 自退双轨；"
        "单一活性裁决表=liveness_verdict（裁定#480 C-2 活性合流：8 套活性机制零改动继续在岗作数据源，"
        "P1-P6 优先级只读折算，唯一结论=state+authoritative_signal——内收式合流非重写）；"
        "活性 schema 契约引用并行协调政策（吸收其路径作节点注解，不复制正文）",
        ref="src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:39",
        anc=[
            "src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:39",
            "src/zephyr/security/access_control/session_concurrency.py:148",
            "src/zephyr/security/access_control/session_concurrency.py:1608",
        ],
        run=[".runtime/（heartbeat jsonl 审计面）"],
        ev=[
            "heartbeat_daemon.py:39-40（30s 刷新+jsonl 审计）",
            "session_concurrency.py:148（90s 新鲜窗+1800s idle 自退）",
            "session_concurrency.py:1608 def liveness_verdict 在位（裁定#480 C-2，"
            "st-sB-surgery-20261003 施工；同批 tests/governance/test_liveness_verdict_20261003.py）",
        ],
    ),
    "D11-S04": dict(
        status="✅",
        name="改前 claim（文件锁+基线快照）",
        q="动手前这份文件归谁？基线快照锚在哪次 claim？",
        mech="lock_files acquire → 网关 claim_files（基线=首次 claim 快照）；git_commit.py --claim-only 前移协议；"
        "热文件写入另走 safe_write_text CAS 通道",
        ref=f"{_LF}:549",
        anc=[f"{_LF}:549", f"{_GW}:1257", "scripts/git_commit.py:476"],
        ev=[
            "scripts/lock_files.py:549 cmd_acquire",
            "git_commit_gateway.py:1257 claim_files（基线=首次 claim 快照）",
            "git_commit.py:476 --claim-only 前移协议",
        ],
        stores=[
            dict(
                artifact="claim 锁与基线快照",
                location=".ailocks/",
                key="文件路径×session_id",
                retention="commit 结算即释放",
            )
        ],
    ),
    "D11-S05": dict(
        status="🔨",
        name="在途编辑与暂存晋升",
        q="staging 产物在 24h TTL 内被晋升了吗？没晋升谁来兜底清理？",
        mech="worktree 编辑隔离=活体（S02）；作业簿 02 全仓 grep 实查=**无任何代码实现 staging→docs/_working "
        "晋升**（同名异物三簇已排除：allow_promote=永久区新文件准入≠暂存晋升、ml_model_factory 反向语义、"
        "reconciler 告警文案里的「疑似未 promote」是清理者不是晋升者）⇒ 机生面只有其反面：24h TTL 清理+漏晋升告警"
        "（专项 reconciler 真源=reconciliation_registry.py:10988，_STAGING_TTL_SECONDS=24*3600 @:11020；"
        "骨架 S05 格所记 :7677 是通用 .runtime TTL 兜底、非 24h staging 专项真源）；abort 即时清理另腿="
        "session_worktree.py:1779 _cleanup_session_staging；骨架状态列仍记 🔨，转性口径归总包",
        ref="src/zephyr/governance/audit/reconciliation_registry.py:10988",
        anc=[
            "src/zephyr/governance/audit/reconciliation_registry.py:10988",
            "src/zephyr/governance/audit/reconciliation_registry.py:11020",
            "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:1779",
            "src/zephyr/governance/audit/reconciliation_registry.py:7677",
        ],
        run=[".runtime/sessions/<sid>/staging/"],
        stores=[
            dict(
                artifact="暂存成果",
                location=".runtime/sessions/<sid>/staging/",
                key="session_id×产物文件",
                retention="24h TTL，promote 到 docs/_working/ 才算交付",
            )
        ],
        ev=[
            "作业簿 02 §2「内」-1 全仓 grep promote∩staging/_working 排除三簇非同物后=空集（纪律-only 定性）",
            "reconciliation_registry.py:10988 make_session_staging_lifecycle_reconciler + :11020 "
            "_STAGING_TTL_SECONDS 在位（本车道 2026-09-25 复跑 grep）",
        ],
    ),
    "D11-S06": dict(
        status="✅",
        name="会话内 worktree 提交",
        q="worktree 内 commit 前，base 新鲜/stash 留痕/DCR/门禁子集四段都校齐了吗？",
        mech="worktree 独立 index 直接 add+commit（不占全局锁）；pre-commit 跑 worktree-compatible 门禁子集"
        "（跳过 _WORKTREE_SKIP_GATES）；DCR 检测 fail-closed；base 过期自动对齐防搭便车提交；"
        "stash 留痕→stash_notice.json 恢复通道",
        ref=f"{_SW}:4580",
        anc=[f"{_SW}:4580", f"{_SW}:3312", f"{_SW}:5254"],
        run=[".runtime/workspace_alerts/stash_notice.json"],
        ev=[
            f"{_SW}:4580 session_worktree_commit",
            f"{_SW}:3312 _ensure_worktree_base_fresh",
            f"{_SW}:5254/7261 stash 留痕+stash_notice 恢复通道",
        ],
        gates=["WORKTREE-REQUIRED"],
    ),
    "D11-S07": dict(
        status="✅",
        name="合并回主区（merge 正门）",
        q="现在能 merge 吗？HIGH drift 与 commit 后新增门禁规则挡不挡？",
        mech="merge 正门双检=_run_pre_merge_topo_check（HIGH drift 阻断；checker 缺失 fail-closed、DB 不可用降 "
        "fail-open 留痕）+_pre_merge_gate_check（reset --soft 模拟 staged 重跑 worktree-compatible 门禁）；"
        "**重大加注（六图终局卷 §4 图11「还差的活」）**：常量 _PRE_MERGE_SKIP_ALL_COMMIT_GATES=True"
        "（session_worktree.py:389，消费点 :7098）使 pre-merge 门预演**默认整体短路**——该阶段主区 sys.path "
        "与 worktree 代码版本错位会 ImportError 假阻断，故现行行为=只保留 TOPO-CHECK、跳过全部 commit gate"
        " ⇒ 本环节 wiring_status=partial（代码在盘而默认不跑，不是没实现）；"
        "git_commit.py --merge-finalize 配套（拒晾置）",
        ref=f"{_SW}:6714",
        anc=[f"{_SW}:6714", f"{_SW}:5828", f"{_SW}:6025", f"{_SW}:389", "scripts/git_commit.py:1053"],
        ev=[
            f"{_SW}:6714 session_worktree_merge",
            f"{_SW}:5828 _run_pre_merge_topo_check",
            f"{_SW}:6025 _pre_merge_gate_check",
            f"{_SW}:389 _PRE_MERGE_SKIP_ALL_COMMIT_GATES=True（预演整体短路的机生实查）",
            "scripts/git_commit.py:1053 --merge-finalize",
        ],
        gates=["WORKTREE-REQUIRED"],
    ),
    "D11-S08": dict(
        status="✅",
        name="放弃与死会话回收",
        q="放弃任务或会话死了，产物怎么 salvage、claim 归谁释放？",
        mech="abort 直通道；lock_files cleanup auto-salvage：双证判死→merge abort+stash 归档+释放 claim，"
        "全程写 salvage_audit.jsonl；死会话 stale claim 亦可经网关 release_files 精准释放",
        ref=f"{_LF}:1160",
        anc=[f"{_SW}:7497", f"{_LF}:786", f"{_LF}:1160"],
        ev=[
            f"{_SW}:7497 abort",
            f"{_LF}:786 cmd_cleanup（auto-salvage）",
            f"{_LF}:1160 salvage_dead_session（双证判死）",
            "审计面 .ailocks/salvage_audit.jsonl 实查在盘",
        ],
        stores=[
            dict(
                artifact="salvage 审计",
                location=".ailocks/salvage_audit.jsonl",
                key="时间戳×session_id",
                retention="永久留痕",
            )
        ],
    ),
    "D11-S09": dict(
        status="✅",
        name="收尾注销与 handoff 交接",
        q="注销前 claim 全放了吗？handoff 包落盘让下一会话可续吗？",
        mech="SessionHandoff schema（政策 §4 契约文本引用不复制）；网关 commit finally 写 handoff；"
        "close-door 序列真源=parallel_session_coordination_policy.md",
        ref="src/zephyr/security/access_control/session_concurrency.py:786",
        anc=["src/zephyr/security/access_control/session_concurrency.py:786", f"{_GW}:3538"],
        run=[".runtime/handoffs/"],
        ev=[
            "session_concurrency.py:786 SessionHandoff",
            "git_commit_gateway.py:3538-3545 commit finally 写 handoff",
            ".runtime/handoffs/ 实查非空（2026-09-24）",
        ],
        stores=[dict(artifact="handoff 交接包", location=".runtime/handoffs/", key="session_id", retention="留档")],
        data=["docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md"],
    ),
    "D11-C01": dict(
        status="✅",
        name="提交正门 CLI 与危险命令外壳",
        q="这次提交走哪个入口？失败退出码能不能定位死因与拆批口径？",
        mech="git_commit.py=唯一合法 CLI 入口封装网关（拆批纪律见文件头；退出码全谱矩阵=本图顶层 exit_codes，"
        "机生半边=AST 读 _COMMIT_RESULT_MAP + 全仓生产者构造计数）；"
        "**反裸提交的真担保是三拦截者而非两壳**（作业簿 04 旁向实查）：pre-commit hook gate-commit-gw + "
        "网关内 _run_git 守卫（in_commit_flow 非真即返伪结果）+ POST-COMMIT-GUARD 回滚；"
        "git_guard.py/git_safety_wrapper.ps1 只管删除类与 plumbing 类（DANGEROUS_SUBCOMMANDS 不含 commit），"
        "骨架 C01 格把两壳与正门并列易误读为「正门拦截器」——本节点按实查口径记",
        ref="scripts/git_commit.py:18",
        anc=[
            "scripts/git_commit.py:18",
            "scripts/git_safety_wrapper.ps1:19",
            "scripts/git_guard.py",
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:4257",
        ],
        ev=[
            "scripts/git_commit.py:18-50 文件头唯一入口声明",
            "git_safety_wrapper.ps1:19,115,153 BLOCKED 清单",
            "git_guard.py:90/:95 危险集与 plumbing 禁列（二者均不含 commit=实查）",
            "AST 扫描公共函数/退出码分发表/生产者构造计数=本节点 machine_facts",
        ],
        api="scripts/git_commit.py",
    ),
    "D11-C02": dict(
        status="🔨",
        name="失败指引锚点递送",
        q="失败时把 playbook/digest 指引锚点递送到修改者眼前了吗？",
        mech="递送接口在 git_commit.py 失败路径（锚=commit_navigation_playbook.md+gate_digest_registry.yaml 双件）；"
        "骨架口径 🔨（递送面无审计 sink；作业簿 04 已实弹核验并建议转 ✅，转性留总包）",
        ref="scripts/git_commit.py:109",
        anc=[
            "scripts/git_commit.py:109",
            "docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md",
            "docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources/gate_digest_registry.yaml",
        ],
        ev=["两锚文件 ls 实查在盘（骨架 §1 C02 行）", "作业簿 04 §2 stderr 可见实弹核验"],
    ),
    "D11-C03": dict(
        status="✅",
        name="claim 结算与失败重试语义",
        q="成功才释放 claim？失败保留并重试要不要带 --adopt-prior-work？",
        mech="结算规则=成功释放/失败保留+--failed-claim-ttl；--adopt-prior-work 治 FOREIGN_CHANGE 恶性循环；"
        "死会话 stale claim 精准释放=网关 release_files",
        ref="scripts/git_commit.py:734",
        anc=["scripts/git_commit.py:680", "scripts/git_commit.py:734", "scripts/git_commit.py:1071", f"{_GW}:1338"],
        ev=[
            "git_commit.py:32-36 结算契约",
            "_retain_claims_after_failure/_settle_claims_after_commit 实查在位",
            "--adopt-prior-work 通道在位",
        ],
    ),
    "D11-C04": dict(
        status="✅",
        name="全局串行锁与锁争用改道",
        q="全局锁拿到吗？拿不到是等待还是自动改道入队？",
        mech="_GlobalCommitLock 单写者串行；gate→stage→commit 不可分割；--no-auto-enqueue 显式退出改道语义；"
        "锁超时 AUTO-ENQUEUE 自动入队（flag 控制）",
        ref=f"{_GW}:495",
        anc=[f"{_GW}:495", "scripts/git_commit.py:1150", "scripts/git_commit.py:1306"],
        ev=[
            "git_commit_gateway.py:495 _GlobalCommitLock（TTL 见实现）",
            "git_commit.py:1150 --no-auto-enqueue",
            "git_commit.py:1306 锁超时改道入队",
        ],
        stores=[
            dict(
                artifact="全局提交锁", location=".ailocks/git_commit_global.lock", key="单锁", retention="TTL 超时自解"
            )
        ],
        data=["config/flags.yaml"],
    ),
    "D11-C05": dict(
        status="✅",
        name="in-process 门禁链执行",
        q="本改动按 priority 逐台过了门禁册登记的 in-process 门禁吗？（数量以册 total_gates 字段为准）",
        mech="in_process_gate_registry.yaml 动态注册（gate_auto_registrar）；锁外预跑+结果缓存+漂移观察"
        "（flags gate_preflight/gate_result_cache）；worktree 跳过面 _WORKTREE_SKIP_GATES；"
        "审批判定收敛器=commit_gates/approval_resolver（三通道：marker 防伪[查无即拒]+裁定册授权+都不命中，"
        "5611dbf3ca 修复 _strip_worktree_prefix 补单数 worktree/ 形态——serializer 落地树授权命中治本）；"
        "create_guard 册读取经 anchor_main_root 锚主仓根（同批修复：主区盘面=登记即时真源，#ARCH-324 先例）；"
        "叶层=册自身（99 条目明细进作业簿 05，INV-1 不抄进图）",
        ref="src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py",
        anc=[
            "src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py",
            f"{_GW}:2880",
            f"{_GW}:347",
            "src/zephyr/gov_enforcement/commit_gates/approval_resolver.py",
            "src/zephyr/gov_enforcement/commit_gates/create_guard.py",
        ],
        data=[_INPROC_REG, "config/flags.yaml"],
        ev=[
            "in_process_gate_registry.yaml total_gates 字段 grep 实查",
            "gateway _preflight_flag_enabled/_check_gates_with_drift_watch 在位",
            "machine_facts 双计数（字段值 vs 条目实扫）由本生成器动态产出",
            "approval_resolver._strip_worktree_prefix 单数 worktree/ 形态在位（5611dbf3ca 时序倒置治本，"
            "#461 落地形态裁定命中放行）",
            "create_guard.py:728 anchor_main_root 主区锚定在位（登记完即可提交，serializer 陈旧册破坏已修）",
        ],
        gate_facts=_INPROC_REG,
    ),
    "D11-C06": dict(
        status="✅",
        name="暂存与提交本体",
        q="gitignored-tracked 怎么分离？rename 检出与 [GW:] 尾标防伪谁守？",
        mech="_commit_locked：gitignored-tracked 分离、pathspec-from-file add/rm、rename fallback、"
        "--no-verify -F msg 提交+[GW:<sid>] 尾标；FORGED-GW-MARKER 门禁守伪标",
        ref=f"{_GW}:2971",
        anc=[f"{_GW}:2971", f"{_GW}:3607", f"{_GW}:3657"],
        ev=[
            "gateway _commit_locked/_has_staged_renames/_commit_with_file_message 行锚实查",
            "FORGED-GW-MARKER 在册（gate_id 引用不抄正文）",
        ],
        gates=["FORGED-GW-MARKER"],
    ),
    "D11-C07": dict(
        status="✅",
        name="pre-commit shell 门禁通道",
        q="shell 侧门禁在网关临时索引通道里拿到执行权了吗？（数量以册 total_gates 字段为准）",
        mech="网关内以子进程重放 pre-commit 框架的补执行拍（git hooks 对经网关的提交恒不触发——提交走 "
        "--no-verify，故本环不是「git hook 通道」而是重放通道，作业簿 05 §3 旁向三证钉界）："
        "_run_precommit_channel+_precommit_build_temp_index（GIT_INDEX_FILE own-scope 临时索引）；"
        "开关读 gate_precommit_run_enabled（**在册键名是 gate_precommit_run ⇒ 未注册 × default=True ⇒ "
        "恒 ON，回滚面失效见 gap 节点 D11-G02**）；SKIP 名单实含 3 门（gate-commit-gw/gate-worktree-required/"
        "gate-protected-paths，2026-09-24 四死信实证后加第三门，flags.yaml 描述仍写两门=文档矛盾待总包收口）；"
        "失败裁决四态：infra_error→warn 放行、mutation 重跑仍变异→阻断、own_failed→阻断、foreign_failed→warn 放行；"
        "叶层=shell 门禁册（条目明细归生成器 generate_gate_registry.py，本图只挂指针）",
        ref=f"{_GW}:3189",
        anc=[f"{_GW}:3189", f"{_GW}:3091", f"{_GW}:358", f"{_GW}:401"],
        data=[_SHELL_REG, "config/flags.yaml"],
        ev=[
            "gateway _run_precommit_channel/_precommit_build_temp_index 行锚实查",
            "config/flags.yaml gate_precommit_run 在册 + gateway:358 代码键 gate_precommit_run_enabled（两名不同=实查）",
            "machine_facts 双计数由本生成器动态产出",
        ],
        gate_facts=_SHELL_REG,
    ),
    "D11-C08": dict(
        status="✅",
        name="入队即转活（快照入袋）",
        q="这条提交请求能过入队轻检（穿越/消息/体积/密钥名），并以内容寻址快照入袋吗？",
        mech="enqueue_item 轻检四规则+_store_blob 内容寻址去重+_create_item_excl O_EXCL 唯一 qid+"
        "_compact_pending 同键覆盖；sys.path 清洗等实现细节进作业簿 06（叶层）",
        ref=f"{_CQ}:636",
        anc=[f"{_CQ}:636", f"{_CQ}:442", f"{_CQ}:489", f"{_CQ}:534"],
        run=[".runtime/commit_queue/pending/", ".runtime/commit_queue/blobs/"],
        ev=[
            "commit_queue.py enqueue_item/_store_blob/_create_item_excl 行锚实查",
            "pending/blobs 目录只读 ls 实查（计数见 machine_facts）",
        ],
        stores=[
            dict(
                artifact="队列项+内容寻址袋",
                location=".runtime/commit_queue/pending + .runtime/commit_queue/blobs",
                key="qid / blob sha",
                retention="pending 同键 compact；排空转 processing",
            )
        ],
        api=_CQ,
    ),
    "D11-C09": dict(
        status="✅",
        name="排空调度与消费端",
        q="这条队列项由谁消费？lease 僵尸回收、通道路由与池并发怎么定？",
        mech="SerializerLease TTL+僵尸 PID 回收；channel_key_for_files 通道路由（hot/shared 单通道）；"
        "k 池并行排空（drain_queue_pool+_pool_cas_replay）；belt daemon 事件触发自举补位",
        ref=f"{_CQ}:769",
        anc=[
            f"{_CQ}:769",
            f"{_CQ}:207",
            "scripts/governance/commit_queue_landing.py:1938",
            "scripts/governance/commit_queue_landing.py:1685",
            "src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py",
        ],
        run=[
            ".runtime/commit_queue/worktrees/（池目录，台数以实扫为准）",
            ".runtime/commit_queue/belt_daemon.heartbeat",
        ],
        ev=[
            "SerializerLease/channel_key_for_files 行锚实查",
            "drain_queue_pool/_pool_cas_replay 在位",
            "belt_daemon.heartbeat 文件实查在盘",
        ],
    ),
    "D11-C10": dict(
        status="✅",
        name="真落盘（worktree+CAS+收敛）",
        q="这条队列项能走完落盘五步（幂等→基底→blob→全门禁→CAS update-ref）真进 dev 吗？",
        mech="落盘流水线五步+主区受限快进收敛；瞬态 git 冲突标记→退回 pending 绝不死信；"
        "单写者 dev 历史断言日检；LandingEnvironmentError 与死信分流边界见作业簿 06/08",
        ref="scripts/governance/commit_queue_landing.py",
        anc=["scripts/governance/commit_queue_landing.py:158", "scripts/governance/commit_queue_landing.py:2315"],
        run=[".runtime/commit_queue/processing/"],
        ev=[
            "landing 文件头落盘流水线声明+关键函数行锚实查",
            "done/ 最新项 landed_at/landed_id 回填实查（骨架 §0 门①）",
            "近 3 日 dev [GW: 标记与队列落地计数复核命令=骨架 §7 附录（只读）",
        ],
        stores=[
            dict(
                artifact="落地回填台账",
                location=".runtime/commit_queue/done",
                key="qid→landed_id",
                retention="done TTL 定期清理（见 C13）",
            )
        ],
    ),
    "D11-C11": dict(
        status="✅",
        name="post-commit 对账与守卫",
        q="这次 commit 之后要跑哪些 reconciler？异步编排与 shell 守卫怎么接力？",
        mech="网关 _register_default_reconcilers 事件触发编排（台数以实扫 register 调用为准，勿背数）；"
        "run_post_commit_reconciler 异步化；git_hooks 双守卫（post_commit_guard/reference_transaction_guard）"
        "红蓝触发；reconciler 必须事件触发禁定时器（永久系统四要素）",
        ref=f"{_GW}:1547",
        anc=[
            f"{_GW}:1547",
            f"{_GW}:1034",
            f"{_GW}:3559",
            "scripts/governance/git_hooks/post_commit_guard.sh",
            "scripts/governance/git_hooks/reference_transaction_guard.sh",
        ],
        ev=["register( 调用动态计数=machine_facts（骨架 §7 复核命令同口径）", "两 shell guard 文件实查在盘"],
    ),
    "D11-C12": dict(
        status="✅",
        name="机器车道与紧急通道",
        q="机器提交要不要按 flag 改道？emergency 通道什么时候合法、伪造标记怎么判？",
        mech="_commit_auto 按 serializer flag 改道回队列（单写者断言日检）；BatchedAutoCommitter 合批；"
        "emergency_commit 仅注册表/锁不可用时合法（commit-tree plumbing+落册审计，手写标记判 forged）",
        ref=f"{_GW}:3845",
        anc=[f"{_GW}:3845", f"{_GW}:3827", "src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py:20"],
        data=["config/flags.yaml"],
        ev=[
            "_commit_auto/_reroute_commit_auto_to_queue 行锚实查",
            "flags.yaml serializer 开关+翻旗留痕实查",
            "emergency_commit 合法边界与审计面实查",
        ],
        gates=["FORGED-GW-MARKER"],
    ),
    "D11-C13": dict(
        status="✅",
        name="队列台账与运维观测",
        q="队列健康可观测吗？TTL、告警阈值与堵点账本各归谁守？",
        mech="四态目录协议+queue_health 只读快照+dead 积压告警（阈值真源=告警阈值册 THD 条目引用）；"
        "done TTL/dead 永不自动清理不变量；堵点账本 jsonl；归属核实纪律 git log -1 --name-only",
        ref=f"{_CQ}:1719",
        anc=[f"{_CQ}:166", f"{_CQ}:2311", f"{_CQ}:1719", f"{_CQ}:1777"],
        data=["docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml"],
        run=[".runtime/audit/bottleneck_ledger.jsonl"],
        ev=[
            "_STATES/cleanup/queue_health/emit_dead_backlog_alert 行锚实查",
            "THD-ALERT-003 在册（编号引用不抄正文）",
            "四态目录只读计数=machine_facts",
        ],
        stores=[
            dict(
                artifact="堵点账本",
                location=".runtime/audit/bottleneck_ledger.jsonl",
                key="时间戳×qid",
                retention="追加",
            )
        ],
        queue_states=True,
    ),
    "D11-D01": dict(
        status="✅",
        name="死信产生（不卡队）",
        q="落地失败了，这一项去哪条道？队列会不会被卡住？",
        mech="落地三分流：普通 Exception→dead/（带 dead_reason/dead_at）；BaseException 留 processing 等回收；"
        "LandingEnvironmentError 退回 pending 绝不死信（Law 4 的执行面）",
        ref=f"{_CQ}:71",
        anc=[f"{_CQ}:71"],
        run=[".runtime/commit_queue/dead/"],
        ev=[
            "commit_queue.py:71-80 分流协议行锚实查",
            "dead/ 目录只读实查含 dead_reason/dead_at 字段样例（骨架 §1 D01 行）",
        ],
        stores=[dict(artifact="死信项", location=".runtime/commit_queue/dead", key="qid", retention="永不自动清理")],
    ),
    "D11-D02": dict(
        status="✅",
        name="死因三分类甄别",
        q="这次死法是环境病、项内病、还是 other？",
        mech="_DEAD_REASON_ENV_MARKERS/_DEAD_REASON_ITEM_MARKERS 标记表（含历史补盲批注）+"
        "classify_dead_reason 三分类；标记串条目=叶层进作业簿 08，图只挂表位置指针",
        ref=f"{_CQ}:1709",
        anc=[f"{_CQ}:240", f"{_CQ}:1709"],
        ev=["两标记表与 classify_dead_reason 行锚实查", "补盲批注（0916/0922）见作业簿 08 史向"],
        data=["docs/01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md"],
    ),
    "D11-D03": dict(
        status="✅",
        name="死信台账联动与告警",
        q="这条死信在任务台账上有标吗？告警发出去了吗？",
        mech="_notify_task_board_dead_letter→task_board tag_dead_letter（metadata 承载，不改表）；"
        "requeue 同步标注；告警走 C13 积压告警通道。task_board=任务治理域，出域引用不吸收",
        ref=f"{_CQ}:930",
        anc=[f"{_CQ}:930", "scripts/task_board.py:332", f"{_CQ}:1349"],
        ev=["notify/tag 两侧函数行锚实查（task_board.py:332 tag_dead_letter）"],
    ),
    "D11-D04": dict(
        status="✅",
        name="requeue 复活链路",
        q="这条死信还能救吗？requeue 基于当前工作区重建快照后原项留什么痕？",
        mech="requeue_dead_item：基于当前工作区重建快照→新 qid 排队尾（回 C08 入队口）；原项留 requeued 指针；"
        "队列项 dead 后读 dead_reason 修正再 requeue 是标准处置",
        ref=f"{_CQ}:1387",
        anc=[f"{_CQ}:1387", f"{_CQ}:2184"],
        run=[".runtime/commit_queue/dead/（requeued 留痕样例实查）"],
        ev=["requeue_dead_item/CLI requeue 行锚实查", "活体样例 0031→0055 requeued 字段只读核验（骨架 §7 命令 8）"],
    ),
    "D11-D05": dict(
        status="✅",
        name="级联失效判定（cascade_stale）",
        q="某项落盘后，还在 pending 的项的依赖声明还成立吗？",
        mech="项 X 落盘后扫 pending：depends_on/base_blob vs HEAD 仍适用→清标放行；不适用→"
        "dead_reason=cascade_stale 死信候选（不消耗 landing）；interactive/machine 双车道 head 选取细节进簿 08",
        ref=f"{_CQ}:104",
        anc=[f"{_CQ}:104", f"{_CQ}:288"],
        ev=["B 段协议注释与标记表收录 cascade_stale 行锚实查"],
    ),
    "D11-D06": dict(
        status="✅",
        name="死信归档轮换与清零战役",
        q="死信最终去哪？轮换袋与清零战役的处置结论谁留档？",
        mech="dead/ 永不自动清理不变量；轮换袋人工搬运（袋名清单以实扫为准）；清零战役三分法"
        "（superseded/真未落地/历史留档）结论落 docs/_working 战役记录；"
        "hold_* 袋出处考古=🌑 候选（骨架 §6 点名，图不编造出处）",
        ref=f"{_CQ}:56",
        anc=[f"{_CQ}:56"],
        run=[".runtime/commit_queue/（dead_archive_*/dead_purged_* 轮换袋，袋名以实扫为准）"],
        data=[
            "docs/_working/2026-09-11-commit-queue-dead-zero-closure.md",
            "docs/_working/archive/2026-09/final3_campaign/p12_queue_terminal_record.md",
        ],
        ev=["队列根轮换袋目录只读实查（骨架 §1 D06 行）", "两篇战役记录在盘"],
        stores=[
            dict(
                artifact="死信轮换归档袋",
                location=".runtime/commit_queue/ + docs/_working/2026-09-11-commit-queue-dead-zero-closure.md",
                key="袋名×qid",
                retention="dead 永不自动清理；战役记录永久",
            )
        ],
    ),
    # ------------------------------------------------------------------
    # gap 节点（六图终局卷 §4 图11 验收判据②：两条作业簿实测缺口显性化）
    # 无运行代码可挂 ⇒ module_id=null + red_reason 必填（§2 裁定二第 2 条）；
    # 代码坐标进 source_anchors（module_ref 留空，避免 CV-BUS "有 ref 无 id" 假矛盾）。
    # ------------------------------------------------------------------
    "D11-G01": dict(
        gap=True,
        lane="C",
        status="🔨",
        name="退出码死分支（码 4 与 STASH_CONFLICT 支无生产者）",
        q="退出码谱里哪些专码永不被产出？按码分诊的调用方会不会白等一个不可能的分支？",
        mech="机生判据=_COMMIT_RESULT_MAP 有专码条目 ∧ 全仓 `status=CommitStatus.X` 生产者构造计数=0"
        "（实扫 SSOT_VIOLATION→4 与 STASH_CONFLICT→2 两支命中，见 machine_facts.exit_code_producers）；"
        "STASH_CONFLICT 支的历史消费者 task_repo 分派仍在盘（阶段3 移除 stash 隔离后成孤儿支路）；"
        "内收判据「零触发零消费→退役」适用，处置权在总包（本图不删表不改码）",
        anc=[
            f"{_CLI}:162",
            f"{_CLI}:149",
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:439",
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:450",
            "src/zephyr/governance/persistence/task_repo.py:2528",
        ],
        ev=[
            f"{_CLI}:149/:162 两条专码映射在表；复跑（簿04 §末-3 命令 2）：全仓 grep 'CommitStatus.SSOT_VIOLATION' "
            "只命中枚举定义+本表 ⇒ 零生产者",
            "gateway:450 逐字「阶段3 已弃用，保留向后兼容」；gateway:439 SSOT_VIOLATION 全仓无构造点",
        ],
        red="unwired",
    ),
    "D11-G02": dict(
        gap=True,
        lane="C",
        status="🔨",
        name="precommit 通道回滚旗恒失效（代码键未注册 × default=True）",
        q="把 flag 关掉能不能停掉 precommit 重放通道？Owner 门位「flag 翻转」在本通道可翻转吗？",
        mech="代码读 `gate_precommit_run_enabled`（gateway:358，is_enabled(…, default=True) :424），"
        "在册键却是 `gate_precommit_run`（flags.yaml:96）——未注册键走 default ⇒ 通道恒 ON；"
        "gateway:413 docstring 自述「Owner 紧急停用=flags.yaml flag OFF」在本通道不可兑现；"
        "唯一可停手柄 env `ZEPHYR_PRECOMMIT_FAST_SUBSET=0` 只关 Phase-A 子集不关通道本体"
        "（gateway:390-398）⇒ 回滚面=幽灵引用（red_reason ghost_ref），开关面与注册表必须同名",
        anc=[
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:358",
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:424",
            "config/flags.yaml:96",
            "src/zephyr/shared/foundation/flags.py:279",
        ],
        ev=[
            "复跑（簿05 §末-3 命令 3）：`gate_precommit_run_enabled` in global_flag_registry._flags=False "
            "而 is_enabled(default=True)=True；`gate_precommit_run` 已注册且 is_enabled=True",
            "gateway:358 常量与 flags.yaml:96 在册键逐字比对（本车道 2026-09-25 复跑一致）",
        ],
        red="ghost_ref",
    ),
}

# ---------------------------------------------------------------------------
# L1 wiring_status / L1 red_reason / L0 exec_evidence / L2 exit_codes·gate_cluster·
# deadletter_class 的逐环节挂载表（与 N 同 key 空间；缺 production 节点的 exec 即生成期报错）
# ---------------------------------------------------------------------------

# 默认 wired；非 wired 者逐环节登记（表达位=L1 裁定"槽挂着但没跑走这一个字段"）
WIRING: dict[str, str] = {
    "D11-S05": "unwired_no_caller",  # 作业簿 02：staging→_working 晋升无任何代码面（纪律-only）
    "D11-S07": "partial",  # _pre_merge_gate_check 在盘但被 _PRE_MERGE_SKIP_ALL_COMMIT_GATES=True 整体短路
    "D11-C02": "partial",  # 递送在盘，审计 sink 无（判据只能以 stderr 可见为凭）
    "D11-C09": "partial",  # channel_key_for_files 在案，k=1 现状 drain 不咨询该路由（池化后才成主面）
    "D11-C10": "partial",  # interactive 正门 base_head 恒 None ⇒ 非注册表整文件覆盖支路无基底比对
    "D11-D05": "unwired_slot_hollow",  # base_blob 恒 None ⇒ _revalidate_stale_base 结构空转（永远判"仍适用"）
    "D11-G01": "unwired_no_caller",
    "D11-G02": "unwired_slot_hollow",
}
RED: dict[str, str] = {
    "D11-S05": "unwired",
    "D11-S07": "unwired",
    "D11-C02": "unwired",
    "D11-C09": "unwired",
    "D11-C10": "broken_supply",
    "D11-D05": "unwired",
}

# exec_evidence=production 节点的"真在产/真在跑"复跑口径（作业簿 §末-3 命令族 + 主区只读实查日）；
# 观察数随并发漂移，故一律写"命令口径 + 断言 + 观察日"，不把静态计数钉进散文。
EXEC: dict[str, list[str]] = {
    "D11-S01": [
        "复跑: python -c \"import json;d=json.load(open('.runtime/session_registry.json',encoding='utf-8'));print(len(d.get('sessions',d)))\""
        "（主区只读 2026-09-25 实查：文件在盘 3725B，schema 可解析）",
        ".runtime/lookup_audit/ 367 件（2026-09-25 只读计数）=冷启动第 4 条能力反查审计在产面",
    ],
    "D11-S02": [
        "主区只读 ls -d .aidrafts/* → 12 个在途会话 worktree（2026-09-25）；本战役目录 .aidrafts/st-mapbuild-20260924 即活体",
        "src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:277 lease 在位（复跑 grep -n 'def lease'）",
    ],
    "D11-S03": [
        "主区只读 ls .runtime/sessions → 49 个会话目录，逐目录 heartbeat.jsonl/heartbeat.pid 面（2026-09-25）",
        "heartbeat_daemon 文件路径节声明审计真源=.runtime/sessions/<sid>/heartbeat.jsonl",
    ],
    "D11-S04": [
        "主区只读 ls .runtime/claim_snapshots → 877 件（2026-09-25，claim 基线快照在产）",
        ".ailocks/registry.json 在盘（2026-09-25 实查 11621B）；复跑: python scripts/lock_files.py status",
    ],
    "D11-S05": [
        "复跑（簿02 §末-3 命令 1）：全仓 grep promot* ∩ staging/sessions/_working 排除三簇非同物后=空集"
        "（⇒ 只有清理面无晋升面，结构事实而非在产流程）",
        "src/zephyr/governance/audit/reconciliation_registry.py:10988 make_session_staging_lifecycle_reconciler "
        "与 :11020 _STAGING_TTL_SECONDS 在位（本车道 2026-09-25 复跑 grep）",
    ],
    "D11-S06": [
        "主区只读 .runtime/gate_audit/worktree_skip.jsonl 与 worktree_status_snapshots.jsonl（2355 行）在盘"
        "（2026-09-25）=worktree 门禁子集/跳门面每日在跑",
        "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:4580 session_worktree_commit 在位",
    ],
    "D11-S07": [
        "主区只读 .runtime/gate_audit/force_merge_usage.jsonl 在盘（2026-09-25，merge 正门 force 计数审计在产）",
        "grep -n '_PRE_MERGE_SKIP_ALL_COMMIT_GATES' src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"
        " → :389=True / :7098 消费（本车道 2026-09-25 复跑；pre-merge 门预演整体短路即此常量的现行行为）",
    ],
    "D11-S08": [
        "主区只读 wc -l .ailocks/salvage_audit.jsonl → 659 行（2026-09-25，死会话回收持续留痕）",
        "复跑: python scripts/lock_files.py cleanup（幂等 auto-salvage 入口）",
    ],
    "D11-S09": [
        "主区只读 ls .runtime/handoffs → 242 件（2026-09-25，跨会话交接包在产）",
        "src/zephyr/security/access_control/session_concurrency.py:786 SessionHandoff 在位",
    ],
    "D11-C01": [
        "复跑: git log refs/heads/dev --since='3 days ago' --format=%B | grep -c '\\[GW:' → 1382 条（2026-09-25）"
        "＝近三日全部提交仍逐条过正门",
        "machine_facts.commit_exit_map（AST 读 _COMMIT_RESULT_MAP）非空＝专码分发表活着",
    ],
    "D11-C02": [
        "复跑（簿04 §末-3 命令 5）：直调 _format_commit_result(COMMIT_FAILED,'门禁 WORKTREE-REQUIRED 阻断: x')"
        " → stderr 打印 GUIDE 锚点行（2026-09-24 实弹，零写盘）",
        "git_commit.py:116-133 函数体只含 print/logger.debug ⇒ 无审计 sink，故判据停在 structure",
    ],
    "D11-C03": [
        "主区只读 .runtime/claim_snapshots/claim_retention.jsonl 在盘（2026-09-25，失败保留+TTL 收窄留痕）",
        "grep -n 'def _settle_claims_after_commit|def _retain_claims_after_failure' scripts/git_commit.py → :734/:680 在位",
    ],
    "D11-C04": [
        "复跑（主区只读）: ls -la .runtime/gate_audit/commit_lock_fallback.jsonl"
        " → 在盘（2026-09-25，锁 fail-open 降级有账）",
        "复跑（主区只读）: wc -l .runtime/audit/commit_block_events.jsonl → 833KB 级持续增长"
        "（2026-09-25 实查）＝锁/门阻断事件每日在写",
    ],
    "D11-C05": [
        "主区只读 .runtime/audit/preflight_events.jsonl 924KB（2026-09-25）＝P0-A 锁外预检每日在跑",
        "复跑: python scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py --dry-run"
        " + grep total_gates in_process_gate_registry.yaml（双计数口径见 machine_facts.gate_registry_facts）",
    ],
    "D11-C06": [
        "主区只读 .runtime/gate_audit/gateway_index_hygiene.jsonl 在盘（2026-09-25，两把 index 卫生清扫留痕）",
        "复跑: git log refs/heads/dev --since='3 days ago' --format=%B | grep -c 'q-2026' → 365 条（2026-09-25）",
    ],
    "D11-C07": [
        "主区只读 .runtime/gate_audit/precommit_incremental_baseline.json 在盘（2026-09-25，precommit 通道审计面）",
        "复跑（簿05 §末-3 命令 3）：is_enabled('gate_precommit_run')=True ⇒ 通道实际在跑；"
        "其回滚面恒失效另见 gap 节点 D11-G02",
    ],
    "D11-C08": [
        "主区只读 ls .runtime/commit_queue/pending → 37 件、blobs → 19992 件（2026-09-25，入队面持续收单）",
        "复跑: grep -n 'def enqueue_item|def _store_blob|def _create_item_excl' scripts/commit_queue.py → :636/:489/:534",
    ],
    "D11-C09": [
        "主区只读 .runtime/commit_queue/belt_daemon.heartbeat mtime=2026-09-25 02:16（消费端守护活着）",
        "主区只读 ls .runtime/commit_queue/worktrees → w0 w1 w2 w3（k=4 池在盘）",
    ],
    "D11-C10": [
        "主区只读 done 最新项 q-20260925-st-metaq-gc-20260924-0018：landed_at=2026-09-25T02:13:14+08:00、"
        "landed_id=a3bb88146cf48403（真 git 落地在产，复跑命令=骨架 §7 附录 1）",
        "主区只读 .runtime/commit_queue/main_workspace_sync.jsonl 在盘（2026-09-25，主区快进收敛留痕）",
    ],
    "D11-C11": [
        '复跑: grep -c "self._reconciliation_registry.register(" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py'
        " → 58（本车道 2026-09-25 复跑=machine_facts 同口径）",
        "主区只读 .git/hooks/post-commit 在盘 + .runtime/reconcile_reports/ 持续产件（2026-09-25）",
    ],
    "D11-C12": [
        "主区只读 grep -l rerouted_from .runtime/commit_queue/done/*.json → 53 件（2026-09-25，"
        "机器车道 reconciler 改道真的落过地）",
        "config/flags.yaml:81 commit_queue_serializer enabled:true（复跑: grep -n commit_queue_serializer config/flags.yaml）",
    ],
    "D11-C13": [
        "主区只读 .runtime/commit_queue/health_alert_state.json 在盘（2026-09-25，告警冷却态在用）",
        "复跑（只读）: python scripts/commit_queue.py health --no-alert（禁 status/drain——二者触发自举排空）",
    ],
    "D11-D01": [
        "主区只读 ls .runtime/commit_queue/dead → 403 件，抽读含 dead_reason/dead_at 字段（2026-09-25）",
        "scripts/commit_queue.py:71-80 分流协议注释 + :1262-1282 落账段在位",
    ],
    "D11-D02": [
        "主区只读 ls .runtime/commit_queue/dead_triage_*.jsonl → 3 份甄别台账（2026-09-25）",
        "machine_facts.deadletter_marker_counts（AST 读两标记表条数）非零＝分类表在维护",
    ],
    "D11-D03": [
        "grep -n '_DEADLETTER_WATCH_TASK_ID' scripts/commit_queue.py → :237 在册告警 task（复跑即可）",
        "scripts/task_board.py:332 tag_dead_letter 在位；联动异常吞掉不阻断排空（:961-962）",
    ],
    "D11-D04": [
        "主区只读双向 trace 复跑（骨架 §7 命令 8）：dead/0031.requeued.new_qid=…-0055、"
        "dead/0055.meta.requeued_from=…-0031（2026-09-25 复核仍成立）"
    ],
    "D11-D05": [
        "主区只读 grep -l cascade_stale .runtime/commit_queue/dead/*.json → 10 件（2026-09-25，级联判定真的降过死信）",
        "复跑: grep -n '\"base_blob\": None' scripts/commit_queue.py → :696/:712（恒 None＝重校验器结构空转的机生证据）",
    ],
    "D11-D06": [
        "主区只读 ls -d .runtime/commit_queue/{dead_archive*,dead_purged*,hold_*} → 11 袋（2026-09-25）",
        "两篇战役记录在盘（docs/_working/2026-09-11-commit-queue-dead-zero-closure.md 与 final3 p12 终态记录）",
    ],
    "D11-G01": [
        "复跑（簿04 §末-3 命令 2/4）：SSOT_VIOLATION/STASH_CONFLICT 全仓仅命中枚举定义+分发表+task_repo 消费支路，"
        "生产者构造计数=0（machine_facts.exit_code_producers 同源）"
    ],
    "D11-G02": [
        "复跑（簿05 §末-3 命令 3）：代码键 gate_precommit_run_enabled 未注册而 is_enabled(default=True)=True ⇒ 恒 ON"
    ],
}

# L2 专属层·提交退出码（值取作业簿 04 §1 内矩阵；全谱矩阵在顶层 exit_codes）
XCODES: dict[str, list[int]] = {
    "D11-C01": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "D11-C03": [1, 6, 7],
    "D11-C04": [2],
    "D11-C05": [3, 5, 6, 8, 9],
    "D11-C06": [1, 10],
    "D11-C07": [1],
    "D11-G01": [2, 4],
}
# L2 专属层·门禁簇（机生计数在 machine_facts，此处只挂"该节点吃哪一簇"的归属）
GCLUSTER: dict[str, str] = {
    "D11-C05": "in_process",
    "D11-C06": "gw_marker_chain",
    "D11-C07": "pre_commit",
    "D11-S06": "worktree_compatible_subset",
    "D11-S07": "pre_merge_topo_check",
}
# L2 专属层·死信分类归属（env/item/other + cascade_stale 专支 + 处置三分法）
DLC: dict[str, list[str]] = {
    "D11-C10": ["env→退回 pending 绝不死信（LandingEnvironmentError）", "item→dead/"],
    "D11-D01": ["item", "env", "other"],
    "D11-D02": ["env", "item", "other"],
    "D11-D05": ["item(cascade_stale)"],
    "D11-D06": ["superseded", "真未落地", "历史留档"],
    "D11-C13": ["env", "item", "other"],
}

# 边=骨架 §2 三车道交接关系（车道内串行主干 + 跨车道交接点；反向边全部走 feedback_loops 声明）
EDGES = [
    # 会话车道主干（起止=对话启动→会话注销）
    ["D11-S01", "D11-S02"],
    ["D11-S02", "D11-S03"],
    ["D11-S03", "D11-S04"],
    ["D11-S04", "D11-S05"],
    ["D11-S05", "D11-S06"],
    ["D11-S06", "D11-S07"],
    ["D11-S06", "D11-S08"],
    ["D11-S07", "D11-S09"],
    ["D11-S08", "D11-S09"],
    # 交接点 会话→提交：merge 后的收尾批再过正门则入 C 道
    ["D11-S07", "D11-C01"],
    # 提交车道主干（claim 结算→锁→门禁→暂存→落地；直连/入队双通道）
    ["D11-C01", "D11-C02"],
    ["D11-C01", "D11-C03"],
    ["D11-C01", "D11-C08"],
    ["D11-C03", "D11-C04"],
    ["D11-C04", "D11-C05"],
    ["D11-C04", "D11-C08"],
    ["D11-C05", "D11-C06"],
    ["D11-C06", "D11-C07"],
    ["D11-C06", "D11-C11"],
    ["D11-C08", "D11-C09"],
    ["D11-C09", "D11-C10"],
    ["D11-C10", "D11-C13"],
    ["D11-C11", "D11-C12"],
    # 交接点 提交→死信：落盘失败判定 / 落盘后级联重校验
    ["D11-C10", "D11-D01"],
    ["D11-C10", "D11-D05"],
    # 死信车道主干（分类→打标→分诊→归档）
    ["D11-D01", "D11-D02"],
    ["D11-D02", "D11-D03"],
    ["D11-D03", "D11-D04"],
    ["D11-D01", "D11-D06"],
    # gap 节点显性化：边从"受影响环节"指向缺口（六图终局卷 §4 图11 判据②）
    ["D11-C01", "D11-G01"],  # 退出码全谱归 C01 机器契约；码 4/STASH 支不可达即该谱上的洞
    ["D11-C07", "D11-G02"],  # precommit 通道回滚手柄恒失效，受影响环节=C07 本身
]

FEEDBACK_LOOPS = [
    {
        "from": "D11-D04",
        "to": "D11-C08",
        "note": "requeue 复活：基于当前工作区重建快照→新 qid 回入队口排队尾（骨架 §2 死信→提交交接点）",
    },
    {
        "from": "D11-C12",
        "to": "D11-C08",
        "note": "机器车道改道：reconciler 产 commit→serializer flag 改道回队列（骨架 §2 提交车道内已声明环路）",
    },
    {
        "from": "D11-D05",
        "to": "D11-D01",
        "note": "级联失效：pending 项依赖声明不再适用→dead_reason=cascade_stale 死信候选（§1 D11-D05 协议）",
    },
]

# L2 专属层·提交退出码全谱矩阵（触发分支/改道/处方三列=作业簿 04 §1「内」向穷举；
# 码↔状态↔生产者计数半边由 machine_facts.commit_exit_map/exit_code_producers 机生补齐）
EXIT_MATRIX = [
    {
        "code": 0,
        "statuses": ["OK"],
        "auto_enqueue": False,
        "prescription_zh": "无（message-file 自动删）；claim-only 全成/release-only 回读通过/--enqueue 入袋成功同码",
    },
    {
        "code": 1,
        "statuses": [
            "COMMIT_FAILED",
            "METADATA_VIOLATION",
            "NAMING_VIOLATION",
            "SCRIPT_INTEGRITY_VIOLATION",
            "REPO_ROOT_VIOLATION",
            "PURE_ASSERTION_VIOLATION",
            "PURE_SHIM_VIOLATION",
            "FOREIGN_CHANGE_VIOLATION",
            "NOTHING_TO_COMMIT",
        ],
        "auto_enqueue": False,
        "prescription_zh": "读 GUIDE 锚点处方后同参重跑；FOREIGN_CHANGE 必带 --adopt-prior-work；"
        "门链非六门阻断/precommit 通道阻断/reconciler block_next 硬闸均落此码",
    },
    {
        "code": 2,
        "statuses": ["LOCK_TIMEOUT", "STASH_CONFLICT"],
        "auto_enqueue": True,
        "prescription_zh": "仅 LOCK_TIMEOUT 支自动改道（前置=非 --no-auto-enqueue ∧ 非 --reconciler-verify "
        "∧ 非 --merge-finalize ∧ flag commit_queue_interactive ON）；"
        "STASH_CONFLICT 支零生产者=D11-G01；argparse 解析失败亦 SystemExit(2)",
    },
    {
        "code": 3,
        "statuses": ["PROMOTION_BLOCKED"],
        "auto_enqueue": False,
        "prescription_zh": "--allow-promote（前置=creation_token 已登记）；gate=FILE-PLACEMENT-TTL 且 detail 前缀命中",
    },
    {
        "code": 4,
        "statuses": ["SSOT_VIOLATION"],
        "auto_enqueue": False,
        "prescription_zh": "不可达码（全仓零生产者=D11-G01 死分支）；语义处方=扩已有文件而非新建",
    },
    {
        "code": 5,
        "statuses": ["HELD_OVERLAP_VIOLATION"],
        "auto_enqueue": False,
        "prescription_zh": "--allow-overlap（前置=67 号冲突三分法判定；滚动 24h 热文件超阈会被 O2 二次阻断）",
    },
    {
        "code": 6,
        "statuses": ["CLAIM_REQUIRED_VIOLATION"],
        "auto_enqueue": False,
        "prescription_zh": "先 claim_files（或 --claim-only）；同码第二义=--release-only 回读仍有持有",
    },
    {
        "code": 7,
        "statuses": [],
        "auto_enqueue": False,
        "prescription_zh": "claim-only 部分文件被他人持有（纯 claim 快速路径，不经 gateway.commit，无状态枚举）",
    },
    {
        "code": 8,
        "statuses": ["WORKTREE_VIOLATION"],
        "auto_enqueue": False,
        "prescription_zh": "双义：①WORKTREE_VIOLATION→--allow-non-worktree；②P0-A 锁外预检 blocking→按清单给旗，"
        "诊断可 --skip-preflight（锁内仍全套照跑）",
    },
    {
        "code": 9,
        "statuses": ["COMMIT_SCOPE_VIOLATION"],
        "auto_enqueue": False,
        "prescription_zh": "--allow-multi-domain（gate+自家测试同批合法）",
    },
    {
        "code": 10,
        "statuses": ["MERGE_IN_PROGRESS"],
        "auto_enqueue": False,
        "prescription_zh": "--merge-finalize（预检自动跳过）；非本人 merge→等待或升级 Owner；"
        "gateway 三处判定（锁外/锁内 TOCTOU 复检/无锁降级路径）",
    },
]

# 机生挂载点：哪些节点吃哪些扫描面
_API_NODES = {nid: spec["api"] for nid, spec in N.items() if spec.get("api")}
_GATE_FACT_NODES = {nid: spec["gate_facts"] for nid, spec in N.items() if spec.get("gate_facts")}
_QUEUE_STATE_NODES = [nid for nid, spec in N.items() if spec.get("queue_states")]

_QUEUE_STATES = ("pending", "processing", "done", "dead")
_GATEWAY_REL = _GW


# ---------------------------------------------------------------------------
# 机生层扫描（全部只读；禁写禁删禁调 commit_queue.py status/drain——触发自举排空）
# ---------------------------------------------------------------------------


def scan_public_api(root: Path, rel_path: str) -> dict[str, Any]:
    """AST 扫单脚本顶层公共函数与 main() 退出码面（可执行真相源，零手工清单）。"""
    p = root / rel_path
    out: dict[str, Any] = {"path": rel_path, "exists": p.exists()}
    if not out["exists"]:
        return out
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    pub = sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_"))
    codes: set[int] = set()
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "main":
            for sub in ast.walk(n):
                if (
                    isinstance(sub, ast.Return)
                    and isinstance(sub.value, ast.Constant)
                    and isinstance(sub.value.value, int)
                ):
                    codes.add(sub.value.value)
    out["public_functions"] = pub
    out["main_exit_codes"] = sorted(codes)
    return out


def scan_gate_registry(root: Path, rel_path: str) -> dict[str, Any]:
    """读门禁册：total_gates 字段与 gates 条目实数（双口径并列呈现，勿手改其一）。

    L2 gate_cluster 来源：shell 册按 enforcement_channel 分簇实扫（commit-gate/pre-commit/manual）
    + own_scope 机生字段 True 计数；in-process 册按 files_trigger 条件触发面计数。
    只取计数与簇名，条目正文一律不入图（INV-1）。
    """
    p = root / rel_path
    out: dict[str, Any] = {"registry": rel_path, "exists": p.exists()}
    if not out["exists"]:
        return out
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    gates = data.get("gates") or []
    out["total_gates_field"] = data.get("total_gates")
    out["entries_scanned"] = len(gates) if isinstance(gates, list) else None
    out["generated_by"] = data.get("generated_by")
    if isinstance(gates, list):
        channels: dict[str, int] = {}
        own_scope_true = 0
        files_trigger_true = 0
        for e in gates:
            if not isinstance(e, dict):
                continue
            ch = str(e.get("enforcement_channel") or "unspecified")
            channels[ch] = channels.get(ch, 0) + 1
            if e.get("own_scope"):
                own_scope_true += 1
            if e.get("files_trigger"):
                files_trigger_true += 1
        out["cluster_by_channel"] = {k: channels[k] for k in sorted(channels)}
        out["own_scope_true_entries"] = own_scope_true
        out["files_trigger_entries"] = files_trigger_true
    return out


def _assign_target_name(node: ast.AST) -> str | None:
    """取赋值语句左值名（Assign/AnnAssign 两形态；非赋值/解构返回 None）。"""
    if isinstance(node, ast.Assign) and node.targets:
        return getattr(node.targets[0], "id", None)
    if isinstance(node, ast.AnnAssign):
        return getattr(node.target, "id", None)
    return None


def scan_commit_exit_map(root: Path) -> dict[str, Any]:
    """AST 扫 git_commit.py 的 CommitStatus→exit_code 查表面（全谱矩阵的机生半边）。"""
    out: dict[str, Any] = {
        "source": f"{_CLI}:_COMMIT_RESULT_MAP",
        "exists": False,
        "map_entries": {},
        "default_exit_code": None,
    }
    p = root / _CLI
    if not p.exists():
        return out
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    for node in tree.body:
        name = _assign_target_name(node)
        value = getattr(node, "value", None)
        if name == "_COMMIT_RESULT_MAP" and isinstance(value, ast.Dict):
            for k, v in zip(value.keys, value.values, strict=True):
                status = getattr(k, "attr", None)
                if (
                    status
                    and isinstance(v, ast.Tuple)
                    and v.elts
                    and isinstance(v.elts[0], ast.Constant)
                    and isinstance(v.elts[0].value, int)
                ):
                    out["map_entries"][str(status)] = v.elts[0].value
            out["exists"] = True
        elif (
            name == "_COMMIT_RESULT_DEFAULT"
            and isinstance(value, ast.Tuple)
            and value.elts
            and isinstance(value.elts[0], ast.Constant)
        ):
            out["default_exit_code"] = value.elts[0].value
    return out


def scan_commit_status_producers(root: Path) -> dict[str, int]:
    """全仓 `status=CommitStatus.X` 生产者构造计数（死分支的机生判据，零手工清单）。

    专码有分发表条目却零生产者 = 不可达分支（作业簿 04 溢出 O-C1/O-C2 的机器化口径）；
    tests/ 排除（测试构造≠生产路径生产者）。
    """
    names = sorted({s for s in scan_commit_exit_map(root).get("map_entries") or {}})
    counts = {n: 0 for n in names}
    if not names:
        return counts
    pats = {n: re.compile(r"status\s*=\s*CommitStatus\." + n + r"\b") for n in names}
    for base in ("src", "scripts"):
        for py in (root / base).rglob("*.py"):
            rel = py.relative_to(root).as_posix()
            if "test" in rel.lower():
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for n, pat in pats.items():
                counts[n] += len(pat.findall(text))
    return counts


def scan_dead_marker_counts(root: Path) -> dict[str, Any]:
    """死因三分类标记表条数（AST 取元组元素数；标记串条目=叶层，只计数不进图，INV-1）。"""
    out: dict[str, Any] = {"source": _CQ, "exists": False}
    p = root / _CQ
    if not p.exists():
        return out
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not node.targets:
            continue
        tname = getattr(node.targets[0], "id", "")
        if tname in ("_DEAD_REASON_ENV_MARKERS", "_DEAD_REASON_ITEM_MARKERS") and isinstance(node.value, ast.Tuple):
            out[tname] = len(node.value.elts)
    out["exists"] = all(k in out for k in ("_DEAD_REASON_ENV_MARKERS", "_DEAD_REASON_ITEM_MARKERS"))
    return out


def scan_reconciler_registrations(root: Path) -> int:
    """post-commit reconciler 登记面：网关 register( 调用动态计数（骨架 §7 复核命令同口径）。"""
    text = (root / _GATEWAY_REL).read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"self\._reconciliation_registry\.register\(", text))


def scan_queue_states(root: Path) -> dict[str, Any]:
    """.runtime/commit_queue 四态目录只读计数（worktree/CI 无该面=exists false，非错误）。"""
    states: dict[str, Any] = {}
    for st in _QUEUE_STATES:
        d = root / ".runtime" / "commit_queue" / st
        exists = d.is_dir()
        states[st] = {"exists": exists, "item_count": len(list(d.iterdir())) if exists else 0}
    return states


def scan_precommit_flag_pair(root: Path) -> dict[str, Any]:
    """precommit 通道回滚面机生扫：代码读键 vs flags.yaml 在册键（gap D11-G02 的机器证据）。"""
    out: dict[str, Any] = {"code_key": None, "registered": None, "in_roster": False, "default_on": None}
    gw = root / _GW
    if gw.exists():
        m = re.search(r'^_PRECOMMIT_RUN_FLAG\s*=\s*"([^"]+)"', gw.read_text(encoding="utf-8", errors="replace"), re.M)
        out["code_key"] = m.group(1) if m else None
        out["default_on"] = (
            bool(
                re.search(
                    r"is_enabled\(_PRECOMMIT_RUN_FLAG,\s*default=True\)",
                    gw.read_text(encoding="utf-8", errors="replace"),
                )
            )
            if out["code_key"]
            else None
        )
    fp = root / "config" / "flags.yaml"
    keys: list[str] = []
    if fp.exists():
        try:
            data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001 — 册不可解析=本面降级（不炸生成）
            data = {}
        for block in ("flags", "global_flags"):
            v = data.get(block) if isinstance(data, dict) else None
            if isinstance(v, dict):
                keys.extend(str(k) for k in v)
    out["roster_keys_scanned"] = len(keys)
    if out["code_key"]:
        out["in_roster"] = out["code_key"] in keys
        out["registered"] = out["in_roster"]
    return out


def load_blood_mount(root: Path) -> dict[str, Any]:
    """挂血肉四字段装载：F5 四件 + 总筹 addendum → 节点级聚合（INV-1：图内只渲染直方图/计数/指针）。

    缺任一输入件=FileNotFoundError 硬失败——四字段层是挂图SOP §6「看得懂验收」三样之一，
    缺件静默降级会让图看似挂满实则空壳（与 build_semantic_layers 的 missing_exec 同级防自粉饰）。
    """

    def _load(rel: str) -> dict[str, Any]:
        """_load implementation."""
        p = root / rel
        if not p.is_file():
            raise FileNotFoundError(f"挂血肉输入件缺失: {rel}（commitmap_cure 战役件；缺件=四字段层不可生成）")
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    purpose_doc = _load(_F5_PURPOSE)
    casebooks_doc = _load(_F5_CASEBOOKS)
    trigger_doc = _load(_F5_TRIGGER)
    consumers_doc = _load(_F5_CONSUMERS)
    addendum = _load(_CHIEF_ADDENDUM)

    legend = [
        {"ordinal": lb.get("ordinal"), "label_name": lb["label_name"], "one_liner": lb["one_liner"]}
        for lb in purpose_doc.get("labels") or []
    ]
    if not legend:
        raise ValueError(f"目的标签图例为空: {_F5_PURPOSE} labels 节")
    label_names = {lb["label_name"] for lb in legend}
    if len(label_names) != len(legend):
        raise ValueError("目的标签图例存在重名标签（SOP §2 规4：说不出一句话的标签回炉）")

    gate_label: dict[str, tuple[str, str]] = {}
    for g in purpose_doc.get("gates") or []:
        if g["gate_id"] in gate_label:
            raise ValueError(f"F5 标签映射重复登记门禁: {g['gate_id']}")
        if g["label_name"] not in label_names:
            raise ValueError(f"F5 标签映射用了图例外标签: {g['gate_id']} -> {g['label_name']}")
        gate_label[g["gate_id"]] = (g["label_name"], g["node_id"])
    addendum_gates = addendum.get("gates") or {}
    for gid, spec in addendum_gates.items():
        if gid in gate_label:
            raise ValueError(f"addendum 与 F5 重复登记门禁: {gid}")
        if spec["label_name"] not in label_names:
            raise ValueError(f"addendum 用了图例外标签: {gid} -> {spec['label_name']}")
        gate_label[gid] = (spec["label_name"], spec["node_id"])

    trig_by_gate = {row["gate_id"]: row for row in trigger_doc.get("facts") or []}
    cons_by_gate = {row["gate_id"]: row for row in consumers_doc.get("aggregates") or []}
    # addendum 台位并入 facts 池（consumers 未抽取=null 显式留缺，随门禁身份一本账收敛批补）
    for gid, spec in addendum_gates.items():
        trig_by_gate[gid] = {
            "gate_id": gid,
            "trigger_count": spec.get("trigger_count"),
            "zero_trigger_candidate": False,
            "evidence": spec.get("evidence"),
        }
        cons_by_gate[gid] = {"gate_id": gid, "consumer_count": None, "top_consumers": []}

    known_nodes = set(NODE_ORDER)
    purpose_hist: dict[str, dict[str, int]] = {}
    trig_by_node: dict[str, dict[str, Any]] = {}
    cons_by_node: dict[str, dict[str, Any]] = {}
    zero_gates: list[str] = []
    for gid, (lname, nid) in gate_label.items():
        if nid not in known_nodes:
            raise ValueError(f"挂载环节越出契约全集: {gid} -> {nid}（增枝须先回写骨架 §1）")
        hist = purpose_hist.setdefault(nid, {})
        hist[lname] = hist.get(lname, 0) + 1
        tf = trig_by_gate.get(gid) or {}
        tn = trig_by_node.setdefault(nid, {"gates": 0, "total_triggers_30d": 0, "zero_trigger_gates": []})
        tn["gates"] += 1
        tn["total_triggers_30d"] += int(tf.get("trigger_count") or 0)
        if tf.get("zero_trigger_candidate"):
            zero_gates.append(gid)
            tn["zero_trigger_gates"].append(gid)
        cn = cons_by_node.setdefault(nid, {"gates": 0, "gates_with_consumers": 0, "sample_consumers": []})
        cn["gates"] += 1
        cg = cons_by_gate.get(gid) or {}
        if cg.get("consumer_count"):
            cn["gates_with_consumers"] += 1
        for name in cg.get("top_consumers") or []:
            if name not in cn["sample_consumers"]:
                cn["sample_consumers"].append(name)
        cn["sample_consumers"] = cn["sample_consumers"][:8]

    casebooks_by_node: dict[str, list[str]] = {}
    for nid, row in (casebooks_doc.get("nodes") or {}).items():
        if nid not in known_nodes:
            raise ValueError(f"casebooks 挂载环节越出契约全集: {nid}")
        casebooks_by_node[nid] = list(row.get("casebooks") or [])
    books = sorted({ptr.split("#", 1)[0] for ptrs in casebooks_by_node.values() for ptr in ptrs})

    return {
        "legend": legend,
        "purpose_hist": purpose_hist,
        "casebooks_by_node": casebooks_by_node,
        "casebooks_unmounted": dict(casebooks_doc.get("unmounted_note") or {}),
        "trig_by_node": trig_by_node,
        "cons_by_node": cons_by_node,
        "books": books,
        "gates_mounted": len(gate_label),
        "addendum_gates": sorted(addendum_gates),
        "zero_gates_total": sorted(zero_gates),
        "sources": [_F5_PURPOSE, _F5_CASEBOOKS, _F5_TRIGGER, _F5_CONSUMERS, _CHIEF_ADDENDUM],
    }


def build_machine_facts(root: Path) -> dict[str, Any]:
    """一次全扫产出 {node_id: machine_facts} + 顶层 machine 计数块。"""
    facts: dict[str, Any] = {}
    for nid, rel in _API_NODES.items():
        facts[nid] = {"public_api": scan_public_api(root, rel)}
    for nid, reg in _GATE_FACT_NODES.items():
        facts.setdefault(nid, {})["gate_registry_facts"] = scan_gate_registry(root, reg)
    try:
        reconciler_calls = scan_reconciler_registrations(root)
    except OSError:
        reconciler_calls = -1
    facts.setdefault("D11-C11", {})["reconciler_register_calls"] = reconciler_calls
    qs = scan_queue_states(root)
    for nid in _QUEUE_STATE_NODES:
        facts.setdefault(nid, {})["queue_state_dirs"] = qs
    # L2 退出码全谱机生半边：分发表 + 生产者构造计数 ⇒ 死分支（gap D11-G01 输入）
    exit_map = scan_commit_exit_map(root)
    producers = scan_commit_status_producers(root)
    dead = sorted(s for s in (exit_map.get("map_entries") or {}) if producers.get(s) == 0)
    exit_face = {"commit_exit_map": exit_map, "exit_code_producers": producers, "dead_branch_statuses": dead}
    facts.setdefault("D11-C01", {}).update(exit_face)
    facts.setdefault("D11-G01", {}).update(exit_face)
    # gap D11-G02：flag 键同名性机生扫
    facts.setdefault("D11-G02", {})["precommit_flag_pair"] = scan_precommit_flag_pair(root)
    # L2 deadletter_class 机生半边：两标记表条数（只计数，串条目=叶层不进图，INV-1）
    facts.setdefault("D11-D02", {})["deadletter_marker_counts"] = scan_dead_marker_counts(root)
    return facts


def build_semantic_layers(
    module_index: dict[str, str],
    skeleton_status: dict[str, str],
) -> tuple[list[dict], list[dict]]:
    """layers（三车道层位）与 nodes（28 环节 + 2 gap 节点语义层，不含 machine_facts）。"""
    layers = [
        {
            "layer_id": "S",
            "name_zh": "会话车道",
            "span_zh": "起=对话启动（冷启动序列）；止=会话注销",
            "handoff_zh": "S06 worktree 内 commit 经 S07 merge 进主区后，收尾批再过正门则入提交车道；"
            "S09 handoff 是跨会话状态交接唯一格式真源（骨架 §2）",
        },
        {
            "layer_id": "C",
            "name_zh": "提交车道",
            "span_zh": "起=任何通道的提交请求；止=done/ 回填+归属核实",
            "handoff_zh": "C10 落盘失败→死信车道；C11 reconciler 产 commit 又触发 C12 机器车道（已声明反馈环）",
        },
        {
            "layer_id": "D",
            "name_zh": "死信车道",
            "span_zh": "起=C10 失败判定；止=requeue 回 pending 或留 dead/ 终态",
            "handoff_zh": "D04 回 C08 入队（新 qid）；D03 出域到 task_board（任务治理域，引用不吸收）",
        },
    ]
    build_status_zh = get_category_map("build_status")
    missing_exec = [nid for nid in NODE_ORDER if nid not in EXEC and not N[nid].get("gap")]
    if missing_exec:  # production 节点缺复跑证据=生成期硬失败（不产出自粉饰的图）
        raise KeyError(f"EXEC 缺环节（production 节点必带 exec_evidence）: {missing_exec}")
    nodes: list[dict] = []
    for nid in NODE_ORDER:
        spec = N[nid]
        # 三态口径唯一同源=骨架 §1 实扫（查无回落本件契约常量）；✅→production、其余→structure
        status = skeleton_status.get(nid) or spec["status"]
        is_gap = bool(spec.get("gap"))
        build_status = "built" if status == "✅" else "partial"
        # gap 节点不在骨架三态表内，其断言面只有"这条映射/这个键存在"＝structure（永不 production）
        verified_scope = "structure" if is_gap else ("production" if status == "✅" else "structure")
        lane = _GAP_LANE.get(nid) or nid.split("-")[1][0]
        ref = spec.get("ref")
        rel = _anchor_rel(ref) if ref else None
        module_id = module_index.get(rel) if rel else None
        if is_gap:
            docs = sorted(
                {
                    f"{_SKELETON} §6 封顶声明（骨架外 gap 件）",
                    f"{_BOOK_DIR}/{_GAP_BOOK_OF[nid]}",
                    "docs/_working/map_build/03_final_blueprint_and_schema.md §4 图11 判据②",
                }
            )
        else:
            docs = sorted({f"{_SKELETON} §1 {nid}", f"{_BOOK_DIR}/{_BOOK_OF[nid[4:]]}"})
        node = {
            "node_id": nid,
            "name_zh": spec["name"],
            "stage": lane,
            "lane": lane,
            "node_type": "gap" if is_gap else "stage",
            "decision_question": spec["q"],
            "note_zh": spec["mech"],
            "build_status": build_status,
            "build_status_zh": build_status_zh.get(build_status, build_status),
            "confidence": "verified",
            "verified_scope": verified_scope,
            "evidence": sorted(spec.get("ev", [])),
            "exec_evidence": sorted(EXEC.get(nid, [])),
            "module_id": module_id,
            "module_ref": ref,
            "source_anchors": list(spec.get("anc", [])),
            "runtime_refs": list(spec.get("run", [])),
            "data_refs": list(spec.get("data", [])),
            "gate_refs": list(spec.get("gates", [])),
            "store_refs": list(spec.get("stores", [])),
            "doc_refs": docs,
            "wiring_status": WIRING.get(nid, "wired"),
        }
        red = spec.get("red") or RED.get(nid)
        if red:
            node["red_reason"] = red
        if nid in XCODES:
            node["exit_codes"] = list(XCODES[nid])
        if nid in GCLUSTER:
            node["gate_cluster"] = GCLUSTER[nid]
        if nid in DLC:
            node["deadletter_class"] = list(DLC[nid])
        if ref:
            node["module_label_bilingual"] = anchor_label_bilingual(rel)
        nodes.append(node)
    return layers, nodes


def _anchor_rel(ref: str) -> str:
    """_anchor_rel implementation."""
    return str(ref).rsplit(":", 1)[0] if str(ref).rsplit(":", 1)[-1].isdigit() else str(ref)


def build_document(as_of: str, root: Path) -> dict[str, Any]:
    """组装图文档：人工语义层 ⊕ 机生 machine_facts（结构契约见校验器 validate_structure）。"""
    module_index = scan_module_id_index(root)
    skeleton_status = scan_skeleton_status(root)
    layers, nodes = build_semantic_layers(module_index, skeleton_status)
    facts = build_machine_facts(root)
    for node in nodes:
        mf = facts.get(node["node_id"])
        if mf:
            node["machine_facts"] = mf
    # 挂血肉四字段（挂图SOP §4）：gap 节点四字段=null（无机制可挂）；机制级映射=叶层留输入件（INV-1）
    blood = load_blood_mount(root)
    for node in nodes:
        if node["node_type"] == "gap":
            node["purpose_tags"] = None
            node["casebooks"] = None
            node["trigger_facts"] = None
            node["consumers"] = None
            continue
        nid = node["node_id"]
        node["purpose_tags"] = blood["purpose_hist"].get(nid, {})
        node["casebooks"] = blood["casebooks_by_node"].get(nid, [])
        node["trigger_facts"] = blood["trig_by_node"].get(
            nid, {"gates": 0, "total_triggers_30d": 0, "zero_trigger_gates": []}
        )
        node["consumers"] = blood["cons_by_node"].get(
            nid, {"gates": 0, "gates_with_consumers": 0, "sample_consumers": []}
        )
    edges = [list(e) for e in EDGES]
    lane_dist = {"S": 0, "C": 0, "D": 0}
    type_dist: dict[str, int] = {}
    scope_dist: dict[str, int] = {}
    wiring_dist: dict[str, int] = {}
    for node in nodes:
        lane_dist[node["lane"]] = lane_dist.get(node["lane"], 0) + 1
        type_dist[node["node_type"]] = type_dist.get(node["node_type"], 0) + 1
        scope_dist[str(node["verified_scope"])] = scope_dist.get(str(node["verified_scope"]), 0) + 1
        wiring_dist[node["wiring_status"]] = wiring_dist.get(node["wiring_status"], 0) + 1
    exit_face = facts.get("D11-G01", {})
    inproc_facts = facts.get("D11-C05", {}).get("gate_registry_facts") or {}
    shell_facts = facts.get("D11-C07", {}).get("gate_registry_facts") or {}
    marker_counts = facts.get("D11-D02", {}).get("deadletter_marker_counts") or {}
    skeleton_counts: dict[str, int] = {}
    for sym in skeleton_status.values():
        skeleton_counts[sym] = skeleton_counts.get(sym, 0) + 1
    doc = {
        "schema_version": "0.3",
        "map_id": "dev_delivery_map",
        "name_zh": "交付流水线全景图",
        "nickname": "交付流水线",
        "effective_from": "2026-09-24",  # 骨架 §6 封顶日（人工层常量，非运行时取时）
        "markets": ["cn_a"],
        "generator": "scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py",
        "generated_at": as_of,
        "ssot_note_zh": (
            "骨架人工语义层（环节名/decision_question/laws/boundary/边/反馈环/L2 退出码处方列）契约真源="
            "docs/_working/map_build/fig11_delivery/00_skeleton.md（§6 封顶 28 环节）+ 八本作业簿（exec_evidence "
            "口径真源=各簿 §末-3 实查命令）；machine_facts 层每次全量重扫可执行真相源（门禁册/reconciler 登记面/"
            "四脚本 AST 面/队列四态目录只读计数/退出码分发表与生产者构造/骨架三态列/depgraph 在册 module_id 投影面），"
            "禁手工维护。节点只存稳定标识符与指针，禁复制条目正文（INV-1）。\n"
            "字段分层（六图终局卷 §1 裁定一）：L0 通用层统一名 note_zh/doc_refs（三个同义异名注解字段与"
            "两个 doc 指针别名已废止，残留由校验器 CV-L0 判红）；"
            "L1 纵轴层本图取用 wiring_status/red_reason/doc_refs/exec_evidence/"
            "purpose_tags/casebooks/trigger_facts/consumers（后四=挂图SOP §4 四标准字段：输入件=commitmap_cure 战役 "
            "f5 四件+总筹 addendum，缺件生成器硬失败；标签图例=purpose_labels 节；机制级 gate→标签/环节映射=叶层"
            "留输入件不进图本体，图内只渲染节点直方图；gap 节点四字段=null 无机制可挂）；"
            "L2 图专属层字段清单=exit_codes（提交门退出码全谱：顶层矩阵+节点级专码归属）、"
            "gate_cluster（门禁簇归属）、deadletter_class（死信分类归属）。\n"
            "双轴口径（六图终局卷 §3）：verified_scope=production ⇔ 骨架 §1 状态列 ✅（26 个，多了算谎少了算欠），"
            "structure=仅结构性事实已核（2 个 🔨 环节 + 2 个 gap 节点）；本生成器不擅改任何判据。\n"
            "gap 节点 D11-G01/G02 是骨架外显性化缺口件（六图终局卷 §4 图11 判据②，作业簿 04/05 溢出实测），"
            "待总包回写骨架 §1；两节点无运行代码可挂 ⇒ module_id=null + red_reason 必填。"
        ),
        "laws": list(LAWS),
        "boundary": list(BOUNDARY),
        "layers": layers,
        "purpose_labels": {
            "law_zh": (
                "目的标签=挂图SOP §2 横切轴：11 条=00_design_basis §1 冻结表（Owner 终审），"
                "12 号「别把钥匙留在门口」=裁定#480 批准增设；冻结后机贴不改名"
            ),
            "machine_input": _F5_PURPOSE,
            "mount_rule_zh": (
                "标签贴在机制上：门禁级 gate→标签/环节映射=叶层（f5_purpose_tags.yaml+chief_purpose_addendum.yaml，"
                "INV-1 不进图本体）；图内渲染=节点 purpose_tags 直方图——同标签多钉=重复簇显影位（内收对审入口）"
            ),
            "legend": blood["legend"],
        },
        "casebooks_index": {
            "law_zh": "病历挂载=挂图SOP §3：只挂本（册码#章码指针）不挂病例；完备性铁律=每本永久病历本 ≥1 环节",
            "machine_input": _F5_CASEBOOKS,
            "books": blood["books"],
            "gap_unmounted_note_zh": "D11-G01/G02=骨架外缺口件无运行代码可挂（F4 §0 显式不挂注记）",
        },
        "exit_codes": {
            "owner_node": "D11-C01",
            "law_zh": "退出码是全车道共用的机器契约：改分发表=改契约，须经本矩阵穷举并进"
            "commit_navigation_playbook 指路面（作业簿 04 §1）",
            "machine": {
                "commit_exit_map": exit_face.get("commit_exit_map"),
                "producer_construction_counts": exit_face.get("exit_code_producers"),
                "dead_branch_statuses": exit_face.get("dead_branch_statuses"),
                "dead_branch_pointer": "D11-G01",
            },
            "matrix": [dict(r) for r in EXIT_MATRIX],
        },
        "gate_cluster": {
            "in_process": {
                "registry": inproc_facts.get("registry"),
                "total_gates_field": inproc_facts.get("total_gates_field"),
                "entries_scanned": inproc_facts.get("entries_scanned"),
                "files_trigger_entries": inproc_facts.get("files_trigger_entries"),
                "note_zh": "priority 真源在代码 GateSpec、own_scope 册面无此字段（作业簿 05 溢出 O-C12）",
            },
            "shell": {
                "registry": shell_facts.get("registry"),
                "total_gates_field": shell_facts.get("total_gates_field"),
                "entries_scanned": shell_facts.get("entries_scanned"),
                "by_enforcement_channel": shell_facts.get("cluster_by_channel"),
                "own_scope_true_entries": shell_facts.get("own_scope_true_entries"),
                "generated_by": shell_facts.get("generated_by"),
                "note_zh": "字段值与条目实数双口径并列（total_gates 落后于列表=册内漂移，由生成器 --check 管）",
            },
            "two_channel_overlap_note_zh": "in-process ∩ pre-commit 实测=1 台（GATE-VOCAB 双执行），"
            "生成器注释「交集 0」已过期（作业簿 05 溢出 O-C10）",
        },
        "deadletter_class": {
            "classify_enum": ["env", "item", "other"],
            "special_branches": [
                "LandingEnvironmentError→退回 pending 绝不死信（env 面）",
                "cascade_stale→死信候选不消耗 landing（item 面）",
                "BaseException→留 processing 等孤儿回收（不分入三类）",
            ],
            "disposal_trichotomy_zh": "superseded / 真未落地 / 历史留档（清零战役三分法，D06 归档维度）",
            "marker_table_anchor": f"{_CQ}:242 / {_CQ}:274（标记串条目=叶层进作业簿 08，图只挂表位置指针）",
            "machine": {"marker_counts": marker_counts},
        },
        "nodes": nodes,
        "edges": edges,
        "feedback_loops": [dict(fl) for fl in FEEDBACK_LOOPS],
        "counts": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "by_lane": {k: lane_dist[k] for k in sorted(lane_dist)},
            "by_node_type": {k: type_dist[k] for k in sorted(type_dist)},
            "by_verified_scope": {k: scope_dist[k] for k in sorted(scope_dist)},
            "by_wiring_status": {k: wiring_dist[k] for k in sorted(wiring_dist)},
            "blood": {
                "purpose_labels": len(blood["legend"]),
                "gates_mounted": blood["gates_mounted"],
                "addendum_gates": len(blood["addendum_gates"]),
                "zero_trigger_candidate_gates": len(blood["zero_gates_total"]),
                "casebooks_books": len(blood["books"]),
                "nodes_with_casebooks": sum(1 for v in blood["casebooks_by_node"].values() if v),
                "sources": list(blood["sources"]),
            },
            "machine": {
                "reconciler_register_calls": facts.get("D11-C11", {}).get("reconciler_register_calls"),
                "in_process_gate_facts": inproc_facts,
                "shell_gate_facts": shell_facts,
                "queue_state_dirs": facts.get("D11-C13", {}).get("queue_state_dirs"),
                "deadletter_marker_counts": marker_counts,
                "skeleton_status_scan": {
                    "source": _SKELETON,
                    "nodes_scanned": len(skeleton_status),
                    "by_symbol": {k: skeleton_counts[k] for k in sorted(skeleton_counts)},
                },
                "module_id_scan": {
                    "source": _PATH_OWNERSHIP,
                    "claims_scanned": len(module_index),
                    "nodes_with_module_id": sum(1 for n in nodes if n.get("module_id")),
                    "nodes_with_module_ref": sum(1 for n in nodes if n.get("module_ref")),
                    "nodes_null_module_id": sum(1 for n in nodes if not n.get("module_id")),
                },
            },
        },
    }
    return doc


_MAP_HEADER = (
    "# 交付流水线全景图（dev_delivery_map，图 11）——由 generate_dev_delivery_map.py 机生。\n"
    "# 本文件禁手改后不回生成（counts 一致性校验判红）；环节契约真源="
    "docs/_working/map_build/fig11_delivery/00_skeleton.md。\n"
    "# 节点只存稳定标识符与指针（INV-1）；machine_facts 层重扫即刷新，人工语义层改动须先回写骨架。\n"
)


def serialize_document(doc: dict[str, Any]) -> str:
    """确定性序列化（键序=插入序，禁 sort_keys 打乱语义分组）——幂等实证的落点。"""
    return serialize_map_document(doc, _MAP_HEADER)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="交付流水线全景图（图 11）生成器（机生优先，幂等）")
    ap.add_argument(
        "--as-of", default=None, help="generated_at 注入值（ISO 字面串）；缺省=HEAD 提交时间派生；禁运行时取时"
    )
    ap.add_argument("--out", default=str(OUTPUT_PATH), help="产出路径（默认 config/dev_delivery_map.yaml）")
    ap.add_argument("--root", default=str(_REPO_ROOT), help="扫描根（默认仓库根；worktree 内跑=worktree 根）")
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要，零写入")
    args = ap.parse_args()

    root = Path(args.root)
    as_of = args.as_of or head_commit_time(root)
    doc = build_document(as_of=as_of, root=root)
    if args.dry_run:
        print(
            f"dry-run: nodes={doc['counts']['total_nodes']} edges={doc['counts']['total_edges']} "
            f"lane={doc['counts']['by_lane']} generated_at={as_of} "
            f"blood=gates_mounted:{doc['counts']['blood']['gates_mounted']} "
            f"labels:{doc['counts']['blood']['purpose_labels']} "
            f"casebooks_books:{doc['counts']['blood']['casebooks_books']}"
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


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 本件=离线机生器（六图族）——对齐台/人工显式触发再生产物，非 cron/daemon/常驻服务；判据面由 validators+对抗尺承载（同款豁免先例=generate_connection_matrix.py:1480, 8454beec5a）
    sys.exit(main())
