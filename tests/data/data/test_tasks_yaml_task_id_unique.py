# [MODULE] tests.data.data.test_tasks_yaml_task_id_unique
# [DOMAIN] D_DATA
# [TTL] task_bound

"""tasks.yaml 同键防重门（Owner 批裁定「立项，机械去重+判重测试钉死」，st-t3b-dedup 2026-10-08）。

背景：全仓唯一重复 task_id=cohort_ledger_daily（fig12 WB12-49 在案）自 2026-09-23 起每夜
16:30/18:00 双触发（scheduler list 直载无判重+TaskQueue 跨批依赖视为已满足）；2026-10-08
去重收敛为 daily_capital 正身后，本门钉死回归：
  - 真册只读断言 task_id 全仓唯一 + cohort 正身字段（schedule/trading_day_only 裁定锚）；
  - tmp_path 注入面：重复 task_id 注入必被拦（红），合法唯一键必放行（绿）。
真册零写入（禁写生产路径）；判重器在本模块定义（消费语义=scheduler/task_queue 同型：
同键唯一是调度注册的最小一致性不变量）。
"""

from __future__ import annotations

import collections
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TASKS_YAML = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "tasks.yaml"


def find_duplicate_task_ids(tasks: list[dict]) -> list[str]:
    """返回重复出现的 task_id（排序去重）；空列表=无重复（放行）。"""
    counts = collections.Counter(t.get("task_id") for t in tasks)
    return sorted(tid for tid, n in counts.items() if tid is not None and n > 1)


def _load_real_tasks() -> list[dict]:
    with open(_TASKS_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("tasks") or []


# ── 绿：真册回归钉死 ─────────────────────────────────────────────────────
def test_real_registry_task_ids_unique():
    tasks = _load_real_tasks()
    assert tasks, "tasks.yaml 加载为空（文件缺失或结构漂移）"
    dups = find_duplicate_task_ids(tasks)
    assert not dups, f"tasks.yaml 出现重复 task_id（回归 WB12-49）：{dups}"


def test_real_registry_cohort_keeper_is_daily_capital():
    """去重裁定锚：cohort_ledger_daily 唯一正身=daily_capital 档+trading_day_only 守卫。"""
    co = [t for t in _load_real_tasks() if t.get("task_id") == "cohort_ledger_daily"]
    assert len(co) == 1, f"cohort_ledger_daily 应恰 1 条，实为 {len(co)}"
    assert co[0].get("schedule") == "daily_capital"
    assert (co[0].get("extra") or {}).get("trading_day_only") is True


# ── 红：重复注入必拦（tmp_path 隔离，零生产写入）────────────────────────
def test_injected_duplicate_task_id_is_caught(tmp_path):
    payload = {
        "tasks": [
            {"task_id": "dup_task", "table": "c0_meta.x", "schedule": "daily_kline"},
            {"task_id": "dup_task", "table": "c0_meta.y", "schedule": "daily_capital"},
            {"task_id": "solo_task", "table": "c0_meta.z", "schedule": "daily_kline"},
        ]
    }
    p = tmp_path / "tasks_inject.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with open(p, encoding="utf-8") as f:
        tasks = (yaml.safe_load(f) or {}).get("tasks") or []
    assert find_duplicate_task_ids(tasks) == ["dup_task"], "重复 task_id 注入未被拦截"


# ── 绿：合法唯一键放行 ───────────────────────────────────────────────────
def test_injected_unique_keys_pass(tmp_path):
    payload = {
        "tasks": [{"task_id": f"ok_task_{i}", "table": f"c0_meta.t{i}", "schedule": "daily_kline"} for i in range(3)]
    }
    p = tmp_path / "tasks_ok.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with open(p, encoding="utf-8") as f:
        tasks = (yaml.safe_load(f) or {}).get("tasks") or []
    assert find_duplicate_task_ids(tasks) == []
