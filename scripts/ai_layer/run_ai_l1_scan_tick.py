# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] scripts.ai_layer.run_ai_l1_scan_tick
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/ai_layer/gen_search_veins.py（同目录兄弟模块，幂等矿脉再生生成器）;
#                zephyr.ai_layer.perceive.search_orders（SearchOrderJournal.expire_due）
# [CONSUMERS] scripts/register_ai_l1_scan_task.ps1（Windows 计划任务宿主，节拍=OS 任务计划程序）
# [STARTUP] scheduled_task
# [MATURITY] new
# [INVARIANTS] 本件=L1 施工项 7「外扫节拍宿主」的被调 tick：①矿脉再生（gen_search_veins，幂等，
#              其 M11 注“运维CLI入口由外部排班/人工点火”所指宿主即本链）②搜索任务单 TTL 过期清
#              （expire_due 事件语义：到期重排=新单，禁复活旧单）。代码内零定时器零 sleep-loop
#              （宪法 §9.3——节拍由 OS 任务计划程序提供，非本进程常驻）；只读派生+运行态 journal
#              写（.runtime/ai_layer/perceive/search_orders/ 既有枚举落点，非 data/ 生产路径）；
#              T3 双前置（R1-F2 裁定）：resource_profile 画像登记 + 裁定登记，两项未齐禁止启用
#              计划任务——守卫在 register_ai_l1_scan_task.ps1 内置，本件被调时不重复判
# [MODIFY-GUARD] docs/_working/ai_layer_vision/P1_full_construction_inventory.md L1 项 7；
#                docs/_working/fullflow_mining/m4_ai_layer/接续收口_20260925/03_f94_f95_construction_orders.md L1-WO-7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] gen_search_veins.main 退出码原样透传（再生失败=本 tick 失败，不吞不续跑写侧）；
#                  search_orders 异常上抛（journal 写失败绝不静默）
# [TESTS] tests/ai_layer/perceive/（宿主依赖件既有测试覆盖；本件为胶水 CLI，验证=启用时人工
#         dry-run+月检外扫段出数，见车道记录册 §复核）
# [TTL] permanent
"""run_ai_l1_scan_tick — L1 外扫节拍宿主 tick（施工项 7，AI2 车道 2026-09-26）。

计划任务动作行的真身（见 ``scripts/register_ai_l1_scan_task.ps1``——该 ps1 属 T3 双前置
门控件，**资源画像登记 + 裁定登记** 齐备并经 Owner 点头启用前不得注册运行）。

用法::

    python scripts/ai_layer/run_ai_l1_scan_tick.py [--dry-run]

``--dry-run`` 透传矿脉再生生成器（只打印派生计数零写入）；TTL 过期清在非 dry-run 下执行。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final

_HERE: Final = Path(__file__).resolve().parent
_REPO: Final = _HERE.parents[1]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_HERE))

import gen_search_veins  # noqa: E402  同目录兄弟（scripts 间依赖，仓内既有惯例）

from zephyr.ai_layer.perceive.search_orders import SearchOrderJournal  # noqa: E402

# create-guard-not-dup: 本件是 L1 外扫单次节拍宿主 CLI（到点执行搜索脉络再生+落台账后即退），非 liquidity_crisis_manager 流动性 tick 能力的第二实现，命中词=通用语料噪声


def main(argv: list[str] | None = None) -> int:
    """单拍：矿脉再生→任务单 TTL 过期清；退出码取再生侧（fail-closed 主信号）。"""
    args = list(argv or [])
    os.chdir(_REPO)  # 计划任务 cwd 不定，产物默认路径按仓根锚定
    rc = int(gen_search_veins.main(args))
    if "--dry-run" in args:
        print("tick dry-run: veins regen only, expire_due skipped")
        return rc
    expired = SearchOrderJournal().expire_due()
    print(f"veins regen rc={rc}; expired_orders={len(expired)}; ids={expired[:5]}")
    return rc


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: OS 计划任务宿主入口（外部排班点火），非自动常驻任务
    sys.exit(main(sys.argv[1:]))
