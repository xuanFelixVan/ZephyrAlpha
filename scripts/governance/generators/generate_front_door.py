# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_front_door.py | §
# [MODULE] scripts.governance.generators.generate_front_door
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出零时间戳=逐字节 regen 幂等；只读永久区真源（INDEX.md/ROOR/registry_master_index/根宪法），禁读写临时区；只新增 FRONT_DOOR.md+llms.txt 两产物，不改任何输入（含 INDEX.md）；真源解析失败=非零退出不落盘
# [MODIFY-GUARD] 产物 docs/library/FRONT_DOOR.md 与 llms.txt 为机生禁手改（手改必被覆盖）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失/解析失败/超行数上限=SystemExit 非零，不写半成品
# [TESTS] regen-clean CLI 自证：--check 零漂移 + 连跑两次第二次跳写（生成闭环支柱）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
generate_front_door.py — FRONT-DOOR 门口文件 + llms.txt 双投生成器（FMS 改造 B56）

从既有真源派生两份导航产物（零手维护、零手写计数）：
  输入：docs/library/INDEX.md（七馆计数，generate_library_index.py 产物）
        docs/registry_of_registries.yaml（ROOR，仅取行数与存在性，散文/计数不复制）
        docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml（total_registries 字段）
        根 AGENTS.md（行数 + §7 速查锚点校验）
        .trae/rules/project_rules.md（行数）、data/capability_cards/（卡片数）
  输出：docs/library/FRONT_DOOR.md（中文任务操作单，≤100 行）
        llms.txt（英文最小路由，≤60 行，社区约定格式）

分工去重由本器结构保证：llms.txt 只允许标题+链接行+一句话注释（无表格/命令块槽位）；
FRONT_DOOR 承载操作级表格与命令全文；两文件重叠面=链接目标，零内容复制。

对标 S6 导航与上下文经济学挖矿簿（docs/_working/fms_overhaul/S6_navigation_context/README.md §4.5）。

Usage:
    python scripts/governance/generators/generate_front_door.py
    python scripts/governance/generators/generate_front_door.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_if_changed  # noqa: E402
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --check, type: bool, description: "检测漂移（产物与真源派生结果不一致即报）"}
warn_only: false
description: >
  从 INDEX.md/ROOR/registry_master_index/根宪法派生 FRONT_DOOR.md 与 llms.txt 双投导航产物。
  输出零时间戳，regen 幂等；--check 报漂移。
"""

FRONT_DOOR_PATH = REPO_ROOT / "docs" / "library" / "FRONT_DOOR.md"
LLMS_TXT_PATH = REPO_ROOT / "llms.txt"
LIBRARY_INDEX_PATH = REPO_ROOT / "docs" / "library" / "INDEX.md"
ROOR_PATH = REPO_ROOT / "docs" / "registry_of_registries.yaml"
MASTER_INDEX_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_master_index.yaml"
)
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
PROJECT_RULES_PATH = REPO_ROOT / ".trae" / "rules" / "project_rules.md"
CAPABILITY_CARDS_DIR = REPO_ROOT / "data" / "capability_cards"

FRONT_DOOR_MAX_LINES = 100
LLMS_TXT_MAX_LINES = 60

# 七馆顺序 = S6 草案口径（INDEX.md 同序）；缺馆即失败，防静默半成品。
HALL_ORDER = ("代码馆", "数据馆", "文档馆", "制度馆", "闸门馆", "管线馆", "基建与备份馆")
_LIBRARY_PAGE_PREFIX = "docs/library/"


def _read_lines(path: Path) -> list[str]:
    """读永久区真源为行列表；缺失即失败（fail-closed，不产半成品）。"""
    if not path.exists():
        raise SystemExit(f"FAIL: 真源缺失 {path}")
    return path.read_text(encoding="utf-8").splitlines()


def _count_lines(path: Path) -> int:
    return len(_read_lines(path))


def parse_library_index() -> tuple[dict[str, tuple[str, int]], int]:
    """解析 INDEX.md 七馆计数与在编总数 → ({馆名: (repo相对页路径, 计数)}, 总数)。"""
    lines = _read_lines(LIBRARY_INDEX_PATH)
    total = 0
    halls: dict[str, tuple[str, int]] = {}
    link_rx = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for line in lines:
        m = re.search(r"在编资产总数：([\d,]+)", line)
        if m:
            total = int(m.group(1).replace(",", ""))
            continue
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] == "馆":
            continue
        hall, page_cell, count_cell = cells
        link = link_rx.search(page_cell)
        if not hall or link is None or not count_cell.isdigit():
            continue
        halls[hall] = (_LIBRARY_PAGE_PREFIX + link.group(2), int(count_cell))
    missing = [h for h in HALL_ORDER if h not in halls]
    if missing:
        raise SystemExit(f"FAIL: INDEX.md 七馆解析缺馆 {missing}——真源不完整，拒绝生成（INDEX.md 归他会话/生成链管）")
    if total <= 0:
        raise SystemExit("FAIL: INDEX.md 在编资产总数解析失败——拒绝生成")
    return halls, total


def parse_total_registries() -> int:
    """从机生总索引取 total_registries 字段（计数用字段不写死——宪法 §4.3）。"""
    data = load_yaml(MASTER_INDEX_PATH)
    value = (data or {}).get("total_registries")
    if not isinstance(value, int) or value <= 0:
        raise SystemExit(f"FAIL: {MASTER_INDEX_PATH} total_registries 字段缺失或非法")
    return value


def verify_constitution_anchor() -> int:
    """校验根宪法 §7 速查锚点在盘（派生源健康检查），返回行数供 llms.txt 注入。"""
    lines = _read_lines(AGENTS_PATH)
    text = "\n".join(lines)
    if "## 7. 核心系统速查" not in text or "scripts/git_commit.py" not in text:
        raise SystemExit("FAIL: 根 AGENTS.md §7 速查锚点漂移——FRONT_DOOR 紧急路径真源失锚，拒绝生成")
    return len(lines)


def build_front_door(halls: dict[str, tuple[str, int]]) -> str:
    """构建 docs/library/FRONT_DOOR.md 全文（零时间戳，regen 幂等）。"""
    hall_rows = "\n".join(f"| {h} | {halls[h][0]} | {halls[h][1]} |" for h in HALL_ORDER)
    content = f"""---
ttl: permanent
doc_type: index
generated_by: scripts/governance/generators/generate_front_door.py
---

<!-- GENERATED FILE — regenerate: python scripts/governance/generators/generate_front_door.py && git diff --exit-code；手改必被覆盖 -->

# ZephyrAlpha 前台门口（FRONT-DOOR）

> 使命：任何 AI/人从本页出发，最多 2 跳抵达任意资产真源。本页是派生视图，真源见各链接；先单口后 Grep，路径禁凭记忆书写（根宪法 §8）。

## 查询五单口

| 你要找 | 唯一入口 | 备注 |
|---|---|---|
| 能力/文件/模块（关键词） | `python -m zephyr.library.lookup <关键词>` | 全馆在编资产；表级真源暂走下行数据册（缺口移交 S5） |
| 注册表（哪个册管什么） | `docs/registry_of_registries.yaml`（ROOR）；册数总索引=`docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml` | 注册表发现唯一真源；总数以字段为准勿背数 |
| 模块/依赖全景 | `python scripts/governance/extract_depgraph.py --summary` | PostgreSQL depgraph，禁裸连 |
| 全图全库对齐 | `alignment_checklist.md`；`python scripts/governance/align_all.py` | 对齐键=module_id/step_id |
| 数据表真源 | 表名 grep `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（REG-DATAFLOW-001）；库连接走 `zephyr.infrastructure.database_service` | lookup 暂不索引表名 |

## 图书馆七馆（计数由生成器注入，勿手填）

| 馆 | 页 | 在编数 |
|---|---|---|
{hall_rows}

## 高频紧急路径

| 场景 | 直达 |
|---|---|
| 宪法（必读 L0） | `AGENTS.md`（IDE 同时注入 `.trae/rules/project_rules.md`） |
| 门禁定义 | commit 门=`src/zephyr/gov_enforcement/commit_gates/`（代码 GateSpec 注册）+ 机生总册 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`；规则管线门=`src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` |
| 提交 | `python scripts/git_commit.py --session <sid> --files <清单>`（禁裸 git commit；锁忙走 `scripts/commit_queue.py --enqueue`） |
| 编辑消失/告警 | 先查 `.runtime/workspace_alerts/stash_notice.json`（stash 保存非丢失）；reaper 状态 `python -m zephyr.trading.process_reaper --status` |
| 新建文件 | 先 creation_token（`scripts/governance/d3_metadata/batch_creation_tokens.py`），再写；7 格式全覆盖（tests/ 豁免） |

## 十年机制五支柱（一行索引；真源=根宪法与本战役骨架）

1. 棘轮：坏指标只降不升，存量入基线豁免。2. 单写者：每类事实一个真源平面，读侧唯一入口=图书馆 lookup。3. 生成闭环：生成物必过 `regenerate && diff --exit-code`。4. 生命周期隔离：永久区禁引临时区（根宪法 §9 条目 4）。5. 墓碑去向：死亡资产留 successor_of 指针。

## 维护说明

- 本页由 generate_front_door.py 从 ROOR/registry_master_index/INDEX.md/根宪法 §7 派生，禁手改。
- 发现本页与真源不一致 = 立即 regenerate；仍不一致 = 真源有病，修真源而非本页。
"""
    if content.count("\n") > FRONT_DOOR_MAX_LINES:
        raise SystemExit(f"FAIL: FRONT_DOOR.md 超 {FRONT_DOOR_MAX_LINES} 行硬上限")
    return content


def build_llms_txt(
    total_assets: int,
    agents_lines: int,
    project_rules_lines: int,
    roor_lines: int,
    total_registries: int,
    card_count: int,
) -> str:
    """构建根 llms.txt 全文（英文最小路由；只允许标题+链接行+一句话注释，零表格）。"""
    content = f"""# ZephyrAlpha

> AI-native quantitative trading platform (100% AI-developed, {total_assets // 1000}k+ registered assets).
> Read AGENTS.md before any write operation; this file is a router only — linked files are the single sources of truth.

## Constitution (must read first)
- [AGENTS.md](AGENTS.md): L0 constitution, {agents_lines} lines (hard cap 300). Cold-start sequence + hard rules.
- [.trae/rules/project_rules.md](.trae/rules/project_rules.md): IDE-injected second entry ({project_rules_lines} lines).

## Query single entries (never write paths from memory)
- [Library INDEX](docs/library/INDEX.md): 7 halls index; query via `python -m zephyr.library.lookup <keyword>`
- [FRONT-DOOR](docs/library/FRONT_DOOR.md): task-routed operation entries (Chinese, canonical door)
- [Registry of Registries](docs/registry_of_registries.yaml): which registry governs what ({roor_lines} lines, read targeted)
- [Registry master index](docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml): generated catalog of {total_registries} registries
- [Data asset registry](docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml): table/dataset/source SSOT

## High-frequency paths
- Commit: `python scripts/git_commit.py --session <sid> --files <list>` (bare `git commit` forbidden)
- Modules/dependencies: `python scripts/governance/extract_depgraph.py --summary` (PostgreSQL; no direct connections)
- Gates: `src/zephyr/gov_enforcement/commit_gates/` (code-registered GateSpec) + generated [gate registry](docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml)
- Alerts: `.runtime/workspace_alerts/stash_notice.json` (missing edits were stashed, not lost)
- Capability cards: `data/capability_cards/` ({card_count} progressive-disclosure cards)

## Generated view notice
- docs/library/FRONT_DOOR.md and this file are regenerated by
  `scripts/governance/generators/generate_front_door.py`. Do not edit by hand.
"""
    if content.count("\n") > LLMS_TXT_MAX_LINES:
        raise SystemExit(f"FAIL: llms.txt 超 {LLMS_TXT_MAX_LINES} 行硬上限")
    return content


def build_outputs() -> dict[str, tuple[Path, str]]:
    """收集全部真源 → 双投产物 {(路径, 内容)}。"""
    halls, total_assets = parse_library_index()
    total_registries = parse_total_registries()
    agents_lines = verify_constitution_anchor()
    roor_lines = _count_lines(ROOR_PATH)
    project_rules_lines = _count_lines(PROJECT_RULES_PATH)
    card_count = len(list(CAPABILITY_CARDS_DIR.glob("*.yaml")))
    return {
        "FRONT_DOOR.md": (FRONT_DOOR_PATH, build_front_door(halls)),
        "llms.txt": (
            LLMS_TXT_PATH,
            build_llms_txt(total_assets, agents_lines, project_rules_lines, roor_lines, total_registries, card_count),
        ),
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="FRONT-DOOR 门口文件 + llms.txt 双投生成器（FMS B56）")
    parser.add_argument("--check", action="store_true", help="检测漂移：派生结果与盘面不一致即非零退出")
    args = parser.parse_args()

    outputs = build_outputs()

    if args.check:
        drift = []
        for name, (path, content) in outputs.items():
            if not path.exists():
                drift.append(f"{name}: 盘面缺失")
            elif path.read_text(encoding="utf-8") != content:
                drift.append(f"{name}: 盘面与派生结果不一致（{path}）")
        if drift:
            print("DRIFT: " + "；".join(drift))
            print("修复：python scripts/governance/generators/generate_front_door.py")
            sys.exit(EXIT_FINDINGS)
        print("OK: FRONT_DOOR.md 与 llms.txt 均与真源派生结果一致（零漂移）")
        return

    for name, (path, content) in outputs.items():
        written = atomic_write_if_changed(path, content)
        note = "" if written else "（内容未变，跳写——幂等）"
        print(f"已生成 {name}（{content.count(chr(10))} 行）→ {path}{note}")


if __name__ == "__main__":
    main()
