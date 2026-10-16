# [BLUEPRINT] MOD-TDMGOAL | docs/03_modules/_domain_gov_enforcement/blueprint.md
# [MODULE] scripts.governance.tdm_goal_blocks
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] config/trading_decision_map.yaml; docs/03_modules/_domain_backtest/exam_cards/;
#   zephyr.shared.io.file_utils
# [CONSUMERS] Q6 goal_readiness 生成器（读 goal 块算就绪度）; Q7 开班令目标块 gate（读族表口径）;
#   align_all 对齐族（goal 块完整性探针）; 人工 CLI（--check 漂移巡检）
# [STARTUP] imported（CLI manual 面＋事件触发面双形态——PERMANENT-SYSTEM-TRIGGER 合规）
# [MATURITY] experimental
# [INVARIANTS] TDM yaml 是手写真源：goal 块注入=节点块尾外科插入（禁整文件重排——
#   writeback_exam_confidence 同款纪律）；写必经 safe_write_text CAS；写后必过
#   yaml.safe_load 校验＋节点数守恒断言（186/151 口径见 CORE_DENOMINATOR 注释）；
#   挂起节点（30 源线＋4 币圈＋V2）goal.status=suspended 且带 suspension_basis；
#   幂等：重跑剥旧 goal 块再插新（--inject）；--check 零写。
# [MODIFY-GUARD] tests/gov/governance/scripts_governance/test_tdm_goal_blocks.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError: 节点块定位失败/写后校验失败/CAS 冲突/SystemExit(check 漂移 exit 2)
# [TESTS] tests/gov/governance/test_tdm_goal_blocks.py
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入 → 族判定 → 期望块生成 → 文本外科 → CAS 写 → 校验
# - 输入: config/trading_decision_map.yaml + exam_cards glob 计数
# - 族判定: _family_for(node_id) 前缀规则表（FAMILY_TABLE v0）
# - 期望块: family→(goal_statement/output_contract/exam_ref/campaign_ref/status)
# - 文本外科: 节点块=「- node_id:」行至下一块/段尾；剥旧 goal: 子块→插块尾
# - CAS 写: safe_write_text(expected_base_sha256)；校验: safe_load+计数+goal 完整性

"""TDM goal 块注入器＋漂移探针（Q5，裁定#516）。

用法：
  python scripts/governance/tdm_goal_blocks.py --stats            # 族分布/goal 覆盖统计（零写）
  python scripts/governance/tdm_goal_blocks.py --check            # 漂移判定（零写；漂移 exit 2）
  python scripts/governance/tdm_goal_blocks.py --inject           # dry-run 预览
  python scripts/governance/tdm_goal_blocks.py --inject --yes     # 落盘（CAS＋写后校验）
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

import yaml

# SSoT-REDEFINITION 处方（q-0037 死因治本）：REPO_ROOT 唯一真源=canonical
# zephyr.shared.io.paths，禁本模块重定义；worktree 语义经 ZEPHYR_WORKTREE_ROOT
# 显式注入（canonical 内建感知），未注入时=主仓根。
from zephyr.shared.io.paths import REPO_ROOT

TDM_PATH = REPO_ROOT / "config" / "trading_decision_map.yaml"
EXAM_CARD_GLOB = "docs/03_modules/_domain_backtest/exam_cards/**/*.yaml"

# ── 分母口径（Q2 批准 151，本工具机械复现）───────────────────────────
# 186 全节点 − 30 源线身份节点（TDM-E-L9-A##/B##/C##，tags+id 双证）
#         − 4 币圈骨架（TDM-C-L*）
#         − 1 AGG（TDM-E-L9-AGG 知识供给汇聚＝机生读数引用型节点，
#           调研档 §2"31 个 L9 源线身份节点"的第 31 个）
#         = 151 核心决策节点。若 Owner 改口径纳 AGG → 152（P1 待裁追认项，默认 151）。
RE_SRC_LINE = re.compile(r"^TDM-E-L9-(A\d{2}|B\d{2}|C\d{2})$")
RE_CRYPTO = re.compile(r"^TDM-C-L\d$")
AGG_NODE = "TDM-E-L9-AGG"

# ── 18＋1 族表（v0；语义真源=调研档 §4，Q9 做T 自成一族）────────────────
FAM_CONDAXIS = "st-condaxis-20261013"
FAM_INFOAXIS = "st-infoaxis-20261013"
FAM_BATCH3 = "三批待开班（裁定#516 Q4：信息轴后）"
FAM_BATCH4 = "四批待开班（组合反馈＋L0 总装）"

FAMILY_TABLE: dict[str, dict[str, str]] = {
    "F01_大盘两态": {
        "goal_statement": "定「什么时候信什么信号」——形态三分类＋灰度＋拐点信号集",
        "output_contract": "形态三分类＋灰度值＋拐点信号集（condaxis P2 契约为准）",
        "campaign_ref": FAM_CONDAXIS,
    },
    "F02_情绪线": {
        "goal_statement": "快变量温度计＋事件源——L1 温度/L2 相位/L3 事件/L4 预测",
        "output_contract": "温度计档位＋相位＋情绪事件流＋滚动预测（三判据：校准/区分度/事件命中）",
        "campaign_ref": FAM_CONDAXIS,
    },
    "F03_板块线": {
        "goal_statement": "定「信哪个板块的什么信号」——主线梯队/生命周期/拐点/传导标的/闸门",
        "output_contract": "板块生命周期五态＋梯队＋拐点信号＋传导标的闸门",
        "campaign_ref": FAM_CONDAXIS,
    },
    "F04_资金行为": {
        "goal_statement": "定「谁在做、还剩谁没卖」——筹码结构/流量性质/主体画像/合成状态",
        "output_contract": "资金四件套＋合成状态变量（事件研究协议＋增量检验）",
        "campaign_ref": FAM_CONDAXIS,
    },
    "F05_传导链": {
        "goal_statement": "事件发生后算出「谁受益、多强、多久」",
        "output_contract": "受益标的集＋方向＋强度＋时滞四元组（chain_event_impact 事件流）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F06_股权穿透": {
        "goal_statement": "把关联网络变成联动信号",
        "output_contract": "同实控人/牛散跨票/质押链信号集（关联事件命中率验收）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F07_研报": {
        "goal_statement": "供「预期修正面」",
        "output_contract": "一致预期＋修正宽度＋评级变动事件流（修正信号 IC 验收）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F08_财报": {
        "goal_statement": "业绩事件＋健康分进选票",
        "output_contract": "超预期/恶化事件流＋财务健康分（PEAD 式事件研究验收）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F09_千股千评互动易": {
        "goal_statement": "出信号先行（散户情绪/公司活跃度微信号），一季内无增量则退役走墓碑",
        "output_contract": "散户情绪微信号＋公司活跃度微信号（带退役判据的考试卡）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F10_宏观S0": {
        "goal_statement": "宏观支撑/压制入总闸（归属=P0 挖矿后出建议，非保留面）",
        "output_contract": "宏观分＋政策事件流（对总闸档位的增量解释力验收）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F11_选股主链L3": {
        "goal_statement": "出「买什么」——候选池＋每股置信度＋适用域",
        "output_contract": "漏斗各级压缩率＋终池样本外 IC（九阶段链完整接通）",
        "campaign_ref": FAM_BATCH3,
    },
    "F12_卖出离场X": {
        "goal_statement": "接条件轴的扳机",
        "output_contract": "六桶信号集＋紧迫度分＋出场效率读数（回撤保护率/假信号率）",
        "campaign_ref": FAM_BATCH3,
    },
    "F13_持仓流P": {
        "goal_statement": "持仓活着（体检结论＋动作清单）",
        "output_contract": "体检结论与动作清单（逻辑存活判定的兑现率）",
        "campaign_ref": FAM_BATCH3,
    },
    "F13T_日内做T": {
        "goal_statement": "持有中增效——做T资格门＋做T信号集＋增厚读数",
        "output_contract": "做T资格判定＋信号集＋逐笔期望增益跟踪读数（增厚判据=逐笔期望增益口径）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F14_组合反馈C3": {
        "goal_statement": "考试-反馈闭环底座（归因报告→L0/L3 回写）",
        "output_contract": "归因报告＋升降级管线（归因解释力＋升降级命中率）",
        "campaign_ref": FAM_BATCH4,
    },
    "F15_L0作战计划": {
        "goal_statement": "全流总装：每天一纸计划",
        "output_contract": "总仓位档＋禁做清单＋分批预案＋应急线（计划-执行一致率）",
        "campaign_ref": FAM_BATCH4,
    },
    "F16_L4执行": {
        "goal_statement": "成本最小化成交",
        "output_contract": "滑点/冲击读数＋执行选型回写（执行成本对比基线）",
        "campaign_ref": "fullflow 在案（F041/F058 处方）",
    },
    "F17_L9汇聚": {
        "goal_statement": "供给健康可见——逐源线/逐节点就绪度读数",
        "output_contract": "l9_readiness_daily＋goal_readiness_daily 机生读数（AGG 汇总非红）",
        "campaign_ref": FAM_INFOAXIS,
    },
    "F18_挂起源线": {
        "goal_statement": "挂起有据，不进应通分母（Owner 门位）",
        "output_contract": "—（挂起登记：B/C 档 13 线/币圈/V2 快照，f31/f33 在册）",
        "campaign_ref": "Owner 门位（裁定#516 Q2）",
    },
}

_SUSPENDED_BASIS = {
    "B": "B 档源线显式挂起（f31 在册）",
    "C": "C 档源线显式挂起（f31 在册；C4 L2 逐笔委托不开采集=裁定#516 Q10）",
}


def _family_for(node_id: str) -> tuple[str, str]:
    """node_id → (family, status)。status∈{active,suspended,suspended_reference}。"""
    if RE_SRC_LINE.match(node_id):
        band = node_id.rsplit("-", 1)[-1][0]
        # band=f31 源线档位（A 在产/B 显式挂起/C 裁定挂起），非 governance_family
        # 复制语境——单字母 A-D 撞词表属误伤面，按 F7 通道声明非复制语境。
        if band in ("B", "C"):  # gate-vocab-context: governance_family
            return "F18_挂起源线", "suspended"
        return "F18_挂起源线", "suspended_reference"  # A 档在产源线=引用型不进分母
    if RE_CRYPTO.match(node_id):
        return "F18_挂起源线", "suspended"
    if node_id == AGG_NODE:
        return "F17_L9汇聚", "active"
    if node_id.startswith("TDM-E-L9-G"):
        g = node_id.rsplit("-", 1)[-1]
        if g == "G3":
            return "F06_股权穿透", "active"
        if g == "G4":
            return "F03_板块线", "active"
        return "F05_传导链", "active"
    if node_id.startswith("TDM-E-L9-V"):
        if node_id.endswith("V2"):
            return "F17_L9汇聚", "suspended"  # V2 快照定案挂起（f33 在册）
        return "F17_L9汇聚", "active"
    if node_id.startswith("TDM-E-L9-"):
        return "F17_L9汇聚", "active"  # D1/D2/E1/E2/Z1/Z2
    if node_id == "TDM-E-L1-S0":
        return "F10_宏观S0", "active"
    if node_id == "TDM-E-L1-S0-1":
        return "F02_情绪线", "active"  # 新闻情绪语义=情绪事件源
    if node_id.startswith("TDM-E-L1"):
        return "F01_大盘两态", "active"
    if node_id.startswith("TDM-E-L2-05"):
        return "F02_情绪线", "active"  # 水温响应=情绪消费
    if node_id.startswith("TDM-E-L2"):
        return "F03_板块线", "active"
    if node_id in ("TDM-E-L3-12-1", "TDM-E-L3-12-2", "TDM-E-L3-12-3"):
        return "F04_资金行为", "active"
    if node_id in ("TDM-E-L3-02", "TDM-E-L3-04"):
        return "F08_财报", "active"  # selection_funnel 挂接位＋负面否决器
    if node_id.startswith("TDM-E-L3-11"):
        return "F13T_日内做T", "active"
    if node_id.startswith("TDM-E-L3"):
        return "F11_选股主链L3", "active"
    if node_id.startswith("TDM-E-L4"):
        return "F16_L4执行", "active"
    if node_id == "TDM-E-L0-04":
        return "F02_情绪线", "active"  # 明日情绪盘中滚动预测
    if node_id.startswith("TDM-E-L0"):
        return "F15_L0作战计划", "active"
    if node_id.startswith("TDM-P-P2"):
        return "F13T_日内做T", "active"
    if node_id.startswith("TDM-P-"):
        return "F13_持仓流P", "active"
    if node_id.startswith("TDM-X-"):
        return "F12_卖出离场X", "active"
    if node_id.startswith("TDM-F-"):
        return "F14_组合反馈C3", "active"
    if node_id.endswith("-FLOW"):
        return "F11_选股主链L3", "active"  # E/X/P/F-FLOW 流出口
    raise RuntimeError(f"未映射节点: {node_id}")


def _exam_counts() -> dict[str, int]:
    """node_id → 考试卡张数（cards 以 node_id 字段绑定）。"""
    counts: dict[str, int] = {}
    for p in glob.glob(str(REPO_ROOT / EXAM_CARD_GLOB), recursive=True):
        try:
            c = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 坏卡不炸探针，计数为准
            continue
        nid = c.get("node_id") if isinstance(c, dict) else None
        if nid:
            counts[str(nid)] = counts.get(str(nid), 0) + 1
    return counts


def _goal_block_lines(node_id: str, exam_n: int) -> list[str]:
    fam, status = _family_for(node_id)
    spec = FAMILY_TABLE[fam]
    basis = ""
    if status != "active":
        m = RE_SRC_LINE.match(node_id)
        if m:
            basis = _SUSPENDED_BASIS.get(node_id.rsplit("-", 1)[-1][0], "A 档源线在产（引用型不进分母）")
        elif RE_CRYPTO.match(node_id):
            basis = "币圈骨架挂起（Q2 不进分母）"
        else:
            basis = "V2 快照定案挂起（f33 在册）"
    ref = (
        f"docs/03_modules/_domain_backtest/exam_cards/**/{node_id}__*（{exam_n} 张）"
        if exam_n
        else "PENDING：无绑定考试卡"
    )
    lines = [
        "  goal:",
        f"    family: {fam}",
        f'    goal_statement: "{spec["goal_statement"]}"',
        f'    output_contract: "{spec["output_contract"]}"',
        f'    exam_ref: "{ref}"',
        f'    campaign_ref: "{spec["campaign_ref"]}"',
        f"    status: {status}",
    ]
    if basis:
        lines.append(f'    suspension_basis: "{basis}"')
    return lines


RE_NODE_START = re.compile(r"^- node_id: (\S+)\s*$", re.M)
RE_GOAL_SUB = re.compile(r"^  goal:\n(?:^    .*\n?)*", re.M)


def _block_spans(text: str) -> list[tuple[str, int, int]]:
    """[(node_id, start, end_exclusive)]——下一「- node_id:」或下一顶级键（edges: 等）为界。"""
    lines = text.split("\n")
    starts: list[tuple[str, int]] = []
    top_key_after: dict[int, int] = {}
    for i, ln in enumerate(lines):
        m = RE_NODE_START.match(ln)
        if m:
            starts.append((m.group(1), i))
        elif starts and re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", ln):
            top_key_after.setdefault(len(starts) - 1, i)
    spans = []
    for k, (nid, s) in enumerate(starts):
        e = starts[k + 1][1] if k + 1 < len(starts) else top_key_after.get(k, len(lines))
        spans.append((nid, s, e))
    return spans


def inject(dry_run: bool = True) -> int:
    """外科注入：块尾剥旧 goal 子块→插新块；dry_run 仅解析校验不落盘。"""
    text = TDM_PATH.read_text(encoding="utf-8")
    exams = _exam_counts()
    lines = text.split("\n")
    spans = _block_spans(text)
    span_map = {nid: (s, e) for nid, s, e in spans}
    out: list[str] = []
    changed = 0
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = RE_NODE_START.match(ln)
        if not m:
            out.append(ln)
            i += 1
            continue
        nid = m.group(1)
        s, e = span_map[nid]
        out.append(ln)
        block = lines[s + 1 : e]
        block_txt = "\n".join(block)
        stripped = RE_GOAL_SUB.sub("", block_txt)
        new_block = stripped.split("\n") if stripped else []
        while new_block and new_block[-1] == "":
            new_block.pop()
        out.extend(new_block)
        out.extend(_goal_block_lines(nid, exams.get(nid, 0)))
        out.append("")  # 块间空行（保持既有版式节奏）
        changed += 1
        i = e
    new_text = "\n".join(out)
    if changed == 0:
        print("NO-OP：无节点块被处理")
        return 1
    d_new = yaml.safe_load(new_text)
    d_old = yaml.safe_load(text)
    if len(d_new["nodes"]) != len(d_old["nodes"]):
        raise RuntimeError(f"节点数守恒失败 {len(d_old['nodes'])}->{len(d_new['nodes'])}")
    with_goal = sum(1 for n in d_new["nodes"] if isinstance(n.get("goal"), dict))
    print(f"nodes={len(d_new['nodes'])} with_goal={with_goal} blocks_injected={changed}")
    if dry_run:
        print("DRY-RUN（--yes 落盘）")
        return 0
    from zephyr.shared.io.file_utils import safe_write_text

    res = safe_write_text(TDM_PATH, new_text, repo_root=REPO_ROOT, newline="\n")
    if not getattr(res, "written", False):
        raise RuntimeError(f"CAS 写失败: {getattr(res, 'reason', res)}")
    print(f"WRITTEN: {TDM_PATH}")
    return 0


def check() -> int:
    """漂移探针：goal 块存在性＋完整性＋族覆盖＋分母口径（零写）。"""
    d = yaml.safe_load(TDM_PATH.read_text(encoding="utf-8"))
    problems: list[str] = []
    fam_stat: dict[str, int] = {}
    core = 0
    for n in d["nodes"]:
        nid = n["node_id"]
        is_core = not (RE_SRC_LINE.match(nid) or RE_CRYPTO.match(nid) or nid == AGG_NODE)
        core += int(is_core)
        g = n.get("goal")
        fam, status = _family_for(nid)
        fam_stat[fam] = fam_stat.get(fam, 0) + 1
        if not isinstance(g, dict):
            problems.append(f"{nid}: 缺 goal 块")
            continue
        for f in ("goal_statement", "output_contract", "exam_ref", "campaign_ref", "status"):
            if not g.get(f):
                problems.append(f"{nid}: goal.{f} 缺失")
        if g.get("family") != fam:
            problems.append(f"{nid}: family 漂移 册={g.get('family')} 期望={fam}")
        # 分母内挂起合法例：V2 快照（f33 在册，挂起有据不计红）；分母外 active 合法例：AGG（引用型）
        if is_core and nid != "TDM-E-L9-V2" and g.get("status") != "active":
            problems.append(f"{nid}: 核心节点 status={g.get('status')} 应为 active")
        if not is_core and RE_SRC_LINE.match(nid) and g.get("status") == "active":
            problems.append(f"{nid}: 源线节点应标 suspended/suspended_reference")
    print(f"total={len(d['nodes'])} core={core} (口径 151) families={len(fam_stat)}")
    for f in sorted(fam_stat):
        print(f"  {f}: {fam_stat[f]}")
    if problems:
        print(f"DRIFT: {len(problems)} 问题")
        for p in problems[:20]:
            print("  -", p)
        return 2
    print("OK: goal 块全覆盖零漂移")
    return 0


_WAKE_TASK_KEYS = ("tdm", "goal", "exam_writeback", "trading_decision_map")


def maybe_inject_goal_blocks(task_id: object = None, success: bool = True, **_kwargs) -> dict:
    """调度器 task_completed 唤醒钩子（事件触发面；宪法 §9.3 禁轮询；永不反噬）。

    TDM/goal 系任务完成后跑 --check 探针：漂移只 log.warning 出声（注入动作仍走
    显式 CLI——探针=读面自动，写面=人工显式，写读分离）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in _WAKE_TASK_KEYS):
        return {"action": "skipped_wake_point"}
    try:
        rc = check()
        if rc != 0:
            import logging

            logging.getLogger(__name__).warning("[TDM-GOAL] goal 块漂移出声（探针面）: rc=%d", rc)
            return {"action": "drift_detected"}
        return {"action": "clean"}
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬
        return {"action": "error", "reason": str(exc)[:200]}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)  # noqa: m11-perm-manual-legitimate  AI/维护按需调用的 goal 块注入/探针 runner（读面事件化=maybe_inject_goal_blocks，写面显式 CLI=设计意图）
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--inject", action="store_true", help="注入/刷新 goal 块（缺 --yes=dry-run）")
    g.add_argument("--check", action="store_true", help="漂移探针（零写，漂移 exit 2）")
    g.add_argument("--stats", action="store_true", help="族分布统计（零写）")
    p.add_argument("--yes", action="store_true", help="配合 --inject 落盘")
    args = p.parse_args(argv)
    if args.inject:
        return inject(dry_run=not args.yes)
    if args.check:
        return check()
    d = yaml.safe_load(TDM_PATH.read_text(encoding="utf-8"))
    from collections import Counter

    c = Counter(_family_for(n["node_id"])[0] for n in d["nodes"])
    print(f"nodes={len(d['nodes'])}")
    for f, k in sorted(c.items()):
        print(f"  {f}: {k}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维一次性注入器＋漂移探针——AI/CI 按需直调（--inject 落盘/--check 读数），非 cron/Timer/sleep-loop/daemon/常驻服务；goal 块读数消费方=l9/goal_readiness 聚合器事件链，本件不订阅事件属合法 manual 面
    raise SystemExit(main())
