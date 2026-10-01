# [MODULE] zephyr.data.miniqmt_caliber_sentinel
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#       退役条件=全仓 miniQMT 文案面收敛完毕且无 pending 交接件）
# [STARTUP] imported
#   （原值 lazy：纯文本扫描，无 IO 副作用之外的全局状态；不挂调度槽，由尺测试/人工 CLI 调用）——GATE-VOCAB 词表归正 imported）
# [CONSUMERS] tests/data/test_wave3_miniqmt_caliber.py（波 3.7 红证 + 回退拦截）;
#             人工排查 `python -m zephyr.data.miniqmt_caliber_sentinel`
# [DEPENDENCIES] 仅 stdlib re/pathlib/dataclasses
# [INVARIANTS] 在册正确口径＝**miniQMT 仅"实盘"通道退役；模拟盘的分钟/tick 唯一源仍是在用状态**
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_DATA
# [MATURITY] draft
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
#              （旧口径"全面清退/已退役/断供"= 把模拟盘供数源也判了死刑，会误导下游断供排产）；
#              尺只在"同一行既点 miniQMT 主题、又出现旧口径词、且无实盘/模拟盘范围限定词"时开火，
#              禁扩成全文模糊匹配（误报会把人推回去放宽尺——在册教训）；
#              本件只读文本、不改文件、不判资金链路
"""miniQMT 口径回退哨兵尺（波 3.7）——命中旧口径文案即红。

工作树里这套文案改过又被回退过一次（00 册 W-37 状态列 🔨被回退），故本尺的 duty 是
"回退即红"，不是"再抄一份口径说明"。界内已修面 `ENFORCED_FILES` 严格零命中；
越界待修面 `PENDING_HANDOFF_FILES`（本包写域外，禁越界改）只登记路径、由尺报告现状。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/wave3/miniqmt_caliber_sentinel.yaml

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

from zephyr.shared.io.paths import REPO_ROOT  # SSoT canonical（SSOT-REDEFINITION 门：禁本地重定义）

__all__: Final = [
    "CALIBER_TRUE",
    "CaliberFinding",
    "ENFORCED_FILES",
    "PENDING_HANDOFF_FILES",
    "enforced_findings",
    "find_old_caliber",
    "pending_findings",
    "scan_file",
    "scan_tree",
]


#: 在册正确口径（唯一表述真源，文档/注释引用它而非再抄一遍）
CALIBER_TRUE = "miniQMT 仅实盘通道退役；模拟盘的分钟/tick 唯一源仍是在用状态"

_TOPIC_RX = re.compile(r"miniqmt|mini\s*qmt|xtmini", re.IGNORECASE)
_OLD_RX = re.compile(
    r"全面清退|已退役|清退|退役冻结|断供|无在跑供给通道|退役后转历史|通道退役冻结"
    r"|下线"  # G 册第 10 条另三件之 HANDOFF 写法："MiniQMT 09-18 下线"=旧口径变体
)
_SCOPE_RX = re.compile(r"仅实盘|模拟盘|实盘.{0,6}退役|实盘通道")


@dataclass(frozen=True)
class CaliberFinding:
    """一行旧口径命中（尺的开火记录）。"""

    path: str
    lineno: int
    line: str

    def render(self) -> str:
        return f"{self.path}:{self.lineno}: {self.line.strip()[:160]}"


def find_old_caliber(text: str) -> list[tuple[int, str]]:
    """文本 → 命中旧口径的行号/原行（纯函数，测试直测；无副作用）。"""
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if not _TOPIC_RX.search(line):
            continue
        if not _OLD_RX.search(line):
            continue
        if _SCOPE_RX.search(line):
            continue  # 已带"仅实盘/模拟盘"范围限定 = 正确口径，放行
        hits.append((i, line))
    return hits


def scan_file(path: Path | str) -> list[CaliberFinding]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"口径尺找不到被扫文件: {p}")
    text = p.read_text(encoding="utf-8", errors="replace")
    rel = _rel(p)
    return [CaliberFinding(rel, ln, line) for ln, line in find_old_caliber(text)]


def scan_tree(root: Path | str, suffixes: Iterable[str] = (".py", ".yaml", ".yml", ".md")) -> list[CaliberFinding]:
    r = Path(root)
    out: list[CaliberFinding] = []
    for f in sorted(r.rglob("*")):
        if f.is_file() and f.suffix in set(suffixes):
            out.extend(scan_file(f))
    return out


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


#: 本包写域内、已按正确口径修好的文件——尺对其严格零容忍
ENFORCED_FILES: tuple[str, ...] = (
    "src/zephyr/data/config/known_data_gaps.yaml",
    "src/zephyr/data/config/data_supply_sentinel.yaml",
)

#: G 册第 10 条点名、但落在本包写域外的口径件（交接给兄弟道；尺只报告不判红，
#: 兄弟道修完后本元组须同步删除——由 test_pending_paths_exist 保证不指空路径）
PENDING_HANDOFF_FILES: tuple[str, ...] = (
    "src/zephyr/ex_core/miniqmt_channel_manager.py",
    "src/zephyr/backtest/implementations/ch_tick_replay.py",
    "src/zephyr/frontend/dashboard/web/features/bridge/br-page.js",
    "src/zephyr/frontend/dashboard/web/pages/bridge.html",
    "docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md",
)


def enforced_findings(base: Path | None = None) -> list[CaliberFinding]:
    b = base or REPO_ROOT
    out: list[CaliberFinding] = []
    for rel in ENFORCED_FILES:
        out.extend(scan_file(b / rel))
    return out


def pending_findings(base: Path | None = None) -> list[CaliberFinding]:
    b = base or REPO_ROOT
    out: list[CaliberFinding] = []
    for rel in PENDING_HANDOFF_FILES:
        p = b / rel
        if p.exists():
            out.extend(scan_file(p))
    return out


if __name__ == "__main__":  # 人工 CLI：打印开火清单（只读）
    ef = enforced_findings()
    pf = pending_findings()
    print(f"口径真源：{CALIBER_TRUE}")
    print(f"[enforced] 命中 {len(ef)} 行（应为 0）")
    for f in ef:
        print("  RED", f.render())
    print(f"[pending 交接（越界不判红）] 命中 {len(pf)} 行")
    for f in pf:
        print("  PEND", f.render())
    raise SystemExit(1 if ef else 0)
