# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/wave3/supply_ledger_report.md | §7
# [MODULE] scripts.governance.data_supply.gen_registration_needs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.data_supply.supply_sources
# [CONSUMERS] 人工/CI 重跑出 docs/_working/total_command_closeout/wave3/registration_needs.yaml; 无生产消费方
# [STARTUP] manual
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 治理锚定头缺失 -> 该件记 ANCHOR_INCOMPLETE 行（不静默漏件）
# [A_module] module_id=MOD-GOV-DS-REGEN | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""生成 wave3/registration_needs.yaml（清单派生自真实件头，禁手工维护）。

AGENTS.md §9 第 5 条「静态清单禁手工维护」：待登记件是"条目列表 + 计数"，因此本件从
新建 .py 的治理锚定头（`[MODULE] / [CONSUMERS] / [STARTUP] / [TTL] / [A_module]`）
现读现出，重复跑即与盘面同步。
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_OUT = _ROOT / "docs" / "_working" / "total_command_closeout" / "wave3" / "registration_needs.yaml"
_SCAN_DIRS = ("scripts/governance/data_supply", "tests/governance/data_supply")
_TAG_RE = re.compile(r"^#\s*\[(?P<tag>MODULE|CONSUMERS|STARTUP|TTL|A_module)\]\s*(?P<val>.*?)\s*$")


def _anchors(path: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[:30]:
        m = _TAG_RE.match(line.strip())
        if m:
            found[m.group("tag")] = m.group("val")
    return found


def _module_id(anchors: dict[str, str]) -> str:
    text = anchors.get("A_module", "")
    match = re.search(r"module_id=([^|]+)", text)
    return match.group(1).strip() if match else ""


def _consumers(anchors: dict[str, str]) -> list[str]:
    raw = anchors.get("CONSUMERS", "")
    return [x.strip() for x in raw.split(";") if x.strip()]


def _collect(root: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for rel_dir in _SCAN_DIRS:
        base = root / rel_dir
        for path in sorted(base.glob("*.py")) if base.is_dir() else []:
            anchors = _anchors(path)
            items.append(
                {
                    "path": f"{rel_dir}/{path.name}",
                    "module": anchors.get("MODULE", ""),
                    "module_id": _module_id(anchors),
                    "startup": anchors.get("STARTUP", ""),
                    "ttl": anchors.get("TTL", ""),
                    "consumers": _consumers(anchors),
                    "anchor_complete": bool(
                        anchors.get("MODULE")
                        and anchors.get("CONSUMERS")
                        and anchors.get("STARTUP")
                        and anchors.get("TTL")
                        and _module_id(anchors)
                    ),
                }
            )
    return items


def _pending_mounts() -> list[dict[str, object]]:
    """判据与生产宿主之间的接线（本包写权之外，逐项申报，不虚报已挂）。"""
    return [
        {
            "target": ".github/workflows/governance.yml",
            "action": "新增一步 `python scripts/governance/data_supply/check_wave3_rulers.py --counterfactual`（rc 非 0 即断链）",
            "why": "W-102 三把尺常设化；控制组点不红＝尺已退化为装饰件，须 CI 硬拦",
            "owner_gate": "非门位（工作流文件在本施工包写权之外）",
        },
        {
            "target": ".github/workflows/governance.yml",
            "action": "新增一步 `... check_wave3_rulers.py --check --offline`（有 CH 的槽位再补 `--check`）",
            "why": "禁缓存背书尺的常设绿面",
            "owner_gate": "非门位",
        },
        {
            "target": "src/zephyr/data/integrity_checker.py::_reconcile_task_runs",
            "action": "把 false_green_crosscheck.evaluate() 接为该函数的真值腿；同批改掉它自陈的'失败返回 {}'fail-silent",
            "why": "3.2（W-31/Z-16）：该宿主只对账台账、不回读目标表，正是假绿宿主",
            "owner_gate": "需 Owner/域主批准（改生产数据域代码）",
        },
        {
            "target": "src/zephyr/data/supply_sentinel.py（scheduler L238 data_supply_sentinel 槽位）",
            "action": "把 supply_conservation.evaluate() 作为该哨兵的新维度（守恒腿），阈值仍读 data_supply_sentinel.yaml",
            "why": "3.3（W-32/G-22）内收：扩既有宿主，不建第二套对账面",
            "owner_gate": "需 Owner/域主批准",
        },
        {
            "target": "gate_registry.yaml / 新尺准入面",
            "action": "准入条件加一条：新增判据尺必须声明其反事实控制组入口",
            "why": "Z-16 尾列硬要求；热册，本包未动",
            "owner_gate": "Owner（注册表净增/热册）",
        },
        {
            "target": "src/zephyr/intelligence/observability/（包归属）",
            "action": "定包归属后再决定是否把两把尺的子件迁入；本包未建该包任何件",
            "why": "许可是「不撞前提下新建子件」，而该目录实测不存在＝建包即撞车面",
            "owner_gate": "Owner/车道协调",
        },
        {
            "target": "add_module_translation.py / TRANSLATION-COVERAGE gate",
            "action": "为本包 9 个新 .py 登记大白话简介",
            "why": "新建 .py 登记义务（本包无权写热册）",
            "owner_gate": "非门位",
        },
        {
            "target": "CREATE-GUARD creation_token",
            "action": "为本包 12 个新文件（9 .py + tests/__init__.py + 2 案卷件）登记 creation_token",
            "why": "CREATE-GUARD 要求新建 .py/.yaml/.md 登记；tests/ 部分豁免以落地侧判定为准",
            "owner_gate": "非门位",
        },
    ]


def build_payload(root: Path, generated_at: dt.datetime) -> dict[str, object]:
    items = _collect(root)
    return {
        "generated_by": "scripts/governance/data_supply/gen_registration_needs.py",
        "generated_at_utc": generated_at.isoformat(),
        "note_zh": "本清单由生成器现读现出（AGENTS.md §9 第 5 条）；重跑即与盘面同步，禁手工增删条目。",
        "total_new_files": len(items) + 2,
        "total_pending_mounts": len(_pending_mounts()),
        "new_files": items,
        "anchor_incomplete": [i["path"] for i in items if not i["anchor_complete"]],
        "pending_mounts": _pending_mounts(),
        "not_registered_here_zh": [
            "裁定号：本包未自赋任何 #NNN（RULE-RULING 走 ruling_registry 正式通道）",
            "阈值/断言/skip/xfail：零改动",
            "docs/01_policies_and_standards/**、config/flags.yaml、热册：零改动",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    payload = build_payload(_ROOT, dt.datetime.now(dt.timezone.utc))
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=110),
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {_OUT} files={payload['total_new_files']} mounts={payload['total_pending_mounts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
